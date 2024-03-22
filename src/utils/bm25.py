from functools import lru_cache

from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

from collections import Counter, defaultdict
import json
import numpy as np


class Tokenizer:
    def __init__(self):
        self.model = RegexpTokenizer(r"\w+")
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))

    @lru_cache(100_000)
    def lemmatize(self, token: str) -> str:
        return self.lemmatizer.lemmatize(token)

    def tokenize(
            self,
            text: str,
            lowercase: bool = True,
            lemmatize: bool = True,
            remove_stopwords: bool = True,
    ) -> list[str]:
        tokens = []
        for token in self.model.tokenize(text):
            if lowercase:
                token = token.lower()
            if lemmatize:
                token = self.lemmatize(token)

            if not remove_stopwords or token not in self.stopwords:
                tokens.append(token)

        return tokens


class BM25Ranker:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def initialize(self, docs: list[str]):
        # get number of documents
        n_docs = len(docs)

        # tokenize documents
        token_counter_per_doc = [
            Counter(self.tokenizer.tokenize(_)) for _ in docs
        ]
        doc_lengths = np.array([sum(_.values()) for _ in token_counter_per_doc])
        avg_doc_length = np.mean(doc_lengths)

        # determine number of times each token appears in each doc
        token2sparse_doc_freqs = defaultdict(list)
        for doc_idx, token_counter in enumerate(token_counter_per_doc):
            for token, count in token_counter.items():
                token2sparse_doc_freqs[token].append((doc_idx, count))

        # fix token ordering and construct mapping
        tokens = list(token2sparse_doc_freqs.keys())
        token2token_idx = {_: i for i, _ in enumerate(tokens)}

        # convert above mapping to list for faster access
        sparse_doc_freqs_per_token = [token2sparse_doc_freqs[_] for _ in tokens]

        # set attributes
        self.n_docs = n_docs
        self.doc_lengths = doc_lengths
        self.avg_doc_length = avg_doc_length
        self.token2token_idx = token2token_idx
        self.sparse_doc_freqs_per_token = sparse_doc_freqs_per_token

    def load(self, filepath: str):
        with open(filepath, 'r') as f:
            info = json.load(f)

        self.n_docs = info['n_docs']
        self.doc_lengths = np.array(info['doc_lengths'])
        self.avg_doc_length = info['avg_doc_length']
        self.token2token_idx = info['token2token_idx']
        self.sparse_doc_freqs_per_token = info['sparse_doc_freqs_per_token']

    def save(self, out_path: str):
        with open(out_path, 'w') as f_out:
            json.dump({
                "n_docs": self.n_docs,
                "doc_lengths": self.doc_lengths.tolist(),
                "avg_doc_length": self.avg_doc_length,
                "token2token_idx": self.token2token_idx,
                "sparse_doc_freqs_per_token": self.sparse_doc_freqs_per_token,
            }, f_out)

    def get_scores(self, query: str, k1: float = 1.2, b: float = 0.75):
        # determine valid query tokens and their indices
        query_tokens = set(self.tokenizer.tokenize(query))
        query_tokens = query_tokens.intersection(self.token2token_idx)
        query_token_idxs = [self.token2token_idx[_] for _ in query_tokens]

        # compute IDF for each token
        n_docs_per_query_token = np.array([
            len(self.sparse_doc_freqs_per_token[_]) for _ in query_token_idxs
        ], dtype=np.float64)

        IDFs = np.log(
            1 + (self.n_docs - n_docs_per_query_token + 0.5) / (n_docs_per_query_token + 0.5)
        )

        # compute DF for each token
        DFs = []
        for token_idx in query_token_idxs:
            DF = np.zeros(self.n_docs)

            sparse_doc_idxs, sparse_doc_freqs = list(
                list(_) for _ in zip(*self.sparse_doc_freqs_per_token[token_idx])
            )
            DF[sparse_doc_idxs] = sparse_doc_freqs
            DFs.append(DF)
        DFs = np.array(DFs)

        # compute scores
        return np.dot(
            IDFs,
            DFs * (k1 + 1) / (DFs + k1 * (1 - b + b * self.n_docs / self.avg_doc_length)),
        )


def bm25_by_paper(queries, targets, candidates, candidate_labels, threshold=0):
    total = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    tokenizer = Tokenizer()
    bm25 = BM25Ranker(tokenizer)
    bm25.initialize(candidates)

    for query, target in zip(queries, targets):
        total = total + 1
        scores = bm25.get_scores(query)

        try:
            scores = list(scores)
        except Exception:
            scores = [0] * len(candidates)

        if max(scores) < threshold:
            prediction = "None"
            tn = tn + (target == prediction)
            fn = fn + (target != "None")
        else:
            prediction = candidate_labels[scores.index(max(scores))]
            tp = tp + (target == prediction)
            fp = fp + (target != prediction)

    return total, tp, fp, tn, fn


def my_test():
    from utils.evaluate_load_data import data_loader
    data_path = '../../output/PMCOA_out.json'
    loader = data_loader(data_path)
    total_acc = 0
    tp_acc = 0
    while True:
        try:
            queries, targets, candidates, candidate_labels = next(loader)
            res = bm25_by_paper(queries, targets, candidates, candidate_labels)
            total_acc += res[0]
            tp_acc += res[1]

        except Exception as e:
            print(e)
            break

    print(total_acc)
    print(tp_acc)


if __name__ == '__main__':
    my_test()
