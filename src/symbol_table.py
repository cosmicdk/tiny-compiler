"""
Phase 4-1: 符号表 (Symbol Table)

生活类比：户口本
  • 每进入一个新作用域（花括号），就翻开新的一页
  • 声明变量 = 在这一页上登记
  • 使用变量 = 从当前页往前翻，找到第一个登记记录
  • 离开作用域 = 撕掉这一页，回到上一页
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, List


class SymbolKind(Enum):
    VARIABLE = auto()
    FUNCTION = auto()
    PARAMETER = auto()
    BUILTIN = auto()


class BuiltinType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    VOID = "void"
    BOOL = "bool"
    ERROR = "<error>"


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    type: BuiltinType
    line: int
    params: List[tuple] = field(default_factory=list)
    return_type: Optional[BuiltinType] = None


class Scope:
    def __init__(self, parent: Optional["Scope"] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent: Optional["Scope"] = parent


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope(parent=None)
        self.current_scope = self.global_scope
        self.errors: List[str] = []
        self._register_builtins()

    def _register_builtins(self):
        print_sym = Symbol(
            name="print",
            kind=SymbolKind.BUILTIN,
            type=BuiltinType.VOID,
            line=0,
            params=[("value", BuiltinType.INT)],
            return_type=BuiltinType.VOID,
        )
        self.global_scope.symbols["print"] = print_sym

    def push_scope(self):
        new_scope = Scope(parent=self.current_scope)
        self.current_scope = new_scope

    def pop_scope(self):
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.current_scope.symbols:
            self.errors.append(
                f"第{symbol.line}行: 符号 '{symbol.name}' 已在本作用域声明"
            )
            return False
        self.current_scope.symbols[symbol.name] = symbol
        return True

    def resolve(self, name: str) -> Optional[Symbol]:
        scope = self.current_scope
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def resolve_current(self, name: str) -> Optional[Symbol]:
        return self.current_scope.symbols.get(name)