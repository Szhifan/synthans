"""Build per-level counterparts of the two existing appendix result tables."""

import csv
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean


PAPER = Path(__file__).resolve().parents[1]
SPLITS = ("BEETLE UQ", "SciEntsBank UQ", "SciEntsBank UD")
LEVELS = ("incorrect", "partially correct", "correct")
METHODS = {
    "w/o synthetic data": ("Real-only", ""),
    "Prompting": ("Random: Prompting", "Prompting"),
    "SFT": ("Random: SFT", "SFT"),
    "SFT+DPO": ("Random: SFT+DPO", "SFT+DPO"),
    "DPO": ("Random: DPO only", "DPO only"),
    "Random": ("Random: DPO only", "DPO only"),
    "Highest-Rank": ("Highest", "DPO only"),
    "Lowest-Rank": ("Lowest", "DPO only"),
    "Hard Selection": ("Hard selection", "DPO only"),
    "$(0, 30)$": ("0/30", "DPO only"),
    "$(0, 50)$": ("0/50", "DPO only"),
    "$(10, 50)$": ("10/50", "DPO only"),
    "$(20, 20)$": ("20/20", "DPO only"),
}


def main():
    groups = defaultdict(list)
    with (PAPER.parent / "appendix_long.csv").open(newline="") as source:
        for row in csv.DictReader(source):
            key = (row["split"], row["model"], row["condition"],
                   row["family"], int(row["fraction"]))
            groups[key].append(row)

    def score(split, model, method, fraction, metric):
        condition, family = METHODS[method]
        rows = groups[(split, model, condition, family, fraction)]
        assert len(rows) == (1 if fraction == 0 else 5), (split, model, method, fraction)
        assert len({row["draw"] for row in rows}) == len(rows)
        return mean(float(row[metric]) for row in rows)

    source = (PAPER / "appendix_tables.tex").read_text()
    tables = re.findall(r"\\begin\{table\*\}.*?\\end\{table\*\}", source, re.S)
    assert len(tables) == 2
    output = []
    verified = 0
    for template in tables:
        for level, name in enumerate(LEVELS):
            metric = f"f1_level_{level}"
            lines = []
            model = None
            for line in template.splitlines():
                match = re.search(r"\\multirow\{\d+\}\{\*\}\{([^}]+)\}", line)
                if match:
                    model = match[1]
                parts = line.split(" & ")
                if len(parts) > 2 and parts[1] in METHODS:
                    method = parts[1]
                    baseline = method == "w/o synthetic data"
                    cells = []
                    for split in SPLITS:
                        base = score(split, model, "w/o synthetic data", 0, metric)
                        if baseline:
                            cells.append(r"\multicolumn{5}{c}{" + f"{base:.1f}" + "}")
                        else:
                            for fraction in range(1, 6):
                                if method in ("Highest-Rank", "Lowest-Rank") and fraction > 1:
                                    cells.append("--")
                                    continue
                                value = score(split, model, method, fraction, metric)
                                cell = f"{value:.1f}"
                                if value < base:
                                    cell = r"\textcolor{red}{" + cell + "}"
                                cells.append(cell)
                    # Check the source mapping against every published macro-F1 cell.
                    expected = []
                    for split in SPLITS:
                        for fraction in ([0] if baseline else range(1, 6)):
                            if method in ("Highest-Rank", "Lowest-Rank") and fraction > 1:
                                continue
                            expected.append(f"{score(split, model, method, fraction, 'f1'):.1f}")
                    actual = re.findall(r"\d+\.\d", " & ".join(parts[2:]))
                    assert actual == expected, (model, method, actual, expected)
                    verified += len(expected)
                    line = " & ".join(parts[:2] + cells) + r" \\"
                if line.startswith(r"\caption{"):
                    line = line.replace("Macro-F1", "F1 for " + name + " answers", 1)
                    line = line.replace("means over 5 sampling draws", "means over five sampling draws")
                    line = line.replace("The score without synthetic data", "The per-level score without synthetic data")
                    line = line.replace("the score without synthetic data", "the per-level score without synthetic data")
                if line.startswith(r"\label{"):
                    line = line[:-1] + f"-level-{level}" + "}"
                lines.append(line)
            output.append("\n".join(lines))
    (PAPER / "appendix_per_level_tables.tex").write_text("\n\n".join(output) + "\n")
    print(f"Generated {len(output)} tables; checked {verified} macro-F1 source mappings.")


if __name__ == "__main__":
    main()
