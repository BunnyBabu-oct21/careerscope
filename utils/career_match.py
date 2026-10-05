from typing import Iterable, Dict
import pandas as pd
from .data_loader import split_pipe

def _norm(values: Iterable[str]):
    return {str(v).strip().lower() for v in values if str(v).strip()}

def skill_match(user_skills, required_skills):
    req = _norm(required_skills)
    if not req:
        return 0.0
    return round(100 * len(req & _norm(user_skills)) / len(req), 1)

def domain_match(user_domains, career_domain):
    domains = _norm(user_domains)
    if not domains:
        return 0.0
    target = str(career_domain).lower()
    if target in domains:
        return 100.0
    aliases = {
        "machine learning": {"artificial intelligence","data science"},
        "artificial intelligence": {"machine learning","generative ai"},
        "generative ai": {"artificial intelligence","machine learning"},
        "data science": {"data analytics","machine learning"},
        "software engineering": {"backend development","frontend development","full stack development"},
        "cloud computing": {"devops"},
        "devops": {"cloud computing"},
    }
    related = aliases.get(target, set())
    return 70.0 if related & domains else 25.0

def education_match(degree, branch, career_name):
    degree = (degree or "").lower()
    branch = (branch or "").lower()
    if not degree:
        return 50.0
    ai = any(x in branch for x in ["ai", "artificial", "machine", "data science"])
    tech = any(x in branch for x in ["cse","it","computer","ece"])
    if any(x in career_name.lower() for x in ["ai","machine learning","data scientist","data engineer","computer vision","nlp","mlops","llm"]):
        return 100.0 if ai or tech else 75.0
    return 95.0 if tech or ai else 75.0

def experience_match(experience, career_name):
    exp = (experience or "Fresher").lower()
    if "fresher" in exp or "0–1" in exp or "0-1" in exp:
        return 75.0 if any(x in career_name.lower() for x in ["engineer","developer","analyst"]) else 65.0
    if "1–3" in exp or "2–5" in exp:
        return 100.0
    return 100.0

def overall_match(skill, domain, education, experience):
    return round(min(100, max(0, .55*skill + .20*domain + .10*education + .15*experience)), 1)

def rank_careers(user, careers: pd.DataFrame):
    rows=[]
    for _, c in careers.iterrows():
        req=split_pipe(c.get("required_skills",""))
        sm=skill_match(user["skills"], req)
        dm=domain_match(user["domains"], c.get("domain",""))
        em=education_match(user.get("degree",""), user.get("branch",""), c["career"])
        xm=experience_match(user.get("experience","Fresher"), c["career"])
        om=overall_match(sm,dm,em,xm)
        rows.append({**c.to_dict(),"skill_match":sm,"domain_match":dm,"education_match":em,"experience_match":xm,"overall_match":om})
    return pd.DataFrame(rows).sort_values(["overall_match","demand"], ascending=False).reset_index(drop=True)

def match_label(score):
    if score >= 80: return "Excellent Match"
    if score >= 65: return "Strong Match"
    if score >= 50: return "Moderate Match"
    return "Low Match"
