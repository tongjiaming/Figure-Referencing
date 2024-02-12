import evaluate
from load_data import data_loader
import time


start_time = time.time()
DATA_PATH = '../../output/PMCOA_out2.json'
rouge = evaluate.load('rouge')

total = 0
correct = [0, 0, 0, 0]

loader = data_loader(DATA_PATH)

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

            prediction_rouge1 = candidate_labels[rouge1.index(max(rouge1))]
            prediction_rouge2 = candidate_labels[rouge2.index(max(rouge2))]
            prediction_rougeL = candidate_labels[rougeL.index(max(rougeL))]
            prediction_rougeLsum = candidate_labels[rougeLsum.index(max(rougeLsum))]

            correct[0] = correct[0] + (target == prediction_rouge1)
            correct[1] = correct[1] + (target == prediction_rouge2)
            correct[2] = correct[2] + (target == prediction_rougeL)
            correct[3] = correct[3] + (target == prediction_rougeLsum)

    except StopIteration:
        break

print('Total number of samples: {}'. format(total))
print('Precision Using rouge1: {}'.format(correct[0] / total))
print('Precision Using rouge2: {}'.format(correct[1] / total))
print('Precision Using rougeL: {}'.format(correct[2] / total))
print('Precision Using rougeLsum: {}'.format(correct[3] / total))
print("Finished in {} seconds".format(time.time() - start_time))
