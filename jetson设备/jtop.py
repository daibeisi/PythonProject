# coding=utf-8
import time
from jtop import jtop


def get_gpu_info():
    with jtop() as jetson:
        while jetson.ok():
            return "gpu,host=1 gpu={0},temp={1} {2}".format(
                jetson.stats['GPU'],
                jetson.stats['GPU Temp'],
                time.time() * 1000000000
            )


if __name__ == "__main__":
    print(get_gpu_info())
