import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
import pandas as pd
from datetime import datetime

//
st.set_page_config(
    page_title="AI-Powered ATS Resume Analyzer with RAG",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
    }
    .main .block-container {
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
        padding-top: 2rem;
    }
    
    /* Main styling */
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #60a5fa !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 0 0 20px rgba(96, 165, 250, 0.3);
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #94a3b8 !important;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Score card styling */
    .score-card {
        background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white !important;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.3);
        border: 1px solid #334155;
    }
    .ats-score {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: #fbbf24 !important;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
    }
    
    /* Skill tags */
    .skill-tag {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: none;
        border: 1px solid transparent;
    }
    .skill-matched {
        background-color: #059669;
        color: #ecfdf5 !important;
        border: 1px solid #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
    }
    .skill-missing {
        background-color: #dc2626;
        color: #fef2f2 !important;
        border: 1px solid #ef4444;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }
    .skill-trending {
        background-color: #d97706;
        color: #fefce8 !important;
        border: 1px solid #f59e0b;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
    }
    
    /* Cards and sections */
    .recommendation-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #60a5fa;
        color: #e2e8f0 !important;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .critical-issue {
        background-color: #450a0a;
        border-left: 4px solid #ef4444;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 6px;
        color: #fca5a5 !important;
        font-weight: 600;
        border: 1px solid #7f1d1d;
    }
    .recommendation {
        background-color: #0c4a6e;
        border-left: 4px solid #0ea5e9;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 6px;
        color: #bae6fd !important;
        font-weight: 500;
        border: 1px solid #075985;
    }
    
    /* Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f1f5f9 !important;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #60a5fa;
        padding-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
    }
    .subsection-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #cbd5e1 !important;
        margin: 1.5rem 0 0.8rem 0;
        border-left: 4px solid #60a5fa;
        padding-left: 1rem;
        background: #1e293b;
        padding: 0.8rem 1rem;
        border-radius: 6px;
    }
    
    /* Bullet improvements */
    .original-bullet {
        background-color: #451a03;
        border: 2px solid #d97706;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        color: #fed7aa !important;
        font-size: 0.95rem;
        line-height: 1.6;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2);
    }
    .improved-bullet {
        background-color: #064e3b;
        border: 2px solid #059669;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        color: #a7f3d0 !important;
        font-size: 0.95rem;
        line-height: 1.6;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
    }
    .improvement-highlight {
        background-color: #0c4a6e;
        border-left: 4px solid #0ea5e9;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        color: #bae6fd !important;
        font-weight: 500;
        border: 1px solid #075985;
    }
    
    /* Override Streamlit defaults for dark theme */
    .stMarkdown p {
        color: #e2e8f0 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f1f5f9 !important;
    }
    .stMarkdown strong {
        color: #f1f5f9 !important;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e293b !important;
    }
    .sidebar .sidebar-content {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        font-weight: 600;
        border: 1px solid #334155;
    }
    .streamlit-expanderContent {
        background-color: #0f172a !important;
        border: 1px solid #334155;
        border-top: none;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #60a5fa;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    [data-testid="metric-container"] > div {
        color: #f1f5f9 !important;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #60a5fa !important;
        font-weight: 700;
    }
    
    /* Text visibility fixes */
    div[data-testid="stMarkdownContainer"] p {
        color: #e2e8f0 !important;
    }
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: #f1f5f9 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%) !important;
        color: white !important;
        border: 1px solid #60a5fa !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background-color: #1e293b !important;
        border: 2px dashed #60a5fa !important;
        border-radius: 8px;
        color: #e2e8f0 !important;
    }
    
    /* Text input styling */
    .stTextArea > div > div > textarea {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        color: #1f2937 !important;
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid #60a5fa !important;
    }
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid #10b981 !important;
        color: #10b981 !important;
    }
    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid #f59e0b !important;
        color: #f59e0b !important;
    }
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid #60a5fa !important;
        color: #60a5fa !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b !important;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        background-color: #0f172a !important;
    }
    
    /* Plotly chart background */
    .js-plotly-plot {
        background-color: #1e293b !important;
        border-radius: 8px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)


def call_api(endpoint: str, files=None, data=None, json_data=None) -> Dict[str, Any]:
    try:
        base_url = "http://127.0.0.1:8000"
        
        if files:
            response = requests.post(f"{base_url}{endpoint}", files=files, data=data, timeout=120)
        elif json_data:
            response = requests.post(f"{base_url}{endpoint}", json=json_data, timeout=60)
        else:
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to API. Make sure the FastAPI server is running on localhost:8000")
        st.info("Run: `uvicorn main:app --reload` in your terminal")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def display_ats_scores(ats_scores: Dict[str, float]):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        score = ats_scores["overall_score"]
        color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
        
        st.markdown(f"""
        <div class="score-card">
            <h3>ATS Score</h3>
            <div class="ats-score" style="color: {color}">{score}%</div>
            <p>Overall Compatibility</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        scores_data = {
            "Metric": ["Keywords", "Format", "Experience", "Education", "Skills"],
            "Score": [
                ats_scores["keyword_score"],
                ats_scores["format_score"], 
                ats_scores["experience_score"],
                ats_scores["education_score"],
                ats_scores["skills_score"]
            ]
        }
        
        fig = go.Figure(data=go.Bar(
            x=scores_data["Score"],
            y=scores_data["Metric"],
            orientation='h',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        ))
        
        fig.update_layout(
            title="ATS Score Breakdown",
            title_font_color="#f1f5f9",
            xaxis_title="Score (%)",
            xaxis_title_font_color="#cbd5e1",
            yaxis_title_font_color="#cbd5e1",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor="#1e293b",
            paper_bgcolor="#1e293b",
            font_color="#e2e8f0"
        )
        
        st.plotly_chart(fig, width='stretch')


def display_skills_analysis(skills_data: Dict[str, Any]):
    resume_skills = skills_data["resume_skills"]
    jd_skills = skills_data["jd_skills"]
    missing_skills = skills_data["missing_skills"]
    matched_skills = skills_data["matched_skills"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Skills Found", len(matched_skills))
    with col2:
        st.metric("Skills Missing", len(missing_skills))
    with col3:
        st.metric("Match Rate", f"{len(matched_skills)/(len(matched_skills)+len(missing_skills))*100:.1f}%")
    with col4:
        st.metric("Gap Percentage", f"{skills_data['skills_gap_percentage']}%")
    
    st.markdown('<div class="subsection-header">Skills by Category</div>', unsafe_allow_html=True)
    
    for category, skills in resume_skills.items():
        if skills:
            st.write(f"**{category.replace('_', ' ').title()}:**")
            skills_html = ""
            for skill in skills:
                if skill in matched_skills:
                    skills_html += f'<span class="skill-tag skill-matched">✓ {skill}</span>'
                else:
                    skills_html += f'<span class="skill-tag skill-trending">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
    
    if missing_skills:
        st.markdown('<div class="subsection-header">Missing Critical Skills</div>', unsafe_allow_html=True)
        missing_html = ""
        for skill in missing_skills[:15]:
            missing_html += f'<span class="skill-tag skill-missing">+ {skill}</span>'
        st.markdown(missing_html, unsafe_allow_html=True)


def display_bullet_improvements(improvements: list):
    st.markdown('<div class="section-header">AI-Enhanced Resume Bullets</div>', unsafe_allow_html=True)
    
    if not improvements or len(improvements) == 0:
        st.info("No bullet points found for improvement. Try uploading a resume with more detailed experience bullets.")
        return
    
    st.success(f"Found {len(improvements)} bullet points to enhance")
    
    for i, bullet_data in enumerate(improvements):
        if not isinstance(bullet_data, dict):
            st.error(f"Invalid bullet data format for improvement {i+1}")
            continue
            
        with st.expander(f"Bullet Enhancement {i+1}", expanded=i < 3):
            
            original = bullet_data.get("original", "")
            improved = bullet_data.get("improved", "")
            
            if not original:
                original = "No original text available"
            if not improved:
                improved = "No improvement generated"
            
            original = str(original).strip()
            improved = str(improved).strip()
            
            st.markdown("### Before vs After Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Version:**")
                st.markdown(f'<div class="original-bullet">{original}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Enhanced Version:**")
                st.markdown(f'<div class="improved-bullet">{improved}</div>', unsafe_allow_html=True)
            
            if original != improved and improved != "No improvement generated":
                st.markdown("### Key Improvements Made:")
                
                improvements_made = []
                
                if len(improved) > len(original):
                    improvements_made.append("Added more detailed content")
                
                if any(word in improved.lower() for word in ['%', 'increased', 'reduced', 'improved', 'achieved']):
                    improvements_made.append("Added quantifiable metrics")
                
                if any(word in improved.lower() for word in ['developed', 'implemented', 'architected', 'optimized', 'engineered']):
                    improvements_made.append("Enhanced with strong action verbs")
                
                if any(word in improved.lower() for word in ['docker', 'aws', 'kubernetes', 'typescript', 'react']):
                    improvements_made.append("Integrated relevant technical skills")
                
                if not improvements_made:
                    improvements_made.append("Professional language enhancement")
                
                for improvement in improvements_made:
                    st.markdown(f'<div class="improvement-highlight">• {improvement}</div>', unsafe_allow_html=True)
            
            if "similar_examples" in bullet_data and bullet_data["similar_examples"]:
                with st.expander("Reference Examples Used"):
                    for j, example in enumerate(bullet_data["similar_examples"][:2]):
                        st.markdown(f"**Example {j+1}:** {str(example)[:150]}...")
            
            if "error" in bullet_data:
                st.warning(f"Note: {bullet_data['error']}")
            
            st.markdown("---")


def display_recommendations_and_insights(result: Dict[str, Any]):
    if result.get("critical_issues") and len(result["critical_issues"]) > 0:
        st.markdown('<div class="subsection-header">Critical Issues</div>', unsafe_allow_html=True)
        for issue in result["critical_issues"]:
            st.markdown(f'<div class="critical-issue"><strong>Warning:</strong> {issue}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown('<div class="subsection-header">ATS Optimization Recommendations</div>', unsafe_allow_html=True)
    
    if result.get("ats_recommendations") and len(result["ats_recommendations"]) > 0:
        for rec in result["ats_recommendations"]:
            st.markdown(f'<div class="recommendation">{rec}</div>', 
                       unsafe_allow_html=True)
    else:
        default_recommendations = [
            "Use strong action verbs at the beginning of each bullet point (Developed, Implemented, Architected)",
            "Include quantifiable achievements and metrics where possible (percentages, numbers, time saved)",
            "Incorporate relevant keywords from the job description naturally throughout your resume",
            "Ensure consistent formatting throughout your resume with proper spacing and alignment",
            "Use standard section headers that ATS systems recognize (Experience, Education, Skills, Certifications)"
        ]
        for rec in default_recommendations:
            st.markdown(f'<div class="recommendation">{rec}</div>', unsafe_allow_html=True)
    
    if result.get("role_recommendations") and len(result["role_recommendations"]) > 0:
        st.markdown('<div class="subsection-header">Role-Specific Advice</div>', unsafe_allow_html=True)
        for rec in result["role_recommendations"]:
            st.markdown(f'<div class="recommendation-card">{rec}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="subsection-header">Career Growth Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Next Level Skills")
        if result.get("career_insights") and result["career_insights"].get("next_level_skills"):
            next_skills = result["career_insights"]["next_level_skills"]
            for skill in next_skills:
                st.markdown(f'<div class="recommendation-card">{skill}</div>', unsafe_allow_html=True)
        else:
            default_skills = ["System Design & Architecture", "Technical Leadership", "Cross-functional Collaboration"]
            for skill in default_skills:
                st.markdown(f'<div class="recommendation-card">{skill}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Certification Suggestions")
        if result.get("career_insights") and result["career_insights"].get("certification_suggestions"):
            certs = result["career_insights"]["certification_suggestions"]
            for cert in certs:
                st.markdown(f'<div class="recommendation-card">{cert}</div>', unsafe_allow_html=True)
        else:
            default_certs = ["AWS Certified Solutions Architect", "Kubernetes Administrator (CKA)", "Certified Scrum Master (CSM)"]
            for cert in default_certs:
                st.markdown(f'<div class="recommendation-card">{cert}</div>', unsafe_allow_html=True)


def display_analytics_dashboard():
    st.markdown('<div class="section-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    
    analytics = call_api("/api/analytics/summary")
    
    if analytics and analytics["total_analyses"] > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Analyses", analytics["total_analyses"])
        with col2:
            st.metric("Avg ATS Score", f"{analytics['average_ats_score']:.1f}%")
        with col3:
            st.metric("Avg Similarity", f"{analytics['average_similarity_score']:.1f}%")
        
        if analytics.get("common_issues"):
            st.markdown('<div class="subsection-header">Common Issues Identified</div>', unsafe_allow_html=True)
            issues_df = pd.DataFrame({
                "Issue": analytics["common_issues"],
                "Frequency": [85, 72, 68]
            })
            
            fig = px.bar(issues_df, x="Frequency", y="Issue", orientation='h')
            fig.update_layout(
                plot_bgcolor="#1e293b",
                paper_bgcolor="#1e293b",
                font_color="#e2e8f0",
                title_font_color="#f1f5f9"
            )
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("No analytics data available yet. Analyze some resumes to see insights!")


def main():
    st.markdown('<h1 class="main-header">AI-Powered ATS Resume Analyzer with RAG</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-powered resume analysis using RAG architecture and FAISS vector retrieval</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Analysis Settings")
        
        target_role = st.selectbox(
            "Target Role",
            ["Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager", 
             "ML Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer"]
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Junior", "Mid", "Senior", "Principal", "Executive"]
        )
        
        st.markdown("---")
        
        st.header("Features")
        st.markdown("""
        **ATS Scoring** - Real ATS compatibility analysis  
        **AI Bullet Enhancement** - RAG-powered improvements  
        **Skills Gap Analysis** - Identify missing skills  
        **Career Insights** - Growth recommendations  
        **Real-time Suggestions** - Instant feedback  
        """)
        
        st.markdown("---")
        
        # Quick skill suggestions
        if st.button("Get Skill Suggestions"):
            suggestions = call_api(f"/api/skill-suggestions/{target_role}?level={experience_level}")
            if suggestions:
                st.subheader("Recommended Skills")
                for skill in suggestions["recommended_skills"][:5]:
                    st.markdown(f"• {skill}")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Resume Analysis", "Analytics", "About"])
    
    with tab1:
        # File upload and job description
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="section-header">Upload Resume</div>', unsafe_allow_html=True)
            resume_file = st.file_uploader(
                "Choose your resume file",
                type=['pdf', 'docx'],
                help="Upload your resume in PDF or DOCX format"
            )
            
            if resume_file:
                st.success(f"File uploaded: {resume_file.name}")
        
        with col2:
            st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)
            job_description = st.text_area(
                "Paste the job description here",
                height=200,
                help="Copy and paste the complete job description",
                placeholder="Paste the job description you want to match against..."
            )
        
        # Analysis button
        if st.button("Analyze Resume", type="primary", width='stretch'):
            if resume_file is None:
                st.error("Please upload a resume file.")
                return
            
            if not job_description.strip():
                st.error("Please enter a job description.")
                return
            
            # Show loading spinner
            with st.spinner("AI is analyzing your resume... This may take a few moments."):
                # Call comprehensive API
                files = {"resume": resume_file}
                data = {
                    "job_description": job_description,
                    "target_role": target_role,
                    "experience_level": experience_level
                }
                
                result = call_api("/api/analyze", files=files, data=data)
            
            if result:
                st.success("Analysis completed successfully")
                
                # Display results in organized sections
                
                # 1. ATS Scores
                st.markdown('<div class="section-header">ATS Compatibility Analysis</div>', unsafe_allow_html=True)
                display_ats_scores(result["ats_score"])
                
                # 2. Skills Analysis
                st.markdown('<div class="section-header">Skills Analysis</div>', unsafe_allow_html=True)
                display_skills_analysis(result["skills_analysis"])
                
                # 3. Bullet Improvements
                display_bullet_improvements(result["bullet_improvements"])
                
                # 4. Recommendations
                st.markdown('<div class="section-header">Professional Recommendations</div>', unsafe_allow_html=True)
                display_recommendations_and_insights(result)
                
                # 5. Summary metrics
                st.markdown('<div class="section-header">Analysis Summary</div>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Overall Match", f"{result['similarity_score']}%")
                with col2:
                    st.metric("ATS Score", f"{result['ats_score']['overall_score']}%")
                with col3:
                    st.metric("Words Analyzed", result["resume_stats"]["word_count"])
                with col4:
                    st.metric("Bullets Enhanced", result["resume_stats"]["bullets_improved"])
                
                # Next steps
                st.info("**Next Steps:** Use the improved bullet points to update your resume, add missing skills, and address the recommendations above.")
    
    with tab2:
        display_analytics_dashboard()
    
    with tab3:
        st.markdown('<div class="section-header">About AI-Powered ATS Resume Analyzer with RAG</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### **AI-Powered ATS Resume Analysis**
        
        This application uses advanced AI and machine learning to provide comprehensive resume analysis:
        
        **AI-Powered Features:**
        - **RAG (Retrieval-Augmented Generation)** for intelligent bullet improvements
        - **FAISS Vector Database** for semantic similarity matching
        - **Advanced NLP** for skill extraction and text analysis
        - **Real ATS Scoring** mimicking actual applicant tracking systems
        
        **Analysis Components:**
        - **Keyword Matching** - Alignment with job description terms
        - **Skills Gap Analysis** - Identification of missing technical skills
        - **Format Optimization** - ATS-friendly formatting recommendations
        - **Experience Relevance** - Career level and experience assessment
        - **Career Insights** - Growth and development suggestions
        
        **Technology Stack:**
        - **Backend:** FastAPI with Python
        - **AI/ML:** LangChain, Sentence Transformers, FAISS
        - **Frontend:** Streamlit with interactive visualizations
        - **NLP:** spaCy for text processing
        
        **Professional Use Cases:**
        - Job application optimization
        - Career transition planning
        - Skills development guidance
        - ATS compatibility testing
        - Resume improvement recommendations
        
        ---
        
        **Built using cutting-edge AI technology**
        """)


if __name__ == "__main__":
    main()
