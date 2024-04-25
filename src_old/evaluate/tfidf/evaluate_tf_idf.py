from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src_old.utils.evaluate_load_data import data_loader
from src_old.utils.find_threshold import find_threshold
import json
import time


def run_tf_idf(data_path, threshold=0):
    total = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    # log_path = '../../../logs/PMCOA_tf_idf_threshold={}.json'.format(threshold)
    # with open(log_path, 'w') as file:
    #     file.write('')

    loader = data_loader(data_path)
    while True:
        try:
            queries, targets, candidates, candidate_labels = next(loader)
            all_texts = queries + candidates

            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform(all_texts)

            for query, target in zip(queries, targets):
                total = total + 1
                # print('Working on sample {}'.format(total))

                query_tfidf = tfidf_vectorizer.transform([query])
                similarities = cosine_similarity(query_tfidf, tfidf_matrix[len(queries):])

                if max(similarities[0]) < threshold:
                    prediction = "None"
                    tn = tn + (target == prediction)
                    fn = fn + (target != "None")
                else:
                    closest_caption_index = similarities.argmax()
                    prediction = candidate_labels[closest_caption_index]
                    tp = tp + (target == prediction)
                    fp = fp + (target != prediction)

                # log = {
                #     "query": query,
                #     "target": target,
                #     "candidates": candidates,
                #     "scores": list(similarities[0]),
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
    total, precision, recall = run_tf_idf(data_path, threshold)

    print('Total number of samples: {}'.format(total))
    print('Precision Using TF_IDF: {}'.format(precision))
    print('Recall Using TF_IDF: {}'.format(recall))
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
