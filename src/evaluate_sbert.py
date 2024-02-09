from sentence_transformers import SentenceTransformer
import time
from numpy import dot
from numpy.linalg import norm
from load_data import data_loader


def cosine_similarity(query, candidates):
    # query: one embedding
    # candidates: a list of embeddings
    similarities = []
    for candidate in candidates:
        similarities.append(dot(query, candidate) / (norm(query) * norm(candidate)))
    return similarities


def main():
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    DATA_PATH = '../output/PMCOA_out2.json'

    total = 0
    correct = 0

    loader = data_loader(DATA_PATH)

    while True:
        try:
            queries, targets, candidates, candidate_labels = next(loader)
            for query, target in zip(queries, targets):
                total = total + 1
                print('Working on sample {}'.format(total))
                embeddings_query = model.encode(query)
                embeddings_candidates = model.encode(candidates)

                similarities = cosine_similarity(embeddings_query, embeddings_candidates)

                prediction = candidate_labels[similarities.index(max(similarities))]

                correct = correct + (prediction == target)

                print('correct: {}'.format(correct))

        except StopIteration:
            break

    print('Total number of samples: {}'.format(total))
    print('Precision Using ST: {}'.format(correct / total))


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("Finished in {} seconds".format(time.time() - start_time))
