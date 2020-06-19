"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""
    opcodes = {"HLT": 0b00000001,    # 1
               "LDI": 0b10000010,    # 130
               "PRN": 0b01000111,    # 71
               "MUL": 0b10100010,    # 162
               "PUSH": 0b01000101,   # 69
               "POP": 0b01000110,    # 70
               "ADD": 0b10100000,  # 160
               "SUB": 0b10100001,  # 161
               "DIV": 0b10100011,  # 163
               "MOD": 0b10100100,  # 164
               "INC": 0b01100101,  # 101
               "DEC": 0b01100110,  # 102
               "CMP": 0b10100111,  # 167
               "AND": 0b10101000,  # 168
               "NOT": 0b01101001,  # 105
               "OR": 0b10101010,  # 170
               "XOR": 0b10101011,  # 171
               "SHL": 0b10101100,  # 172
               "SHR": 0b10101101,  # 173
               "PRA": 0b01001000,   # 72
               "LD": 0b10000011,  # 131
               "ST": 0b10000100,  # 132
               "NOP": 0b00000000,  # 00
               "CALL": 0b01010000,  # 80
               "RET": 0b00010001,  # 17
               "INT": 0b01010010,  # 82
               "IRET": 0b00010011,  # 19
               "JMP": 0b01010100,  # 84
               "JEQ": 0b01010101,  # 85
               "JNE": 0b01010110,  # 86
               "JGT": 0b01010111,  # 87
               "JLT": 0b01011000,  # 88
               "JLE": 0b01011001,  # 89
               "JGE": 0b01011010}  # 90

    def __init__(self):
        """Construct a new CPU."""
        # self.R0 = [0]*8
        # self.R1 = [0]*8
        # self.R2 = [0]*8
        # self.R3 = [0]*8
        # self.R4 = [0]*8
        # self.R5 = [0]*8  # reserved as the interrupt mask (IM)
        # self.R6 = [0]*8  # reserved as the interrupt status (IS)
        # self.R7 = [0]*8  # reserved as the stack pointer (SP)
        self.ram = [0]*256  # available system ram
        self.fl = 0  # Flag register
        # Program Counter, address of the currently executing instruction
        self.pc = 0
        self.stack_pointer = 7
        self.running = True
        self.register = [0, 0, 0, 0, 0, 0, 0, 0xf4]  # 8-bit register
        self.branch_table = {self.opcodes["HLT"]: self.hlt,
                             self.opcodes["LDI"]: self.ldi,
                             self.opcodes["PRN"]: self.prn,
                             self.opcodes["MUL"]: self.mul,
                             self.opcodes["POP"]: self.pop,
                             self.opcodes["PUSH"]: self.push,
                             self.opcodes["ADD"]: self.add,
                             self.opcodes["SUB"]: self.sub,
                             self.opcodes["DIV"]: self.div,
                             self.opcodes["MOD"]: self.mod,
                             self.opcodes["INC"]: self.inc,
                             self.opcodes["DEC"]: self.dec,
                             self.opcodes["CMP"]: self.cmp,
                             self.opcodes["AND"]: self.ls8and,
                             self.opcodes["NOT"]: self.ls8not,
                             self.opcodes["OR"]: self.ls8or,
                             self.opcodes["XOR"]: self.xor,
                             self.opcodes["SHL"]: self.shl,
                             self.opcodes["SHR"]: self.shr,
                             self.opcodes["PRA"]: self.pra,
                             self.opcodes["LD"]: self.ld,
                             self.opcodes["ST"]: self.st,
                             self.opcodes["NOP"]: self.nop,
                             self.opcodes["CALL"]: self.call,
                             self.opcodes["RET"]: self.ret,
                             self.opcodes["INT"]: self.ls8int,
                             self.opcodes["IRET"]: self.iret,
                             self.opcodes["JMP"]: self.jmp,
                             self.opcodes["JEQ"]: self.jeq,
                             self.opcodes["JNE"]: self.jne,
                             self.opcodes["JGT"]: self.jgt,
                             self.opcodes["JLT"]: self.jlt,
                             self.opcodes["JLE"]: self.jle,
                             self.opcodes["JGT"]: self.jgt}

    def call(self):
        ''' CALL register
        Calls a subroutine (function) at the address stored in the register. '''
        # set the return address
        return_addr = self.pc + 2
        # push in on the stack
        self.register[self.stack_pointer] -= 1
        top_of_stack = self.register[self.stack_pointer]
        self.ram[top_of_stack] = return_addr

        # set the pc to the subroutine address
        reg_num = self.ram[self.pc+1]
        subroutine_addr = self.register[reg_num]
        self.pc = subroutine_addr

    def ret(self):
        ''' Return from subroutine. '''
        # pop the return address off the stack
        top_of_stack = self.register[self.stack_pointer]
        return_addr = self.ram[top_of_stack]
        self.register[self.stack_pointer] += 1
        # store it in the pc
        self.pc = return_addr

    def ls8int(self):
        '''INT register
        Issue the interrupt number stored in the given register. '''
        pass

    def iret(self):
        ''' Return from an interrupt handler. '''
        pass

    def jmp(self):
        ''' JMP register
        Jump to the address stored in the given register. '''
        # next register holds the address we want to jump to
        register_with_addr = self.ram[self.pc+1]
        # set the pc to point to this address
        self.pc = self.register[register_with_addr]

    def jeq(self):
        ''' JEQ register
        If equal flag is set (true), jump to the address stored in the given register. '''
        if self.fl == 0b00000001:
            self.jmp()
        else:
            self.pc += 2  # move past current opcode and operand

    def jne(self):
        ''' JNE register
        If E flag is clear (false, 0), jump to the address stored in the given register. '''
        if self.fl != 0b00000001:
            self.jmp()
        else:
            self.pc += 2  # move past current opcode and operand

    def jgt(self):
        ''' JGT register
        If greater-than flag is set (true), jump to the address stored in the given register. '''
        if self.fl == 0b00000010:
            self.jmp()
        else:
            self.pc += 2  # move past current opcode and operand

    def jlt(self):
        ''' JLT register
        If less-than flag is set (true), jump to the address stored in the given register. '''
        if self.fl == 0b00000100:
            self.jmp()
        else:
            self.pc += 2  # move past current opcode and operand

    def jle(self):
        '''JLE register
        If less-than flag or equal flag is set (true), jump to the address stored in the given register. '''
        if self.fl == 0b00000100 or self.fl == 0b00000001:
            self.jmp()
        else:
            self.pc += 2  # move past current opcode and operand

    def jge(self):
        ''' JGE register
        If greater-than flag or equal flag is set (true), jump to the address stored in the given register.'''
        if self.fl == 0b00000010 or self.fl == 0b00000001:
            self.jmp()
        else:
            self.pc += 2  # move past current opcode and operand

    def load(self, filename):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        address = 0
        try:
            with open(filename) as f:
                for line in f:
                    # split lines into opcodes and other cruft
                    line = line.split("#")[0].strip()
                    # print(address, line)
                    if line == "":  # if no opcode is present
                        continue
                    else:  # add opcode to memory
                        v = int(line, 2)
                        # print(address, v)
                        self.ram[address] = v
                        address += 1
        # handle user not supplying correct data
        except (IndexError, FileNotFoundError):
            print("Please provide a valid filename!")
            exit(1)

        # filename = sys.argv[1]
        # with open(filename) as f:
        #     for address, line in enumerate(f):
        #         print(address, line)
        #         line = line.split("#")
        #         try:
        #             v = int(line[0], 2)
        #         except FileNotFoundError:
        #             print("Please provide a valid filename!")
        #         except ValueError:
        #             continue
        #         self.ram[address] = v

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        ''' accept the address to read and return the value stored there
        input: Memory Address Register (MAR)
        output: Memory Data Register (MDR)'''
        try:
            return self.ram[MAR]
        except IndexError:
            raise ValueError(f"The address {MAR} isn't valid.")

    def ram_write(self, MAR, MDR):
        ''' accept a value to write, and the address to write it to
        input: Memory Address Register (MAR)
               Memory Data Register (MDR) '''
        try:
            self.ram[MAR] = MDR
        except IndexError:
            raise ValueError(f"The address {MAR} isn't valid.")

    def nop(self):
        ''' No operation. Do nothing for this instruction. '''
        self.pc += 1

    def hlt(self):
        ''' system halt '''
        self.running = False

    def ldi(self):
        ''' load a value into a register '''
        self.register[self.ram[self.pc+1]] = self.ram[self.pc+2]
        # print(f'''
        #       self.pc {self.pc}
        #       self.ram[self.pc] {self.ram[self.pc]}
        #       self.register[self.ram[self.pc+1]] {self.register[self.ram[self.pc+1]]}
        #       self.ram[self.pc] bitshift {(self.ram[self.pc] & 0b11000000 >> 6)+1}''')
#        self.pc += (self.ram[self.pc] & 0b11000000 >> 6) + 1
        self.pc += 3

    def addi(self):
        ''' add a value to that in a register '''
        self.register[self.ram[self.pc+1]] += self.ram[self.pc+2]
        self.pc += 3

    def ld(self):
        '''LD registerA registerB
        Loads registerA with the value at the memory address stored in registerB. '''
        self.register[self.ram[self.pc+1]
                      ] = self.ram_read(self.register[self.ram[self.pc+2]])

    def st(self):
        ''' ST registerA registerB
        Store value in registerB in the address stored in registerA. '''
        self.ram_write(self.register[self.ram[self.pc+1]],
                       self.register[self.ram[self.pc+2]])

    def push(self):
        ''' push a value on to the stack '''
        self.register[self.stack_pointer] -= 1
        self.ram[self.register[self.stack_pointer]
                 ] = self.register[self.ram[self.pc + 1]]
        self.pc += 2

    def pop(self):
        ''' pop a value from the stack '''
        self.register[self.ram[self.pc + 1]
                      ] = self.ram[self.register[self.stack_pointer]]
        self.register[self.stack_pointer] += 1
        self.pc += 2

    def prn(self):
        ''' print value of a register '''
        print(self.register[self.ram[self.pc+1]])
#        self.pc += (self.ram[self.pc] & 0b11000000 >> 6) + 1
        self.pc += 2

    def pra(self):
        ''' print ascii value of a register '''
        print(ascii(self.register[self.ram[self.pc+1]]))
        self.pc += 2

    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "SUB":
            self.register[reg_a] -= self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "DIV":
            self.register[reg_a] /= self.register[reg_b]
        elif op == "MOD":
            self.register[reg_a] %= self.register[reg_b]
        elif op == "INC":
            self.register[reg_a] += 1
        elif op == "DEC":
            self.register[reg_a] -= 1
        elif op == "CMP":
            # FL bits: 00000LGE
            if self.register[reg_a] < self.register[reg_b]:
                self.fl = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        elif op == "AND":
            self.register[reg_a] &= self.register[reg_b]
        elif op == "NOT":
            self.register[reg_a] = ~self.register[reg_a]
        elif op == "OR":
            self.register[reg_a] |= self.register[reg_b]
        elif op == "XOR":
            self.register[reg_a] ^= self.register[reg_b]
        elif op == "SHL":
            self.register[reg_a] <<= self.register[reg_b]
        elif op == "SHR":
            self.register[reg_a] >>= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def add(self):
        ''' ADD registerA registerB
        Add the value in two registers and store the result in registerA. '''
        self.alu("ADD", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def sub(self):
        self.alu("SUB", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def mul(self):
        ''' MUL registerA registerB
        Multiply the values in two registers together and store the result in registerA. '''
        #self.register[self.ram[self.pc+1]] = self.register[self.ram[self.pc+2]]*self.register[self.ram[self.pc+1]]
        self.alu("MUL", self.ram[self.pc+1], self.ram[self.pc+2])
#        self.pc += (self.ram[self.pc] & 0b11000000 >> 6) + 1
        self.pc += 3

    def div(self):
        ''' DIV registerA registerB
        Divide the value in the first register by the value in the second, storing the result in registerA. '''
        self.alu("DIV", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def mod(self):
        ''' MOD registerA registerB
        Divide the value in the first register by the value in the second, storing the remainder of the result in registerA. '''
        self.alu("MOD", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def inc(self):
        ''' INC register
        Increment (add 1 to) the value in the given register. '''
        self.alu("INC", self.ram[self.pc+1])
        self.pc += 2

    def dec(self):
        '''DEC register
        Decrement (subtract 1 from) the value in the given register. '''
        self.alu("DEC", self.ram[self.pc+1])
        self.pc += 2

    def cmp(self):
        '''CMP registerA registerB
        Compare the values in two registers. '''
        self.alu("CMP", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def ls8and(self):
        ''' AND registerA registerB
        Bitwise-AND the values in registerA and registerB, then store the result in registerA. '''
        self.alu("AND", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def ls8not(self):
        ''' NOT register
        Perform a bitwise-NOT on the value in a register, storing the result in the register. '''
        self.alu("NOT", self.ram[self.pc+1])
        self.pc += 2

    def ls8or(self):
        ''' OR registerA registerB
        Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA. '''
        self.alu("OR", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def xor(self):
        '''XOR registerA registerB
        Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA. '''
        self.alu("XOR", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def shl(self):
        ''' Shift the value in registerA left by the number of bits specified in registerB, filling the low bits with 0. '''
        self.alu("SHL", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def shr(self):
        ''' Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0. '''
        self.alu("SHR", self.ram[self.pc+1], self.ram[self.pc+2])
        self.pc += 3

    def call_function(self, function):
        ''' branch table call functionality '''
        try:
            self.branch_table[function]()
        except KeyError:
            print(f"This operation ({bin(function)}) not yet implemented!")
            exit(1)
        # if self.branch_table[function] is not None:
        #     self.branch_table[function]()
        # else:
        #     print("This operation not yet implemented!")
        #     exit(1)

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            self.call_function(ir)
        # running = True
        # while running:
        #     ir = self.ram_read(self.pc)
        #     # print(ir)
        #     # command = self.ram_read(self.pc)
        #     # print(bin(command))
        #     # operand_A = self.ram_read(self.pc + 1)
        #     # operand_B = self.ram_read(self.pc + 2)
        #     # print("ir is ", ir)
        #     # print(self.commands["HLT"])
        #     # print(self.commands["LDI"])
        #     # print(self.commands["PRN"])
        #     # print(self.ram[self.commands["HLT"]])
        #     # print(self.ram[self.commands["LDI"]])
        #     # print(self.ram[self.commands["PRN"]])
        #     # print(self.R0[self.commands["HLT"]])
        #     # print(self.R0[self.commands["LDI"]])
        #     # print(self.R0[self.commands["PRN"]])
        #     if ir == self.opcodes["HLT"]:
        #         running = False
        #         self.pc += 1
        #     elif ir == self.opcodes["LDI"]:
        #         self.register[self.ram[self.pc+1]] = self.ram[self.pc+2]
        #         self.pc += 3
        #     elif ir == self.opcodes["PRN"]:
        #         print(self.register[self.ram[self.pc+1]])
        #         self.pc += 2
        #     elif ir == self.opcodes["MUL"]:
        #         self.register[self.ram[self.pc+1]
        #                       ] = self.register[self.ram[self.pc+2]]*self.register[self.ram[self.pc+1]]
        #         self.pc += 3
        #     else:
        #         print(f'Unknown instruction {ir} at address {self.pc}')
        #         sys.exit(1)

# if __name__ == "__main__":
#     filename = sys.argv[1]

#     with open(filename) as f:
#         for address, line in enumerate(f):
#             line = line.split("#")
#             try:
#                 v = int(line[0], 10)
#             except ValueError:
#                 continue
#             memory[address] = v
