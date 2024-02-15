from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json


DATA_PATH = '../../output/PMCOA_out.json'

total = 0
correct = 0

with open(DATA_PATH) as file:
    for line in file:
        data = json.loads(line)

        if len(data['referenced_items']) <= 1:
            continue

        queries = []
        gts = []
        for reference in data['references']:
            sentence_id = reference['sentence']
            start = reference['start']
            end = reference['end']

            for sentence in data['sentences']:
                if sentence_id == sentence['id']:
                    for paragraph in data['paragraphs']:
                        if paragraph['id'] == sentence['paragraph']:
                            sentence_text = paragraph['text'][sentence['start']:sentence['end']]
                            break
                    break
            query = sentence_text[:start] + '<ref>' + sentence_text[:end]
            queries.append(query)

            gt = reference['target']
            gts.append(gt)

        candidates = []
        candidate_labels = []
        for candidate in data['referenced_items']:
            candidates.append(candidate['caption'])
            candidate_labels.append(candidate['id'])

        all_texts = queries + candidates

        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(all_texts)

        for query, gt in zip(queries, gts):
            total = total + 1
            print('Working on sample {}'.format(total))

            # if total == 53:
            #     pass

            query_tfidf = tfidf_vectorizer.transform([query])
            similarities = cosine_similarity(query_tfidf, tfidf_matrix[len(queries):])
            closest_caption_index = similarities.argmax()

            prediction = candidate_labels[closest_caption_index]

            correct = correct + (gt == prediction)

print('Total number of samples: {}'. format(total))
print('Precision Using TF-IDF: {}'.format(correct / total))
