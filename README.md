# Curating an ML-Ready Dataset from Crowd-Sourced Hardware Records

A case study on California EV charging equipment (Open Charge Map), with exploratory data analysis and TensorFlow.

**Question:** how much of the path to a trustworthy model comes from dataset curation (validation, cleaning, versioning,
leakage control, honest splits) versus model choice? The task is to predict the rated power (kW) of an EV charger connector.

## Headline results (test set, grouped by charging location)

| Model | MAE (kW) | R² |
|---|---|---|
| Global median | 27.2 | -0.15 |
| Connector-type median | 15.8 | 0.30 |
| Ridge (one-hot) | 12.7 | 0.67 |
| Gradient boosting | 9.6 | 0.76 |
| TensorFlow (3 seeds: 9.78 ± 0.18; ensemble) | 9.7 | 0.75 |

- Curation removed 2.3% of raw rows (15 records outside California, 107 duplicates, 373 with no power value, 4 contradictory labels) and excluded two target-leaking features.
- TensorFlow **matches but does not beat** gradient boosting on this small tabular dataset. The big gain comes from moving beyond simple baselines.
- Operator is the most informative feature after connector type. Location features add noise.
- Errors are concentrated in high-power DC fast chargers, where the same connector type is installed at many power ratings.

Full write-up, figures and error analysis: `reports/01_ev_power_case_study.html` (or the notebook).

## What is in this project

```
data/raw/            California export (from Open Charge Map, via scripts/ocm_california.py)
data/processed/      v2 clean + model-ready datasets (parquet) and manifest.json (checksums + cleaning ledger)
notebooks/           01_ev_power_case_study.ipynb  (the full case study, executed)
reports/             HTML export, figures, data dictionary, results and ablation CSVs, experiment log
models/              trained TensorFlow model (seed 0)
scripts/             ocm_california.py: builds the raw CSV from the ocm-export repository
```

## Run it yourself (macOS)

TensorFlow needs a recent Python (3.10 or newer is recommended). The Python that ships with macOS Command Line Tools may be too old, so check with `python3 --version`. If needed, install a newer one from python.org or Homebrew.

```bash
cd ev_power_case_study
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab notebooks/01_ev_power_case_study.ipynb
```

Then choose **Run > Run All Cells**. It takes a few minutes on a laptop.

**Optional experiment tracking:** set `WANDB_API_KEY` in your environment before launching Jupyter to log runs and the dataset artifact to Weights & Biases. A local log (`reports/experiment_log.jsonl`) is always written. The W&B path was not exercised in the original run, since no key was available.

Tested with Python 3.13, TensorFlow 2.21, scikit-learn 1.9, pandas 3.0 (exact versions in `reports/environment.json`).

## Rebuilding the raw data from scratch

```bash
git clone --depth 1 https://github.com/openchargemap/ocm-export ~/open_charge_map
python3 scripts/ocm_california.py ~/open_charge_map data/raw/california_ev_chargers.csv
```

## Data governance

- **Source and license:** Open Charge Map. Records from contributors use the Open Charge Map license, while other records come from data providers with their own open-data licenses (see `referencedata.json` in the source repository). Attribution is required, and the licenses should be reviewed before redistributing derived data.
- **Provenance:** every dataset version has a SHA-256 checksum and every dropped row is accounted for in `data/processed/manifest.json`.
- **Sensitivity:** business locations and operator names only. Contact fields from the source were not carried over.
- **Leakage controls:** `charge_level` (a bucket of the target) and `amps`/`voltage` (which reconstruct power) are excluded. Splits are grouped by location. Vocabularies and scalers are fit on training data only.

## Limitations

No usage or reliability data exists in the source, so this predicts a hardware *specification*, not demand or failures. Labels are crowd-sourced and some records are stale. `date_created` reflects bulk imports, not install dates, so no time trends are analysed. The data is a single snapshot of one state.
