// TinyLang 示例程序
// 这个文件将伴随你整个学习过程，逐步支持更多特性

fn add(a: int, b: int) -> int {
    return a + b;
}

fn factorial(n: int) -> int {
    if n < 2 {
        return 1;
    }
    return n * factorial(n - 1);
}

fn main() {
    let x = 42;
    let y = 8;
    let sum = add(x, y);
    print(sum);

    let f = factorial(5);
    print(f);

    let name = "TinyLang";
    print(name);
}