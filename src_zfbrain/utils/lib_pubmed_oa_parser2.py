from pubmed_parser import read_xml, stringify_children, parse_article_meta
from sentence_splitter import split_text_into_sentences
import random


def parse_pubmed_paragraph2(path, paper_id):
    """
    Old version of paper parser, no longer supported and updated.
    """
    tree = read_xml(path)
    raw_paragraphs = tree.xpath("//body//p")
    paragraphs = []
    sentences = []
    references = []
    referenced_items = []
    target_ids = []
    global_sentence_id = 0
    global_reference_id = 0

    for idx, raw_paragraph in enumerate(raw_paragraphs):
        paragraph_id = '{}_{}'.format(paper_id, idx)
        paragraph_text = stringify_children(raw_paragraph)
        section = raw_paragraph.find("../title")

        if section is not None:
            section = stringify_children(section).strip()
        else:
            section = ""

        paragraph = {
            "id": paragraph_id,
            "text": paragraph_text,
            "section": section
        }
        paragraphs.append(paragraph)

        paragraph_sentences = []
        raw_sentences = split_text_into_sentences(paragraph_text, 'en')

        for raw_sentence in raw_sentences:
            sentence_id = '{}_{}'.format(paper_id, global_sentence_id)
            global_sentence_id = global_sentence_id + 1
            start = paragraph_text.find(raw_sentence)
            end = start + len(raw_sentence)
            sentence = {
                "id": sentence_id,
                "paragraph": paragraph_id,
                "start": start,
                "end": end,
                "text": raw_sentence  # Temp var for reference find
            }
            paragraph_sentences.append(sentence)
        sentences = sentences + paragraph_sentences

        available_references = []
        for raw_reference in raw_paragraph.getchildren():
            if "ref-type" in raw_reference.attrib.keys():
                if raw_reference.attrib["ref-type"] in ['fig', 'table']:
                    if raw_reference.text is not None:
                        available_references.append(raw_reference)

        for reference in available_references:
            ref_id = '{}_{}'.format(paper_id, global_reference_id)
            global_reference_id = global_reference_id + 1
            target_id = reference.attrib["rid"]
            ref_label = reference.text

            for sentence_idx, sentence in enumerate(paragraph_sentences):
                sentence_text = sentence['text']
                if (ref_label is not None) and (ref_label in sentence_text):
                    context_sentence = sentence['id']
                    start = sentence_text.find(ref_label)
                    end = start + len(ref_label)
                    reference_out = {
                        "id": ref_id,
                        "sentence": context_sentence,
                        "start": start,
                        "end": end,
                        "label": ref_label,
                        "target": target_id,
                    }
                    references.append(reference_out)

                    # # mask saved reference to avoid repeat
                    sentence_text = sentence_text[:start] + '#'*len(ref_label) + sentence_text[end:]
                    paragraph_sentences[sentence_idx]['text'] = sentence_text
                    break

            if target_id in target_ids:
                for item in referenced_items:
                    if target_id == item["id"]:
                        item["referencing_source"].append(ref_id)
            else:
                target_ids.append(target_id)
                referenced_item = {
                    "id": target_id,
                    "URL": "",
                    "label": ref_label,
                    "type": reference.attrib["ref-type"],
                    "referencing_source": [ref_id],
                    "caption": ""
                }
                referenced_items.append(referenced_item)

    for sentence in sentences:  # Remove temp var
        del sentence['text']

    return paragraphs, sentences, references, referenced_items


def parse_pubmed_paragraph3(path, paper_id, with_fake_refs=False, fake_refs_ratio=0.5):
    """
    A new version of the parser that parse a single paper and return the parsed information.
    INPUT:
        with_fake_refs: if we want refs without any target. Fake refs are sentences in the paragraph without any refs.
        fake_refs_ratio: the ratio of fake refs in all refs.
    RETURN: paragraphs, sentences, references, referenced_items
    """
    tree = read_xml(path)
    raw_paragraphs = tree.xpath("//body//p")
    paragraphs = []
    sentences = []
    references = []
    referenced_items = []
    target_ids = []
    global_sentence_id = 0  # unique within the paper
    global_reference_id = 0  # unique within the paper(but final ref_id is unique among all papers)

    # loop all paragraphs in the paper
    for paragraph_id, raw_paragraph in enumerate(raw_paragraphs):
        paragraph_text = stringify_children(raw_paragraph)
        section = raw_paragraph.find("../title")
        paragraph_has_ref = False

        if section is not None:
            section = stringify_children(section).strip()
        else:
            section = ""

        paragraph = {
            "id": paragraph_id,
            "text": paragraph_text,
            "section": section
        }
        paragraphs.append(paragraph)

        # loop all sentences in the paragraph
        paragraph_sentences = []
        raw_sentences = split_text_into_sentences(paragraph_text, 'en')

        for raw_sentence in raw_sentences:
            start = paragraph_text.find(raw_sentence)
            end = start + len(raw_sentence)
            sentence = {
                "id": global_sentence_id,
                "paragraph": paragraph_id,
                "start": start,
                "end": end,
                "text": raw_sentence,  # Temp var for reference find
                "fake_ref_candidate": True
            }
            paragraph_sentences.append(sentence)
            global_sentence_id = global_sentence_id + 1

        available_references = []
        for raw_reference in raw_paragraph.getchildren():
            if "ref-type" in raw_reference.attrib.keys():
                if raw_reference.attrib["ref-type"] in ['fig', 'table']:
                    if raw_reference.text is not None:
                        available_references.append(raw_reference)
                        paragraph_has_ref = True

        if paragraph_has_ref:
            for sentence in paragraph_sentences:
                sentence["fake_ref_candidate"] = False
        sentences = sentences + paragraph_sentences

        # loop references
        for reference in available_references:
            ref_id = '{}_{}'.format(paper_id, global_reference_id)
            global_reference_id = global_reference_id + 1
            target_id = reference.attrib["rid"]
            ref_label = reference.text

            for sentence_pid, sentence in enumerate(paragraph_sentences):
                sentence_text = sentence['text']
                if (ref_label is not None) and (ref_label in sentence_text):
                    start = sentence_text.find(ref_label)
                    end = start + len(ref_label)
                    reference_out = {
                        "id": ref_id,
                        "sentence": sentence["id"],
                        "start": start,
                        "end": end,
                        "label": ref_label,
                        "target": target_id,
                    }
                    references.append(reference_out)

                    # # mask saved reference to avoid repeat
                    sentence_text = sentence_text[:start] + '#'*len(ref_label) + sentence_text[end:]
                    paragraph_sentences[sentence_pid]['text'] = sentence_text
                    break

            # referenced items
            if target_id in target_ids:
                for item in referenced_items:
                    if target_id == item["id"]:
                        item["referencing_source"].append(ref_id)
            else:
                target_ids.append(target_id)
                referenced_item = {
                    "id": target_id,
                    "URL": "",
                    "label": ref_label,
                    "type": reference.attrib["ref-type"],
                    "referencing_source": [ref_id],
                    "caption": ""
                }
                referenced_items.append(referenced_item)

    for sentence in sentences:  # Remove temp var
        del sentence['text']

    # add fake refs
    if with_fake_refs:
        random.seed(42)

        num_fake_queries = round(fake_refs_ratio / (1 - fake_refs_ratio) * len(references))
        valid_sentences = [sentence for sentence in sentences if sentence['fake_ref_candidate']]
        selected_sentences = random.sample(valid_sentences, min(num_fake_queries, len(valid_sentences)))

        for sentence in selected_sentences:
            ref_id = '{}_{}'.format(paper_id, global_reference_id)
            global_reference_id = global_reference_id + 1

            fake_ref = {
                "id": ref_id,
                "sentence": sentence["id"],
                "start": 0,
                "end": 0,
                "label": '',
                "target": 'None',
            }
            references.append(fake_ref)

    return paragraphs, sentences, references, referenced_items


def parse_pubmed_caption2(path):
    """
    My version based on parse_pubmed_caption
    """
    tree = read_xml(path)

    figs = tree.findall(".//fig")
    dict_captions = list()
    if figs is not None:
        for fig in figs:
            fig_id = ''
            if 'id' in fig.keys():
                fig_id = fig.attrib["id"]
            if fig.find("caption") is not None:
                fig_captions = fig.find("caption").getchildren()
                caption = " ".join([stringify_children(c) for c in fig_captions])
            else:
                caption = None
            dict_caption = {
                "fig_caption": caption,
                "fig_id": fig_id,
            }
            dict_captions.append(dict_caption)
    if not dict_captions:
        dict_captions = None
    return dict_captions


def parse_pubmed_table2(path):
    tree = read_xml(path)
    dict_article_meta = parse_article_meta(tree)
    pmid = dict_article_meta["pmid"]
    pmc = dict_article_meta["pmc"]

    tables = tree.findall('.//table-wrap')
    dict_captions = list()
    if tables is not None:
        for table in tables:
            table_id = ''
            if 'id' in table.keys():
                table_id = table.attrib["id"]
            if table.find("caption") is not None:
                table_captions = table.find("caption").getchildren()
                caption = " ".join([stringify_children(c) for c in table_captions])
            else:
                caption = None
            dict_caption = {
                "pmid": pmid,
                "pmc": pmc,
                "table_caption": caption,
                "table_id": table_id,
            }
            dict_captions.append(dict_caption)
    if not dict_captions:
        dict_captions = None
    return dict_captions


def parse_pubmed_xml2(path, include_path=False, nxml=False):
    """
    Given an input XML path to PubMed XML file, extract information and metadata
    from a given XML file and return parsed XML file in dictionary format.
    You can check ``ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/`` to list of available files to download

    Parameters
    ----------
    path: str
        A path to a given PumMed XML file
    include_path: bool
        if True, include a key 'path_to_file' in an output dictionary
        default: False
    nxml: bool
        if True, this will strip a namespace of an XML after reading a file
        see https://stackoverflow.com/questions/18159221/remove-namespace-and-prefix-from-xml-in-python-using-lxml to
        default: False

    Return
    ------
    dict_out: dict
        A dictionary contains a following keys from a parsed XML path
        'full_title', 'abstract', 'journal', 'pmid', 'pmc', 'doi',
        'publisher_id', 'author_list', 'affiliation_list', 'publication_year',
        'publication_date', 'subjects'
    }
    """
    tree = read_xml(path, nxml)

    tree_title = tree.find(".//title-group/article-title")
    if tree_title is not None:
        title = [t for t in tree_title.itertext()]
        sub_title = tree.xpath(".//title-group/subtitle/text()")
        title.extend(sub_title)
        title = [t.replace("\n", " ").replace("\t", " ") for t in title]
        full_title = " ".join(title)
    else:
        full_title = ""

    try:
        abstracts = list()
        abstract_tree = tree.findall(".//abstract")
        for a in abstract_tree:
            for t in a.itertext():
                text = t.replace("\n", " ").replace("\t", " ").strip()
                abstracts.append(text)
        abstract = " ".join(abstracts)
    except BaseException:
        abstract = ""

    journal_node = tree.findall(".//journal-title")
    if journal_node is not None:
        journal = " ".join([j.text for j in journal_node])
    else:
        journal = ""

    dict_article_meta = parse_article_meta(tree)
    pub_year_node = tree.find(".//pub-date/year")
    pub_year = pub_year_node.text if pub_year_node is not None else ""
    pub_month_node = tree.find(".//pub-date/month")
    pub_month = pub_month_node.text if pub_month_node is not None else "01"
    pub_day_node = tree.find(".//pub-date/day")
    pub_day = pub_day_node.text if pub_day_node is not None else "01"

    subjects_node = tree.findall(".//article-categories//subj-group/subject")
    subjects = list()
    if subjects_node is not None:
        for s in subjects_node:
            subject = " ".join([s_.strip() for s_ in s.itertext()]).strip()
            subjects.append(subject)
        subjects = "; ".join(subjects)
    else:
        subjects = ""

    # create affiliation dictionary
    affil_id = tree.xpath(".//aff[@id]/@id")
    if len(affil_id) > 0:
        affil_id = list(map(str, affil_id))
    else:
        affil_id = [""]  # replace id with empty list

    affil_name = tree.xpath(".//aff[@id]")
    affil_name_list = list()
    for e in affil_name:
        name = stringify_affiliation_rec(e)
        name = name.strip().replace("\n", " ")
        affil_name_list.append(name)
    affiliation_list = [[idx, name] for idx, name in zip(affil_id, affil_name_list)]

    tree_author = tree.xpath('.//contrib-group/contrib[@contrib-type="author"]')
    author_list = list()
    for author in tree_author:
        author_aff = author.findall('xref[@ref-type="aff"]')
        try:
            ref_id_list = [str(a.attrib["rid"]) for a in author_aff]
        except BaseException:
            ref_id_list = ""
        try:
            author_list.append(
                [
                    author.find("name/surname").text,
                    author.find("name/given-names").text,
                    ref_id_list,
                ]
            )
        except BaseException:
            author_list.append(["", "", ref_id_list])
    author_list = flatten_zip_author(author_list)

    coi_statement = '\n'.join(parse_coi_statements(tree))

    dict_out = {
        "full_title": full_title.strip(),
        "abstract": abstract,
        "journal": journal,
        "pmid": dict_article_meta["pmid"],
        "pmc": dict_article_meta["pmc"],
        "doi": dict_article_meta["doi"],
        "publisher_id": dict_article_meta["publisher_id"],
        "author_list": author_list,
        "affiliation_list": affiliation_list,
        "publication_year": pub_year,
        "publication_date": "{}-{}-{}".format(pub_day, pub_month, pub_year),
        "subjects": subjects,
        "coi_statement": coi_statement,
    }
    if include_path:
        dict_out["path_to_file"] = path
    return dict_out
