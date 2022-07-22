import ztk_update
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')
    ztk_update.truetime(2)
    ztk_update.truetime(1)
