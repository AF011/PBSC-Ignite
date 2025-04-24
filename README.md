# PBSC-Ignite: AI-Powered Career Readiness Platform

> **PBSC-Ignite**: Personalized Blueprint for Skill & Career - Ignited by Leo011-AI

PBSC-Ignite is an intelligent career development platform designed to bridge the gap between academic learning and industry requirements through personalized AI guidance, structured learning roadmaps, and interactive tutoring.

## 🚀 The Problem I'm Solving

Despite abundant online resources and educational content, students still face significant challenges:

- **Personalization Gap**: Traditional education follows a one-size-fits-all approach
- **Lack of Structured Guidance**: Students struggle to create coherent learning paths
- **Disconnect Between Learning and Career**: Education often isn't aligned with industry needs
- **Limited Mentorship**: Individual guidance is unavailable to most students

PBSC-Ignite addresses these challenges by providing AI-powered personalized learning experiences that adapt to each student's unique goals, strengths, and pace.

## 🛠️ Key Features of the MVP

### 🔍 Personalized Profile Analysis
- Comprehensive profile creation capturing career goals and skills
- Integration with LinkedIn, GitHub, and other professional platforms
- Data-driven assessment of strengths and areas for improvement

### 🗺️ AI-Generated Career Roadmaps
- Tailored learning paths based on individual career aspirations
- Phase-based structure with clear milestones and timelines
- Daily task breakdowns with curated resources
- Progress tracking with visual indicators

### 🤖 AI Tutor for Interactive Learning
- Topic-specific AI mentoring for each module
- Contextual conversation that retains learning history
- Integration with multiple resource sources:
  - Academic papers from Google Scholar
  - Educational videos from YouTube
  - Curated web resources
  - Real-time Q&A and concept explanations

### 💬 LEO-AI: 24/7 Personal Mentor
- Intelligent personal assistant with deep knowledge of user's profile
- Skill gap analysis and project recommendations
- Career guidance aligned with industry trends
- Technical support and learning assistance

## 🧠 Technology Stack Used for the MVP

### UI Technologies
- HTML, CSS, JavaScript
- Bootstrap for responsive design

### Backend & Database
- Python (Flask) for backend operations and API handling
- MongoDB for user data, roadmap progress, and interaction history

### APIs & Integrations
- Medium API for tech blogs
- YouTube API for video resources
- LinkedIn API for professional profile analysis
- GitHub API for technical capabilities assessment

### AI Technologies
- Gemini Flash 1.5 for real-time assistance and chat interactions
- meta-llama/llama-4-scout-17b-16e-instruct for roadmap generation and AI guidance

## ⚙️ Installation

1. Clone the repository
```bash
git clone https://github.com/AF011/PBSC-Ignite.git
cd PBSC-Ignite
```

2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables (.env file)
```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=PBSC-Ignite-db
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
GENMI_API_KEY=your-gemini-api-key
YOUTUBE_API_KEY=your-youtube-api-key
GOOGLE_SCHOLOR_API_KEY=your-google-scholar-api-key
GOOGLE_CUSTOM_SEARCH_API_KEY=your-google-search-api-key
LINKEDIN_API_KEY=your-linkedin-api-key
```

5. Run the application
```bash
python run.py
```

## 📂 Project Structure

```
PBSC-Ignite/
├── .env               # Environment variables
├── .gitignore         # Git ignore file
├── run.py             # Application entry point
├── app/
│   ├── __init__.py    # App factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── career_coach.py
│   │   ├── roadmap.py
│   │   └── tutor.py
│   ├── static/
│   ├── templates/
│   └── utils/
│       ├── __init__.py
│       ├── db_utils.py
│       ├── llm_utils.py
│       └── resource_utils.py
```

## 🎥 MVP Demo Video

Experience PBSC-Ignite in action through my demo video that showcases the platform's key features:

[![PBSC-Ignite Demo Video](https://img.youtube.com/vi/ao5RaBryRAA/0.jpg)](https://youtu.be/ao5RaBryRAA)

The video demonstrates:
- User onboarding and profile creation
- AI-generated personalized roadmaps
- Interactive AI tutoring sessions
- LEO-AI chatbot providing contextual guidance
- Progress tracking visualizations

## 💫 Impact & Purpose

PBSC-Ignite is not just for elite institutions or privileged students - it's for everyone. This platform directly aligns with the **UN Sustainable Development Goal 4 (Quality Education)** by ensuring inclusive and equitable quality education and promoting lifelong learning opportunities for all.

This platform aims to democratize access to quality career guidance and personalized learning paths, serving as a beacon of hope for:

* Students from underserved communities lacking mentorship resources
* Self-learners navigating complex career transitions without guidance
* Educational institutions seeking to provide personalized support at scale
* Anyone feeling lost in their educational journey

By leveraging AI to make personalized education accessible regardless of geographical or socioeconomic barriers, PBSC-Ignite helps bridge the global education divide. The platform embodies SDG 4's core mission of ensuring that all learners acquire the knowledge and skills needed for sustainable development and successful careers.

Every student deserves a mentor who understands their unique strengths, challenges, and aspirations - a guiding light in the darkness of career uncertainty. PBSC-Ignite ensures that quality mentorship and personalized guidance is accessible to all, regardless of background or resources.

## 🔮 Vision and Future Scope

PBSC-Ignite is designed to evolve into a comprehensive educational ecosystem:

- **For Students**: Personalized guidance that adapts to individual learning styles and career goals
- **For Educational Institutions**: Data-driven insights to improve curriculum and teaching methods
- **For Companies**: Better talent assessment based on verified skills and industry-relevant projects

Future enhancements include:
- Enhanced AI interaction with advanced reasoning capabilities
- Deeper integration with learning management systems
- Expanded analytics for educational institutions
- Mobile application development
- Support for diverse career paths beyond technology

### Upcoming Features:

- **AI-Driven Evaluation System**: After completing each topic, users will toggle the 'Completed' button, and the AI will assess their understanding through interactive tests.

- **Strategic Career Growth Recommendations**: The system will suggest when to create LinkedIn posts about newly acquired skills, what projects to build to showcase these skills, and how to effectively manage GitHub repositories to highlight growth.

- **Engagement Optimization**: For continuous progress, the platform will send notifications after 20-30 days of inactivity, ensuring consistent advancement toward career goals.

- **Adaptive Learning Experience**: The AI Tutor feature will transform passive learning into an interactive, guided experience that adapts to each user's unique learning path and pace.

## 👤 Creator & Maintainer

This project was created and is maintained by:

**Leo Programmer - AF011 (Abdul Faheem)**

## 🙏 Acknowledgements

* Groq for their powerful LLM API that powers our AI Tutor
* MongoDB for the flexible document database
* Bootstrap for the responsive UI components
* The creators of the open-source template used for parts of the UI
* All the libraries and APIs that made this project possible

## 📄 License

This project is licensed under the MIT License with additional terms - see the [LICENSE](LICENSE) file for details.

---

*An AF's Endeavor Developed with 🥤 and 💡*
=======
