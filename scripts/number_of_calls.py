import json
import os
import pathlib
from typing import List

from argmagic import argmagic
import pandas as pd

from befaas.logentry import RequestLog, cast_log_type


def log_entry_iterator(path: pathlib.Path):
    print(f"Iterate over {path} ...")
    with open(path) as f:
        newtext = f.read(100)  # Reads the first 100 character and moves pointer to 101th character
        buffer = newtext

        while len(newtext) > 0:
            newtext = f.read(100)  # Move pointer to end of next 100 character
            buffer = buffer + newtext

            count = buffer.count("{\"__logentry__\"")
            end = buffer.count("]")
            if (end == 1):
                startidx = buffer.index("{\"__logentry__\"")
                endidx = buffer.index("]")
                entrystring = buffer[startidx:endidx]
                buffer = ""
                yield (cast_log_type(json.loads(entrystring)))
            if (count > 1):
                startidx = buffer.index("{\"__logentry__\"")
                endidx = buffer.index(",{\"__logentry__\"", startidx + 1)

                entrystring = buffer[startidx:endidx]
                buffer = buffer[endidx:]
                yield cast_log_type(json.loads(entrystring))

            # entry = "{__logentry .... }"
            # logentry = cast_log_type(json.load(entry))


def main(logdumps: List[pathlib.Path]):
    """
        Counts nummber of calls per function for each logdump.

        Args:
            logdumps: List of logdumps (e.g., [dumpAWS.json,dumpGoogle.json]).

        Raises:
            Nothing.

        Returns:
            Nothing.
    """
    df = pd.DataFrame()
    df.index.name = 'function'

    for dump in logdumps:
        print(f"Include dump {dump} ...")
        df.insert(len(df.columns), str(dump), 0)
        requests = 0
        old_id = str("")
        for entry in log_entry_iterator(dump):
            if isinstance(entry, RequestLog):
                new_id = entry.data.get("deploymentId")
                if old_id != new_id:
                    print(f"Found New Deployment ID: {new_id}")
                    old_id = new_id
                requests = requests + 1
                if str(entry.function) == "payment":
                    print(str(entry))
                if (requests % 10000 == 0):
                    print(f"processed {requests} requests")
                if str(entry.function) in df.index:
                    oldval = df.loc[str(entry.function), str(dump)]
                    df.loc[str(entry.function), str(dump)] = oldval + 1
                else:
                    df.loc[str(entry.function), str(dump)] = 1

        print(df)


if __name__ == "__main__":
    # Move one level up
    os.chdir('../')
    argmagic(main, positional=("logdumps",))
