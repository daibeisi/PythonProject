# -*- coding: utf-8 -*-
import os
import random
import time
from multiprocessing import Pool


def long_time_task(name):
    print('%s任务（%s）开始运行...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('任务（%s）运行了%0.2f秒。' % (name, (end - start)))


if __name__ == '__main__':
    print('程序（%s）开始运行...' % os.getpid())
    # Only works on Unix/Linux/Mac:
    # pid = os.fork()
    # if pid == 0:
    #     print('我是子进程（%s），我的父进程是（%s）。' % (os.getpid(), os.getppid()))
    # else:
    #     print('我（%s）只创建了一个子进程（%s）。' % (os.getpid(), pid))

    pool = Pool(4)
    for i in range(5):
        pool.apply_async(long_time_task, args=(i,))
    print('等待所有子进程完成...')
    pool.close()
    pool.join()
    print('所有子进程完成。')
