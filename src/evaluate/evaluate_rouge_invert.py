import evaluate
import json


DATA_PATH = '../../output/PMCOA_out2.json'
rouge = evaluate.load('rouge')


total = 0
correct = [0, 0, 0, 0]

with open(DATA_PATH) as file:
    for line in file:
        data = json.loads(line)

        if len(data['referenced_items']) <= 1:
            continue

        candidates = []
        candidate_ids = []

        for reference in data['references']:
            sentence_id = reference['sentence']
            for sentence in data['sentences']:
                if sentence_id == sentence['id']:
                    for paragraph in data['paragraphs']:
                        if paragraph['id'] == sentence['paragraph']:
                            sentence_text = paragraph['text'][sentence['start']:sentence['end']]
                            start = reference['start']
                            end = reference['end']
                            sentence_text = sentence_text[:start] + '<ref>' + sentence_text[:end]
                            candidates.append(sentence_text)
                            candidate_ids.append(reference['id'])
                            break
                    break

        for referenced_item in data['referenced_items']:
            total = total + 1
            print('Working on sample {}'.format(total))

            query = referenced_item['caption']
            gt = referenced_item['referencing_source']

            queries = [query] * len(candidates)

            results = rouge.compute(predictions=queries,
                                    references=candidates,
                                    use_aggregator=False)

            rouge1 = results["rouge1"]
            rouge2 = results["rouge2"]
            rougeL = results["rougeL"]
            rougeLsum = results["rougeLsum"]

            prediction_rouge1 = candidate_ids[rouge1.index(max(rouge1))]
            prediction_rouge2 = candidate_ids[rouge2.index(max(rouge2))]
            prediction_rougeL = candidate_ids[rougeL.index(max(rougeL))]
            prediction_rougeLsum = candidate_ids[rougeLsum.index(max(rougeLsum))]

            correct[0] = correct[0] + (prediction_rouge1 in gt)
            correct[1] = correct[1] + (prediction_rouge2 in gt)
            correct[2] = correct[2] + (prediction_rougeL in gt)
            correct[3] = correct[3] + (prediction_rougeLsum in gt)

print('Total number of samples: {}'. format(total))
print('Precision Using rouge1: {}'.format(correct[0] / total))
print('Precision Using rouge2: {}'.format(correct[1] / total))
print('Precision Using rougeL: {}'.format(correct[2] / total))
print('Precision Using rougeLsum: {}'.format(correct[3] / total))
