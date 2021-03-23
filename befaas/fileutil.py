import json
import pathlib


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
                yield json.loads(entrystring)
            if (count > 1):
                startidx = buffer.index("{\"__logentry__\"")
                endidx = buffer.index(",{\"__logentry__\"", startidx + 1)
                entrystring = buffer[startidx:endidx]
                # print(entrystring)
                buffer = buffer[endidx:]
                yield json.loads(entrystring)
