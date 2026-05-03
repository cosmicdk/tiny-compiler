"""
Phase 2: 词法分析器 (Lexer / Scanner)

核心原理：
  源代码 → [字符流] → Lexer → [Token流]
  
  将字符串逐字符扫描，按"最长匹配"原则切成 Token。
  例如 "int" 是关键字，而 "interval" 是标识符。

关键概念：
  • 前瞻 (Lookahead): 看下一个字符来决定当前 Token 边界
  • 最长匹配: 数字 "123" 是一个 Token，而不是1、2、3三个
  • 状态机: 根据当前字符切换到对应的解析模式
"""

from src.token import (
    Token, TokenType, KEYWORDS, SINGLE_CHAR_TOKENS
)


class Lexer:
    """手写词法分析器"""

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.errors: list[str] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.token_start_line = 1
        self.token_start_column = 1

    def tokenize(self) -> list[Token]:
        """主循环：扫描所有 Token"""
        while not self._is_at_end():
            self.start = self.current
            self.token_start_line = self.line
            self.token_start_column = self.column
            self._scan_token()
        self._add_token(TokenType.EOF, "")
        return self.tokens

    def _scan_token(self):
        """扫描单个 Token"""
        c = self._advance()
        if c in (' ', '\t', '\r'):
            pass
        elif c == '\n':
            self.line += 1
            self.column = 1
        elif c in SINGLE_CHAR_TOKENS:
            self._add_token(SINGLE_CHAR_TOKENS[c], c)
        elif c == '!':
            tok_type = TokenType.NEQ if self._match('=') else TokenType.NOT
            self._add_token(tok_type)
        elif c == '=':
            tok_type = TokenType.EQ if self._match('=') else TokenType.ASSIGN
            self._add_token(tok_type)
        elif c == '<':
            tok_type = TokenType.LTE if self._match('=') else TokenType.LT
            self._add_token(tok_type)
        elif c == '>':
            tok_type = TokenType.GTE if self._match('=') else TokenType.GT
            self._add_token(tok_type)
        elif c == '-':
            tok_type = TokenType.ARROW if self._match('>') else TokenType.MINUS
            self._add_token(tok_type)
        elif c == '/':
            if self._match('/'):
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH, '/')
        elif c == '"':
            self._scan_string()
        elif c.isdigit():
            self._scan_number()
        elif c.isalpha() or c == '_':
            self._scan_identifier()
        else:
            self.errors.append(
                f"第{self.line}行第{self.column}列: 非法字符 '{c}'"
            )

    def _scan_string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
                self.column = 1
            self._advance()
        if self._is_at_end():
            self.errors.append(
                f"第{self.token_start_line}行: 未闭合的字符串"
            )
            return
        self._advance()
        value = self.source[self.start + 1 : self.current - 1]
        self._add_token(TokenType.STRING, value, value)

    def _scan_number(self):
        while self._peek().isdigit():
            self._advance()
        is_float = False
        if self._peek() == '.' and self._peek_next().isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()
        text = self.source[self.start : self.current]
        if is_float:
            value = float(text)
            self._add_token(TokenType.FLOAT, text, value)
        else:
            value = int(text)
            self._add_token(TokenType.INTEGER, text, value)

    def _scan_identifier(self):
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        text = self.source[self.start : self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type, text)

    def _advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self._advance()
        return True

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _add_token(self, token_type: TokenType, lexeme: str = None,
                   literal: object = None):
        if lexeme is None:
            lexeme = self.source[self.start : self.current]
        token = Token(
            type=token_type,
            lexeme=lexeme,
            literal=literal,
            line=self.token_start_line,
            column=self.token_start_column,
        )
        self.tokens.append(token)