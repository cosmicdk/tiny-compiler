"""
Phase 6: 代码优化器

优化策略（多趟扫描）：
  1. 常量折叠：%1 = 3 + 5 → %1 = 8
  2. 代数简化：x + 0 → x, x * 1 → x, x * 0 → 0
  3. 死代码消除：return 后面的所有指令都是死代码
"""

from src.ir import (
    TACInstruction, TACOperand, IROp, print_ir,
)
from typing import List, Optional, Tuple


class Optimizer:
    """TAC 代码优化器"""

    def __init__(self):
        self.changed = False
        self.stats = {
            "constant_folded": 0,
            "algebraic_simplified": 0,
            "dead_code_removed": 0,
            "copy_propagated": 0,
        }

    def optimize(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        self.stats = {k: 0 for k in self.stats}
        ir = list(instructions)
        while True:
            self.changed = False
            ir = self._pass_constant_folding(ir)
            ir = self._pass_algebraic_simplification(ir)
            ir = self._pass_dead_code_elimination(ir)
            if not self.changed:
                break
        return ir

    def _pass_constant_folding(self, ir: List[TACInstruction]) -> List[TACInstruction]:
        new_ir = []
        for inst in ir:
            if inst.op in (IROp.ADD, IROp.SUB, IROp.MUL, IROp.DIV, IROp.MOD):
                if (inst.left and inst.left.is_constant and
                    inst.right and inst.right.is_constant):
                    result = self._eval_binary(
                        inst.op,
                        inst.left.value, inst.left.const_type,
                        inst.right.value, inst.right.const_type,
                    )
                    if result is not None:
                        new_ir.append(TACInstruction(
                            IROp.MOV,
                            dest=inst.dest,
                            left=result,
                        ))
                        self.changed = True
                        self.stats["constant_folded"] += 1
                        continue
            new_ir.append(inst)
        return new_ir

    def _eval_binary(self, op: IROp, left_val: str, left_type: str,
                     right_val: str, right_type: str) -> Optional[TACOperand]:
        try:
            if left_type in ("int", "float") and right_type in ("int", "float"):
                l = float(left_val)
                r = float(right_val)
            else:
                return None
            if op == IROp.ADD:
                result = l + r
            elif op == IROp.SUB:
                result = l - r
            elif op == IROp.MUL:
                result = l * r
            elif op == IROp.DIV:
                if r == 0:
                    return None
                result = l / r
            elif op == IROp.MOD:
                if r == 0:
                    return None
                result = l % r
            else:
                return None
            if result == int(result) and left_type == "int" and right_type == "int":
                return TACOperand.const_int(int(result))
            else:
                return TACOperand.const_float(result)
        except (ValueError, ZeroDivisionError):
            return None

    def _pass_algebraic_simplification(self, ir):
        new_ir = []
        for inst in ir:
            simplified = self._try_simplify(inst)
            if simplified is not None:
                new_ir.append(simplified)
                self.changed = True
                self.stats["algebraic_simplified"] += 1
            else:
                new_ir.append(inst)
        return new_ir

    def _try_simplify(self, inst):
        if inst.op not in (IROp.ADD, IROp.SUB, IROp.MUL, IROp.DIV):
            return None
        if not inst.left or not inst.right:
            return None
        left = inst.left
        right = inst.right
        if inst.op == IROp.ADD:
            if self._is_const(right, 0):
                return TACInstruction(IROp.MOV, dest=inst.dest, left=left)
            if self._is_const(left, 0):
                return TACInstruction(IROp.MOV, dest=inst.dest, left=right)
        if inst.op == IROp.SUB:
            if self._is_const(right, 0):
                return TACInstruction(IROp.MOV, dest=inst.dest, left=left)
        if inst.op == IROp.MUL:
            if self._is_const(right, 1):
                return TACInstruction(IROp.MOV, dest=inst.dest, left=left)
            if self._is_const(left, 1):
                return TACInstruction(IROp.MOV, dest=inst.dest, left=right)
            if self._is_const(right, 0) or self._is_const(left, 0):
                return TACInstruction(IROp.MOV, dest=inst.dest,
                                     left=TACOperand.const_int(0))
        if inst.op == IROp.DIV:
            if self._is_const(right, 1):
                return TACInstruction(IROp.MOV, dest=inst.dest, left=left)
        return None

    def _is_const(self, operand, value):
        if not operand.is_constant:
            return False
        if operand.const_type != "int":
            return False
        try:
            return int(operand.value) == value
        except ValueError:
            return False

    def _pass_dead_code_elimination(self, ir):
        new_ir = []
        skip_until_label = False
        for inst in ir:
            if inst.op in (IROp.LABEL, IROp.FUNC):
                skip_until_label = False
                new_ir.append(inst)
                continue
            if skip_until_label:
                self.changed = True
                self.stats["dead_code_removed"] += 1
                continue
            if inst.op in (IROp.RETURN, IROp.RET_VOID, IROp.JMP):
                new_ir.append(inst)
                skip_until_label = True
                continue
            new_ir.append(inst)
        return self._remove_redundant_jumps(new_ir)

    def _remove_redundant_jumps(self, ir):
        result = []
        i = 0
        while i < len(ir):
            inst = ir[i]
            if (inst.op == IROp.JMP and i + 1 < len(ir) and
                ir[i + 1].op == IROp.LABEL and
                inst.dest and ir[i + 1].dest and
                inst.dest.value == ir[i + 1].dest.value):
                self.changed = True
                self.stats["dead_code_removed"] += 1
                i += 1
                continue
            result.append(inst)
            i += 1
        return result