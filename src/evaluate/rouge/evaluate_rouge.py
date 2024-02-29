import evaluate
from src.utils.evaluate_load_data import data_loader
from src.utils.find_threshold import find_threshold
import time


def run_rouge(data_path, threshold=0):
    rouge = evaluate.load('rouge')
    total = 0
    correct = [0, 0, 0, 0]

    loader = data_loader(data_path)
    while True:
        try:
            queries, targets, candidates, candidate_labels = next(loader)
            for query, target in zip(queries, targets):
                total = total + 1
                print('Working on sample {}'.format(total))

                queries = [query] * len(candidates)

                results = rouge.compute(predictions=queries,
                                        references=candidates,
                                        use_aggregator=False)

                rouge1 = results["rouge1"]
                rouge2 = results["rouge2"]
                rougeL = results["rougeL"]
                rougeLsum = results["rougeLsum"]

                if max(rouge1) < threshold:
                    prediction_rouge1 = "None"
                else:
                    prediction_rouge1 = candidate_labels[rouge1.index(max(rouge1))]

                if max(rouge2) < threshold:
                    prediction_rouge2 = "None"
                else:
                    prediction_rouge2 = candidate_labels[rouge2.index(max(rouge2))]

                if max(rougeL) < threshold:
                    prediction_rougeL = "None"
                else:
                    prediction_rougeL = candidate_labels[rougeL.index(max(rougeL))]

                if max(rougeLsum) < threshold:
                    prediction_rougeLsum = "None"
                else:
                    prediction_rougeLsum = candidate_labels[rougeLsum.index(max(rougeLsum))]

                correct[0] = correct[0] + (target == prediction_rouge1)
                correct[1] = correct[1] + (target == prediction_rouge2)
                correct[2] = correct[2] + (target == prediction_rougeL)
                correct[3] = correct[3] + (target == prediction_rougeLsum)

        except StopIteration:
            break

    precision = [item / total for item in correct]
    return total, precision


def evaluate_all():
    DATA_PATH = '../../../output/PMCOA_out.json'
    total, precision = run_rouge(DATA_PATH)

    print('Total number of samples: {}'.format(total))
    print('Precision Using rouge1: {}'.format(precision[0]))
    print('Precision Using rouge2: {}'.format(precision[1]))
    print('Precision Using rougeL: {}'.format(precision[2]))
    print('Precision Using rougeLsum: {}'.format(precision[3]))


def main():
    start_time = time.time()
    # find_threshold(run_rouge)
    evaluate_all()
    print("Finished in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
