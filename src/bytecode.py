"""
Phase 7-1: 字节码指令定义

栈式虚拟机指令集：
  数据操作：PUSH, LOAD, STORE, POP
  算术运算：ADD, SUB, MUL, DIV, MOD
  一元运算：NEG, NOT
  比较运算：EQ, NEQ, LT, GT, LTE, GTE
  控制流：JMP, JMP_IF, JMP_IFN, LABEL
  函数：FUNC, CALL, RET, RET_VOID
  内置：PRINT, HALT
"""

from dataclasses import dataclass
from typing import Optional, Any, List


class OpCode:
    PUSH = "PUSH"
    LOAD = "LOAD"
    STORE = "STORE"
    POP = "POP"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    NEG = "NEG"
    NOT = "NOT"
    EQ = "EQ"
    NEQ = "NEQ"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    JMP = "JMP"
    JMP_IF = "JMP_IF"
    JMP_IFN = "JMP_IFN"
    LABEL = "LABEL"
    CALL = "CALL"
    RET = "RET"
    RET_VOID = "RET_VOID"
    FUNC = "FUNC"
    PRINT = "PRINT"
    HALT = "HALT"


@dataclass
class Bytecode:
    op: str
    operand: Any = None

    def __repr__(self):
        if self.operand is not None:
            return f"  {self.op:10s} {self.operand}"
        return f"  {self.op}"


def disassemble(bytecodes: List[Bytecode]) -> str:
    lines = []
    for i, bc in enumerate(bytecodes):
        lines.append(f"[{i:3d}] {bc}")
    return "\n".join(lines)