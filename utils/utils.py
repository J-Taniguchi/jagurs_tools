import pandas as pd

def read_tsun_par(path):
    tsun_par = dict()
    with open(path, "r") as f:
        for line in f:
            if "=" in line:
                line = line.split("=")
                key = line[0]
                val = line[1][:-1]
                try :
                    tsun_par[key] = int(val)
                except:
                    try:
                        tsun_par[key] = float(val)
                    except:
                        val = val.replace("\"", "")
                        val = val.replace("\'", "")
                        val = val.replace(" ", "")
                        tsun_par[key] = val
    return tsun_par

def read_gridfile(path):
    heads = [
        "ID",
        "PID",
        "liner_flag",
        "bathy_path",
        "disp_path",
        "wet_or_dry_path",
        "line_path"
    ]

    gridfile = []
    with open(path, "r") as f:
        for line in f:
            line = line.replace("\t", " ")
            line = line.replace("\n", "")
            while True:
                line = line.replace("  ", " ")
                if "  " not in line:
                    break
            line = line.split(" ")
            while len(line) < len(heads):
                line.append(None)
            gridfile.append(line)
    gridfile = pd.DataFrame(gridfile, columns=heads)
    return gridfile