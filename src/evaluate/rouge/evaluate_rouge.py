import evaluate
from src.utils.evaluate_load_data import data_loader
from src.utils.find_threshold import find_threshold
import time
import json


def run_rouge(data_path, threshold=0):
    rouge = evaluate.load('rouge')
    total = 0
    tp = [0, 0, 0, 0]
    fp = [0, 0, 0, 0]
    tn = [0, 0, 0, 0]
    fn = [0, 0, 0, 0]

    # log_path = '../../../logs/PMCOA_rouge_threshold={}.json'.format(threshold)
    # with open(log_path, 'w') as file:
    #     file.write('')

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
                prediction = ''

                for idx, score in enumerate([rouge1, rouge2, rougeL, rougeLsum]):
                    if max(score) < threshold:
                        prediction = "None"
                        tn[idx] = tn[idx] + (target == prediction)
                        fn[idx] = fn[idx] + (target != "None")
                    else:
                        prediction = candidate_labels[score.index(max(score))]
                        tp[idx] = tp[idx] + (target == prediction)
                        fp[idx] = fp[idx] + (target != prediction)

                # log = {
                #     "query": query,
                #     "target": target,
                #     "candidates": candidates,
                #     "rouge1": rouge1,
                #     "rouge2": rouge2,
                #     "rougeL": rougeL,
                #     "rougeLsum": rougeLsum,
                #     "threshold": threshold,
                #     "prediction": prediction
                # }
                # with open(log_path, 'a') as file:
                #     json.dump(log, file)
                #     file.write('\n')

        except StopIteration:
            break

    precisions = [0, 0, 0, 0]
    recalls = [0, 0, 0, 0]
    for i in range(4):
        precisions[i] = tp[i] / max(1, (tp[i] + fp[i]))
        recalls[i] = tp[i] / max(1, (tp[i] + fn[i]))

    return total, precisions, recalls


def evaluate_all(data_path):
    total, precisions, recalls = run_rouge(data_path)
    print('Total number of samples: {}'.format(total))
    print('Precision Using rouge1: {}'.format(precisions[0]))
    print('Precision Using rouge2: {}'.format(precisions[1]))
    print('Precision Using rougeL: {}'.format(precisions[2]))
    print('Precision Using rougeLsum: {}'.format(precisions[3]))


def main():
    start_time = time.time()
    DATA_PATH = '../../../output/PMCOA_out.json'
    find_threshold(DATA_PATH, run_rouge)
    # evaluate_all(DATA_PATH)
    print("Finished in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
