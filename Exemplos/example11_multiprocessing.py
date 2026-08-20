#!/usr/bin/env python

from multiprocessing import Process

import os

def hello(name):
    print('Hello world',name)
    print('pid        ',os.getpid())
    print('parent pid ',os.getppid())
    print

for i in range(5):
    p = Process(target=hello, args={"testi%s"%i,})
    p.start()
