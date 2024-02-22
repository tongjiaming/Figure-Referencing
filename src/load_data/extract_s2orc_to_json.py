import json
from sentence_splitter import split_text_into_sentences


def extract_s2orc(data_path, out_path, n=-1):
    with open(data_path) as file, open(out_path, 'w') as file2:
        paper_id = 0
        while paper_id != n:
            print('Extracting paper {}'.format(paper_id))
            line = file.readline()
            json_object = json.loads(line)
            if not json_object['ref_entries']:
                continue

            with_ref = False
            for body_text in json_object['body_text']:
                if body_text['ref_spans']:
                    with_ref = True
            if not with_ref:
                continue

            paper_URL = ''
            pmcid = ''
            s2orcid = json_object['paper_id']
            title = ''
            if json_object['abstract']:
                abstract = json_object['abstract'][0]['text']

            paragraphs = []
            paragraph_id = 0
            sentences = []
            sentence_id = 0
            references = []
            local_reference_id = 0
            referenced_items = dict()

            for body_text in json_object['body_text']:
                if body_text['text'] != '':
                    paragraph = dict()
                    paragraph_sentences = []
                    paragraph['id'] = paragraph_id
                    paragraph['text'] = body_text['text']
                    paragraph['section'] = body_text['section']
                    paragraphs.append(paragraph)

                    raw_sentences = split_text_into_sentences(paragraph['text'], 'en')
                    for raw_sentence in raw_sentences:
                        sentence = dict()
                        sentence['id'] = sentence_id
                        sentence['paragraph'] = paragraph_id
                        sentence['start'] = paragraph['text'].find(raw_sentence)
                        sentence['end'] = sentence['start'] + len(raw_sentence)
                        sentence['text'] = raw_sentence
                        sentence['fake_ref_candidate'] = False
                        paragraph_sentences.append(sentence)
                        sentence_id = sentence_id + 1

                    if body_text['ref_spans']:
                        for span in body_text['ref_spans']:
                            reference = dict()
                            for sentence in paragraph_sentences:
                                if sentence['start'] < span['start'] < sentence['end']:
                                    reference['reference_id'] = 'S2ORC' + str(local_reference_id + 1000 * paper_id)
                                    reference['sentence'] = sentence['id']
                                    reference['start'] = span['start'] - sentence['start']
                                    reference['end'] = span['end'] - sentence['start']
                                    reference['label'] = span['text']
                                    reference['target'] = span['ref_id']
                                    references.append(reference)
                                    local_reference_id = local_reference_id + 1

                                    raw_referenced_item = json_object['ref_entries'][span['ref_id']]
                                    if span['ref_id'] not in referenced_items.keys():
                                        referenced_item = dict()
                                        referenced_item['item_id'] = span['ref_id']
                                        referenced_item['item_URL'] = ''
                                        referenced_item['item_label'] = reference['label']
                                        referenced_item['item_type'] = raw_referenced_item['type']
                                        referenced_item['referencing_source'] = [reference['reference_id']]
                                        referenced_item['caption'] = raw_referenced_item['text']
                                        referenced_items[span['ref_id']] = referenced_item
                                    else:
                                        referenced_items[
                                            span['ref_id']]['referencing_source'].append(reference['reference_id'])

                    paragraph_id = paragraph_id + 1
                    sentences = sentences + paragraph_sentences

            data_sample = {
                "paper_id": paper_id,
                "paper_URL": paper_URL,
                "paper_PMCID": pmcid,
                "paper_s2orc_id": s2orcid,
                "paper_title": title,
                "paper_abstract": abstract,
                "paragraphs": paragraphs,
                "sentences": sentences,
                "references": references,
                "referenced_items": list(referenced_items.values())
            }

            file2.write(json.dumps(data_sample) + '\n')
            paper_id = paper_id + 1


def main():
    DATA_PATH = '../../data/S2ORC/pdf_parses_0.jsonl'
    OUT_DATA_PATH = '../../output/S2ORC/s2orc_out.json'
    extract_s2orc(DATA_PATH, OUT_DATA_PATH, n=100)


if __name__ == "__main__":
    main()