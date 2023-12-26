import seaborn as sns
from utils import race_report as RR
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from typing import List


def plot_frequency(df: pd.DataFrame, ax: matplotlib.axes.Axes
                   , lap_indices: List[int]
                   , distances: List[str]) -> None:
    """
    Plots frequency as function of distance.
    """
    graph = sns.lineplot(data=df, y=RR.COL_Y, x=RR.COL_X, ax=ax)
    for lap_idx in lap_indices:
        RR.add_vertical(graph, lap_idx)
    ax.set_xticks(labels=distances, ticks=lap_indices)
    # TODO: should the limit be dynamic?
    ax.set_ylim([30, 70])
    ax.set_title("Frequency/Distance")
    
    
def plot_speed(df: pd.DataFrame, ax: matplotlib.axes.Axes) -> None:
    """
    Plots speed as function of distance.
    """
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
            num_cycles.append(0)
        else:
            if not num_cycles:
                num_cycles.append(0)
            num_cycles[-1] += 1
    df_stroke_count = pd.DataFrame({"Lap": range(1, len(num_cycles)+1), "#Cycles": num_cycles})
    sns.barplot(data=df_stroke_count, y="#Cycles", x="Lap", alpha=0.3, ax=ax)
    ax.set_title("#Cycles/Lap")