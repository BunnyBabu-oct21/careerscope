def roadmap_for(career, missing):
    plans = {
        "Machine Learning Engineer":["Advanced Python","Statistics","Deep Learning","PyTorch","Docker","Cloud","MLOps","Production ML Project","Resume + Interview preparation"],
        "AI Engineer":["Advanced Python","Machine Learning","Deep Learning","PyTorch","Generative AI","API Development","Docker","Production AI Project"],
        "Data Scientist":["Statistics","Advanced SQL","Pandas","Machine Learning","Experimentation","Visualization","Portfolio Projects","Interview preparation"],
        "Data Analyst":["Advanced SQL","Excel","Power BI","Statistics","Python/Pandas","Dashboard Project","Portfolio + Resume"],
        "Generative AI Engineer":["LLM fundamentals","Transformers","RAG","Vector Databases","Evaluation","FastAPI","Docker","Production GenAI Project"],
        "LLM Engineer":["Transformers","Hugging Face","RAG","Vector Databases","LLM Evaluation","FastAPI","Docker","LLM Portfolio Project"],
        "AI Agent Engineer":["LLMs","Tool Calling","RAG","Agent Workflows","FastAPI","Docker","Evaluation","Production Agent"],
        "Data Engineer":["Advanced SQL","ETL","Airflow","Spark","Data Warehousing","Cloud","Data Pipeline Project"],
        "Cloud Engineer":["Linux","Networking","AWS/Azure","Docker","Terraform","Kubernetes","Cloud Project"],
        "DevOps Engineer":["Linux","Git","CI/CD","Docker","Kubernetes","Terraform","Monitoring","Production Deployment"],
    }
    base=plans.get(career, ["Strengthen core skills","Learn missing skills","Build 2 portfolio projects","Deploy a project","Resume optimization","Interview preparation"])
    missing_l={m.lower() for m in missing}
    ordered=[]
    for item in base:
        if item.lower() in missing_l or not missing:
            ordered.append(item)
    ordered += [x for x in base if x not in ordered]
    return ordered[:9]

def project_recommendations(career):
    common=[
        ("Portfolio Dashboard","Medium","Python, SQL, Plotly, Streamlit","1–2 weeks","High"),
        ("End-to-End Production Project","Hard","Git, Docker, API, deployment","3–5 weeks","Very High"),
        ("Resume + Interview Portfolio","Easy","Documentation, GitHub, communication","3–5 days","Medium"),
    ]
    specific={
        "Machine Learning Engineer":[("House Price Prediction","Easy","Python, Pandas, Scikit-learn","3–5 days","Medium"),("Customer Churn Prediction","Medium","ML, feature engineering, evaluation","1 week","High"),("Recommendation System","Hard","ML, embeddings, evaluation","2 weeks","Very High"),("Fraud Detection","Hard","ML, imbalanced data, deployment","2 weeks","Very High"),("Image Classification","Medium","PyTorch/TensorFlow, CV","1–2 weeks","High"),("RAG Application","Medium","LLMs, embeddings, vector DB","1 week","Very High"),("AI Agent","Hard","LLMs, tools, APIs, evaluation","1–2 weeks","Very High")],
        "Data Analyst":[("Sales Analytics Dashboard","Easy","SQL, Excel, Power BI","3–5 days","High"),("Customer Segmentation","Medium","Python, statistics, visualization","1 week","High"),("Business KPI Dashboard","Medium","SQL, Power BI, storytelling","1 week","Very High")],
    }
    return specific.get(career, common)
