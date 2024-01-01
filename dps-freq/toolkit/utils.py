import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import seaborn as sns
from scipy.stats import linregress
from typing import Tuple


def read_data(path: str, swimmer_name: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[df["Swimmer Name"] == swimmer_name]


def read_data_new(path: str, swimmer_name: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    return df[df["Swimmer Name"] == swimmer_name]


def __plot3d(df: pd.DataFrame) -> None:
    (X, Y, Z) = (df[col] for col in ["Frequency", "Num strokes", "Speed"])
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
    ax.set_ylabel("# Strokes")
    ax.set_zlabel("Speed")
    plt.title("Frequency, DPS, time hyperplane")
    plt.show()

    display(df[["Frequency", "Num strokes"]].corr())
    display(df[["Num strokes", "Time"]].corr())


def __dervatives(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(ncols=2)
    sns.regplot(data=df, x="Frequency", y="Num strokes", ax=ax[0])
    sns.regplot(data=df, x="Frequency", y="Speed", ax=ax[1])
    fig.subplots_adjust(wspace=0.5)
    plt.show()


def prepare_dps_freq(df: pd.DataFrame) -> pd.DataFrame:
    colnames = {
        "measurement": "measurement",
        "time": "interval-time",
        "speed": "Speed",
        }
    df_cycles = df.loc[df[colnames["measurement"]] == "cycle"]
    # Frequency.
    df_freq = 60 / df_cycles.groupby("id", as_index=False).mean(colnames["time"])

    # Num Strokes.
    df_strokes = df_cycles.groupby("id", as_index=False).count()

    # Distance.
    df_distance = df.loc[~np.isnan(df["distance"])].reset_index()[["distance"]]
    df_distance["distance"] = 25 - df_distance["distance"]
    
    # Speed.
    df_time = df_cycles.groupby("id", as_index=False).sum([colnames["time"]])[[colnames["time"]]]
    df_speed = pd.merge(df_time, df_distance, left_index=True, right_index=True)
    df_speed[colnames["speed"]] = df_speed["distance"] / df_speed[colnames["time"]]
    
    df_ret = pd \
        .merge(df_freq, df_strokes, how="inner", left_index=True, right_index=True) \
        .rename(columns={f"{colnames['time']}_x": "Frequency",
                         f"{colnames['time']}_y": "Num strokes"})[["Frequency", "Num strokes"]] \
        .merge(df_speed[[colnames["speed"], colnames["time"]]], left_index=True, right_index=True)
    return df_ret.rename(columns={colnames["time"]: "Time"})


def display_analysis(df: pd.DataFrame) -> None:
    display(df.sort_values(["Speed"], ascending=[False]))
    __plot3d(df)
    __dervatives(df)
    

def derive_dvdf(df: pd.DataFrame) -> Tuple[float, float]:
    """
    Returns a tuple; in which the first number is the slope of the derivative of dV/Df, assuming it is linear.
    The second number is the Pvalue, whereas the NULL-hypo is that the slope is 0.
    """
    result = linregress(df["Frequency"], y=df["Speed"], alternative='two-sided')
    return (round(f, 2) for f in [result.slope, result.pvalue])
