import LR_3_mod

step = 3

weights = [100.1, 99.5, 96.8, 101.2, 103.5, 100.0, 98.9, 100.4, 101.8]

good, bad = LR_3_mod.reject_defective_items(weights)
stats = LR_3_mod.get_weight_distribution(weights)
sample = LR_3_mod.get_sample_pack(weights, step)

print("Годная продукция:", good)
print("Брак:", bad)
print("Статистика:", stats)
print("Контрольная выборка каждого", step,"-го изделия:", sample)

