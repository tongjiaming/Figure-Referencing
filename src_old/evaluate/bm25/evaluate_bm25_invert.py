import time
import json
from src_old.utils.metrics_NDCG import similarities_to_ndcg
from rank_bm25 import BM25Okapi


def run_pm25(data_path):
    total = 0
    correct = 0
    ndcg_acc = 0

    with open(data_path) as file:
        for line in file:
            data = json.loads(line)

            if len(data['referenced_items']) <= 1:
                continue

            candidates = []
            candidate_ids = []
            queries = []
            gts = []

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
                query = referenced_item['caption']
                gt = referenced_item['referencing_source']

                queries.append(query)
                gts.append(gt)

            corpus = [candidate.split() for candidate in candidates]
            bm25 = BM25Okapi(corpus)

            for query, gt in zip(queries, gts):
                total = total + 1
                print('Working on sample {}'.format(total))

                scores = bm25.get_scores(query.split(' '))
                scores = list(scores)
                normalized_scores = [(x - min(scores)) / (max(scores) - min(scores)) for x in scores]

                closest_caption_index = normalized_scores.index(max(normalized_scores))
                prediction = candidate_ids[closest_caption_index]

                correct = correct + (prediction in gt)

                ndcg = similarities_to_ndcg(normalized_scores, gt)
                ndcg_acc = ndcg_acc + ndcg

    print('Total number of samples: {}'.format(total))
    print('Precision Using BM25: {}'.format(correct / total))
    print('NDCG Using BM25: {}'.format(ndcg_acc / total))


def main():
    start_time = time.time()
    DATA_PATH = '../../../output/PMCOA_out.json'
    run_pm25(DATA_PATH)
    print("Finished in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
