import os
from dataclasses import dataclass
from typing import Dict

import numpy as np
import numpy.typing as npt
import pandas as pd


@dataclass
class Config:
    times: Dict[str, npt.NDArray]
    strokes: Dict[str, npt.NDArray]
    line_diff: float


def init(input_dir: str, line_diff=1.0) -> Config:
    input_files = [in_file for in_file in os.listdir(input_dir)
                   if in_file.endswith(".csv")]
    names = ['.'.join(os.path.basename(infile).split(".")[:-1])
             for infile
             in input_files]
    times = {}
    for (name, infile) in list(zip(names, input_files)):
        if not infile.startswith("times"):
            continue
        arr = np.genfromtxt(os.path.join(input_dir, infile), delimiter=",")
        times[name] = np.array([x for x in zip(*arr)])
    strokes = {}
    for (name, infile) in list(zip(names, input_files)):
        if not infile.startswith("strokes"):
            continue
        strokes[name] = np.genfromtxt(os.path.join(input_dir, infile),
                                      delimiter=",")
    return Config(times=times, strokes=strokes, line_diff=line_diff)


def distances(config: Config) -> Dict[str, np.array]:
    ret = {}
    for name, arr in config.times.items():
        print(name)
        assert len(arr) == 2, "Expected format is: [lines_arr, times_arr]"
        x = arr[0]
        d_l = (x - np.roll(x, 1))[1:]
        ret[name] = d_l * config.line_diff
    return ret


def speeds(config: Config) -> Dict[str, np.array]:
    ret = {}
    for name, arr in config.times.items():
        assert len(arr) == 2, "Expected format is: [lines_arr, times_arr]"
        (d_l, d_times) = ((x - np.roll(x, 1))[1:] for x in arr)
        ret[name] = ((d_l * config.line_diff) / d_times).round(2)
    return ret


def frequency(config: Config) -> Dict[str, np.array]:
    ret = {}
    for name, s_array in config.strokes.items():
        s_diff = (s_array - np.roll(s_array, 1))[1:]
        ret[name] = (60 / s_diff).round(2)
    return ret


def dps(config: Config) -> Dict[str, np.array]:
    times = config.times
    strokes = config.strokes
    tkeys = [x.replace("times", "") for x in times.keys()]
    skeys = [x.replace("strokes", "") for x in strokes.keys()]
    joint_keys = [k for k in tkeys if k in skeys]
    # Convert the strokes pointers from time to distance.

    stroke_distances = {}
    for joint_key in joint_keys:
        tarray = times[f"times{joint_key}"]
        (distances_arr, times_arr) = tarray
        sarray = strokes[f"strokes{joint_key}"]

        stroke_distance_markers = []
        for stroke_time in sarray:
            insertion_idx = np.searchsorted(times_arr, stroke_time)
            if insertion_idx == 0 or insertion_idx >= len(distances_arr):
                continue
            # Linear interpulation.
            (ld, rd) = (distances_arr[insertion_idx-1],
                        distances_arr[insertion_idx])
            (lt, rt) = (times_arr[insertion_idx-1], times_arr[insertion_idx])
            stroke_time_offset = stroke_time - lt
            time_interval = rt - lt
            ratio = stroke_time_offset / time_interval
            distance_interval = rd - ld
            stroke_distance_markers.append(ld + distance_interval * ratio)

        # Calculate diff.
        dps = (np.array(stroke_distance_markers) -
               np.roll(stroke_distance_markers, 1))[1:]
        stroke_distances[joint_key] = np.array(dps * config.line_diff)

    return stroke_distances


def to_df(data: Dict[str, np.array]) -> pd.DataFrame:
    L = max([len(data[k]) for k in data.keys()])
    for k in data.keys():
        arr = data[k]
        data[k] = np.pad(arr, pad_width=(0, L-len(arr)), mode="constant",
                         constant_values=np.nan)
    return pd.DataFrame(data).round(2)
