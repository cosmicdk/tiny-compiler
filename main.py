#!/usr/bin/env python3
"""
TinyLang 编译器入口
用法:
  python main.py run examples/hello.tl      # 编译并执行
  python main.py compile examples/hello.tl  # 仅编译，输出字节码
  python main.py lex examples/hello.tl      # 仅词法分析，输出 Token 流
  python main.py ast examples/hello.tl      # 仅语法分析，输出 AST
"""

import sys
import os

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.compiler import Compiler, CompilePhase


def print_tokens(tokens):
    """美化打印 Token 流"""
    print(f"\n{'='*60}")
    print(f"📋 Token 流 ({len(tokens)} 个)")
    print(f"{'='*60}")
    for i, tok in enumerate(tokens):
        extra = f" → {tok.literal}" if tok.literal is not None else ""
        print(f"  [{i:3d}] {tok.type.name:12s} '{tok.lexeme}'{extra}")


def print_errors(result):
    """打印编译错误"""
    print(f"\n{'='*60}")
    print(f"❌ 编译失败: {len(result.errors)} 个错误")
    print(f"{'='*60}")
    for err in result.errors:
        print(f"  {err}")


def print_bytecode(bytecode):
    """美化打印字节码"""
    print(f"\n{'='*60}")
    print(f"📟 字节码 ({len(bytecode)} 条指令)")
    print(f"{'='*60}")
    for i, instr in enumerate(bytecode):
        print(f"  [{i:3d}] {instr}")


def main():
    if len(sys.argv) < 3:
        print("TinyLang 编译器 v0.1")
        print("用法:")
        print("  python main.py lex <文件>      仅词法分析")
        print("  python main.py compile <文件>   完整编译")
        print("  python main.py run <文件>       编译并执行")
        sys.exit(1)

    command = sys.argv[1]
    filepath = sys.argv[2]

    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"📄 源文件: {filepath}")
    print(f"📏 大小: {len(source)} 字符, {source.count(chr(10))+1} 行")
    print(f"\n{'─'*60}")
    print("📝 源代码:")
    print(f"{'─'*60}")
    for i, line in enumerate(source.split('\n'), 1):
        print(f"  {i:3d} | {line}")
    print(f"{'─'*60}")

    compiler = Compiler()

    if command == "lex":
        tokens = compiler._lex(source)
        if compiler.result.success:
            print_tokens(tokens)
        else:
            print_errors(compiler.result)

    elif command == "compile":
        result = compiler.compile(source)
        if result.success:
            print_bytecode(result.bytecode)
        else:
            print_errors(result)

    elif command == "run":
        result = compiler.compile(source)
        if result.success:
            print_bytecode(result.bytecode)
            output = compiler.run_vm(result.bytecode)
            print(f"\n{'='*60}")
            print(f"▶️  执行结果:")
            print(f"{'='*60}")
            for i, val in enumerate(output):
                print(f"  [{i}] {val}")
        else:
            print_errors(result)

    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()