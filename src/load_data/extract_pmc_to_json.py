import pubmed_parser as pp
import lib_pubmed_oa_parser2 as pp2
import json
import os

DATA_PATH = '../../data/pmc/'
TEST_DATA_PATH = '../../data/pmc/PMC516027.xml'
OUTPUT_PATH = '../../output/PMCOA_out.json'
TEST_OUTPUT_PATH = '../../output/PMCOA_extract_test.json'


def process_paper(path, paper_id):
    paper_URL = ""

    dict_out = pp.parse_pubmed_xml(path)
    title = dict_out["full_title"]
    pmcid = dict_out["pmc"]
    abstract = dict_out["abstract"]
    paper_year = dict_out["publication_year"]

    paragraphs, sentences, references, referenced_items = (
        pp2.parse_pubmed_paragraph3(path, paper_id, with_fake_refs=True))

    out_figure = pp2.parse_pubmed_caption2(path)
    out_table = pp2.parse_pubmed_table2(path)

    for item in referenced_items:
        if item["type"] == "fig":
            for fig in out_figure:
                if item["id"] == fig["fig_id"] and fig["fig_caption"] is not None:
                    item["caption"] = fig["fig_caption"]
                    break
        elif item["type"] == "table":
            for fig in out_table:
                if item["id"] == fig["table_id"] and fig["table_caption"] is not None:
                    item["caption"] = fig["table_caption"]
                    break

    data_sample = {
        "paper_id": paper_id,
        "paper_URL": paper_URL,
        "paper_PMCID": pmcid,
        "paper_year": paper_year,
        "paper_title": title,
        "paper_abstract": abstract,
        "paragraphs": paragraphs,
        "sentences": sentences,
        "references": references,
        "referenced_items": referenced_items
    }

    return data_sample


def my_test():
    data_sample = process_paper(TEST_DATA_PATH, 0)
    print('Extracting from ' + TEST_DATA_PATH)
    with open(TEST_OUTPUT_PATH, 'w') as file:  # clear old content
        json.dump(data_sample, file)


def main():
    with open(OUTPUT_PATH, 'w') as file:  # clear old content
        file.write('')

    for foldername, subfolders, filenames in os.walk(DATA_PATH):
        foldername = foldername.replace('\\', '/')
        print(foldername)
        for paper_id, filename in enumerate(filenames):
            file_path = foldername + filename
            print('Extracting from ' + file_path)
            data_sample = process_paper(file_path, paper_id)
            with open(OUTPUT_PATH, 'a') as file:
                json.dump(data_sample, file)
                file.write('\n')


if __name__ == "__main__":
    # my_test()
    main()
