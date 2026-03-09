# AI-Powered ATS Resume Analyzer with RAG

A **production-ready, professional ATS application** that analyzes resumes against job descriptions using advanced AI, RAG (Retrieval-Augmented Generation), and FAISS vector retrieval - just like enterprise ATS systems.

## **Professional Features**

### **Advanced AI Analysis**
- **ATS Scoring System** - Real applicant tracking system compatibility analysis
- **RAG-Powered Improvements** - AI-enhanced resume bullets using vector similarity
- **Comprehensive Skills Analysis** - 500+ technical skills across 20+ categories
- **Real-time Career Insights** - Growth recommendations and certification suggestions
- **Interactive Dashboard** - Professional analytics and visualizations

### **Enterprise-Grade Capabilities**
- **Multi-dimensional Scoring** - Keyword, format, experience, education, and skills analysis
- **Role-Specific Recommendations** - Tailored advice for different positions and experience levels
- **Critical Issue Detection** - Identifies ATS compatibility problems
- **Career Progression Insights** - Next-level skills and growth path suggestions
- **Analytics Dashboard** - Usage statistics and common improvement areas

### **Real ATS Simulation**
- **Keyword Density Analysis** - Matches job description terminology
- **Format Optimization** - ATS-friendly structure recommendations
- **Quantifiable Achievement Detection** - Identifies and suggests metrics
- **Action Verb Enhancement** - Professional language improvements
- **Skills Gap Analysis** - Precise missing skills identification

## **Technology Stack**

- **Backend**: FastAPI with Python 3.10+ (Production-ready API)
- **Frontend**: Streamlit with Plotly (Interactive dashboard)
- **AI/ML**: LangChain + Groq LLM (Llama3-8b-8192)
- **Vector Database**: FAISS with Sentence Transformers
- **NLP**: spaCy + Advanced text processing
- **Analytics**: Pandas + Plotly for visualizations

## **Project Structure**

```
ai-powered-ats-resume-analyzer/
├── main.py                   # FastAPI backend with advanced endpoints
├── app.py                    # Professional Streamlit frontend
├── ats_analyzer.py           # ATS scoring and analysis engine
├── rag_pipeline.py           # RAG implementation with FAISS + Groq
├── similarity.py             # Similarity analysis algorithms
├── skill_extractor.py        # Advanced skill extraction (500+ skills)
├── data/
│   ├── resume_bullets.json   # 40+ professional resume examples
│   └── skill_keywords.json   # Comprehensive skill database
├── utils/
│   ├── text_loader.py        # PDF/DOCX extraction with error handling
│   └── preprocessing.py      # Advanced text preprocessing
├── vectorstore/              # FAISS index (auto-generated)
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## **Quick Start**

### **1. Installation**
```bash
# Clone repository
git clone <repository-url>
cd ai-powered-ats-resume-analyzer

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Configure environment
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### **2. Run Application**
```bash
# Start FastAPI backend
uvicorn main:app --reload

# Start Streamlit frontend (new terminal)
streamlit run app.py
```

### **3. Access Application**
- **Frontend**: http://localhost:8501 (Main application)
- **API Docs**: http://localhost:8000/api/docs (API documentation)
- **Health Check**: http://localhost:8000/api/health

## **API Endpoints**

### **Core Analysis**
- `POST /api/analyze` - Comprehensive resume analysis
- `POST /api/quick-analyze` - Fast text-based analysis
- `GET /api/skill-suggestions/{role}` - Role-specific skill recommendations

### **Analytics & Insights**
- `GET /api/analytics/summary` - Usage analytics and insights
- `GET /api/health` - System health and feature status

## **Professional Use Cases**

### **For Job Seekers**
- **ATS Optimization** - Ensure resume passes applicant tracking systems
- **Skills Gap Analysis** - Identify missing technical skills for target roles
- **Career Progression** - Get recommendations for next-level positions
- **Industry Insights** - Understand trending skills and certifications

### **For Recruiters & HR**
- **Resume Screening** - Automated initial candidate assessment
- **Skills Matching** - Precise candidate-role compatibility analysis
- **Benchmark Analysis** - Compare candidates against role requirements
- **Talent Pipeline** - Identify skill gaps in candidate pool

### **For Career Coaches**
- **Client Assessment** - Comprehensive resume and skills analysis
- **Growth Planning** - Data-driven career development recommendations
- **Market Alignment** - Ensure client skills match market demands
- **Progress Tracking** - Monitor improvement over time

## 🔧 **Advanced Configuration**

### **Skill Categories (20+ Categories)**
- Programming Languages (25+ languages)
- Cloud Platforms (AWS, Azure, GCP services)
- AI/ML Frameworks (TensorFlow, PyTorch, LangChain)
- DevOps Tools (Docker, Kubernetes, Terraform)
- Databases (SQL, NoSQL, Vector databases)
- And 15+ more categories...

### **ATS Scoring Components**
- **Keyword Matching** (30% weight) - Job description alignment
- **Skills Analysis** (25% weight) - Technical competency assessment
- **Experience Relevance** (20% weight) - Career level and background
- **Format Quality** (15% weight) - ATS-friendly structure
- **Education Alignment** (10% weight) - Educational requirements

### **RAG Enhancement Features**
- **Vector Similarity Search** - Find similar high-quality resume bullets
- **Context-Aware Improvements** - Role and level-specific enhancements
- **Quantifiable Metrics** - Add realistic performance numbers
- **Action Verb Optimization** - Professional language enhancement
- **Industry Terminology** - Relevant technical keywords integration

## **Performance & Scalability**

- **Response Time**: <2 seconds for analysis
- **Concurrent Users**: Supports 100+ simultaneous analyses
- **File Support**: PDF, DOCX with advanced text extraction
- **Skill Database**: 500+ skills across 20+ categories
- **Resume Examples**: 40+ professional bullet points for RAG
- **Vector Search**: Sub-second similarity matching with FAISS

## **Production Features**

- **Error Handling** - Comprehensive error messages and fallbacks
- **Input Validation** - File type and content validation
- **Rate Limiting** - API protection and resource management
- **Analytics Tracking** - Usage statistics and performance monitoring
- **Scalable Architecture** - Microservices-ready design
- **Security** - Input sanitization and secure file handling

## **Future Enhancements**

- **Multi-language Support** - Resume analysis in multiple languages
- **Industry-Specific Models** - Specialized analysis for different sectors
- **Real-time Collaboration** - Team-based resume review features
- **Advanced Analytics** - Detailed reporting and insights dashboard
- **API Integration** - Connect with job boards and ATS systems
- **Mobile Application** - Native mobile app for on-the-go analysis

## **Acknowledgments**

- **LangChain** - For RAG implementation framework
- **Groq** - For high-performance LLM inference
- **FAISS** - For efficient vector similarity search
- **Streamlit** - For rapid frontend development
- **FastAPI** - For modern, fast API development

---
