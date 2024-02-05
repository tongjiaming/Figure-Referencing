import json

DATA_PATH = '../data/S2ORC/pdf_parses_0.jsonl'
SINGLE_LINE_DATA_PATH = '../data/S2ORC/single_line.json'

with open(DATA_PATH) as file, open(SINGLE_LINE_DATA_PATH, 'w') as file2:
    for _ in range(100):
        line = file.readline()
        json_object = json.loads(line)
        file2.write(json.dumps(json_object) + '\n')
