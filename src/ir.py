"""
Phase 5-1: 三地址码 (TAC) 指令定义

三地址码 (Three-Address Code)：
  每条指令最多有三个"地址"（操作数 + 结果）。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum, auto


class IROp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    NEG = auto()
    NOT = auto()
    MOV = auto()
    JMP = auto()
    JMP_IF_TRUE = auto()
    JMP_IF_FALSE = auto()
    LABEL = auto()
    CALL = auto()
    RETURN = auto()
    RET_VOID = auto()
    FUNC = auto()
    PARAM = auto()


@dataclass
class TACOperand:
    value: str = ""
    is_temp: bool = False
    is_constant: bool = False
    const_type: str = ""

    def __repr__(self):
        if self.is_temp:
            return f"%{self.value}"
        if self.is_constant:
            if self.const_type == "string":
                return f'"{self.value}"'
            return str(self.value)
        return self.value

    @staticmethod
    def var(name: str) -> "TACOperand":
        return TACOperand(value=name)

    @staticmethod
    def temp(num: int) -> "TACOperand":
        return TACOperand(value=str(num), is_temp=True)

    @staticmethod
    def const_int(val: int) -> "TACOperand":
        return TACOperand(value=str(val), is_constant=True, const_type="int")

    @staticmethod
    def const_float(val: float) -> "TACOperand":
        return TACOperand(value=str(val), is_constant=True, const_type="float")

    @staticmethod
    def const_str(val: str) -> "TACOperand":
        return TACOperand(value=val, is_constant=True, const_type="string")

    @staticmethod
    def label(name: str) -> "TACOperand":
        return TACOperand(value=name)


@dataclass
class TACInstruction:
    op: IROp
    dest: Optional[TACOperand] = None
    left: Optional[TACOperand] = None
    right: Optional[TACOperand] = None

    def __repr__(self):
        if self.op == IROp.LABEL:
            return f"L{self.dest.value}:"
        if self.op == IROp.JMP:
            return f"  goto L{self.dest.value}"
        if self.op == IROp.JMP_IF_TRUE:
            return f"  if {self.left} goto L{self.dest.value}"
        if self.op == IROp.JMP_IF_FALSE:
            return f"  if_not {self.left} goto L{self.dest.value}"
        if self.op == IROp.RETURN:
            return f"  return {self.left}"
        if self.op == IROp.RET_VOID:
            return f"  return"
        if self.op == IROp.CALL:
            return f"  {self.dest} = call {self.left.value}"
        if self.op == IROp.PARAM:
            return f"  param {self.left}"
        if self.op == IROp.FUNC:
            params = self.left.value if self.left else ""
            return f"  # func {self.dest.value}({params})"
        if self.op == IROp.NEG:
            return f"  {self.dest} = -{self.left}"
        if self.op == IROp.NOT:
            return f"  {self.dest} = !{self.left}"
        if self.op == IROp.MOV:
            return f"  {self.dest} = {self.left}"
        op_map = {
            IROp.ADD: "+", IROp.SUB: "-", IROp.MUL: "*", IROp.DIV: "/", IROp.MOD: "%",
            IROp.EQ: "==", IROp.NEQ: "!=", IROp.LT: "<", IROp.GT: ">",
            IROp.LTE: "<=", IROp.GTE: ">=",
        }
        op_str = op_map.get(self.op, "?")
        return f"  {self.dest} = {self.left} {op_str} {self.right}"


def print_ir(instructions: List[TACInstruction]) -> str:
    lines = []
    for inst in instructions:
        lines.append(str(inst))
    return "\n".join(lines)