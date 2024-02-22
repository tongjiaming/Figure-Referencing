import json


DATA_PATH = '../../data/S2ORC/pdf_parses_0.jsonl'
SAMPLE_DATA_PATH = '../../data/S2ORC/sample_s2orc.json'


with open(DATA_PATH) as file, open(SAMPLE_DATA_PATH, 'w') as file2:
    for paper_id in range(1000):
        line = file.readline()
        json_object = json.loads(line)
        file2.write(json.dumps(json_object) + '\n')