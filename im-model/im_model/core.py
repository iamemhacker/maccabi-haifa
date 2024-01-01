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

    print(f"EF: {config.efficiency_factors}")
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
    LAP_LEN = 50

    with open(os.path.join(input_dir, "model_configuration.json")) as \
         config_file:
        config = json.loads(config_file.read())
        dps = config["dps"]
        assert (len(dps) == 4 and len(frequencies) == 4), \
            f"Expected DPS and Frequencies both to be 4. (Got {len(dps)} and {len(frequencies)})"
        times = []
        for (d, f) in zip(dps, frequencies):
            num_cycles = LAP_LEN/d
            lap_time = num_cycles * (60/f)
            times.append(lap_time * (100/LAP_LEN))

    total_time = sum(times)
    (min, sec) = (total_time // 60, round(total_time % 60, 2))
    return f"{int(min)}:{sec}"
