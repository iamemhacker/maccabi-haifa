import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import seaborn as sns
from scipy.stats import linregress
from typing import Tuple
from functools import partial


SPEED_COL = "Speed"
POOL_LEN = 50

def read_data(path: str, swimmer_name: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[df["Swimmer Name"] == swimmer_name]


def read_data_new(path: str, swimmer_name: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    return df[df["Swimmer Name"] == swimmer_name]


def __plot3d(df: pd.DataFrame) -> None:
    (X, Y, Z) = (df[col] for col in ["Frequency", "DPS", SPEED_COL])
    fig = plt.figure()
    # fig.set_size_inches(8, 4)
    sns.set(rc={'figure.figsize':(10,7)})
    ax = fig.add_subplot(projection='3d')
    
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    surf = ax.plot_trisurf(X, Y, Z,
                           cmap="summer",
                           linewidth=0,
                           antialiased=False)
    ax.set_xlabel("stroke/minute")
    ax.set_ylabel("DPS")
    ax.set_zlabel("Speed")
    plt.title("Frequency, DPS, time hyperplane")
    plt.show()

    display(df[["Frequency", "DPS"]].corr())
    display(df[["DPS", "Time"]].corr())


def __dervatives(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(ncols=2)
    sns.regplot(data=df, x="Frequency", y="DPS", ax=ax[0])
    sns.regplot(data=df, x="Frequency", y="Time", ax=ax[1])
    fig.subplots_adjust(wspace=0.5)
    plt.show()


def __assert_schema(df: pd.DataFrame) -> None:
    columns = df.columns
    schema_columns = [
        "measurement",
        "interval-time",
        "id",
        "distance"
    ]
    for col in schema_columns:
        assert col in columns, f"Column '{col}' is missing from data file"
    # ids = df["id"].unique()
    # bo_distances = df.loc[~np.isnan(df["distance"])]["distance"]
    # assert len(ids) == len(bo_distances), \
    #     f"# of ids ({len(ids)} != $of bo-distances ({len(bo_distances)}))"


def prepare_dps_freq(df: pd.DataFrame) -> pd.DataFrame:
    __assert_schema(df)
    colnames = {
        "measurement": "measurement",
        "time": "interval-time",
        "speed": SPEED_COL,
        }
    df_cycles = df.loc[df[colnames["measurement"]] == "cycle"]
    
    # Frequency.
    df_cycles["freq"] = 60 / df[colnames["time"]]
    freq = df_cycles.groupby("id", as_index=False)
    freq = freq.mean("freq")[["id", "freq"]] \
        .round(decimals=2)["freq"]
    # display(freq)
    
    # DPS.
    df_distance = df.loc[~np.isnan(df["distance"])] \
        .reset_index()[["distance"]]
    df_distance = pd.Series(POOL_LEN - df_distance["distance"])
    
    # print(df_distance)
    stroke_counts = df_cycles[["id", "interval-time"]] \
        .groupby("id", as_index=False) \
        .count()["interval-time"]
    # print(stroke_counts)
    dps = (df_distance / stroke_counts).round(decimals=2)
    
    # Overall times.
    time = df.groupby("id", as_index=False) \
        .sum("interval-time")["interval-time"] \
        .round(decimals=2)
    
    speed = (POOL_LEN / time).round(decimals=2)
    return pd.DataFrame({"Frequency": freq, "DPS": dps, "Time": time, "Speed": speed})


def display_analysis(df: pd.DataFrame) -> None:
    # display(df.sort_values(["Speed"], ascending=[False]))
    __plot3d(df)
    __dervatives(df)
    

def derive_dvdf(df: pd.DataFrame) -> Tuple[float, float]:
    """
    Returns a tuple; in which the first number is the slope of the derivative of dV/Df, assuming it is linear.
    The second number is the Pvalue, whereas the NULL-hypo is that the slope is 0.
    """
    result = linregress(df["Frequency"], y=df["Time"], alternative='two-sided')
    return (round(f, 2) for f in [result.slope, result.pvalue])

def __group_agg(df: pd.DataFrame, num_cycles: int) -> pd.DataFrame:
    __assert_schema(df)
    # print(f'M {df["interval-time"].max()}')
    # print(f'm {df["interval-time"].min()}')
    time = df["interval-time"].max() - df["interval-time"].min()
    cycles = df[df["measurement"] == "cycle"]["interval-time"]
    frequency = np.round(np.average((60 / (cycles - np.roll(cycles, 1)))[1:]), 0)
    distance = df["distance"].max() - df["distance"].min()
    dps = np.round(distance / num_cycles, 2)
    return pd.DataFrame({"Frequency": [frequency],
                         "DPS": [dps],
                         "Time": [time],
                         "Speed": [distance/time]})


def fixed_stroke_experiment(df: pd.DataFrame) -> pd.DataFrame:
    func = partial(__group_agg, num_cycles=13)
    return df.groupby("id").apply(func)