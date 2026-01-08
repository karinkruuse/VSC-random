import re
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
IN_DIR = BASE  / "data" / "2505020"
IN_DIR = IN_DIR.resolve()

OUT_DIR = IN_DIR / "converted"
OUT_DIR.mkdir(exist_ok=True)



for f in IN_DIR.glob("DeviceData_#*.csv"):
    n = int(re.search(r"#(\d+)", f.name).group(1))

    new_num = (n - 10) * 25
    if n >= 60:
        new_num += 50

    out_name = f"{int(new_num)}.csv"# if new_num.is_integer() else f"{new_num}.csv"

    df = pd.read_csv(f, encoding="latin1", skiprows=15)     # use the encoding that worked for your example
    df.iloc[:, :4].to_csv(OUT_DIR / out_name, index=False)

    print(f"{f.name} -> {out_name}")
