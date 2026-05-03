"""
Phase 5-2: IR 生成器 (AST → TAC)

核心思路：遍历 AST，对每个表达式节点生成对应的 TAC 指令序列。
"""

from src.ast_nodes import (
    ASTNode, Program, FunctionDecl, BlockStmt,
    LetStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, CallExpr,
    Identifier, IntegerLiteral, FloatLiteral, StringLiteral,
    BinaryOp, UnaryOp, AssignExpr,
)
from src.ir import (
    TACInstruction, TACOperand, IROp, print_ir,
)
from typing import List


class IRGenerator:
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0

    def _new_temp(self) -> TACOperand:
        self.temp_counter += 1
        return TACOperand.temp(self.temp_counter)

    def _new_label(self) -> str:
        self.label_counter += 1
        return str(self.label_counter)

    def _emit(self, op: IROp, dest=None, left=None, right=None):
        inst = TACInstruction(op=op, dest=dest, left=left, right=right)
        self.instructions.append(inst)

    def _emit_label(self, name: str):
        self.instructions.append(TACInstruction(IROp.LABEL, dest=TACOperand.label(name)))

    def generate(self, program: Program) -> List[TACInstruction]:
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        for func in program.functions:
            self._gen_function(func)
        for stmt in program.statements:
            self._gen_statement(stmt)
        return self.instructions

    def _gen_function(self, func: FunctionDecl):
        param_names = [p[0] for p in func.params]
        self._emit(IROp.FUNC, dest=TACOperand.var(func.name),
                   left=TACOperand.var(",".join(param_names)))
        self._emit_label(f"func_{func.name}")
        self._gen_block(func.body)
        self._emit(IROp.RET_VOID)

    def _gen_block(self, block: BlockStmt):
        for stmt in block.statements:
            self._gen_statement(stmt)

    def _gen_statement(self, stmt: ASTNode):
        if isinstance(stmt, LetStmt):
            self._gen_let(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._gen_return(stmt)
        elif isinstance(stmt, IfStmt):
            self._gen_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self._gen_while(stmt)
        elif isinstance(stmt, ForStmt):
            self._gen_for(stmt)
        elif isinstance(stmt, ExpressionStmt):
            self._gen_expr(stmt.expression)
        elif isinstance(stmt, BlockStmt):
            self._gen_block(stmt)

    def _gen_let(self, stmt: LetStmt):
        if stmt.initializer:
            val = self._gen_expr(stmt.initializer)
            self._emit(IROp.MOV, dest=TACOperand.var(stmt.name), left=val)

    def _gen_return(self, stmt: ReturnStmt):
        if stmt.value:
            val = self._gen_expr(stmt.value)
            self._emit(IROp.RETURN, left=val)
        else:
            self._emit(IROp.RET_VOID)

    def _gen_if(self, stmt: IfStmt):
        label_then = self._new_label()
        label_end = self._new_label()
        has_else = stmt.else_branch is not None
        label_else = self._new_label() if has_else else label_end
        cond = self._gen_expr(stmt.condition)
        self._emit(IROp.JMP_IF_TRUE, dest=TACOperand.label(label_then), left=cond)
        self._emit(IROp.JMP, dest=TACOperand.label(label_else))
        self._emit_label(label_then)
        self._gen_block(stmt.then_branch)
        if has_else:
            self._emit(IROp.JMP, dest=TACOperand.label(label_end))
        if has_else:
            self._emit_label(label_else)
            if isinstance(stmt.else_branch, BlockStmt):
                self._gen_block(stmt.else_branch)
            elif isinstance(stmt.else_branch, IfStmt):
                self._gen_if(stmt.else_branch)
        self._emit_label(label_end)

    def _gen_while(self, stmt: WhileStmt):
        label_start = self._new_label()
        label_end = self._new_label()
        self._emit_label(label_start)
        cond = self._gen_expr(stmt.condition)
        self._emit(IROp.JMP_IF_FALSE, dest=TACOperand.label(label_end), left=cond)
        self._gen_block(stmt.body)
        self._emit(IROp.JMP, dest=TACOperand.label(label_start))
        self._emit_label(label_end)

    def _gen_for(self, stmt: ForStmt):
        label_start = self._new_label()
        label_end = self._new_label()
        if stmt.initializer:
            if isinstance(stmt.initializer, LetStmt):
                self._gen_let(stmt.initializer)
            else:
                self._gen_expr(stmt.initializer)
        self._emit_label(label_start)
        if stmt.condition:
            cond = self._gen_expr(stmt.condition)
            self._emit(IROp.JMP_IF_FALSE, dest=TACOperand.label(label_end), left=cond)
        self._gen_block(stmt.body)
        if stmt.update:
            self._gen_expr(stmt.update)
        self._emit(IROp.JMP, dest=TACOperand.label(label_start))
        self._emit_label(label_end)

    def _gen_expr(self, node: ASTNode) -> TACOperand:
        if isinstance(node, IntegerLiteral):
            return TACOperand.const_int(node.value)
        if isinstance(node, FloatLiteral):
            return TACOperand.const_float(node.value)
        if isinstance(node, StringLiteral):
            return TACOperand.const_str(node.value)
        if isinstance(node, Identifier):
            return TACOperand.var(node.name)
        if isinstance(node, BinaryOp):
            left_op = self._gen_expr(node.left)
            right_op = self._gen_expr(node.right)
            op_map = {
                '+': IROp.ADD, '-': IROp.SUB, '*': IROp.MUL,
                '/': IROp.DIV, '%': IROp.MOD,
                '==': IROp.EQ, '!=': IROp.NEQ, '<': IROp.LT,
                '>': IROp.GT, '<=': IROp.LTE, '>=': IROp.GTE,
            }
            ir_op = op_map.get(node.operator, IROp.ADD)
            temp = self._new_temp()
            self._emit(ir_op, dest=temp, left=left_op, right=right_op)
            return temp
        if isinstance(node, UnaryOp):
            operand = self._gen_expr(node.operand)
            ir_op = IROp.NEG if node.operator == '-' else IROp.NOT
            temp = self._new_temp()
            self._emit(ir_op, dest=temp, left=operand)
            return temp
        if isinstance(node, AssignExpr):
            val = self._gen_expr(node.value)
            self._emit(IROp.MOV, dest=TACOperand.var(node.name), left=val)
            return TACOperand.var(node.name)
        if isinstance(node, CallExpr):
            arg_ops = []
            for arg in node.arguments:
                arg_ops.append(self._gen_expr(arg))
            for arg_op in arg_ops:
                self._emit(IROp.PARAM, left=arg_op)
            temp = self._new_temp()
            func_op = TACOperand.var(node.callee)
            self._emit(IROp.CALL, dest=temp, left=func_op)
            return temp
        if isinstance(node, ExpressionStmt):
            return self._gen_expr(node.expression)
        raise ValueError(f"未知表达式节点: {type(node).__name__}")