#!/bin/bash

for i in $(seq 1 10); do
    ./hello "$i" > "output_${i}.txt" &
done

wait
