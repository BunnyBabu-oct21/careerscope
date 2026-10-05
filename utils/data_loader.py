from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def _load(name: str, required=None):
    path = DATA_DIR / name
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=required or [])
    return df

def load_careers(): return _load("careers.csv")
def load_skills(): return _load("skills.csv")
def load_companies(): return _load("companies.csv")
def load_jobs(): return _load("jobs.csv")
def load_salaries(): return _load("salaries.csv")
def load_trends(): return _load("career_trends.csv")

def split_pipe(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [x.strip() for x in str(value).split("|") if x.strip()]
