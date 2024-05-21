def add(x, y):
    return (x + y)
def subtract(x, y):
    return (x - y)
def main():
    x = int(input("첫번째 숫자를 입력해주세요 : "))
    y = int(input("두번째 숫자를 입력해주세요 : "))
    total = add(x, y)
    sub = subtract(x, y)
    print(str(x), "+", str(y), "=", str(total))
    print(str(x), "-", str(y), "=", str(sub))

if __name__ == "__main__":
    main()