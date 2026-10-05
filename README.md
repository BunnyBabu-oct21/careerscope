# CareerScope AI

CareerScope AI is a professional Streamlit career-intelligence application for students, freshers and job seekers. It matches a user's education, skills, domains and experience to career profiles, analyzes skill gaps, estimates job readiness, explores demo job-market data, compares careers, and builds a personalized roadmap.

## Important data honesty rule

The bundled `data/` files are **sample/demo data**. They are not claimed to be current vacancies, current salary statistics, or current news. The app explicitly labels demo data and does not fabricate live job counts.

## Features

- Profile and multi-skill/domain selection
- Weighted career matching
- Top career recommendations
- Required vs missing skill analysis
- Job readiness score and Plotly radar
- Demo job search with filters
- Market analytics and interactive charts
- Salary estimates by experience and city
- Company information separated from live vacancies
- Career comparison
- Personalized roadmap
- Portfolio project recommendations
- Resume PDF keyword/skill analyzer
- Historical demo hiring trend charts
- SQLite initialization
- Offline operation without paid APIs
- Optional architecture for approved live providers
- Defensive error handling and empty states

## Architecture

```text
careerscope_ai/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── careers.csv
│   ├── skills.csv
│   ├── companies.csv
│   ├── jobs.csv
│   ├── salaries.csv
│   └── career_trends.csv
├── database/
│   └── careerscope.db       # created automatically
└── utils/
    ├── career_match.py
    ├── skill_gap.py
    ├── market_analysis.py
    ├── recommendations.py
    └── data_loader.py
```

## Installation

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux/Mac

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Database

SQLite is initialized automatically at:

`database/careerscope.db`

Tables include:

- users
- skills
- careers
- career_skills
- companies
- jobs
- salaries
- career_trends
- user_profiles
- user_skills

## How career matching works

The application uses:

`Overall Match = 0.55 × Skill Match + 0.20 × Domain Match + 0.10 × Education Match + 0.15 × Experience Match`

The result is normalized to 0–100.

Labels:
- 80–100: Excellent Match
- 65–79: Strong Match
- 50–64: Moderate Match
- Below 50: Low Match

## How skill gap works

The target career's required skills are compared against the user's selected skills. The app shows:

- Skills you have
- Skills you are missing
- Critical skills
- Recommended/preferred skills
- Job readiness indicator

## Adding careers

Edit `data/careers.csv`. Required columns:

`career, description, required_skills, preferred_skills, domain, demand, growth, salary_potential, competition, future_score, common_titles, education, entry_difficulty, industries`

Use `|` to separate multiple skills/titles.

## Adding skills

Edit `data/skills.csv` with:

`skill, category`

## Adding jobs

Edit `data/jobs.csv`. Required columns include:

`job_id,title,career,company,location,experience,required_skills,salary_min_lpa,salary_max_lpa,work_mode,source,source_url,posted_date,is_demo,domain`

If a real job source is added, preserve its legitimate URL and source name.

## Adding live data

Use an approved provider such as:
- public/authorized API
- RSS feed
- company career pages where permitted
- user-provided CSV

Do not:
- bypass CAPTCHA
- bypass authentication
- ignore robots.txt
- violate website terms
- claim demo data is live

A future implementation can introduce a `JobDataProvider` interface with `fetch_jobs()` and `source_name` methods.

## Optional AI mode

The basic version does not need OpenAI, Gemini or Claude keys. If optional AI features are later added, use Streamlit secrets or environment variables. Never hard-code API keys.

## Resume analyzer

The app accepts PDF resumes up to 5 MB, extracts text with `pypdf`, and checks catalog skill keywords against the selected career. Its keyword coverage is an ATS-style indicator only and does not reproduce any real ATS.

## Sample dataset

The project includes:
- 30 career profiles
- 100+ skill entries
- 30 companies
- 220 demo job records
- salary ranges by experience
- historical demo hiring indices

## Streamlit deployment

Upload the project to GitHub and deploy with Streamlit Community Cloud or another Streamlit-compatible host. Make sure `requirements.txt` is in the repository root.

## Mobile

The interface is designed to remain usable in Android browsers, tablets and desktops. Large tables are kept limited and most detailed information is placed in tabs/expanders.

## Limitations

- Bundled jobs and market trends are demo data.
- Salary values are estimates derived from the bundled dataset.
- No live vacancy or news claim is made in offline mode.
- Resume keyword detection is not semantic ATS scoring.
- Future score is an analytical indicator, not a guaranteed prediction.

## Future improvements

- Authorized live job providers
- User authentication
- Saved profiles
- More detailed city-level salary datasets
- Embedding-based semantic resume matching
- Interview preparation
- Application tracking
- Employer-side analytics
- Scheduled market refresh jobs
