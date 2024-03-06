import math


def tokenizer_bm25(text):
    tokens = text.split(' ')
    return tokens


def get_idf(num_docs, n_qi):
    idf = math.log((num_docs - n_qi + 0.5) / (n_qi + 0.5) + 1)
    return idf


def my_bm25(query, docs, k_1=1.2, b=0.75):
    scores = []
    query_tokens = tokenizer_bm25(query)

    tokenized_docs = [tokenizer_bm25(doc) for doc in docs]
    avg_dl = sum([len(doc) for doc in tokenized_docs]) / len(tokenized_docs)

    for doc in tokenized_docs:
        score_acc = 0
        for query_token in query_tokens:
            num_docs = len(tokenized_docs)
            n_qi = sum([query_token in tokenized_doc for tokenized_doc in tokenized_docs])
            idf = get_idf(num_docs, n_qi)
            fd = doc.count(query_token)

            score = idf * fd * (k_1 + 1) / (fd + k_1 * (1 - b + b * num_docs / avg_dl))
            score_acc = score_acc + score
        scores.append(score_acc)

    return scores


def main():
    docs = [
        "this first sentence has six words",
        "this second sentence has six words",
        "sentence"
    ]

    query = docs[2]
    scores = my_bm25(query, docs)
    print(scores)


if __name__ == '__main__':
    main()
