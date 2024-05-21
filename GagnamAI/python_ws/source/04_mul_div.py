def mul(x, y):
    return (x * y)

def div(x, y):
    if y != 0:
        return (x / y)
    else:
        print("0으로 나눌 수 없습니다.")

def main():
    x = float(input("첫번째 숫자를 입력해주세요 : "))
    y = float(input("두번째 숫자를 입력해주세요 : "))
    result_mul = mul(x, y)
    result_div = div(x, y)
    print(f"{x} x {y} = {result_mul}")
    print(f"{x} / {y} = {result_div}")

if __name__ == "__main__":
    main()