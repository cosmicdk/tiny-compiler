"""
主编译器管线 —— 串联所有阶段
这就是你未来逐步填充的"装配线"
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional


class CompilePhase(Enum):
    """编译阶段标记"""
    LEX = auto()
    PARSE = auto()
    SEMANTIC = auto()
    IR_GEN = auto()
    OPTIMIZE = auto()
    CODEGEN = auto()


@dataclass
class CompileError:
    """编译错误"""
    phase: CompilePhase
    message: str
    line: int
    column: int

    def __str__(self):
        return f"[{self.phase.name}] 第{self.line}行第{self.column}列: {self.message}"


@dataclass
class CompileResult:
    """编译结果"""
    success: bool
    errors: List[CompileError] = field(default_factory=list)
    bytecode: List[str] = field(default_factory=list)
    ast_json: Optional[str] = None

    def add_error(self, phase: CompilePhase, msg: str, line: int, col: int):
        self.errors.append(CompileError(phase, msg, line, col))
        self.success = False


class Compiler:
    """
    主编译器类
    用法: Compiler().compile("let x = 42; print(x);")
    """

    def __init__(self):
        self.result = CompileResult(success=True)

    def compile(self, source: str) -> CompileResult:
        """执行完整编译管线"""
        self.result = CompileResult(success=True)

        # Phase 2: 词法分析
        tokens = self._lex(source)
        if not self.result.success:
            return self.result
        print(f"✅ 词法分析完成: {len(tokens)} 个 Token")

        # Phase 3: 语法分析
        ast = self._parse(tokens)
        if not self.result.success:
            return self.result
        print(f"✅ 语法分析完成: AST 已生成")

        # Phase 4: 语义分析
        self._semantic_analysis(ast)
        if not self.result.success:
            return self.result
        print(f"✅ 语义分析完成: 无类型错误")

        # Phase 5: IR 生成
        ir = self._generate_ir(ast)
        self.result.ir = ir
        print(f"✅ IR 生成完成: {len(ir)} 条指令")

        # Phase 6: 优化
        optimized_ir = self._optimize(ir)
        opt_reduction = len(ir) - len(optimized_ir)
        self.result.ir = optimized_ir
        print(f"✅ 优化完成: {len(optimized_ir)} 条指令 (-{opt_reduction})")

        # Phase 7: 代码生成
        bytecode = self._generate_code(optimized_ir)
        self.result.bytecode = bytecode
        print(f"✅ 代码生成完成: {len(bytecode)} 条指令")

        return self.result

    def _lex(self, source: str) -> list:
        from src.lexer import Lexer
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        if lexer.errors:
            for err in lexer.errors:
                self.result.add_error(CompilePhase.LEX, err, 0, 0)
        return tokens

    def _parse(self, tokens: list):
        from src.parser import Parser
        parser = Parser(tokens)
        ast = parser.parse()
        if parser.errors:
            for err in parser.errors:
                self.result.add_error(CompilePhase.PARSE, err, 0, 0)
        return ast

    def _semantic_analysis(self, ast):
        from src.semantic import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        ok = analyzer.analyze(ast)
        if not ok:
            for err in analyzer.errors:
                self.result.add_error(CompilePhase.SEMANTIC, err, 0, 0)

    def _generate_ir(self, ast) -> list:
        from src.ir_gen import IRGenerator
        gen = IRGenerator()
        ir = gen.generate(ast)
        return ir

    def _optimize(self, ir: list) -> list:
        from src.optimizer import Optimizer
        opt = Optimizer()
        optimized = opt.optimize(ir)
        return optimized

    def _generate_code(self, ir: list) -> list:
        from src.codegen import CodeGenerator
        cg = CodeGenerator()
        bytecodes = cg.generate(ir)
        return bytecodes

    def run_vm(self, bytecodes: list):
        """Phase 8: 虚拟机执行并返回输出"""
        from src.vm import VM
        vm = VM()
        vm.load(bytecodes)
        vm.run()
        return vm.output