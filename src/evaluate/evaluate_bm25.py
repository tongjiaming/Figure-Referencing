from evaluate_load_data import data_loader
from rank_bm25 import BM25Okapi
import time


def run_pm25(data_path, threshold=-1):
    total = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0

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
                normalized_scores = [(x - min(scores)) / (max(scores) - min(scores)) for x in scores]

                if max(normalized_scores) < threshold:
                    prediction = "None"
                    tn = tn + (target == prediction)
                    fn = fn + (target != "None")
                else:
                    prediction = candidate_labels[normalized_scores.index(max(normalized_scores))]
                    tp = tp + (target == prediction)
                    fp = fp + (target != prediction)

        except StopIteration:
            break

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return total, recall, precision


def evaluate_all():
    DATA_PATH = '../../output/PMCOA_out.json'
    total, recall, precision = run_pm25(DATA_PATH)

    print('Total number of samples: {}'.format(total))
    print('Precision Using BM25: {}'.format(precision))
    print('Recall Using Bm25: {}'.format(recall))


def main():
    start_time = time.time()
    evaluate_all()
    print("Finished in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
