"""
postproc_parser.py

parser for OpenFoam postProcessing .dat files
"""
from __future__ import print_function

import numpy as np
from pathlib import Path
from typing import Tuple, List


def parse_postproc_matrix(path:Path) -> Tuple[np.array, List, List]:

    def _read_headers(line:str, vector_count:int):
        _headers = line.split()
        if vector_count == 0:
            return _headers
        # if vectors, add subscripts to headers
        else:
            if vector_count != len(_headers) - 1:
                raise ValueError(f"Unexpected format in file {path}")
            headers = [_headers[0]]
            for h in _headers[1:]:
                headers.extend([
                    f"{h}_1", f"{h}_2", f"{h}_3"
                ])
            return headers

    data = []
    comments = []
    headers = None
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                comments.append(line.strip("# ")) 
            else:
                # expect the last comment line to be labels
                if not headers:
                    vector_count = line.count("(")
                    headers = _read_headers(comments.pop(-1), vector_count=vector_count)

                line = line.replace("(", " ").replace(")", " ")
                line_split = line.split()
                row = []
                for v in line_split:
                    if v == "N/A":
                        row.append(np.nan)
                    else:
                        row.append(float(v))
                data.append(row)

    data = np.array(data)
    return data, headers, comments


def parse_postproc_time_series(path:Path, filename:str):
    data = []
    comments = []
    headers = None
    path = Path(path)
    for time in path.iterdir():
        _data, _headers, _comments = parse_postproc_matrix(time / filename)
        if headers is None:
            headers = _headers
        elif headers != _headers:
            raise ValueError(f"The files in the time series have different headers.")
        data.append(_data)
        comments.append(_comments)
    data = np.concatenate(data, axis=0)
    return data, headers, comments


def parse_patch_data(path:Path):
    raise NotImplementedError