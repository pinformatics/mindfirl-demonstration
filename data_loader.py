#! /usr/bin/python
# encoding=utf-8

import json

def save_data_to_json(filename, data):
    fileout = open(filename, 'w+')
    fileout.write(data)
    fileout.close()


def get_pair(filename, pair_num):
    filein = open(filename, 'r')
    ret = list()
    for line in filein:
        record = line.split(',')
        if record[0] == pair_num:
            ret.append(record)
            if len(ret) == 2:
                break
    return ret

