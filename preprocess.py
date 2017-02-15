'''Dataset preprocessing.'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import concurrent.futures
import os

import numpy as np

import wavenet.utils as utils

BATCH = 10240
RATE = 8000
CHUNK = 2048
OVERLAP = 256


def split_into(data, n):
    res = []
    for i in range(n):
        res.append(data[i::n])
    return res


def process_files(files, id, output, rate, chunk_length, chunk_overlap, batch):
    data = []
    ofilename = os.path.join(output, 'vctk_{}'.format(id))
    with open(ofilename, 'wb') as ofile:
        for filename in files:
            for chunk in utils._preprocess(filename, rate, chunk_length, chunk_overlap):
                data.append(chunk)

            if len(data) >= batch:
                np.save(ofile, np.array(data))
                data.clear()
        np.save(ofile, np.array(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default=os.getcwd())
    parser.add_argument('--output', type=str, default='')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--rate', type=int, default=RATE)
    parser.add_argument('--chunk', type=int, default=CHUNK)
    parser.add_argument('--overlap', type=int, default=OVERLAP)
    parser.add_argument('--flush_every', type=int, default=BATCH)
    args = parser.parse_args()

    files = list(utils.wav_files_in(args.data))
    file_groups = split_into(files, args.workers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i in range(args.workers):
            pool.submit(process_files, file_groups[i], i, args.output, args.rate, args.chunk,
                        args.overlap, args.flush_every)


if __name__ == '__main__':
    main()
