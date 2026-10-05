from .data_loader import split_pipe

def analyze_skill_gap(user_skills, required_skills, preferred_skills=None):
    have = {x.lower(): x for x in user_skills}
    required = split_pipe(required_skills) if isinstance(required_skills, str) else list(required_skills)
    preferred = split_pipe(preferred_skills) if isinstance(preferred_skills, str) else list(preferred_skills or [])
    have_l = set(have)
    required_l = {x.lower() for x in required}
    preferred_l = {x.lower() for x in preferred}
    present = [x for x in required if x.lower() in have_l]
    missing = [x for x in required if x.lower() not in have_l]
    critical = missing[:max(1, min(3, len(missing)))]
    recommended = [x for x in preferred if x.lower() not in have_l]
    readiness = round(100 * len(present) / len(required), 1) if required else 0
    return {"present":present,"missing":missing,"critical":critical,"recommended":recommended,"readiness":readiness}

def readiness_score(user_skills, gap, has_projects=False, tools_score=None, domain_score=50, experience_score=50):
    technical = gap["readiness"]
    projects = 75 if has_projects else 35
    tools = tools_score if tools_score is not None else min(100, technical + 5)
    return round(.40*technical + .20*projects + .15*tools + .15*domain_score + .10*experience_score, 1)
