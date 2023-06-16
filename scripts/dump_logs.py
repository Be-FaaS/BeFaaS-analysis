#!/usr/bin/env python3
import json
import pathlib
import datetime
from collections import Counter

from typing import Callable

from loguru import logger

from argmagic import argmagic

import befaas as bf


def parse_timewindow(timewindow: str) -> datetime.timedelta:
    tdelta_args = {}
    if timewindow.endswith("s"):
        tdelta_args["seconds"] = int(timewindow[:-1])
    elif timewindow.endswith("m"):
        tdelta_args["minutes"] = int(timewindow[:-1])
    elif timewindow.endswith("h"):
        tdelta_args["hours"] = int(timewindow[:-1])
    elif timewindow.endswith("d"):
        tdelta_args["days"] = int(timewindow[:-1])
    else:
        raise ValueError(f"Time window should be number with d/h/m/s suffix (eg 30h) but got: {timewindow}")
    return datetime.timedelta(**tdelta_args)


def path_line_iterator(path: pathlib.Path):
    for filepath in path.glob("*.log"):
        logger.debug("Reading {}", filepath)
        platform = filepath.stem
        with open(filepath, encoding="utf8") as f:
            for line in f:
                yield (platform, line)



def parse_logdir_iter(logdir: pathlib.Path, outdir: pathlib.Path, filters: [Callable] = None):
    """Iteratively parse and store log entries.
    """
    if outdir.is_dir():
        outdir = outdir / f"{logdir.name}.json"

    if filters is None:
        filters = []

    logger.debug("Writing to {}", outdir)
    with open(outdir, "w") as jsfile:
        jsfile.write("[")
        initial = True
        for platform, line in path_line_iterator(logdir):
            # print(f"plattform: {platform}, line: {line}")
            entry = bf.parse_entry(line, platform)

            if entry is not None:
                if all([f(entry) for f in filters]):
                    jsfile.write(("" if initial else ",") + json.dumps(entry))
                    initial = False

        jsfile.write("]")
    logger.debug("Finished writing logdump")


def dump_logs_iter(
        logdir: pathlib.Path,
        outdir: pathlib.Path,
        version: str = None,
        timewindow: str = None,
):
    filters = [
        bf.is_valid
    ]

    deploy_path = logdir / "deployment_id.txt"
    if deploy_path.exists():
        with open(deploy_path) as dfile:
            deploy_id = dfile.read().strip()

        filters.append(lambda e: e.data.get("deploymentId", "") == deploy_id)

    if version is not None:
        filters.append(lambda e: e.data["version"] == version)

    if timewindow is not None:
        raise NotImplementedError("Timewindow currently not supported in iterative version.")

    parse_logdir_iter(logdir, outdir, filters)


def dump_logs(
        logdir: pathlib.Path,
        outdir: pathlib.Path,
        version: str = None,
        timewindow: str = None,
):
    """Output logs to the given destination directory.

    Args:
        logdir: Directory containing raw log entries.
        outdir: Destination for outputting collected log json.
        version: Version requirement for inclusion.
        timewindow: Only include events inside a timewindow up to latest.
    """
    log_entries = bf.parse_logdir(logdir)
    print(f"Loading {len(log_entries)} entries from {logdir}")

    if version is not None:
        print(f"Filtering: version={version}")
        num_before = len(log_entries)
        log_entries = list(filter(lambda e: e.data["version"] == version, log_entries))
        num_after = len(log_entries)
        print(f"  Kept {num_after}/{num_before} ({num_before - num_after} removed)")

    if timewindow is not None:
        end_time = max(*[e.timestamp for e in log_entries])
        timedelta = parse_timewindow(timewindow)
        start_time = end_time - timedelta
        print(f"Filtering timewindow of {timewindow}: {start_time} {end_time}")
        num_before = len(log_entries)
        log_entries = [e for e in log_entries if e.timestamp >= start_time]
        num_after = len(log_entries)
        print(f"  Kept {num_after}/{num_before} ({num_before - num_after} removed)")

    deploy_path = logdir / "deployment_id.txt"
    if deploy_path.exists():
        with open(deploy_path) as dfile:
            deploy_id = dfile.read().strip()
        print(f"Filtering on deploy ID: {deploy_id}")
        num_before = len(log_entries)
        log_entries = [e for e in log_entries if e.data.get("deploymentId", "") == deploy_id]
        num_after = len(log_entries)
        print(f"  Kept {num_after}/{num_before} ({num_before - num_after} removed)")

    if outdir.is_dir():
        outdir = outdir / f"{logdir.name}.json"

    print(f"Dumping {len(log_entries)} entries to {outdir}")
    with open(outdir, "w") as jsfile:
        json.dump(log_entries, jsfile)


if __name__ == "__main__":
    argmagic(dump_logs_iter, positional=("logdir", "outdir"))
