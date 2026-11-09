print("Программа расчета тепловых потерь стены \n")
print("Введите значение k \n")
while True:
    k = float(input())
    if k > 0:
        break
    print("Введено некорректное значение")
print("Введите значение s \n")
while True:
    s = float(input())
    if s > 0:
        break
    print("Введено некорректное значение")
print("Введите значение t1 \n")
t1 = float(input())
print("Введите значение t2 \n")
t2 = float(input())
print("Введите значение d \n")
while True:
    d = float(input())
    if d > 0:
        break
    print("Введено некорректное значение")
print("Тепловые потери стены составляют: ")
print(k*s*((t1 - t2))/d)