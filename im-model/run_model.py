from typing import Optional
import sys
import argparse
from im_model.core import optimize_400im, optimize_200im, estimate_time
from typing import List


def __run_model(flavor: str, input_dir: str, output_file: Optional[str],
                time_estimate: bool) -> None:
    if flavor == "200-im":
        frequencies = optimize_200im(input_dir)
    elif flavor == "400-im":
        frequencies = optimize_400im(input_dir)
    else:
        raise Exception(f"Unknown flavor {flavor}")

    out_handle = sys.stdout if output_file is None else open(output_file)
    headers = ["fly", "bk", "bs", "free"]
    d = dict(zip(headers, frequencies))
    out_handle.write(', '.join([f"{k} -> {int(v)}\n" for (k, v) in d.items()]))

    if time_estimate:
        print(f"Time estimation: {estimate_time(input_dir, frequencies)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="i.m. model driver")
    parser.add_argument("--flavor", type=str,
                        choices=["200-im", "400-im", "time-predictor"])
    parser.add_argument("--input-dir", type=str, required=True)
    parser.add_argument("--output-file", type=str, required=False)
    parser.add_argument("-estimate-time", action='store_true', default=False)
    args = parser.parse_args()
    print(args)
    __run_model(args.flavor, args.input_dir, args.output_file,
                args.estimate_time)
