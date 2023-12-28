import argparse
from typing import Dict, Any
import video_utils.api as API
from pathlib import Path
import sys


def __launch(args: argparse.Namespace) -> None:
    actions = {"mute": API.mute}

    if args.action not in actions:
        print(f"Unkown action {args.action}")
        sys.exit(1)
    for file in args.filename:
        path = Path(file)
        API.mute(file, f"{path.parent}/{path.stem}_silent{path.suffix}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description ="Video Utils")
    parser.add_argument("filename", nargs="+")
    parser.add_argument("--action", action="store", type=str, required=True, choices=["mute"])
    arguments = parser.parse_args()
    __launch(arguments)
