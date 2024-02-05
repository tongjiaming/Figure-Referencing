import evaluate
import json


DATA_PATH = '../output/PMCOA_out2.json'
rouge = evaluate.load('rouge')


total = 0
correct = [0, 0, 0, 0]

with open(DATA_PATH) as file:
    for line in file:
        data = json.loads(line)
        for reference in data['references']:
            total = total + 1
            print('Working on sample {}'.format(total))

            sentence_id = reference['sentence']
            start = reference['start']
            end = reference['end']
            candidates = []
            candidate_labels = []

            for sentence in data['sentences']:
                if sentence_id == sentence['id']:
                    for paragraph in data['paragraphs']:
                        if paragraph['id'] == sentence['paragraph']:
                            sentence_text = paragraph['text'][sentence['start']:sentence['end']]
                            break
                    break

            query = sentence_text[:start] + '<mask>' + sentence_text[:end]
            gt = reference['target']
            for candidate in data['referenced_items']:
                candidates.append(candidate['caption'])
                candidate_labels.append(candidate['id'])

            if not isinstance(candidates, list):
                candidates = [candidates]
            queries = [query] * len(candidates)

            assert isinstance(queries, list)
            assert isinstance(candidates, list)
            assert len(queries) == len(candidates)

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

            correct[0] = correct[0] + (gt == prediction_rouge1)
            correct[1] = correct[1] + (gt == prediction_rouge2)
            correct[2] = correct[2] + (gt == prediction_rougeL)
            correct[3] = correct[3] + (gt == prediction_rougeLsum)

print('Total number of samples: {}'. format(total))
print('Precision Using rouge1: {}'.format(correct[0] / total))
print('Precision Using rouge2: {}'.format(correct[1] / total))
print('Precision Using rougeL: {}'.format(correct[2] / total))
print('Precision Using rougeLsum: {}'.format(correct[3] / total))
