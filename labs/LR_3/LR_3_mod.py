def reject_defective_items(weight_list, min_w=98.0, max_w=102.0):
    good = []
    bad = []
    for w in weight_list:
        if min_w <= w <= max_w:
            good.append(w)
        else:
            bad.append(w)
    return good, bad

def get_weight_distribution(weight_list):
    stats = {"легкие": 0, "нормальные": 0, "тяжелые": 0}
    for w in weight_list:
        if w < 98.0:
            stats["легкие"] += 1
        elif w > 102.0:
            stats["тяжелые"] += 1
        else:
            stats["нормальные"] += 1
    return stats

def get_sample_pack(weight_list, step=3):
    return weight_list[::step]