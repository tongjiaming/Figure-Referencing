# from utils.sbert import sbert_by_paper
# from utils.specter import specter_by_paper
# from utils.galactica import galactica_by_paper
# from utils.gpt import gpt_by_paper
# from utils.gpt2 import gpt_by_paper_2
from utils.gpt3 import gpt_by_paper_3
# from utils.gpt_emb import gpt_emb_by_paper

from utils.utils import config_log, count_json_lines, data_loader, execution_time
from torchdata.datapipes.iter import IterableWrapper
from tqdm import tqdm
from multiprocessing import Pool
from datetime import datetime
import logging
import os
import torch
import csv
import json


def wrap_func(func):
    # def wrapped_func(args):
    #     if args != None:
    #         try:
    #             return func(*args)
    #         except Exception as e:
    #             logging.error(e)

    def wrapped_func(args):
        if args != None:
            return func(*args, threshold=THRESHOLD)
            
    return wrapped_func


@execution_time
def main():
    iter_obj = data_loader(DATA_PATH, with_fake_ref=WITH_FAKE_REF)
    dp = IterableWrapper(iter_obj)
    dp_use = dp.random_split(total_length=LEN_PMCOA_TEST, weights={"use": RATIO, "not_use": 1 - RATIO}, seed=0, target='use')

    total_acc = 0
    recall_1_acc = 0
    recall_5_acc = 0
    recall_n_2_acc = 0 # recall @ n/2
    mrr_acc = 0
    logs = []

    wrapped_func = wrap_func(FUNC)

    with open(RESULT_LOG_PATH, 'w', newline='') as file:
        for res in tqdm(map(wrapped_func, dp_use), total=round(RATIO * LEN_PMCOA_TEST)):
            if res != None:
                total, recall_1, recall_5, recall_n_2, mrr, logs = res
                total_acc += total
                recall_1_acc += recall_1
                recall_5_acc += recall_5
                recall_n_2_acc += recall_n_2
                mrr_acc += mrr
                for log in logs:
                    # print(log)
                    json_line = json.dumps(log)
                    file.write(json_line + '\n')

    print(f'total:{total_acc}')
    print(f'Average Recall@1:{round(recall_1_acc / total_acc, 4)}')
    print(f'Average Recall@5:{round(recall_5_acc / total_acc, 4)}')
    print(f'Average Recall@n/2:{round(recall_n_2_acc / total_acc, 4)}')
    print(f'Average MMR:{round(mrr_acc / total_acc, 4)}')
        

if __name__ == '__main__':
    # Global
    LEN_PMCOA_TEST = 669697
    LEN_PMCOA = 5736512
    
    # Data
    DATA_PATH = '../data/pmcoa/jsonl/pmcoa_test.jsonl'
    WITH_FAKE_REF = False
    RATIO = 0.0002 # use how much of input data [0.1, 0.0002]

    # Method
    FUNC = gpt_by_paper_3
    THRESHOLD = 0.1 * WITH_FAKE_REF

    # Log
    RESULT_LOG_PATH = 'result_log/gpt_3.jsonl'
    config_log('gpt_3')
    
    main()
