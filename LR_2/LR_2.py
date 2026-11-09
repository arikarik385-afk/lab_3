def filter_adc_signal(data):
    clean = []
    total = 0
    for x in data:
        if x == 0 or x == 1023:
            continue
        clean.append(x)
        total = total + x

    if len(clean) > 0:
        average = total / len(clean)
    else:
        average = 0
    return clean, average


data = [1023, 500, 512, 498, 505, 1023, 300]

clean, average = filter_adc_signal(data)
print("Отфильтрованный список:", clean)
print("Среднее значение:", average)