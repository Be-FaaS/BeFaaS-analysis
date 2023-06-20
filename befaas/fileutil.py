import json
import pathlib


def log_entry_iterator(path: pathlib.Path):
    print(f"Iterate over {path} ...")
    start = True
    with open(path) as f:
        newtext = f.read(300)  # Reads the first 100 character and moves pointer to 101th character
        buffer = newtext
        if start:
            buffer = buffer[1:]
            start = False

        while len(newtext) > 0:
            newtext = f.read(300)  # Move pointer to end of next 100 character
            buffer = buffer + newtext

            if buffer.__contains__("["):
                #print(buffer)
                tmpend = buffer.find("]", buffer.find("["))
                if (tmpend < 0):
                    #print("ERROR, buffer to small" + buffer)
                    newtext = f.read(300)  # Move pointer to end of next 100 character
                    buffer = buffer + newtext
                buffer = buffer.replace("]","",1)
                buffer = buffer.replace("[", "",1)


            count = buffer.count("{\"__logentry__\"")
            end = buffer.count("]")
            if (end == 1):
                startidx = buffer.index("{\"__logentry__\"")
                endidx = buffer.index("]")
                entrystring = buffer[startidx:endidx]
                buffer = ""
                # print(entrystring)
                yield json.loads(entrystring)
            if (count > 1):
                startidx = buffer.index("{\"__logentry__\"")
                endidx = buffer.index(",{\"__logentry__\"", startidx + 1)
                entrystring = buffer[startidx:endidx]
                buffer = buffer[endidx:]
                # print(entrystring)
                yield json.loads(entrystring)
