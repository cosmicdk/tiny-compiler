"""
Phase 4-2: 语义分析器 (Semantic Analyzer)

遍历 AST，建立符号表并检查类型。

核心原则：
  • 声明先于使用
  • 类型必须匹配
  • 作用域隔离
"""

from src.ast_nodes import (
    ASTNode, Program, FunctionDecl, BlockStmt,
    LetStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, CallExpr,
    Identifier, IntegerLiteral, FloatLiteral, StringLiteral,
    BinaryOp, UnaryOp, AssignExpr,
)
from src.symbol_table import (
    SymbolTable, Symbol, SymbolKind, BuiltinType,
)


class SemanticError(Exception):
    def __init__(self, message: str, line: int):
        self.message = message
        self.line = line


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: list[str] = []
        self.current_function_return_type: BuiltinType = BuiltinType.VOID

    def analyze(self, program: Program) -> bool:
        self.errors = []
        for func in program.functions:
            self._declare_function(func)
        for func in program.functions:
            try:
                self._analyze_function(func)
            except SemanticError as e:
                self.errors.append(f"第{e.line}行: {e.message}")
        for stmt in program.statements:
            try:
                self._analyze_statement(stmt)
            except SemanticError as e:
                self.errors.append(f"第{e.line}行: {e.message}")
        self.errors.extend(self.symbol_table.errors)
        return len(self.errors) == 0

    def _declare_function(self, func: FunctionDecl):
        param_list = [(p[0], BuiltinType(p[1])) for p in func.params]
        ret_type = BuiltinType(func.return_type) if func.return_type else BuiltinType.VOID
        symbol = Symbol(
            name=func.name,
            kind=SymbolKind.FUNCTION,
            type=ret_type,
            line=0,
            params=param_list,
            return_type=ret_type,
        )
        self.symbol_table.define(symbol)

    def _analyze_function(self, func: FunctionDecl):
        self.symbol_table.push_scope()
        for param_name, param_type_str in func.params:
            param_symbol = Symbol(
                name=param_name,
                kind=SymbolKind.PARAMETER,
                type=BuiltinType(param_type_str),
                line=0,
            )
            self.symbol_table.define(param_symbol)
        self.current_function_return_type = (
            BuiltinType(func.return_type)
            if func.return_type
            else BuiltinType.VOID
        )
        self._analyze_block(func.body)
        self.symbol_table.pop_scope()

    def _analyze_block(self, block: BlockStmt):
        for stmt in block.statements:
            self._analyze_statement(stmt)

    def _analyze_statement(self, stmt: ASTNode):
        if isinstance(stmt, LetStmt):
            self._analyze_let(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._analyze_return(stmt)
        elif isinstance(stmt, IfStmt):
            self._analyze_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self._analyze_while(stmt)
        elif isinstance(stmt, ForStmt):
            self._analyze_for(stmt)
        elif isinstance(stmt, ExpressionStmt):
            self._analyze_expression_stmt(stmt)
        elif isinstance(stmt, BlockStmt):
            self._analyze_block(stmt)

    def _analyze_let(self, stmt: LetStmt):
        existing = self.symbol_table.resolve_current(stmt.name)
        if existing:
            raise SemanticError(
                f"变量 '{stmt.name}' 已在本作用域声明", 0
            )
        declared_type = None
        inferred_type = None
        if stmt.type_annotation:
            try:
                declared_type = BuiltinType(stmt.type_annotation)
            except ValueError:
                raise SemanticError(f"未知类型 '{stmt.type_annotation}'", 0)
        if stmt.initializer:
            inferred_type = self._infer_type(stmt.initializer)
        if declared_type and inferred_type:
            if not self._types_compatible(declared_type, inferred_type):
                raise SemanticError(
                    f"类型不匹配: 声明 '{stmt.name}: {declared_type.value}' "
                    f"但初始值是 '{inferred_type.value}'", 0
                )
            final_type = declared_type
        elif declared_type:
            final_type = declared_type
        elif inferred_type:
            final_type = inferred_type
        else:
            raise SemanticError(f"变量 '{stmt.name}' 既无类型注解也无初始值", 0)
        symbol = Symbol(
            name=stmt.name,
            kind=SymbolKind.VARIABLE,
            type=final_type,
            line=0,
        )
        self.symbol_table.define(symbol)

    def _analyze_return(self, stmt: ReturnStmt):
        if stmt.value:
            return_type = self._infer_type(stmt.value)
            if not self._types_compatible(self.current_function_return_type, return_type):
                raise SemanticError(
                    f"返回类型不匹配: 函数声明返回 '{self.current_function_return_type.value}'"
                    f" 但实际返回 '{return_type.value}'", 0
                )
        else:
            if self.current_function_return_type != BuiltinType.VOID:
                raise SemanticError(
                    f"函数声明返回 '{self.current_function_return_type.value}'"
                    f" 但 return 语句没有值", 0
                )

    def _analyze_if(self, stmt: IfStmt):
        self._infer_type(stmt.condition)
        self._analyze_block(stmt.then_branch)
        if stmt.else_branch:
            if isinstance(stmt.else_branch, BlockStmt):
                self._analyze_block(stmt.else_branch)
            elif isinstance(stmt.else_branch, IfStmt):
                self._analyze_if(stmt.else_branch)

    def _analyze_while(self, stmt: WhileStmt):
        self._infer_type(stmt.condition)
        self._analyze_block(stmt.body)

    def _analyze_for(self, stmt: ForStmt):
        if stmt.initializer:
            if isinstance(stmt.initializer, LetStmt):
                self._analyze_let(stmt.initializer)
            else:
                self._infer_type(stmt.initializer)
        if stmt.condition:
            self._infer_type(stmt.condition)
        if stmt.update:
            self._infer_type(stmt.update)
        self._analyze_block(stmt.body)

    def _analyze_expression_stmt(self, stmt: ExpressionStmt):
        self._infer_type(stmt.expression)

    def _infer_type(self, node: ASTNode) -> BuiltinType:
        if isinstance(node, IntegerLiteral):
            return BuiltinType.INT
        if isinstance(node, FloatLiteral):
            return BuiltinType.FLOAT
        if isinstance(node, StringLiteral):
            return BuiltinType.STRING
        if isinstance(node, Identifier):
            symbol = self.symbol_table.resolve(node.name)
            if symbol is None:
                raise SemanticError(f"未声明的标识符 '{node.name}'", 0)
            return symbol.type
        if isinstance(node, BinaryOp):
            left_type = self._infer_type(node.left)
            right_type = self._infer_type(node.right)
            if node.operator in ('+', '-', '*', '/', '%'):
                if left_type == BuiltinType.FLOAT or right_type == BuiltinType.FLOAT:
                    if left_type in (BuiltinType.INT, BuiltinType.FLOAT) and \
                       right_type in (BuiltinType.INT, BuiltinType.FLOAT):
                        return BuiltinType.FLOAT
                if left_type == BuiltinType.INT and right_type == BuiltinType.INT:
                    return BuiltinType.INT
                if node.operator == '+' and \
                   left_type == BuiltinType.STRING and right_type == BuiltinType.STRING:
                    return BuiltinType.STRING
                raise SemanticError(
                    f"运算符 '{node.operator}' 不能用于 "
                    f"'{left_type.value}' 和 '{right_type.value}'", 0
                )
            if node.operator in ('<', '>', '<=', '>=', '==', '!='):
                if left_type in (BuiltinType.INT, BuiltinType.FLOAT) and \
                   right_type in (BuiltinType.INT, BuiltinType.FLOAT):
                    return BuiltinType.BOOL
                raise SemanticError(
                    f"比较运算符 '{node.operator}' 不能用于 "
                    f"'{left_type.value}' 和 '{right_type.value}'", 0
                )
            return BuiltinType.ERROR
        if isinstance(node, UnaryOp):
            operand_type = self._infer_type(node.operand)
            if node.operator == '-':
                if operand_type in (BuiltinType.INT, BuiltinType.FLOAT):
                    return operand_type
                raise SemanticError(f"一元 '-' 不能用于 '{operand_type.value}'", 0)
            if node.operator == '!':
                return BuiltinType.BOOL
            return BuiltinType.ERROR
        if isinstance(node, CallExpr):
            func_symbol = self.symbol_table.resolve(node.callee)
            if func_symbol is None:
                raise SemanticError(f"未声明的函数 '{node.callee}'", 0)
            if func_symbol.kind not in (SymbolKind.FUNCTION, SymbolKind.BUILTIN):
                raise SemanticError(f"'{node.callee}' 不是函数", 0)
            expected_params = func_symbol.params
            if len(node.arguments) != len(expected_params):
                raise SemanticError(
                    f"函数 '{node.callee}' 需要 {len(expected_params)} 个参数，"
                    f"但传入了 {len(node.arguments)} 个", 0
                )
            if func_symbol.kind != SymbolKind.BUILTIN:
                for i, arg in enumerate(node.arguments):
                    arg_type = self._infer_type(arg)
                    expected_type = expected_params[i][1]
                    if not self._types_compatible(expected_type, arg_type):
                        raise SemanticError(
                            f"函数 '{node.callee}' 的第 {i+1} 个参数需要 "
                            f"'{expected_type.value}'，但传入了 '{arg_type.value}'", 0
                        )
            return func_symbol.return_type or BuiltinType.VOID
        if isinstance(node, AssignExpr):
            value_type = self._infer_type(node.value)
            symbol = self.symbol_table.resolve(node.name)
            if symbol is None:
                raise SemanticError(f"未声明的变量 '{node.name}'", 0)
            if not self._types_compatible(symbol.type, value_type):
                raise SemanticError(
                    f"不能将 '{value_type.value}' 赋值给 "
                    f"'{node.name}: {symbol.type.value}'", 0
                )
            return value_type
        raise SemanticError(f"无法推断类型的节点: {type(node).__name__}", 0)

    def _types_compatible(self, expected: BuiltinType, actual: BuiltinType) -> bool:
        if expected == actual:
            return True
        if expected == BuiltinType.FLOAT and actual == BuiltinType.INT:
            return True
        if expected == BuiltinType.ERROR or actual == BuiltinType.ERROR:
            return True
        return False