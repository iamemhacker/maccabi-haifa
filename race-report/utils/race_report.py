from typing import Tuple, NamedTuple, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


[COL_MES, COL_TIME, COL_Y, COL_X, COL_V, VAL_CYCLE, VAL_BO] = [
    "measurement",
    "interval-time",
    "frequency",
    "distance",
    "speed",
    "cycle",
    "breakout"]


class Stats(NamedTuple):
    std: float
    mean: float


def calc_frequency(df: pd.DataFrame) -> Tuple[Stats, pd.DataFrame]:
    """
    Adds the frequency column to the given dataframe, and
    calculates distribution statistics.
    """
    df_tmp = df.copy()
    frequencies = df_tmp[COL_Y]
    mean, std = np.mean(frequencies), np.std(frequencies)
    lower, upper = mean-std, mean+std
    df_tmp[COL_Y] = df_tmp[COL_Y].clip(lower=lower, upper=upper).round(2)
    df_tmp[COL_X] = df_tmp.index
    return (Stats(std=std, mean=mean), df_tmp)


def calc_speed(df: pd.DataFrame, index: List[int]) -> pd.DataFrame:
    """
    Calculates the speed per distance checkpoint (descrete speed as a function of distance).
    """
    def __calc_diff(row: pd.Series) -> float:
        return row.iloc[1] - row.iloc[0] if len(row) > 1 else row.iloc[0]

    (col_d_split, col_t_split) = ("split-distance", "split-time")
    df_tmp = df.copy()
    (rel_col_d, rel_col_t) = (
        df_tmp[col_d_split] \
            .rolling(window=2, min_periods=1) \
            .apply(__calc_diff),
        df_tmp[col_t_split] \
        .rolling(window=2, min_periods=1) \
        .apply(__calc_diff))
    df_tmp[COL_V] = rel_col_d / rel_col_t
    return  df_tmp[~np.isnan(df_tmp[col_d_split])].rename(columns={col_d_split: COL_X})


def add_vertical(graph:plt.figure, idx: int) -> None:
    graph.axvline(idx, linestyle=":", color="green")

    
def get_bo_indices(df: pd.DataFrame) -> List[int]:
    ret = [idx for idx in df[df[COL_MES] == VAL_BO].index[1:]]
    ret.append(df.index[-1])
    return ret


def format_distance(d: float) -> str:
    """
    Formats a human readable label for the given distance.
    """
    return f"{int(d)}m"