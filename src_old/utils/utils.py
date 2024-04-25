import logging
import os
from datetime import datetime


def config_log(log_name):
    log_file_name = os.path.join('log', log_name + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')