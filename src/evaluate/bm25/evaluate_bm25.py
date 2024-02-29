from src.utils.evaluate_load_data import data_loader
from src.utils.find_threshold import find_threshold
from rank_bm25 import BM25Okapi
import time
import json


def run_pm25(data_path, threshold=0):
    total = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    # log_path = '../../../logs/PMCOA_bm25_threshold={}.json'.format(threshold)
    # with open(log_path, 'w') as file:
    #     file.write('')

    loader = data_loader(data_path)
    while True:
        try:
            queries, targets, candidates, candidate_labels = next(loader)
            corpus = [candidate.split() for candidate in candidates]
            bm25 = BM25Okapi(corpus)

            for query, target in zip(queries, targets):
                total = total + 1
                print('Working on sample {}'.format(total))
                scores = bm25.get_scores(query.split(' '))
                scores = list(scores)
                normalized_scores = [max(0, x) for x in scores]
                normalized_scores = [x / (sum(normalized_scores) + 0.000001) for x in normalized_scores]

                if max(normalized_scores) < threshold:
                    prediction = "None"
                    tn = tn + (target == prediction)
                    fn = fn + (target != "None")
                else:
                    prediction = candidate_labels[normalized_scores.index(max(normalized_scores))]
                    tp = tp + (target == prediction)
                    fp = fp + (target != prediction)

                # log = {
                #     "query": query,
                #     "target": target,
                #     "candidates": candidates,
                #     "scores": scores,
                #     "normalized_scores": normalized_scores,
                #     "threshold": threshold,
                #     "prediction": prediction
                # }
                # with open(log_path, 'a') as file:
                #     json.dump(log, file)
                #     file.write('\n')

        except StopIteration:
            break

    precision = tp / max(1, (tp + fp))
    recall = tp / max(1, (tp + fn))
    return total, precision, recall


def evaluate_all(data_path, threshold=0):
    total, recall, precision = run_pm25(data_path, threshold)

    print('Total number of samples: {}'.format(total))
    print('Precision Using BM25: {}'.format(precision))
    print('Recall Using Bm25: {}'.format(recall))
    print('==========================================')

    return total, precision, recall


def main():
    start_time = time.time()

    DATA_PATH = '../../../output/PMCOA_out.json'
    # evaluate_all(DATA_PATH)
    find_threshold(DATA_PATH, evaluate_all)
    print("Finished in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
