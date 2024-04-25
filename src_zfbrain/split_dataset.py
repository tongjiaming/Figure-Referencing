import json
import os
import logging
import pickle
from tqdm import tqdm
from datetime import datetime
from utils.decorater import execution_time


@execution_time
def divide_data(input_path, train_path, test_path):
    log_file_name = os.path.join('log', 'split_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # with open(FILEPAHTS_PATH, "rb") as file:
    #     filepaths = pickle.load(file)

    with open(input_path, "r") as infile, open(train_path, 'a') as train_file, open(test_path, 'w') as test_file:
        for line in tqdm(infile, total=LEN_PMCOA_TEST):
            try:
                data = json.loads(line)
                year = int(data.get('paper_year', '').strip())

                if year < 2023:
                    json.dump(data, train_file)
                    train_file.write('\n')
                else:
                    json.dump(data, test_file)
                    test_file.write('\n')
                    
            except Exception as e:
                # logging.info(data)
                logging.error(e)

if __name__ == "__main__":
    input = input('Old dataset will be overided, enter y to continue:')
    assert input == 'y'
    
    LEN_PMCOA = 5736512
    LEN_PMCOA_TEST = 1495765
    INPUT_PATH = '../data/pmcoa/jsonl/pmcoa_test.jsonl'
    TRAIN_PATH = '../data/pmcoa/jsonl/pmcoa_train.jsonl'
    TEST_PATH = '../data/pmcoa/jsonl/pmcoa_test2.jsonl'
    # FILEPAHTS_PATH = "filepaths_pmc.txt"
    
    divide_data(INPUT_PATH, TRAIN_PATH, TEST_PATH)
    