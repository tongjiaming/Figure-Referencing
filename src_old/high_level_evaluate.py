from utils.evaluate_load_data import data_loader
from utils.bm25 import bm25_by_paper
from torchdata.datapipes.iter import IterableWrapper
from tqdm import tqdm
from multiprocessing import Pool


def bm25_by_paper_star(args):
    if args == 0:  # means illegal data sample here
        return 0, 0, 0, 0, 0
    else:
        return bm25_by_paper(*args)


def main():
    DATA_PATH = '../output/PMCOA_out.json'
    iter_obj = data_loader(DATA_PATH)
    datapipe = IterableWrapper(iter_obj)
    shuffle_dp = datapipe.shuffle()

    total_acc = 0
    tp_acc = 0

    pool = Pool(8)
    with pool:
        for res in tqdm(pool.imap_unordered(func=bm25_by_paper_star, iterable=shuffle_dp), total=1000):
            total_acc += res[0]
            tp_acc += res[1]

    print(total_acc)
    print(tp_acc)


if __name__ == '__main__':
    main()
