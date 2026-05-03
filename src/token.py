"""
Token 类型定义 —— 编译器的"字母表"
每个 Token 代表源代码中的一个最小语义单元
"""

from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """Token ���型枚举"""
    FN = auto()          # fn
    LET = auto()         # let
    IF = auto()          # if
    ELSE = auto()        # else
    RETURN = auto()      # return
    PRINT = auto()       # print（内置函数）
    WHILE = auto()       # while
    FOR = auto()         # for
    INTEGER = auto()     # 123
    FLOAT = auto()       # 3.14
    STRING = auto()      # "hello"
    IDENTIFIER = auto()  # 变量名/函数名
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    MOD = auto()         # %
    EQ = auto()          # ==
    NEQ = auto()         # !=
    LT = auto()          # <
    GT = auto()          # >
    LTE = auto()         # <=
    GTE = auto()         # >=
    ASSIGN = auto()      # =
    NOT = auto()         # !
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    COMMA = auto()       # ,
    SEMICOLON = auto()   # ;
    COLON = auto()       # :
    ARROW = auto()       # ->
    EOF = auto()         # 文件结束
    ILLEGAL = auto()     # 非法字符


KEYWORDS = {
    "fn": TokenType.FN,
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
}


@dataclass
class Token:
    """Token 数据结构"""
    type: TokenType
    lexeme: str
    literal: object
    line: int
    column: int

    def __repr__(self):
        if self.literal is not None:
            return f"<{self.type.name} '{self.lexeme}' {self.literal}>"
        return f"<{self.type.name} '{self.lexeme}'>"


SINGLE_CHAR_TOKENS = {
    '+': TokenType.PLUS,
    '*': TokenType.STAR,
    '%': TokenType.MOD,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ',': TokenType.COMMA,
    ';': TokenType.SEMICOLON,
    ':': TokenType.COLON,
}