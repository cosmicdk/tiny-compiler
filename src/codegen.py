"""
Phase 7-2: 代码生成器 (TAC → 字节码)
"""

from src.ir import TACInstruction, TACOperand, IROp
from src.bytecode import Bytecode, OpCode, disassemble
from typing import List


class CodeGenerator:
    def generate(self, tac_instructions: List[TACInstruction]) -> List[Bytecode]:
        self.bytecodes: List[Bytecode] = []
        self.param_count = 0
        for inst in tac_instructions:
            self._translate(inst)
        self.bytecodes.append(Bytecode(OpCode.HALT))
        return self.bytecodes

    def _emit(self, op: str, operand=None):
        self.bytecodes.append(Bytecode(op, operand))

    def _translate(self, inst: TACInstruction):
        op = inst.op
        if op == IROp.LABEL:
            self._emit(OpCode.LABEL, inst.dest.value)
        elif op == IROp.MOV:
            self._push_operand(inst.left)
            self._emit(OpCode.STORE, self._dest_name(inst.dest))
        elif op in (IROp.ADD, IROp.SUB, IROp.MUL, IROp.DIV, IROp.MOD,
                     IROp.EQ, IROp.NEQ, IROp.LT, IROp.GT, IROp.LTE, IROp.GTE):
            self._push_operand(inst.left)
            self._push_operand(inst.right)
            bytecode_op = self._map_binary_op(op)
            self._emit(bytecode_op)
            self._emit(OpCode.STORE, self._dest_name(inst.dest))
        elif op in (IROp.NEG, IROp.NOT):
            self._push_operand(inst.left)
            bytecode_op = OpCode.NEG if op == IROp.NEG else OpCode.NOT
            self._emit(bytecode_op)
            self._emit(OpCode.STORE, self._dest_name(inst.dest))
        elif op == IROp.JMP:
            self._emit(OpCode.JMP, inst.dest.value)
        elif op == IROp.JMP_IF_TRUE:
            self._push_operand(inst.left)
            self._emit(OpCode.JMP_IF, inst.dest.value)
        elif op == IROp.JMP_IF_FALSE:
            self._push_operand(inst.left)
            self._emit(OpCode.JMP_IFN, inst.dest.value)
        elif op == IROp.FUNC:
            func_name = inst.dest.value
            param_names = inst.left.value.split(",") if inst.left and inst.left.value else []
            self._emit(OpCode.FUNC, (func_name, param_names))
        elif op == IROp.PARAM:
            self._push_operand(inst.left)
            self.param_count += 1
        elif op == IROp.CALL:
            func_name = inst.left.value if inst.left else "unknown"
            if func_name == "print":
                self._emit(OpCode.PRINT)
                self.param_count = 0
            else:
                self._emit(OpCode.CALL, (func_name, self.param_count))
                self.param_count = 0
                if inst.dest:
                    self._emit(OpCode.STORE, self._dest_name(inst.dest))
        elif op == IROp.RETURN:
            if inst.left:
                self._push_operand(inst.left)
                self._emit(OpCode.RET)
            else:
                self._emit(OpCode.RET_VOID)
        elif op == IROp.RET_VOID:
            self._emit(OpCode.RET_VOID)

    def _dest_name(self, operand: TACOperand) -> str:
        if operand is None:
            return "?"
        if operand.is_temp:
            return f"%{operand.value}"
        return operand.value

    def _push_operand(self, operand: TACOperand):
        if operand is None:
            return
        if operand.is_constant:
            if operand.const_type == "int":
                self._emit(OpCode.PUSH, int(operand.value))
            elif operand.const_type == "float":
                self._emit(OpCode.PUSH, float(operand.value))
            elif operand.const_type == "string":
                self._emit(OpCode.PUSH, operand.value)
            else:
                self._emit(OpCode.PUSH, operand.value)
        else:
            name = f"%{operand.value}" if operand.is_temp else operand.value
            self._emit(OpCode.LOAD, name)

    def _map_binary_op(self, tac_op: IROp) -> str:
        mapping = {
            IROp.ADD: OpCode.ADD, IROp.SUB: OpCode.SUB,
            IROp.MUL: OpCode.MUL, IROp.DIV: OpCode.DIV, IROp.MOD: OpCode.MOD,
            IROp.EQ: OpCode.EQ, IROp.NEQ: OpCode.NEQ,
            IROp.LT: OpCode.LT, IROp.GT: OpCode.GT,
            IROp.LTE: OpCode.LTE, IROp.GTE: OpCode.GTE,
        }
        return mapping.get(tac_op, OpCode.ADD)