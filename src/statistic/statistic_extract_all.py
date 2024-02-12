from statistic_paper_info import extract_paper_info
import os
import json

DATA_PATH = '../../data/pmc/'
OUTPUT_PATH = '../../output/PMCOA_out.json'

with open(OUTPUT_PATH, 'w') as file:  # clear old content
    file.write('')

for foldername, subfolders, filenames in os.walk(DATA_PATH):
    foldername = foldername.replace('\\', '/')
    print(foldername)
    for filename in filenames:
        file_path = foldername + filename
        print('Extracting from ' + file_path)
        paper_info = extract_paper_info(file_path)
        if paper_info['num_table+figure'] > 0:
            with open(OUTPUT_PATH, 'a') as file:
                json.dump(paper_info, file)
                file.write('\n')
