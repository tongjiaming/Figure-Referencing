import math


def dcg(scores):
    dcg_value = sum(score / math.log2((i+1) + 1) for i, score in enumerate(scores))
    return dcg_value


def idcg(scores):
    ideal_scores = sorted(scores, reverse=True)
    idcg_value = dcg(ideal_scores)
    return idcg_value


def ndcg(scores):
    dcg_value = dcg(scores)
    idcg_value = idcg(scores)
    ndcg_value = dcg_value / idcg_value if idcg_value > 0 else 0
    return ndcg_value


def similarities_to_ndcg(similarities, gt):
    sorted_similarities = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
    scores = [1 if item in gt else 0 for item in sorted_similarities]

    return ndcg(scores)
