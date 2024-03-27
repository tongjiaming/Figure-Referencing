import json
import os
from sentence_splitter import split_text_into_sentences
from src.utils.utils import config_log
from src.utils.decorater import execution_time
from multiprocessing import Pool
from tqdm import tqdm


def extract_s2orc_meta(meta_data_path, meta_dict_path):
    if not os.path.exists(meta_dict_path):
        meta_dict = dict()
        with open(meta_data_path) as file, open(meta_dict_path, 'w') as file2:
            for line in file:
                data_object = json.loads(line)
                meta_dict[data_object['paper_id']] = {
                    'year': data_object['year'],
                    'title': data_object['title']
                }

            file2.write(json.dumps(meta_dict) + '\n')


def extract_s2orc(data_path, meta_dict_path, idx):
    data_samples = []

    with open(meta_dict_path) as file:
        line = file.readline()
        meta_dict = json.loads(line)

    with open(data_path) as file:
        paper_id = 0
        print(paper_id)
        for line in file:
            json_object = json.loads(line)
            if not json_object['ref_entries']:
                continue

            with_ref = False
            for body_text in json_object['body_text']:
                if body_text['ref_spans']:
                    with_ref = True
                    break
            if not with_ref:
                continue

            paper_URL = ''
            pmcid = ''
            s2orcid = json_object['paper_id']

            abstract = ''
            if json_object['abstract']:
                abstract = json_object['abstract'][0]['text']

            paper_year = meta_dict[s2orcid]['year']
            title = meta_dict[s2orcid]['title']

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
                                    reference['reference_id'] = 'S2ORC_{}_{}_{}'.format(idx, paper_id, local_reference_id)
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
                "paper_id": '{}_{}'.format(idx, paper_id),
                "paper_URL": paper_URL,
                "paper_PMCID": pmcid,
                "paper_s2orc_id": s2orcid,
                "paper_year": paper_year,
                "paper_month": '',
                "paper_day": '',
                "paper_title": title,
                "paper_abstract": abstract,
                "paragraphs": paragraphs,
                "sentences": sentences,
                "references": references,
                "referenced_items": list(referenced_items.values())
            }

            paper_id = paper_id + 1
            data_samples.append(data_sample)
            print(len(data_samples))

    return data_samples


def process_s2orc(idx):
    data_path = DATA_PATH.format(idx)
    meta_data_path = META_DATA_PATH.format(idx)
    meta_dict_path = META_DICT_PATH.format(idx)

    extract_s2orc_meta(meta_data_path, meta_dict_path)
    return extract_s2orc(data_path, meta_dict_path, idx)


@execution_time
def main():
    decision = input("The old output {} will be deleted, continue? (y/n): ".format(OUT_DATA_PATH))
    if decision.lower() != 'y':
        return 0

    # config_log('s2orc')

    with open(OUT_DATA_PATH, 'w') as file:
        with Pool(2) as pool:
            res = tqdm(pool.imap_unordered(func=process_s2orc, iterable=range(0, NUM_S2ORC)), total=NUM_S2ORC)
            for data_samples in res:
                for data_sample in data_samples:
                    if data_sample is not None:
                        json.dump(data_sample, file)
                        file.write('\n')


DATA_PATH = '../../data/S2ORC/pdf_parses_{}.jsonl'
META_DATA_PATH = '../../data/S2ORC/metadata_{}.jsonl'
META_DICT_PATH = 'meta_dict_{}.json'
OUT_DATA_PATH = 's2orc.jsonl'
NUM_S2ORC = 1
main()
