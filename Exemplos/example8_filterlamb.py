#!/usr/bin/env python

nums = range(1,10)
for i in range(2,4):
    print(i)
    nums = filter(lambda x: x % i == 0, nums)
    print(list(nums))
