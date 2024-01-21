import seaborn as sns
from utils import race_report as RR
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from typing import List
from functools import reduce


def plot_frequency(df: pd.DataFrame, bo_indices: pd.Series,
                   ax: matplotlib.axes.Axes) -> None:
    """
    Plots frequency as function of distance.
    """
    df_tmp = df.copy()
    df_tmp[RR.COL_Y] = df[RR.COL_Y].rolling(window=6, step=6).mean()
    graph = sns.lineplot(data=df_tmp, y=RR.COL_Y, x="time", marker="o",
                         ax=ax)
    for idx in bo_indices[1:]:
        # Add the wall touches as vertical.
        RR.add_vertical(graph=graph, idx=df.loc[:, "time"].iloc[idx])
    RR.add_vertical(graph=graph, idx=df.loc[:, "time"].iloc[-1])
    ax.set_ylim([30, 70])
    ax.set_title("Frequency/Time")
    
    
def plot_speed(df: pd.DataFrame, ax: matplotlib.axes.Axes) -> None:
    """
    Plots speed as function of distance.
    """
    # print(f"emhacker, columns: {df.columns}")
    # display(df)
    graph = sns.lineplot(data=df, y=RR.COL_V, x=RR.COL_X, ax=ax)
    col_distance = df[RR.COL_X]
    for d in col_distance:
        RR.add_vertical(graph, d)
    ax.set_xticks(labels=[RR.format_distance(d) for d in col_distance], ticks= df[RR.COL_X])
    # TODO: should the limit be dynamic?
    ax.set_ylim([1.0, 3.0])
    ax.set_title("Speed/Distance")
    
    
def plot_dps(df: pd.DataFrame, ax: matplotlib.axes.Axes) -> None:
    """
    Plots #of cycle for each lap.
    """
    num_cycles = []
    for m in df[RR.COL_MES]:
        if m == RR.VAL_BO:
            num_cycles.append(1)
        else:
            if not num_cycles:
                num_cycles.append(1)
            num_cycles[-1] += 1
    df_stroke_count = pd.DataFrame({"Lap": range(1, len(num_cycles)+1), "#Cycles": num_cycles})
    sns.barplot(data=df_stroke_count, y="#Cycles", x="Lap", alpha=0.3, ax=ax)
    ax.bar_label(ax.containers[0], label="#strokes")
    ax.set_title("#Cycles/Lap")