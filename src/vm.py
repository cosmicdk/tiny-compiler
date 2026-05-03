"""
Phase 8: 栈式虚拟机 (Stack VM)

核心状态：
  • stack: 操作数栈
  • variables: 当前函数变量表
  • call_stack: 调用栈（保存返回地址+变量表）
  • pc: 程序计数器
  • labels: 标签映射表
  • functions: 函数表

执行循环 (FETCH-DECODE-EXECUTE):
  while True:
      取指令 = bytecodes[pc]
      根据指令类型执行
      pc += 1
"""

from src.bytecode import Bytecode, OpCode, disassemble
from typing import List, Dict, Any, Tuple


class VMRuntimeError(Exception):
    pass


class VM:
    def __init__(self):
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.call_stack: List[Tuple[int, Dict[str, Any]]] = []
        self.pc: int = 0
        self.labels: Dict[str, int] = {}
        self.functions: Dict[str, Tuple[int, List[str]]] = {}
        self.halted: bool = False
        self.output: List[str] = []

    def load(self, bytecodes: List[Bytecode]):
        self.bytecodes = bytecodes
        for i, bc in enumerate(bytecodes):
            if bc.op == OpCode.LABEL:
                self.labels[bc.operand] = i
            elif bc.op == OpCode.FUNC:
                name, param_names = bc.operand
                self.functions[name] = (i + 1, param_names)

    def run(self):
        self.pc = 0
        self.halted = False
        if "func_main" in self.labels:
            self.pc = self.labels["func_main"]
        while not self.halted and self.pc < len(self.bytecodes):
            inst = self.bytecodes[self.pc]
            self._execute(inst)
            self.pc += 1

    def _execute(self, inst: Bytecode):
        op = inst.op
        if op == OpCode.PUSH:
            self.stack.append(inst.operand)
        elif op == OpCode.LOAD:
            name = inst.operand
            if name not in self.variables:
                raise VMRuntimeError(f"变量 '{name}' 未定义 (PC={self.pc})")
            self.stack.append(self.variables[name])
        elif op == OpCode.STORE:
            if not self.stack:
                raise VMRuntimeError(f"STORE 时栈为空 (PC={self.pc})")
            value = self.stack.pop()
            self.variables[inst.operand] = value
        elif op == OpCode.POP:
            if self.stack:
                self.stack.pop()
        elif op in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD):
            if len(self.stack) < 2:
                raise VMRuntimeError(f"{op} 需要两个操作数 (PC={self.pc})")
            b = self.stack.pop()
            a = self.stack.pop()
            if op == OpCode.ADD and (isinstance(a, str) or isinstance(b, str)):
                self.stack.append(str(a) + str(b))
                return
            if op == OpCode.ADD:
                self.stack.append(a + b)
            elif op == OpCode.SUB:
                self.stack.append(a - b)
            elif op == OpCode.MUL:
                self.stack.append(a * b)
            elif op == OpCode.DIV:
                self.stack.append(a / b)
            elif op == OpCode.MOD:
                self.stack.append(a % b)
        elif op == OpCode.NEG:
            if not self.stack:
                raise VMRuntimeError(f"NEG 需要操作数 (PC={self.pc})")
            self.stack.append(-self.stack.pop())
        elif op == OpCode.NOT:
            if not self.stack:
                raise VMRuntimeError(f"NOT 需要操作数 (PC={self.pc})")
            self.stack.append(not self.stack.pop())
        elif op in (OpCode.EQ, OpCode.NEQ, OpCode.LT, OpCode.GT, OpCode.LTE, OpCode.GTE):
            if len(self.stack) < 2:
                raise VMRuntimeError(f"{op} 需要两个操作数 (PC={self.pc})")
            b = self.stack.pop()
            a = self.stack.pop()
            if op == OpCode.EQ:
                self.stack.append(a == b)
            elif op == OpCode.NEQ:
                self.stack.append(a != b)
            elif op == OpCode.LT:
                self.stack.append(a < b)
            elif op == OpCode.GT:
                self.stack.append(a > b)
            elif op == OpCode.LTE:
                self.stack.append(a <= b)
            elif op == OpCode.GTE:
                self.stack.append(a >= b)
        elif op == OpCode.JMP:
            label = inst.operand
            if label not in self.labels:
                raise VMRuntimeError(f"未定义的标签 L{label} (PC={self.pc})")
            self.pc = self.labels[label]
        elif op == OpCode.JMP_IF:
            if not self.stack:
                raise VMRuntimeError(f"JMP_IF 需要条件 (PC={self.pc})")
            cond = self.stack.pop()
            label = inst.operand
            if label not in self.labels:
                raise VMRuntimeError(f"未定义的标签 L{label} (PC={self.pc})")
            if cond:
                self.pc = self.labels[label]
        elif op == OpCode.JMP_IFN:
            if not self.stack:
                raise VMRuntimeError(f"JMP_IFN 需要条件 (PC={self.pc})")
            cond = self.stack.pop()
            label = inst.operand
            if label not in self.labels:
                raise VMRuntimeError(f"未定义的标签 L{label} (PC={self.pc})")
            if not cond:
                self.pc = self.labels[label]
        elif op == OpCode.LABEL:
            pass
        elif op == OpCode.FUNC:
            pass
        elif op == OpCode.CALL:
            func_name, arg_count = inst.operand
            if func_name not in self.functions:
                raise VMRuntimeError(f"未定义的函数 '{func_name}' (PC={self.pc})")
            func_pc, param_names = self.functions[func_name]
            if len(self.stack) < arg_count:
                raise VMRuntimeError(
                    f"函数 '{func_name}' 需要 {arg_count} 个参数，"
                    f"但栈上只有 {len(self.stack)} 个 (PC={self.pc})"
                )
            args = []
            for _ in range(arg_count):
                args.insert(0, self.stack.pop())
            return_pc = self.pc
            self.call_stack.append((return_pc, self.variables))
            self.variables = {}
            for name, value in zip(param_names, args):
                self.variables[name] = value
            self.pc = func_pc
        elif op == OpCode.RET:
            if not self.stack:
                raise VMRuntimeError(f"RET 需要返回值在栈顶 (PC={self.pc})")
            return_value = self.stack.pop()
            if not self.call_stack:
                self.halted = True
                return
            return_pc, caller_vars = self.call_stack.pop()
            self.variables = caller_vars
            self.pc = return_pc
            self.stack.append(return_value)
        elif op == OpCode.RET_VOID:
            if not self.call_stack:
                self.halted = True
                return
            return_pc, caller_vars = self.call_stack.pop()
            self.variables = caller_vars
            self.pc = return_pc
        elif op == OpCode.PRINT:
            if not self.stack:
                raise VMRuntimeError(f"PRINT 需要操作数 (PC={self.pc})")
            value = self.stack.pop()
            self.output.append(str(value))
            print(f"  🖨️  输出: {value}")
        elif op == OpCode.HALT:
            self.halted = True
        else:
            raise VMRuntimeError(f"未知指令: {op} (PC={self.pc})")