"""Load json into queries, targets, candidates, candidate_labels for experiments."""
import json

DATA_PATH = '../../output/PMCOA_out2.json'


def data_loader(data_path):
    with open(data_path) as file:
        for line in file:

            data = json.loads(line)

            queries = []
            targets = []
            candidates = []
            candidate_labels = []

            if len(data['referenced_items']) <= 1:
                continue

            for reference in data['references']:
                sentence_id = reference['sentence']
                start = reference['start']
                end = reference['end']

                sentence = data['sentences'][sentence_id]
                paragraph = data['paragraphs'][sentence['paragraph']]
                sentence_text = paragraph['text'][sentence['start']:sentence['end']]

                # for sentence in data['sentences']:
                #     if sentence_id == sentence['id']:
                #         for paragraph in data['paragraphs']:
                #             if paragraph['id'] == sentence['paragraph']:
                #                 sentence_text = paragraph['text'][sentence['start']:sentence['end']]
                #                 break
                #         break

                query = sentence_text[:start] + '<ref>' + sentence_text[:end]
                queries.append(query)

                target = reference['target']
                targets.append(target)

            for candidate in data['referenced_items']:
                candidates.append(candidate['caption'])
                candidate_labels.append(candidate['id'])

            assert len(queries) == len(targets) and len(queries) != 0
            assert len(candidates) == len(candidate_labels) and len(candidates) != 0

            yield queries, targets, candidates, candidate_labels


def main():
    total = 0
    loader = data_loader(DATA_PATH)
    while True:
        try:
            queries, targets, candidates, candidate_labels = next(loader)
            total = total + 1
            print(total)
        except StopIteration:
            break


if __name__ == "__main__":
    main()
