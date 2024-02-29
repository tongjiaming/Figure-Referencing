# Figure Referencing
This repo is for the master thesis of figure referencing.

# How to Use
## Make sure the pubmed_parser works
Replace `.venv/Lib/site-packages/pubmed_parser/__init__.py` with `src/utils/pubmed__init__.py` before using.

After replacing, change filename of `pubmed__init__.py` to `__init__.py` and uncomment the content.

## Prepare Data
Run the `load_data/extract_pmc_to_json.py` after putting raw data at the right place.

When loading data, you can set `fake_ref_ratio` to control the number of fake refs.

Fake refs are refs that are targeting nothing.

## Evaluate
Run script in `src/evaluate/` such as `evaluate_rouge.py`

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
        "paper_s2orc_id": {
            "description": "(optional) The s2orc_ID of the paper.",
            "type": "string"
        },
        "paper_year": {
            "description": "(optional) The publication year of the paper.",
            "type": "integer"
        },
        "paper_month": {
            "description": "(optional) The publication month of the paper.",
            "type": "integer"
        },
        "paper_day": {
            "description": "(optional) The publication day of the paper.",
            "type": "integer"
        },
        "paper_title": {
            "description": "The title of the paper.",
            "type": "string"
        },
        "paper_abstract": {
            "description": "(optional) The abstract of the paper.",
            "type": "string"
        },
        "paragraphs": {
            "description": "The paragraph list.",
            "type": "array",
            "items": {
                "description": "The paragraph object.",
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "text": {
                        "type": "string"
                    },
                    "section": {
                        "type": "string"
                    }
                }
            }
        },
        "sentences": {
            "description": "The sentence list.",
            "type": "array",
            "items": {
                "description": "The sentence object.",
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "paragraph": {
                        "description": "The ID of the paragraph which the sentence belongs to",
                        "type": "integer"
                    },
                    "start": {
                        "description": "Starting position of the sentence in the paragraph.",
                        "type": "integer"
                    },
                    "end": {
                        "description": "End position of the sentence in the paragraph.",
                        "type": "integer"
                    },
                    "text": {
                        "type": "string"
                    },
                    "has_ref": {
                        "description": "If the sentence is referencing something.",
                        "type": "bool"
                    }
                }
            }
        },
        "references": {
            "description": "The reference list.",
            "type": "array",
            "items": {
                "description": "The reference object.",
                "type": "object",
                "properties": {
                    "id": {
                        "description": "The unique id for all data samples, different from the IDs of paragraphs or sentences which are paper-unique only.",
                        "type": "string"
                    },
                    "sentence": {
                        "description": "The ID of the sentence which the reference belongs to",
                        "type": "integer"
                    },
                    "start": {
                        "description": "Starting position of the reference in the sentence.",
                        "type": "integer"
                    },
                    "end": {
                        "description": "End position of the reference in the sentence.",
                        "type": "integer"
                    },
                    "label": {
                        "type": "string"
                    },
                    "target": {
                        "description": "The ID of the referenced target.",
                        "type": "string"
                    }
                }
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
   "required": ["sample_id", "paper_title", "paragraphs", "sentences", "references", "referenced_items"]
}
```

# 12, Feb, 2024
- [x] index optimization
- [x] fake referencing sentences
- [x] NDCG for caption -> sentence
- [x] sentence-bert embedding cosine-sim
- [x] split into train validate test (manually)
- [x] threshold score rather than top match
find out the best threshold value
- [ ] The entire dataset
- [ ] play with GPT

# Results
## Baseline: sentence -> caption
| Approach  | Num of Samples |      Precision      |
|:---------:|:--------------:|:-------------------:|
|  rouge1   |     13023      | 0.35844275512554713 |
|  rouge2   |     13023      | 0.3798663902326653  |
|  rougeL   |     13023      | 0.33517622667588115 |
| rougeLsum |     13023      |  0.336097673347155  |
|  TF-IDF   |     13023      |  0.336097673347155  |


## Baseline: caption -> sentence
| Approach  | Num of Samples |      Precision      |        NDCG        |
|:---------:|:--------------:|:-------------------:|:------------------:|
|  rouge1   |      4364      | 0.41796516956920254 | 0.6431754482431424 |
|  rouge2   |      4364      | 0.42231897341888175 | 0.6435906255214052 |
|  rougeL   |      4364      | 0.4129239230064161  | 0.6413681886087096 |
| rougeLsum |      4364      | 0.4129239230064161  | 0.6414643042504324 |
|  TF-IDF   |      4364      | 0.4711274060494959  | 0.6637401154137255 |
|   BM25    |      4364      | 0.40765352887259393 | 0.6343334546427268 |


## With Fake Refs of ratio 0.5, threshold = 0
| Approach  | Num of Samples |      Precision      | Recall |
|:---------:|:--------------:|:-------------------:|:------:|
|  rouge1   |     26046      | 0.17664900560546726 |  1.0   |
|  rouge2   |     26046      | 0.20590493741841356 |  1.0   |
|  rougeL   |     26046      | 0.16524610304845275 |  1.0   |
| rougeLsum |     26046      | 0.16593718805190816 |  1.0   |
|  TF-IDF   |     26046      |  0.255087153497658  |  1.0   |
|   BM25    |     26046      | 0.20763264992705213 |  1.0   |


# 22, Feb, 2024
- [x] when finding fake refs, only take refs from sections have no ref.
show some examples of the results
- [x] Bm25 as new baseline (some negative scores)
- [x] S2ORC
- [ ] Precision and Recall (MultiClass)
- [ ] galactica model
- [ ] arxiv
- [x] play with GPT
- [x] publication year for the extracted data


# 29, Feb, 2024
- [x] Explore Arxiv, script for downloading 'tex.tar's of arxiv papers done.
  - 21 of 100 S2ORC papers can be found in arxiv
  - Can use freely, not sure for a huge data
  - https://aws.amazon.com/cn/s3/pricing/ 0.02695 USD / GB
- [x] Explore the threshold thing
  - Experiments on bm25, rouge and tf-idf
  - Line charts and results uploaded to google drive
- [x] Code refactored, data_loader bug fixing, better normalized method for bm25 and etc
  - Dataloader, wrong position of ':' causing the referencing sentence is not complete but the results change slightly
  - The old normalize method for bm25 is not good, used a different method for that
- [x] Explore on GPT
  - ChatGPT and GPT api should be different
  - My credit card is refused
- [x] Explore Galactica
  - Basic codes are done
  - Training papers are up to July 2022 (But training dataset not only papers)
  - Interesting special tokens used
  - https://huggingface.co/facebook/galactica-6.7b/raw/main/tokenizer.json
- [x] Month information ()
- [ ] Entire dataset
