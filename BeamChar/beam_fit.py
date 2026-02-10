import pandas as pd
from pathlib import Path

# -------- config --------
IN_FILE = Path("BEAM2.xlsx")

ROW_MAP = {
    "Distance": "z_mm",
    "Beam Width Clip X (13.5%)": "Dmin_um",
    "Beam Width Clip Y (13.5%)": "Dmaj_um",
}
# ------------------------

# read raw sheet (no header assumptions)
df_raw = pd.read_excel(IN_FILE, header=None)

# first column = row labels
labels = df_raw.iloc[:, 0].astype(str)
data = df_raw.iloc[:, 1:]

out = {}

for label, new_name in ROW_MAP.items():
    mask = labels.str.strip() == label
    if not mask.any():
        raise ValueError(f"Row '{label}' not found in Excel file")

    values = data.loc[mask].values.squeeze()
    out[new_name] = values.astype(float)

# build clean dataframe
df = pd.DataFrame(out)
df.to_csv("BEAM2.csv", index=False)
print(df.head())
