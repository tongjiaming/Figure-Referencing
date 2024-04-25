from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from src_old.utils.metrics_NDCG import similarities_to_ndcg


DATA_PATH = '../../../output/PMCOA_out.json'

total = 0
correct = 0
ndcg_acc = 0

with open(DATA_PATH) as file:
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

        all_texts = queries + candidates

        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(all_texts)

        for query, gt in zip(queries, gts):
            total = total + 1
            print('Working on sample {}'.format(total))

            query_tfidf = tfidf_vectorizer.transform([query])
            similarities = cosine_similarity(query_tfidf, tfidf_matrix[len(queries):])
            closest_caption_index = similarities.argmax()

            prediction = candidate_ids[closest_caption_index]

            correct = correct + (prediction in gt)

            ndcg = similarities_to_ndcg(similarities[0], gt)
            ndcg_acc = ndcg_acc + ndcg

print('Total number of samples: {}'.format(total))
print('Precision Using TF-IDF: {}'.format(correct / total))
print('NDCG Using TF-IDF: {}'.format(ndcg_acc / total))
