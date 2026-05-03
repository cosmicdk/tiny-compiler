"""
AST 节点定义 —— 抽象语法树的"积木块"

AST 与 CST 的区别：
  CST (具体语法树): 包含所有语法细节（括号、分号等）
  AST (抽象语法树): 只保留语义相关的结构

例如 "a + b * c" 的 AST:
       (+)
      /   \
    (a)   (*)
          /  \
        (b)  (c)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


class ASTNode:
    """所有 AST 节点的基类"""
    pass


@dataclass
class IntegerLiteral(ASTNode):
    value: int

@dataclass
class FloatLiteral(ASTNode):
    value: float

@dataclass
class StringLiteral(ASTNode):
    value: str

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode

@dataclass
class CallExpr(ASTNode):
    callee: str
    arguments: List[ASTNode] = field(default_factory=list)

@dataclass
class AssignExpr(ASTNode):
    name: str
    value: ASTNode

@dataclass
class ExpressionStmt(ASTNode):
    expression: ASTNode

@dataclass
class LetStmt(ASTNode):
    name: str
    type_annotation: Optional[str] = None
    initializer: Optional[ASTNode] = None

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode] = None

@dataclass
class BlockStmt(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None

@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: ASTNode

@dataclass
class ForStmt(ASTNode):
    initializer: Optional[ASTNode]
    condition: Optional[ASTNode]
    update: Optional[ASTNode]
    body: ASTNode

@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[tuple]
    return_type: Optional[str]
    body: BlockStmt

@dataclass
class Program(ASTNode):
    functions: List[FunctionDecl] = field(default_factory=list)
    statements: List[ASTNode] = field(default_factory=list)


def ast_to_string(node: ASTNode, indent: int = 0) -> str:
    """将 AST 转为可读的字符串"""
    prefix = "  " * indent
    if isinstance(node, Program):
        lines = [f"{prefix}Program"]
        for fn in node.functions:
            lines.append(ast_to_string(fn, indent + 1))
        for stmt in node.statements:
            lines.append(ast_to_string(stmt, indent + 1))
        return "\n".join(lines)
    elif isinstance(node, FunctionDecl):
        params = ", ".join(f"{n}:{t}" for n, t in node.params)
        lines = [f"{prefix}FunctionDecl: {node.name}({params}) -> {node.return_type}"]
        lines.append(ast_to_string(node.body, indent + 1))
        return "\n".join(lines)
    elif isinstance(node, BlockStmt):
        lines = [f"{prefix}Block"]
        for stmt in node.statements:
            lines.append(ast_to_string(stmt, indent + 1))
        return "\n".join(lines)
    elif isinstance(node, LetStmt):
        init = f" = ..." if node.initializer else ""
        return f"{prefix}LetStmt: {node.name}{init}"
    elif isinstance(node, ReturnStmt):
        if node.value:
            return f"{prefix}Return\n{ast_to_string(node.value, indent + 1)}"
        return f"{prefix}Return"
    elif isinstance(node, IfStmt):
        lines = [f"{prefix}IfStmt"]
        lines.append(f"{prefix}  Condition:")
        lines.append(ast_to_string(node.condition, indent + 2))
        lines.append(f"{prefix}  Then:")
        lines.append(ast_to_string(node.then_branch, indent + 2))
        if node.else_branch:
            lines.append(f"{prefix}  Else:")
            lines.append(ast_to_string(node.else_branch, indent + 2))
        return "\n".join(lines)
    elif isinstance(node, BinaryOp):
        lines = [f"{prefix}BinaryOp: {node.operator}"]
        lines.append(ast_to_string(node.left, indent + 1))
        lines.append(ast_to_string(node.right, indent + 1))
        return "\n".join(lines)
    elif isinstance(node, UnaryOp):
        return f"{prefix}UnaryOp: {node.operator}\n{ast_to_string(node.operand, indent + 1)}"
    elif isinstance(node, CallExpr):
        lines = [f"{prefix}Call: {node.callee}"]
        for arg in node.arguments:
            lines.append(ast_to_string(arg, indent + 1))
        return "\n".join(lines)
    elif isinstance(node, IntegerLiteral):
        return f"{prefix}Integer: {node.value}"
    elif isinstance(node, FloatLiteral):
        return f"{prefix}Float: {node.value}"
    elif isinstance(node, StringLiteral):
        return f"{prefix}String: \"{node.value}\""
    elif isinstance(node, Identifier):
        return f"{prefix}Identifier: {node.name}"
    elif isinstance(node, ExpressionStmt):
        return ast_to_string(node.expression, indent)
    else:
        return f"{prefix}{type(node).__name__}"