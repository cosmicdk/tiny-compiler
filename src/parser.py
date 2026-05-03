"""
Phase 3: 语法分析器 (Parser)

核心算法：递归下降 + Pratt 解析（运算符优先级）

为什么用 Pratt 解析？
  • 传统递归下降需要为每个优先级写一个函数
  • Pratt 用一张「优先级表」统一处理所有运算符
  • 代码更短、更优雅、更容易扩展

Pratt 核心思想：
  每个运算符有两个"权力级别"：
    • 左绑定力 (lbp): 运算符左边能"抓多紧"
    • 右绑定力 (rbp): 传递给右侧子表达式的"门槛"
"""

from src.token import Token, TokenType
from src.ast_nodes import (
    ASTNode, Program, FunctionDecl, BlockStmt,
    LetStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, CallExpr,
    Identifier, IntegerLiteral, FloatLiteral, StringLiteral,
    BinaryOp, UnaryOp, AssignExpr,
    ast_to_string,
)


class ParseError(Exception):
    """解析错误"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"第{token.line}行: {message}")


class Parser:
    """递归下降 + Pratt 解析器"""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors: list[str] = []

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, *types: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type in types

    def _match(self, *types: TokenType) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    def _consume(self, ttype: TokenType, error_msg: str) -> Token:
        if self._check(ttype):
            return self._advance()
        raise ParseError(error_msg, self._peek())

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _sync(self):
        self._advance()
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            if self._peek().type in (
                TokenType.FN, TokenType.LET, TokenType.IF,
                TokenType.WHILE, TokenType.FOR, TokenType.RETURN,
                TokenType.RBRACE,
            ):
                return
            self._advance()

    def parse(self) -> Program:
        """解析整个程序"""
        program = Program()
        while not self._is_at_end():
            try:
                if self._match(TokenType.FN):
                    program.functions.append(self._parse_function())
                else:
                    program.statements.append(self._parse_statement())
            except ParseError as e:
                self.errors.append(str(e))
                self._sync()
        return program

    def _parse_function(self) -> FunctionDecl:
        """fn add(a: int, b: int) -> int { ... }"""
        name = self._consume(TokenType.IDENTIFIER, "需要函数名").lexeme
        self._consume(TokenType.LPAREN, "需要 '('")
        params = []
        if not self._check(TokenType.RPAREN):
            params = self._parse_params()
        self._consume(TokenType.RPAREN, "需要 ')'")
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._consume(TokenType.IDENTIFIER, "需要返回类型").lexeme
        body = self._parse_block()
        return FunctionDecl(
            name=name,
            params=params,
            return_type=return_type,
            body=body,
        )

    def _parse_params(self) -> list:
        params = []
        while True:
            pname = self._consume(TokenType.IDENTIFIER, "需要参数名").lexeme
            self._consume(TokenType.COLON, "需要 ':'")
            ptype = self._consume(TokenType.IDENTIFIER, "需要参数类型").lexeme
            params.append((pname, ptype))
            if not self._match(TokenType.COMMA):
                break
        return params

    def _parse_block(self) -> BlockStmt:
        self._consume(TokenType.LBRACE, "需要 '{'")
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._parse_statement())
        self._consume(TokenType.RBRACE, "需要 '}'")
        return BlockStmt(statements=statements)

    def _parse_statement(self) -> ASTNode:
        if self._match(TokenType.LET):
            return self._parse_let()
        if self._match(TokenType.RETURN):
            return self._parse_return()
        if self._match(TokenType.IF):
            return self._parse_if()
        if self._match(TokenType.WHILE):
            return self._parse_while()
        if self._match(TokenType.FOR):
            return self._parse_for()
        if self._match(TokenType.LBRACE):
            return self._finish_block()
        return self._parse_expression_statement()

    def _parse_let(self) -> LetStmt:
        name = self._consume(TokenType.IDENTIFIER, "需要变量名").lexeme
        type_annotation = None
        if self._match(TokenType.COLON):
            type_annotation = self._consume(TokenType.IDENTIFIER, "需要类型名").lexeme
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "需要 ';'")
        return LetStmt(name=name, type_annotation=type_annotation, initializer=initializer)

    def _parse_return(self) -> ReturnStmt:
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "需要 ';'")
        return ReturnStmt(value=value)

    def _parse_if(self) -> IfStmt:
        condition = self._parse_expression()
        then_branch = self._parse_block()
        else_branch = None
        if self._match(TokenType.ELSE):
            if self._match(TokenType.IF):
                else_branch = self._parse_if()
            else:
                else_branch = self._parse_block()
        return IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _parse_while(self) -> WhileStmt:
        condition = self._parse_expression()
        body = self._parse_block()
        return WhileStmt(condition=condition, body=body)

    def _parse_for(self) -> ForStmt:
        self._consume(TokenType.LPAREN, "需要 '('")
        initializer = None
        if self._match(TokenType.LET):
            initializer = self._parse_let()
        elif not self._check(TokenType.SEMICOLON):
            initializer = self._parse_expression_statement()
        else:
            self._advance()
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "需要 ';'")
        update = None
        if not self._check(TokenType.RPAREN):
            update = self._parse_expression()
        self._consume(TokenType.RPAREN, "需要 ')'")
        body = self._parse_block()
        return ForStmt(initializer=initializer, condition=condition, update=update, body=body)

    def _parse_expression_statement(self) -> ExpressionStmt:
        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "需要 ';'")
        return ExpressionStmt(expression=expr)

    def _finish_block(self) -> BlockStmt:
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._parse_statement())
        self._consume(TokenType.RBRACE, "需要 '}'")
        return BlockStmt(statements=statements)

    # Pratt 表达式解析

    PRECEDENCE = {
        TokenType.ASSIGN:  1,
        TokenType.EQ:      3,
        TokenType.NEQ:     3,
        TokenType.LT:      4,
        TokenType.GT:      4,
        TokenType.LTE:     4,
        TokenType.GTE:     4,
        TokenType.PLUS:    5,
        TokenType.MINUS:   5,
        TokenType.STAR:    6,
        TokenType.SLASH:   6,
        TokenType.MOD:     6,
        TokenType.LPAREN:  9,
    }

    def _get_precedence(self, token_type: TokenType) -> int:
        return self.PRECEDENCE.get(token_type, 0)

    def _parse_expression(self, min_prec: int = 0) -> ASTNode:
        left = self._parse_prefix()
        while min_prec < self._get_precedence(self._peek().type):
            left = self._parse_infix(left)
        return left

    def _parse_prefix(self) -> ASTNode:
        token = self._advance()
        if token.type == TokenType.INTEGER:
            return IntegerLiteral(value=token.literal)
        if token.type == TokenType.FLOAT:
            return FloatLiteral(value=token.literal)
        if token.type == TokenType.STRING:
            return StringLiteral(value=token.literal)
        if token.type in (TokenType.IDENTIFIER, TokenType.PRINT):
            return Identifier(name=token.lexeme)
        if token.type == TokenType.LPAREN:
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "需要 ')'")
            return expr
        if token.type in (TokenType.MINUS, TokenType.NOT):
            operand = self._parse_expression(min_prec=7)
            return UnaryOp(operator=token.lexeme, operand=operand)
        raise ParseError(f"意外的 Token: '{token.lexeme}'", token)

    def _parse_infix(self, left: ASTNode) -> ASTNode:
        token = self._advance()
        if token.type == TokenType.ASSIGN:
            if not isinstance(left, Identifier):
                raise ParseError("赋值目标必须是标识符", token)
            right = self._parse_expression(min_prec=self._get_precedence(token.type))
            return AssignExpr(name=left.name, value=right)
        if token.type == TokenType.LPAREN:
            args = []
            if not self._check(TokenType.RPAREN):
                args = self._parse_arguments()
            self._consume(TokenType.RPAREN, "需要 ')'")
            if not isinstance(left, Identifier):
                raise ParseError("函数调用需要函数名", token)
            return CallExpr(callee=left.name, arguments=args)
        right = self._parse_expression(
            min_prec=self._get_precedence(token.type) + 1
        )
        return BinaryOp(left=left, operator=token.lexeme, right=right)

    def _parse_arguments(self) -> list:
        args = [self._parse_expression()]
        while self._match(TokenType.COMMA):
            args.append(self._parse_expression())
        return args