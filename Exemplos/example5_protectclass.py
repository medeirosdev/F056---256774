#!/usr/bin/env python

class JustCounter:
    def __init__(self):
        self.__secretCount = 0
    def count(self):
        self.__secretCount += 1
        print(self.__secretCount)

counter = JustCounter()
counter.count()
counter.count()

print(counter.__secretCount)
#print(counter._JustCounter__secretCount)
