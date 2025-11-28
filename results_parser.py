import re
import json
import pandas as pd
from pathlib import Path

# Path to your raw data file
raw_file = Path("raw_results.txt")  # adjust if needed
text = raw_file.read_text()

rows = []

def add_row(method, env, metric, value):
    rows.append({
        "method": method,
        "env": env,
        "metric": metric,
        "value": value
    })

# -------------------------------------------------------------------
# 1. Parse Reinforcement Learning (PPO and SAC)
# -------------------------------------------------------------------

rl_block_pattern = r"# Reinforcement Learning \((.*?)\)(.*?)(?=# Reinforcement Learning|\Z)"
env_section_pattern = r"## ([^\n]+)\n(.*?)\n([0-9][^\n]+)"

for method_block, block_content in re.findall(rl_block_pattern, text, flags=re.S):
    method = f"RL-{method_block.strip()}"
    for env, header, csv_line in re.findall(env_section_pattern, block_content, flags=re.S):
        columns = header.split(",")
        values = csv_line.split(",")
        for c, v in zip(columns, values):
            val = v.strip()
            val = None if val == "" else val
            add_row(method, env, c.strip(), val)

# -------------------------------------------------------------------
# 2. Parse Imitation Learning (Diffusion Policy) FROM FILES
# -------------------------------------------------------------------

# Pattern:  ## Motion2D-p0-v0  \n Load from path/to/file.json
il_pattern = r"## ([^\n]+)\nLoad from ([^\n]+)"

for env, json_path in re.findall(il_pattern, text):
    method = "ImitationLearning-DiffusionPolicy"
    json_file = Path(json_path.strip())

    if not json_file.exists():
        print(f"WARNING: File not found: {json_path}")
        continue

    with open(json_file, "r") as f:
        data = json.load(f)

    # --- Training results ---
    if "train_results" in data:
        for k, v in data["train_results"].items():
            add_row(method, env, f"train_{k}", v)

    # --- Eval summary stats ---
    eval_section = data.get("eval_results", {}).get("summary statistics", {})
    for metric_name, metric_dict in eval_section.items():
        for stat_name, stat_val in metric_dict.items():
            if stat_name != "values":  # we do not store raw lists
                add_row(method, env, f"{metric_name}_{stat_name}", stat_val)

# -------------------------------------------------------------------
# 3. Parse LLM/VLM Planning (CSV sections)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# 3. Parse LLM/VLM Planning (CSV sections)
# -------------------------------------------------------------------

planning_pattern = r"# (LLM Planning|VLM Planning)[^\n]*\n+([^\n]+)\n(.*?)(?=\n#|\Z)"

for planning_method, header, block in re.findall(planning_pattern, text, flags=re.S):
    method = planning_method.replace(" ", "")  # LLMPlanning or VLMPlanning

    header = header.strip()
    cols = header.split(",")

    # Extract data rows
    lines = [
        line.strip() for line in block.splitlines()
        if line.strip() and not line.startswith("#")
    ]

    for line in lines:
        values = line.split(",")
        env = values[0]
        for c, v in zip(cols[1:], values[1:]):  # skip env col
            add_row(method, env, c.strip(), v.strip())

# -------------------------------------------------------------------
# 4. Parse Bilevel Planning (mini tables)
# -------------------------------------------------------------------
# Match:
#   ## EnvName
#   metric,mean,std
#   row,row,row
# until the next "##" or next "#" section OR end of file
bilevel_pattern = r"## ([^\n]+)\nmetric,mean,std\n(.*?)(?=\n## |\n# |\Z)"

for env, block in re.findall(bilevel_pattern, text, flags=re.S):
    method = "BilevelPlanning"
    lines = [l.strip() for l in block.splitlines() if l.strip()]

    for line in lines:
        metric, mean, std = line.split(",")
        add_row(method, env, f"{metric}_mean", mean)
        add_row(method, env, f"{metric}_std", std)


# -------------------------------------------------------------------
# 5. Build final table
# -------------------------------------------------------------------

df = pd.DataFrame(rows)

print(df)
df.to_csv("unified_table.csv", index=False)
