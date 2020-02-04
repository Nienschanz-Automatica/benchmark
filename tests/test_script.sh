#!/bin/bash

COUNTER=0
line="this is a sample input line this is a sample input line this is a sample input line"

for word in $line; do
    echo "This i a word number $COUNTER: $word"
    sleep 0.1
    COUNTER=$((COUNTER+1))
done