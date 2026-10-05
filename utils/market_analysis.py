import pandas as pd

def filter_jobs(jobs, keyword="", career=None, skill=None, location=None, experience=None, salary=None, work_mode=None, company=None):
    df=jobs.copy()
    if keyword:
        q=keyword.lower()
        mask=df.astype(str).apply(lambda col: col.str.lower().str.contains(q, na=False)).any(axis=1)
        df=df[mask]
    for col,val in [("career",career),("location",location),("experience",experience),("work_mode",work_mode),("company",company)]:
        if val and val != "Any" and col in df:
            df=df[df[col]==val]
    if skill and skill != "Any":
        df=df[df["required_skills"].fillna("").str.lower().str.contains(skill.lower(), na=False)]
    if salary is not None:
        df=df[(df["salary_max_lpa"].fillna(0)>=salary)]
    return df

def market_summary(jobs):
    if jobs.empty:
        return {"total":0,"top_location":"—","top_career":"—","top_company":"—"}
    return {
        "total":len(jobs),
        "top_location":jobs["location"].value_counts().index[0],
        "top_career":jobs["career"].value_counts().index[0],
        "top_company":jobs["company"].value_counts().index[0]
    }

def future_score(row):
    # Analytical indicator only; not a guaranteed prediction.
    demand=float(row.get("demand",0)); growth=float(row.get("growth",0))
    salary=float(row.get("salary_potential",0)); adoption=float(row.get("future_score",0))
    competition=float(row.get("competition",0))
    return round(max(0,min(100,.24*demand+.22*growth+.18*salary+.22*adoption+.14*(100-competition))),1)
