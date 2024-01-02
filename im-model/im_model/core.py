from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

import os
import json

import scipy.optimize as OPT
import numpy as np


@dataclass
class Limits:
    lower: float
    upper: float


@dataclass
class ModelConfig:
    fly: Limits
    bk: Limits
    bs: Limits
    free: Limits
    total_energy: float
    efficiency_factors: List[float]
    fatigue_factors: List[float]


@dataclass
class TimeCalcConfig:
    dps: List[float]
    uw_fly: Tuple[float, float]
    uw_bk: Tuple[float, float]
    uw_bs: Tuple[float, float]
    uw_fr: Tuple[float, float]


def __parse_config(d: Dict[str, Any]) -> ModelConfig:
    """
    Converts the raw JSON data into a typed model configuration object.
    """
    def __to_lim(lim: List[float]) -> Limits:
        [lower, upper] = lim
        return Limits(lower=lower, upper=upper)

    limits = d["frequency_limits"]
    [fly_lim, bk_lim, bs_lim, fr_lim] = [__to_lim(limits[k]) for k
                                         in ["fly", "bk", "bs", "fr"]]
    return ModelConfig(fly=fly_lim,
                       bk=bk_lim,
                       bs=bs_lim,
                       free=fr_lim,
                       total_energy=d["total_energy"],
                       efficiency_factors=d["efficiency_factors"],
                       fatigue_factors=d["fatigue_factors"])


def __parse_time_data(d: Dict[str, Any]) -> TimeCalcConfig:
    dps = d["dps"]
    [uw_fly, uw_bk, uw_bs, uw_fr] = [d["uw_td"][k] for k in ["fly", "bk", "bs", "fr"]]
    return TimeCalcConfig(dps=dps,
                          uw_fly=uw_fly,
                          uw_bk=uw_bk,
                          uw_bs=uw_bs,
                          uw_fr=uw_fr)


def __stroke_frequency_limits(config: ModelConfig) \
  -> List[Tuple[float, float]]:
    """
    Returns lower and upper bounds for each stroke frequency.
    """
    return [(l.lower, l.upper) for l
            in [config.fly, config.bk, config.bs, config.free]]


def optimize_400im(input_dir: str) -> List[str]:
    with open(os.path.join(input_dir, "model_configuration.json")) as \
            f_constraints:
        content = f_constraints.read()
        config = __parse_config(json.loads(content))

    # Bounds for the frequency of each stroke.
    bounds = __stroke_frequency_limits(config)

    res = OPT.linprog(
        c=-1*np.array(config.efficiency_factors),
        A_ub=np.array([config.fatigue_factors]),
        b_ub=np.array(config.total_energy),
        bounds=bounds,
        integrality=1)
    return res["x"]


def optimize_200im(input_dir: str) -> List[str]:
    raise Exception("Not yet implemented")


def estimate_time(input_dir: str, frequencies: List[float]) -> str:
    # 100m for each stroke.
    STROKE_LEN = 100

    with open(os.path.join(input_dir, "model_configuration.json")) as \
         config_file:
        time_data = __parse_time_data(json.loads(config_file.read()))

    uw_td = [time_data.uw_fly, time_data.uw_bk, time_data.uw_bs, time_data.uw_fr]
    times = []

    for (dps, f, uw) in zip(time_data.dps, frequencies, uw_td):
        # UW time and distance, per stroke.
        (uw_t, uw_d) = uw
        num_cycles = (STROKE_LEN - uw_d)/(dps)

        # Surfaced swim time for the stroke.
        stroke_time = num_cycles * (60/f)

        # Adding up the surfaced and uw swim-time.
        times.append(stroke_time + uw_t)

    total_time = sum(times)
    (min, sec) = (total_time // 60, round(total_time % 60, 2))
    return f"{int(min)}:{sec}"
