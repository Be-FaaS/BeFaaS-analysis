import json
import os
import pathlib
from typing import List

from argmagic import argmagic
import shutil

from befaas.fileutil import log_entry_iterator
from befaas.logentry import ColdstartLog



def main(logdumps: List[pathlib.Path]):
    """
        Sorts log entries based on its context ids in separate files and one folder for each provider.

        Args:
            logdumps: List of logdumps (e.g., [dumpAWS.json,dumpGoogle.json]).

        Raises:
            Nothing.

        Returns:
            Nothing.
    """

    for dump in logdumps:
        print(f"Include dump {dump} ...")
        # Create folder for dump
        foldername = str(dump)[:-5]
        # delete already existing folder
        if pathlib.Path(foldername).exists() and pathlib.Path(foldername).is_dir():
            print(f"{foldername} already exists, skip...")
            continue
            print(f"folder {foldername} already exist, deleting...")
            shutil.rmtree(pathlib.Path(foldername))
            print(f"done.")

        print(f"Create empty folder for provider {foldername}")
        pathlib.Path(foldername).mkdir(parents=True, exist_ok=True)

        # Count entries to get some progress feedback
        entries = 0

        for entry in log_entry_iterator(dump):
            entries = entries + 1
            if (entries % 10000 == 0):
                print(f"processed {entries} entries")

            # Add entry file based on context id
            # if entry.get("context_id") != None:
            if not isinstance(entry, ColdstartLog):
                id = entry.context_id
                subfolder = str(id)[:1]
                pathlib.Path(foldername + "/" + subfolder).mkdir(parents=True, exist_ok=True)

                with open(foldername + "/" + subfolder + "/" + str(id) + ".json", "a+") as jsfile:
                    jsfile.write(json.dumps(entry) + "\n")
                    jsfile.close()


if __name__ == "__main__":
    # Move one level up
    os.chdir('../')
    argmagic(main, positional=("logdumps",))
