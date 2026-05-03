# 🧬 TinyLang Compiler

> **零基础速通编译原理 —— 从 Token 到字节码，手写完整编译器**

一个用纯 Python 编写的教学编译器，将 TinyLang（类 C 的玩具语言）编译为栈式虚拟机字节码并执行。

**总代码量 ~2500 行，零外部依赖，支持递归函数调用。**

## 🚀 快速开始

```bash
python main.py run examples/hello.tl
```

预期输出：
```
🖨️  输出: 50        ← add(42, 8)
🖨️  输出: 120       ← factorial(5)
🖨️  输出: TinyLang  ← 字符串
```

## 📖 完整教程

参见 [TUTORIAL.md](./TUTORIAL.md) —— 从零到完整编译器的 9 阶段详细教程。

## 🏗️ 编译管线

```
源代码 → [Lexer] → Token流 → [Parser] → AST
  → [Semantic] → 标注AST → [IR Gen] → TAC
  → [Optimizer] → 优化TAC → [CodeGen] → 字节码
  → [VM] → 执行结果
```

## 🛠️ 技术特点

- **Pratt 解析器**：用优先级表优雅处理运算符
- **嵌套符号表**：实现词法作用域
- **三地址码 (TAC)**：经典中间表示
- **多趟优化**：常量折叠、代数简化、死代码消除
- **栈式虚拟机**：支持递归函数调用

## 📄 License

MIT