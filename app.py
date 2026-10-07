from pathlib import Path
import os, sqlite3, re
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_careers, load_skills, load_companies, load_jobs, load_salaries, load_trends, split_pipe
from utils.career_match import rank_careers, match_label
from utils.skill_gap import analyze_skill_gap, readiness_score
from utils.market_analysis import filter_jobs, future_score, market_summary
from utils.recommendations import roadmap_for, project_recommendations

ROOT=Path(__file__).resolve().parent
DB_PATH=ROOT/"database"/"careerscope.db"

st.set_page_config(page_title="CareerScope AI", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container{padding-top:1.2rem;padding-bottom:2rem}
.metric-card{padding:1rem 1.1rem;border:1px solid rgba(128,128,128,.18);border-radius:14px;background:rgba(128,128,128,.05)}
.small-muted{color:#777;font-size:.85rem}
.badge{display:inline-block;padding:.25rem .6rem;border-radius:999px;background:rgba(70,120,255,.12);font-size:.82rem}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_careers(), load_skills(), load_companies(), load_jobs(), load_salaries(), load_trends()

@st.cache_resource
def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    con=sqlite3.connect(DB_PATH)
    cur=con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS skills(id INTEGER PRIMARY KEY AUTOINCREMENT, skill TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS careers(id INTEGER PRIMARY KEY AUTOINCREMENT, career TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS career_skills(career_id INTEGER, skill_id INTEGER, required INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS companies(id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS jobs(job_id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, career TEXT, work_mode TEXT);
    CREATE TABLE IF NOT EXISTS salaries(career TEXT, experience TEXT, min_lpa REAL, median_lpa REAL, max_lpa REAL);
    CREATE TABLE IF NOT EXISTS career_trends(date TEXT, category TEXT, index_value REAL);
    CREATE TABLE IF NOT EXISTS user_profiles(user_id INTEGER, education TEXT, degree TEXT, branch TEXT, year TEXT, experience TEXT, preferred_location TEXT, work_mode TEXT);
    CREATE TABLE IF NOT EXISTS user_skills(user_id INTEGER, skill TEXT);
    """)
    con.commit(); con.close()
    return True

init_db()
careers, skills_df, companies, jobs, salaries, trends = get_data()

if jobs.empty or careers.empty:
    st.error("Core local dataset is missing. The app can still open, but add the CSV files from the project data folder.")
    st.stop()

# Session profile
defaults={"name":"","education":"B.Tech","degree":"B.Tech","branch":"AI","year":"3rd Year","experience":"Fresher","location":"Hyderabad","work_mode":"Any","skills":[],"domains":[],"analyzed":False}
for k,v in defaults.items():
    st.session_state.setdefault(k,v)

with st.sidebar:
    st.title("🎯 CareerScope AI")
    st.caption("Personalized Job Market, Skill Gap & Career Intelligence")
    st.divider()
    page=st.radio("Navigation",[
        "🏠 Dashboard","👤 My Profile","🎯 Career Explorer","💼 Job Market","📊 Market Analytics",
        "🧩 Skill Gap","💰 Salary Insights","🏢 Companies","⚖️ Compare Careers","🛣️ Career Roadmap",
        "📄 Resume Analyzer","📰 Job Market Intelligence","⚙️ Settings"
    ])
    st.divider()
    st.caption("📦 Sample Dataset — for demonstration")
    st.caption("Live job/news data is never presented as live unless a valid provider is configured.")

def profile_form():
    st.subheader("👤 Your Career Profile")
    c1,c2=st.columns(2)
    with c1:
        st.session_state.name=st.text_input("Name",st.session_state.name)
        st.session_state.education=st.selectbox("Education",["B.Tech","B.E.","BCA","MCA","M.Tech","M.Sc","B.Sc","MBA","Diploma","Other"],index=["B.Tech","B.E.","BCA","MCA","M.Tech","M.Sc","B.Sc","MBA","Diploma","Other"].index(st.session_state.education) if st.session_state.education in ["B.Tech","B.E.","BCA","MCA","M.Tech","M.Sc","B.Sc","MBA","Diploma","Other"] else 0)
        st.session_state.branch=st.selectbox("Branch",["AI","AI & ML","CSE","Data Science","AIML","IT","ECE","EEE","Mechanical","Civil","Other"],index=["AI","AI & ML","CSE","Data Science","AIML","IT","ECE","EEE","Mechanical","Civil","Other"].index(st.session_state.branch) if st.session_state.branch in ["AI","AI & ML","CSE","Data Science","AIML","IT","ECE","EEE","Mechanical","Civil","Other"] else 0)
        st.session_state.year=st.selectbox("Year of study",["1st Year","2nd Year","3rd Year","4th Year","Graduate"],index=["1st Year","2nd Year","3rd Year","4th Year","Graduate"].index(st.session_state.year) if st.session_state.year in ["1st Year","2nd Year","3rd Year","4th Year","Graduate"] else 2)
    with c2:
        st.session_state.experience=st.selectbox("Experience",["Fresher","0–1 years","1–3 years","3–5 years","5+ years"],index=["Fresher","0–1 years","1–3 years","3–5 years","5+ years"].index(st.session_state.experience) if st.session_state.experience in ["Fresher","0–1 years","1–3 years","3–5 years","5+ years"] else 0)
        st.session_state.location=st.selectbox("Preferred location",["Any"]+sorted(jobs.location.dropna().unique().tolist()),index=(["Any"]+sorted(jobs.location.dropna().unique().tolist())).index(st.session_state.location) if st.session_state.location in ["Any"]+sorted(jobs.location.dropna().unique().tolist()) else 0)
        st.session_state.work_mode=st.selectbox("Preferred work mode",["Any","Remote","Hybrid","On-site"],index=["Any","Remote","Hybrid","On-site"].index(st.session_state.work_mode) if st.session_state.work_mode in ["Any","Remote","Hybrid","On-site"] else 0)
    st.markdown("### 🧠 Skills")
    all_skills=skills_df["skill"].dropna().tolist()
    st.session_state.skills=st.multiselect("Select the skills you know",all_skills,default=[x for x in st.session_state.skills if x in all_skills])
    st.markdown("### 🎯 Domains")
    domains=["Artificial Intelligence","Machine Learning","Generative AI","Data Science","Data Analytics","Full Stack Development","Backend Development","Frontend Development","Software Engineering","Cloud Computing","DevOps","Cybersecurity","Data Engineering","Mobile Development","IoT","Blockchain","Embedded Systems","Research","Business Intelligence"]
    st.session_state.domains=st.multiselect("Select your domains",domains,default=[x for x in st.session_state.domains if x in domains])
    if st.button("🚀 Analyze My Career",type="primary",use_container_width=True):
        st.session_state.analyzed=True
        st.rerun()

def get_ranked():
    user={"skills":st.session_state.skills,"domains":st.session_state.domains,"degree":st.session_state.education,"branch":st.session_state.branch,"experience":st.session_state.experience}
    return rank_careers(user,careers)

def selected_profile():
    return {"skills":st.session_state.skills,"domains":st.session_state.domains,"degree":st.session_state.education,"branch":st.session_state.branch,"experience":st.session_state.experience}

def metric_row(items):
    cols=st.columns(len(items))
    for col,(label,val) in zip(cols,items):
        with col:
            st.markdown(f'<div class="metric-card"><div class="small-muted">{label}</div><h3>{val}</h3></div>',unsafe_allow_html=True)

def career_card(row):
    with st.container(border=True):
        a,b,c,d=st.columns([2.4,1,1,1])
        a.markdown(f"### {row['career']}")
        a.write(match_label(row["overall_match"]))
        b.metric("Match",f"{row['overall_match']:.0f}%")
        c.metric("Demand",f"{row['demand']}/100")
        d.metric("Future",f"{row['future_score']}/100")
        st.caption(f"Domain: {row['domain']} • Difficulty: {row['entry_difficulty']} • Competition: {row['competition']}/100")
        st.write("**Required:** "+", ".join(split_pipe(row["required_skills"])))
        gap=analyze_skill_gap(st.session_state.skills,row["required_skills"],row["preferred_skills"])
        if gap["missing"]:
            st.write("**Missing:** "+", ".join(gap["missing"]))

def dashboard():
    st.title("🏠 CareerScope AI")
    st.caption("Personalized job market, skill-gap and career intelligence.")
    if not st.session_state.analyzed:
        st.info("Complete your profile in **My Profile**, choose your skills/domains, then click **Analyze My Career**.")
        metric_row([("Careers tracked",len(careers)),("Skills catalog",len(skills_df)),("Demo jobs",len(jobs)),("Companies",len(companies))])
        st.markdown("### How it works")
        st.write("1. Select education, skills and domains → 2. Match against career requirements → 3. Inspect skill gaps → 4. Explore demo market data → 5. Follow your roadmap.")
        return
    ranked=get_ranked(); top=ranked.iloc[0]
    gap=analyze_skill_gap(st.session_state.skills,top.required_skills,top.preferred_skills)
    ready=readiness_score(st.session_state.skills,gap,False,domain_score=top.domain_match,experience_score=top.experience_match)
    metric_row([("Career Match",f"{top.overall_match:.0f}%"),("Job Readiness",f"{ready:.0f}%"),("Best Career",top.career),("Future Score",f"{top.future_score}/100")])
    st.markdown("### Top 5 Career Matches")
    for _,r in ranked.head(5).iterrows(): career_card(r)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### Skills to learn")
        for s in gap["missing"][:6]: st.warning(s)
    with c2:
        st.markdown("### Best locations")
        locs=jobs[jobs.career==top.career]["location"].value_counts().head(5)
        st.bar_chart(locs)
    st.markdown("### Career roadmap")
    for i,item in enumerate(roadmap_for(top.career,gap["missing"]),1):
        st.write(f"**Phase {i}:** {item}")

def explorer():
    st.title("🎯 Career Explorer")
    ranked=get_ranked() if st.session_state.analyzed else careers.assign(overall_match=careers["demand"]*.8).sort_values("overall_match",ascending=False)
    selected=st.selectbox("Select a career",ranked["career"].head(15).tolist())
    row=ranked[ranked.career==selected].iloc[0]
    st.subheader(row["career"])
    st.write(row["description"])
    metric_row([("Match",f"{row['overall_match']:.0f}%"),("Demand",row["demand"]),("Growth",row["growth"]),("Future",row["future_score"])])
    t1,t2,t3,t4=st.tabs(["Overview","Skills","Market","Projects"])
    with t1:
        st.write("**What this person does:** "+row["description"])
        st.write("**Responsibilities:** Build, test, deploy, monitor and improve solutions relevant to the target career.")
        st.write("**Education:** "+row["education"])
        st.write("**Entry difficulty:** "+row["entry_difficulty"])
        st.write("**Common titles:** "+", ".join(split_pipe(row["common_titles"])))
        st.write("**Industries:** "+", ".join(split_pipe(row["industries"])))
    with t2:
        gap=analyze_skill_gap(st.session_state.skills,row["required_skills"],row["preferred_skills"])
        st.success("You have: "+", ".join(gap["present"]) if gap["present"] else "You have not selected required skills yet.")
        st.warning("Missing: "+", ".join(gap["missing"]) if gap["missing"] else "No required skill gaps.")
        st.info("Recommended: "+", ".join(gap["recommended"]) if gap["recommended"] else "No additional preferred skills identified.")
    with t3:
        cj=jobs[jobs.career==selected]
        metric_row([("Demo job records",len(cj)),("Top city",cj.location.value_counts().index[0] if not cj.empty else "—"),("Avg max salary",f"₹{cj.salary_max_lpa.mean():.1f} LPA" if not cj.empty else "—")])
        if not cj.empty: st.dataframe(cj[["title","company","location","experience","work_mode","salary_min_lpa","salary_max_lpa"]].head(20),use_container_width=True,hide_index=True)
    with t4:
        for p in project_recommendations(selected): st.write(f"**{p[0]}** — {p[1]} • {p[2]} • {p[3]} • Portfolio: {p[4]}")

def job_market():
    st.title("💼 Job Market")
    c1,c2,c3=st.columns(3)
    keyword=c1.text_input("Keyword")
    career=c2.selectbox("Career",["Any"]+sorted(jobs.career.unique()))
    location=c3.selectbox("Location",["Any"]+sorted(jobs.location.unique()))
    c4,c5,c6=st.columns(3)
    skill=c4.selectbox("Skill",["Any"]+sorted(skills_df.skill.unique()))
    experience=c5.selectbox("Experience",["Any"]+sorted(jobs.experience.unique()))
    mode=c6.selectbox("Work mode",["Any"]+sorted(jobs.work_mode.unique()))
    result=filter_jobs(jobs,keyword,career if career!="Any" else None,skill if skill!="Any" else None,location if location!="Any" else None,experience if experience!="Any" else None,work_mode=mode if mode!="Any" else None)
    st.info("Demo/Local Dataset — for demonstration. These records are not claimed to be current vacancies.")
    st.metric("Matching records",len(result))
    if result.empty: st.warning("No matching demo records. Try relaxing a filter."); return
    show=result[["job_id","title","company","location","experience","required_skills","salary_min_lpa","salary_max_lpa","work_mode","source","posted_date"]].copy()
    st.dataframe(show,use_container_width=True,hide_index=True)

def analytics():
    st.title("📊 Market Analytics")
    st.info("All figures on this page are generated from the bundled sample dataset.")
    c1,c2=st.columns(2)
    with c1:
        x=jobs.location.value_counts().head(10).reset_index(); x.columns=["location","jobs"]
        st.plotly_chart(px.bar(x,x="location",y="jobs",title="Jobs by Location"),use_container_width=True)
    with c2:
        x=jobs.domain.value_counts().reset_index(); x.columns=["domain","jobs"]
        st.plotly_chart(px.pie(x,names="domain",values="jobs",title="Jobs by Domain"),use_container_width=True)
    x=jobs.career.value_counts().head(12).reset_index(); x.columns=["career","jobs"]
    st.plotly_chart(px.bar(x,x="career",y="jobs",title="Jobs by Role"),use_container_width=True)
    x=jobs.groupby("location",as_index=False)["salary_max_lpa"].mean().sort_values("salary_max_lpa",ascending=False).head(12)
    st.plotly_chart(px.scatter(x,x="location",y="salary_max_lpa",size="salary_max_lpa",title="Average Demo Salary Ceiling by City"),use_container_width=True)
    demand=careers[["career","demand","growth","future_score"]].melt("career")
    st.plotly_chart(px.treemap(demand,path=["variable","career"],values="value",title="Career Intelligence Overview"),use_container_width=True)

def skill_gap_page():
    st.title("🧩 Skill Gap")
    ranked=get_ranked() if st.session_state.analyzed else careers
    target=st.selectbox("Target career",ranked.career.tolist())
    row=ranked[ranked.career==target].iloc[0]
    gap=analyze_skill_gap(st.session_state.skills,row.required_skills,row.preferred_skills)
    ready=readiness_score(st.session_state.skills,gap,False,row.demand,row.domain_match)
    metric_row([("Job Readiness",f"{ready:.0f}%"),("Required skills",len(split_pipe(row.required_skills))),("You have",len(gap["present"])),("Missing",len(gap["missing"]))])
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Skills You Have")
        for x in gap["present"]: st.success("✓ "+x)
    with c2:
        st.subheader("Skills You Are Missing")
        for x in gap["missing"]: st.error("✗ "+x)
    if gap["missing"]:
        # Skill gap summary
            vals = pd.DataFrame({
                "status": ["Have", "Missing"],
                "count": [len(gap["present"]), len(gap["missing"])]
            })

            st.bar_chart(vals.set_index("status"))
    st.subheader("Job Readiness Breakdown")
    radar=go.Figure(data=go.Scatterpolar(r=[gap["readiness"],ready,row.domain_match,row.experience_match,75],theta=["Technical Skills","Projects/Readiness","Domain Knowledge","Experience","Tools"],fill="toself"))
    radar.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),showlegend=False)
    st.plotly_chart(radar,use_container_width=True)

def salary_page():
    st.title("💰 Salary Insights")
    target=st.selectbox("Career",sorted(salaries.career.unique()))
    df=salaries[salaries.career==target]
    st.info("Estimated market ranges from the bundled demo dataset. Values are not guaranteed.")
    st.dataframe(df[["experience","min_lpa","median_lpa","max_lpa"]],use_container_width=True,hide_index=True)
    st.plotly_chart(px.bar(df,x="experience",y=["min_lpa","median_lpa","max_lpa"],barmode="group",title=f"Estimated Salary by Experience — {target}"),use_container_width=True)
    city=jobs[jobs.career==target].groupby("location",as_index=False).agg(avg_max=("salary_max_lpa","mean"),jobs=("job_id","count")).sort_values("avg_max",ascending=False)
    st.plotly_chart(px.bar(city.head(12),x="location",y="avg_max",title="Demo Salary Ceiling by City"),use_container_width=True)

def companies_page():
    st.title("🏢 Companies")
    q=st.text_input("Search company")
    df=companies
    if q: df=df[df.company.str.contains(q,case=False,na=False)]
    for _,r in df.iterrows():
        with st.expander(r.company):
            st.write("**Industry:**",r.industry)
            st.write("**Locations:**",", ".join(split_pipe(r.locations)))
            st.write("**Typical roles:**",", ".join(split_pipe(r.typical_roles)))
            st.write("**Popular skills:**",", ".join(split_pipe(r.popular_skills)))
            st.write("**Experience:**",", ".join(split_pipe(r.experience_levels)))
            st.write("**Work modes:**",", ".join(split_pipe(r.work_modes)))
            st.caption("Company career information only; this does not assert current vacancies.")

def compare():
    st.title("⚖️ Compare Careers")
    options=sorted(careers.career.tolist())
    selected=st.multiselect("Select up to 4 careers",options,default=options[:min(4,len(options))])
    selected=selected[:4]
    if not selected: st.info("Select at least one career."); return
    df=careers[careers.career.isin(selected)].copy()
    if st.session_state.analyzed:
        ranked=get_ranked()[["career","overall_match"]]; df=df.merge(ranked,on="career",how="left")
    else: df["overall_match"]=np.nan
    cols=["career","overall_match","demand","growth","salary_potential","future_score","competition","entry_difficulty"]
    st.dataframe(df[cols].rename(columns={"overall_match":"Match %","salary_potential":"Salary Potential","future_score":"Future Score"}),use_container_width=True,hide_index=True)
    plot=df.melt(id_vars="career",value_vars=["demand","growth","future_score","salary_potential"],var_name="metric",value_name="score")
    st.plotly_chart(px.bar(plot,x="career",y="score",color="metric",barmode="group",title="Career Comparison"),use_container_width=True)

def roadmap():
    st.title("🛣️ Career Roadmap")
    ranked=get_ranked() if st.session_state.analyzed else careers
    target=st.selectbox("Target career",ranked.career.tolist())
    row=ranked[ranked.career==target].iloc[0]
    gap=analyze_skill_gap(st.session_state.skills,row.required_skills,row.preferred_skills)
    plan=roadmap_for(target,gap["missing"])
    st.info(f"Roadmap is personalized around the selected career and current missing skills. Estimated duration is indicative.")
    for i,item in enumerate(plan,1):
        st.markdown(f"### Phase {i} — {item}")
        st.progress(max(5,100-int((i-1)*8)))
        st.write("Priority:", "High" if i<=3 else "Medium")
        st.write("Estimated learning time:", "1–3 weeks")
    st.subheader("Recommended portfolio projects")
    for p in project_recommendations(target): st.write(f"• **{p[0]}** — {p[2]} — {p[3]} — {p[4]} portfolio value")

def resume_analyzer():
    st.title("📄 Resume Analyzer")
    ranked=get_ranked() if st.session_state.analyzed else careers
    target=st.selectbox("Target career",ranked.career.tolist())
    row=ranked[ranked.career==target].iloc[0]
    file=st.file_uploader("Upload resume PDF",type=["pdf"])
    if not file:
        st.info("Upload a PDF resume to extract text and compare detectable skill keywords.")
        return
    if file.size > 5*1024*1024:
        st.error("File exceeds the 5 MB limit."); return
    try:
        from pypdf import PdfReader
        reader=PdfReader(file)
        text="\n".join(page.extract_text() or "" for page in reader.pages)
        text_l=text.lower()
        catalog=skills_df.skill.tolist()
        detected=[s for s in catalog if s.lower() in text_l]
        required=split_pipe(row.required_skills)
        missing=[s for s in required if s.lower() not in text_l]
        coverage=round(100*len([s for s in required if s.lower() in text_l])/len(required),1) if required else 0
        st.success(f"Detected {len(detected)} catalog skills.")
        metric_row([("Career match",f"{coverage:.0f}%"),("ATS-style keyword coverage",f"{coverage:.0f}%"),("Detected skills",len(detected)),("Missing target keywords",len(missing))])
        st.subheader("Detected skills")
        st.write(", ".join(detected) if detected else "No catalog skills detected.")
        st.subheader("Recommended improvements")
        for s in missing[:10]: st.warning(f"Consider adding evidence for: {s}")
        st.caption("This is an ATS-style keyword coverage indicator, not a reproduction of any real ATS scoring system.")
    except Exception as e:
        st.error(f"Could not process this PDF safely: {e}")

def intelligence():
    st.title("📰 Job Market Intelligence")
    st.info("No live news API is configured in the basic offline version. Current news is therefore not invented.")
    st.subheader("Bundled market themes")
    themes=["AI","Machine Learning","Generative AI","Cloud","Cybersecurity","Data Science","Software Engineering","Semiconductors","Startups","GCC hiring","Fresher hiring"]
    for t in themes:
        st.write("•",t)
    st.markdown("### Historical demo hiring index")
    period=st.selectbox("Period",["7 days","30 days","90 days","1 year","3 years"],index=3)
    df=trends.copy(); df["date"]=pd.to_datetime(df["date"])
    if period=="7 days": start=df.date.max()-pd.Timedelta(days=7)
    elif period=="30 days": start=df.date.max()-pd.Timedelta(days=30)
    elif period=="90 days": start=df.date.max()-pd.Timedelta(days=90)
    elif period=="1 year": start=df.date.max()-pd.Timedelta(days=365)
    else: start=df.date.min()
    st.plotly_chart(px.line(df[df.date>=start],x="date",y="index",color="category",title="Demo Hiring Trend Index"),use_container_width=True)
    st.caption("Sample historical index — for demonstration, not current market measurement.")

def settings():
    st.title("⚙️ Settings")
    st.subheader("Data mode")
    st.write("**Basic mode:** offline CSV + SQLite + Python analytics. No paid API keys are required.")
    st.write("**Live data:** can be added through an approved JobDataProvider/RSS/public API integration. Do not bypass authentication, CAPTCHA, robots.txt or website terms.")
    st.subheader("Optional AI mode")
    st.write("API credentials, if later added, should be supplied through `st.secrets` or environment variables. Never hard-code keys.")
    if st.button("Reset profile"):
        for k,v in defaults.items(): st.session_state[k]=v
        st.rerun()
    st.subheader("Database")
    st.write(str(DB_PATH))
    st.success("SQLite database is initialized automatically when the app starts.")

# Routing
routes={
"🏠 Dashboard":dashboard,"👤 My Profile":profile_form,"🎯 Career Explorer":explorer,"💼 Job Market":job_market,
"📊 Market Analytics":analytics,"🧩 Skill Gap":skill_gap_page,"💰 Salary Insights":salary_page,"🏢 Companies":companies_page,
"⚖️ Compare Careers":compare,"🛣️ Career Roadmap":roadmap,"📄 Resume Analyzer":resume_analyzer,
"📰 Job Market Intelligence":intelligence,"⚙️ Settings":settings
}
routes[page]()
