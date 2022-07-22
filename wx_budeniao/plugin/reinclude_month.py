import ztk_update
import logging
import time

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')
    for i in range(29, 1, -1):
        todaytext = time.strftime("%Y-%m-%d", time.localtime(time.time() - (86400 * i)))
        # print(todaytext)
        ztk_update.updateTodayOrders(todaytext)
