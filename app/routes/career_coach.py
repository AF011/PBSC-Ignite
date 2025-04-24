from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from markdown2 import Markdown
from app.utils.llm_utils import get_gemini_response, fetch_linkedin_profile, fetch_github_projects
from app.utils.db_utils import get_db, get_user_by_id

# Initialize markdown converter
markdowner = Markdown()

# Career coach blueprint
career_coach_bp = Blueprint('career_coach_bp', __name__)

def generate_prompt(user_data, user_query, chat_history):
    """Generate a conversational prompt including chat history and GitHub projects."""
    
    # Extract user data
    name = f"{user_data.get('firstName', 'there')} {user_data.get('lastName', '')}".strip()
    headline = user_data.get("headline", "No headline available")
    summary = user_data.get("summary", "No summary available")
    certifications = user_data.get("certifications", [])
    skills = user_data.get("skills", [])
    projects = user_data.get("projects", {}).get("items", [])
    honors = user_data.get("honors", [])
    geo = user_data.get("geo", {}).get("full", "Location not specified")
    github_username = user_data.get("github_username", None)
    
    # Process certifications
    certifications_str = []
    for cert in certifications:
        cert_name = cert.get("name", "Unnamed Certification")
        cert_authority = cert.get("authority", "Unknown Authority")
        cert_company = cert.get("company", {}).get("name", "Unknown Company")
        cert_time = f"{cert.get('start', {}).get('year', 'Unknown Start Year')} - {cert.get('end', {}).get('year', 'Unknown End Year')}"
        certifications_str.append(f"{cert_name} ({cert_authority} - {cert_company} - {cert_time})")
    
    certifications_str = ', '.join(certifications_str) if certifications_str else 'None'
    
    # Process honors
    honors_str = []
    for honor in honors:
        honor_title = honor.get("title", "Unknown Honor")
        honor_description = honor.get("description", "No description available")
        honor_issuer = honor.get("issuer", "Unknown Issuer")
        honor_time = f"{honor.get('issuedOn', {}).get('year', 'Unknown Year')}"
        honors_str.append(f"{honor_title} - {honor_description} (Issued by {honor_issuer} in {honor_time})")
    
    honors_str = ', '.join(honors_str) if honors_str else 'None'
    
    # Handle skills to ensure they are strings
    skills_str = ', '.join([skill.get("name", "Unknown Skill") for skill in skills]) if skills else 'None'

    # Handle projects to ensure they are strings
    projects_str = ', '.join([proj.get("title", "Unknown Project") for proj in projects]) if projects else 'None'

    # Fetch GitHub projects if a GitHub username exists
    github_projects_str = "None"
    if github_username:
        github_projects = fetch_github_projects(github_username)
        github_projects_str = ', '.join([f"{proj['title']}: {proj['description']}" for proj in github_projects]) if isinstance(github_projects, list) else github_projects

    # Build the history string, ensuring each entry is valid
    history_str = "\n".join([f"User: {entry.get('prompt', '')}\nBot: {entry.get('raw_response', '')}" 
                            for entry in chat_history if isinstance(entry, dict) and 'prompt' in entry and ('response' in entry or 'raw_response' in entry)])

    # Create the new prompt
    prompt = f"""
    You are a helpful assistant responding in a friendly and conversational tone. 
    The user's profile contains the following:
    - Name: {name}
    - Headline: {headline}
    - Summary: {summary}
    - Location: {geo}
    - Certifications: {certifications_str if certifications else 'None'}
    - Skills: {skills_str if skills else 'None'}
    - Projects (LinkedIn): {projects_str if projects else 'None'}
    - Honors: {honors_str if honors else 'None'}

    Chat history:
    {history_str}

    User Question: "{user_query}"

    Respond in a friendly and concise manner:
    - Continue the conversation based on the chat history and user profile.
    - Keep responses brief and focused while maintaining context.
    """
    return prompt

@career_coach_bp.route('/your-career_coach-leo011', methods=['POST', 'GET'])
def career_coach():
    if "user_id" in session:
        db = get_db()
        leo_chat_history = db.career_coach
        students_collection = db.linkedin_data
        
        if request.method == 'POST':
            user_id = session['user_id']
            user_query = request.form['userQuery']
            
            user_record = get_user_by_id(user_id)
            linkedin_url = user_record.get('linkedinProfile') if user_record else None
            
            # Fetch user data from MongoDB
            if linkedin_url:
                fetch_linkedin_profile(linkedin_url, user_id)
            else:
                flash("LinkedIn profile URL not found. Please update your profile.")
                return redirect(url_for('main_bp.student_profile'))
                
            user_data = students_collection.find_one({"user_id": user_id})
            if not user_data:
                flash("User data not found. Please update your profile.")
                return redirect(url_for('main_bp.student_profile'))

            # Generate prompt and get response
            existing_conversation = leo_chat_history.find_one({"user_id": user_id})
            chat_history = existing_conversation.get("messages", []) if existing_conversation else []
            
            prompt = generate_prompt(user_data, user_query, chat_history)
            response = get_gemini_response(prompt, 300)
            
            # Convert markdown response to HTML
            html_response = markdowner.convert(response)

            if not existing_conversation:
                conversation_id = f"conv_{str(datetime.now().timestamp()).replace('.', '')}"
                new_conversation = {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "messages": [
                        {
                            "prompt": user_query,
                            "response": html_response,
                            "raw_response": response,
                            "time": datetime.utcnow(),
                        },
                    ]
                }
                leo_chat_history.insert_one(new_conversation)
                updated_messages = new_conversation["messages"]
            else:
                updated_messages = sorted(
                    [
                        {
                            "prompt": msg["prompt"], 
                            "response": msg.get("response", markdowner.convert(msg.get("raw_response", ""))),
                            "time": msg["time"]
                        }
                        for msg in existing_conversation["messages"]
                    ] + [{
                        "prompt": user_query, 
                        "response": html_response,
                        "raw_response": response,
                        "time": datetime.utcnow()
                    }],
                    key=lambda x: x["time"]
                )

                leo_chat_history.update_one(
                    {"user_id": user_id},
                    {"$set": {"messages": updated_messages}}
                )

            return render_template(
                "career_coach.html", 
                messages=updated_messages
            )

        # GET request: load existing conversation
        existing_conversation = leo_chat_history.find_one({"user_id": session["user_id"]})
        if existing_conversation:
            messages = [{
                "prompt": msg["prompt"],
                "response": msg.get("response", markdowner.convert(msg.get("raw_response", ""))),
                "time": msg["time"]
            } for msg in existing_conversation["messages"]]
        else:
            messages = []
            
        return render_template("career_coach.html", messages=messages)
    
    return redirect(url_for("auth_bp.sign_in"))