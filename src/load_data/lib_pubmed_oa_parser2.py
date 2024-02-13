from pubmed_parser import read_xml, stringify_children, parse_article_meta
from sentence_splitter import split_text_into_sentences


def parse_pubmed_paragraph2(path, paper_id):
    """
    return referencing placeholders and their information
    Also find reference placeholders and referencing sentences
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

    if len(raw_paragraphs) > 1000:
        raise NotImplementedError('More than 1000 paragraphs not supported!')
    else:
        for idx, raw_paragraph in enumerate(raw_paragraphs):
            paragraph_id = 'P' + str(paper_id * 1000 + idx).zfill(12)
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
            if len(raw_sentences) > 10000:
                raise NotImplementedError('More than 10000 sentences not supported!')
            else:
                for raw_sentence in raw_sentences:
                    sentence_id = 'S' + str(paper_id * 10000 + global_sentence_id).zfill(12)
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

            if len(available_references) > 1000:
                raise NotImplementedError('More than 1000 references not supported!')
            else:
                for reference in available_references:
                    ref_id = 'R' + str(paper_id * 1000 + global_reference_id).zfill(12)
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


def parse_pubmed_paragraph3(path, paper_id):
    """
    return referencing placeholders and their information
    Also find reference placeholders and referencing sentences
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

    if len(raw_paragraphs) > 1000:
        raise NotImplementedError('More than 1000 paragraphs not supported!')
    else:
        for paragraph_id, raw_paragraph in enumerate(raw_paragraphs):
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
            if len(raw_sentences) > 10000:
                raise NotImplementedError('More than 10000 sentences not supported!')
            else:
                for raw_sentence in raw_sentences:
                    start = paragraph_text.find(raw_sentence)
                    end = start + len(raw_sentence)
                    sentence = {
                        "id": global_sentence_id,
                        "paragraph": paragraph_id,
                        "start": start,
                        "end": end,
                        "text": raw_sentence  # Temp var for reference find
                    }
                    paragraph_sentences.append(sentence)
                    global_sentence_id = global_sentence_id + 1
            sentences = sentences + paragraph_sentences

            available_references = []
            for raw_reference in raw_paragraph.getchildren():
                if "ref-type" in raw_reference.attrib.keys():
                    if raw_reference.attrib["ref-type"] in ['fig', 'table']:
                        if raw_reference.text is not None:
                            available_references.append(raw_reference)

            if len(available_references) > 1000:
                raise NotImplementedError('More than 1000 references not supported!')
            else:
                for reference in available_references:
                    ref_id = 'R' + str(paper_id * 1000 + global_reference_id).zfill(12)
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


def parse_pubmed_caption2(path):
    """
    My version based on parse_pubmed_caption
    """
    tree = read_xml(path)

    figs = tree.findall(".//fig")
    dict_captions = list()
    if figs is not None:
        for fig in figs:
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
