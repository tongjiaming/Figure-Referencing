# Figure Referencing
This repo is for the master thesis of figure referencing.

# How to Use
Replace `.venv\Lib\site-packages\pubmed_parser\__init__.py` with `src/load_data/pubmed__init__.py` before using.

After replacing, change filename of pubmed__init__.py to `__init__.py`

# Json Schema
The `start` and `end` in `references` indicate the index of the sentence.

The `start` and `end` in `sentences` indicate the index of the paragraph.

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "None",
    "title": "Figure Referencing Data",
    "description": "A data sample for figure referencing task.",
    "type": "object",
    "properties":{
        "paper_id": {
            "description": "The unique ID for this paper.",
            "type": "integer"
        },
        "paper_URL": {
            "description": "(optional) The URL for the paper from which this sample is derived.",
            "type": "string"
        },
        "paper_PMCID": {
            "description": "(optional) The PMCID of the paper.",
            "type": "string"
        },
        "paper_title": {
            "description": "The title of the paper.",
            "type": "string"
        },
        "paper_abstract": {
            "description": "(optional) The abstract of the paper.",
            "type": "string"
        },
        "query_placeholders": {
            "description": "The query placeholder set.",
            "type": "array",
            "items": {
                "description": "The placeholder that references a figure or table.",
                "type": "object",
                "properties": {
                    "placeholder_id": {
                        "description": "The unique ID of the referencing placeholder in the paper.",
                        "type": "integer"
                    },
                    "placeholder_label": {
                        "description": "The label text of the referencing.",
                        "type": "string"
                    },
                    "target_id": {
                        "description": "The referenced figure or table's unique id",
                        "type": "string"
                    },
                    "context_sentence": {
                        "description": "The referencing sentence that the placeholder belongs to.",
                        "type": "string"
                    },
                    "context_paragraph": {
                        "description": "The paragraph that the placeholder belongs to.",
                        "type": "string"
                    },
                    "section": {
                        "description": "Indicating which section the placeholder belongs to.",
                        "type": "string"
                    },
                    "position": {
                        "description": "In case some referencing sentence has more than one reference, this indicates which position the placeholder is in.",
                        "type": "integer"
                    },
                    "target_type": {
                        "description": "The type of the referenced target, one of the following values: table or figure.",
                        "type": "string"
                    }
                },
                "required": ["placeholder_id", "placeholder_label", "target_id", "context_sentence", "context_paragraphs", "section", "position"]
            }
        },
        "referenced_items": {
            "description": "The referenced table/figure set.",
            "type": "array",
            "items": {
                "description": "The item that is referenced by some referencing placeholder.",
                "type": "object",
                "properties": {
                    "item_id": {
                        "description": "The unique ID for the referenced item.",
                        "type": "string"
                    },
                    "item_URL": {
                        "description": "The URL of the item.",
                        "type": "string"
                    },
                    "item_label": {
                        "description": "The label of the referenced item.",
                        "type": "string"
                    },
                    "item_type": {
                        "description": "One of the following values: table or figure.",
                        "type": "string"
                    },
                    "referencing_source": {
                        "description": "The ID of the referencing placeholder that referenced this item.",
                        "type": "integer"
                    },
                    "caption": {
                        "description": "The caption of the item.",
                        "type": "string"
                    }
                },
                "required": ["item_id", "item_URL", "item_type", "referencing_source", "caption"]
            }
        }
    },
   "required": ["sample_id", "paper_title", "paragraphs", "referencing_sentences", "query_placeholders", "referenced_items"]
}
```

# 12, Feb, 2024
5.index optimization

4.NDCG for caption -> sentence

1.The entire dataset

2.split into train validate test
threshold score rather than top match
find out the best threshold value

3.sentence-bert embedding cosine-sim (done)
