import os
import json
import requests
from groq import Groq
import google.generativeai as genai
from markdown2 import Markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

markdowner = Markdown()

# Configure Gemini API - use environment variable without default value
GENMI_API_KEY = os.getenv("GENMI_API_KEY")
genai.configure(api_key=GENMI_API_KEY)

# Groq API Key - use environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def get_roadmap_from_groq(topic):
    """
    Generate a learning roadmap for the given topic using Groq API
    
    Args:
        topic (str): The topic to generate a roadmap for
    
    Returns:
        dict: JSON structure with the roadmap data
    """
    # Use the Groq API key from environment variables
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""Create a structured learning roadmap for {topic} in this exact JSON format:
    {{
        "phases": [
            {{
                "name": "Phase Name",
                "duration": "X-Y months",
                "description": "Brief description",
                "skills": ["skill1", "skill2", "skill3"],
                "resources": {{
                    "Category1": ["Resource1", "Resource2"],
                    "Category2": ["Resource3", "Resource4"],
                    "Category3": ["Resource5", "Resource6"]
                }}
            }}
        ]
    }}
    Include exactly 4 phases. Return ONLY the JSON without any markdown formatting or code blocks."""

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a technical expert. Respond with valid JSON only. Do not include markdown formatting, code blocks, or any explanatory text."},
            {"role": "user", "content": prompt}
        ],
        model=MODEL,  # Use the model that works with Groq
        temperature=0.1,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if they exist
    if content.startswith("```json") or content.startswith("```"):
        # Find the first and last backtick groups
        start_idx = content.find("\n") + 1
        end_idx = content.rfind("```")
        
        # Extract only the JSON part
        if end_idx != -1:
            content = content[start_idx:end_idx].strip()
        else:
            # If closing backticks aren't found, try to extract after the first line
            content = content[start_idx:].strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error generating roadmap: {e}")
        # Return a basic structure if JSON parsing fails
        return {
            "phases": [
                {
                    "name": f"Getting Started with {topic}",
                    "duration": "1-3 months",
                    "description": f"Learn the fundamentals of {topic}",
                    "skills": ["Basic skills"],
                    "resources": {
                        "Online Courses": ["Recommended courses"],
                        "Books": ["Recommended books"]
                    }
                }
            ]
        }

def get_gemini_response(prompt, tokens=8192):
    """
    Get a response from Gemini API
    
    Args:
        prompt (str): The prompt to send to Gemini
        tokens (int): Maximum number of tokens in the response
        
    Returns:
        str: The generated response
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config={
                "temperature": 0.5,
                "top_p": 0.95,
                "max_output_tokens": tokens,
            },
        )
        convo = model.start_chat(history=[])
        response = convo.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def generate_learning_plan(phase_name, skills):
    """
    Generate a detailed learning plan for a specific phase
    
    Args:
        phase_name (str): Name of the phase
        skills (list): List of skills to include in the plan
        
    Returns:
        dict: JSON structure with the learning plan
    """
    # Use the Groq API key from environment variables
    client = Groq(api_key=GROQ_API_KEY)
    
    skills_str = ', '.join(skills)
    prompt = f"""Generate learning plan for {phase_name} phase with skills: {skills_str}. Return pure JSON:
            {{
                "weekly_schedule": [
                    {{
                        "week": 1,
                        "learning_objectives": ["Objective 1", "Objective 2"],
                        "daily_tasks": [
                            {{
                                "day": 1,
                                "tasks": ["Task 1", "Task 2"],
                                "resources": ["Resource 1"],
                                "duration_hours": 2
                            }}
                        ],
                        "assessment": "Project description"
                    }}
                ]
            }}"""

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "Return valid JSON only"},
                 {"role": "user", "content": prompt}],
        model=MODEL,
        temperature=0
    )
    
    return json.loads(response.choices[0].message.content.strip()
                     .replace("```json", "").replace("```", ""))

def fetch_github_projects(github_username):
    """
    Fetch the user's public GitHub repositories
    
    Args:
        github_username (str): GitHub username
        
    Returns:
        list: List of repository information
    """
    github_api_url = f"https://api.github.com/users/{github_username}/repos"
    try:
        response = requests.get(github_api_url)
        response.raise_for_status()
        repos = response.json()
        projects = [{"title": repo["name"], "description": repo["description"] or "No description available"} 
                    for repo in repos]
        return projects
    except requests.RequestException as e:
        return f"Error fetching GitHub data: {e}"

def fetch_linkedin_profile(linkedin_url, user_id):
    """
    Fetch LinkedIn profile data using LinkedIn Data API
    
    Args:
        linkedin_url (str): LinkedIn profile URL
        user_id (str): User ID to associate with the profile
        
    Returns:
        dict: LinkedIn profile data or error message
    """
    from app.utils.db_utils import get_db
    db = get_db()
    students_collection = db["linkedin_data"]
    
    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url"
    querystring = {"url": linkedin_url}
    headers = {
        'x-rapidapi-key': os.getenv("LINKEDIN_API_KEY"),
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }    

    try:
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            profile_data = response.json()
            profile_data["user_id"] = user_id

            # Check if a profile with the same user_id already exists
            existing_profile = students_collection.find_one({"user_id": user_id})

            if existing_profile:
                # Update existing profile
                result = students_collection.update_one(
                    {"user_id": user_id},
                    {"$set": profile_data}
                )
                return {"status": "success", "message": f"Profile data updated for user_id: {user_id}."}
            else:                
                # Insert new profile
                students_collection.insert_one(profile_data)
                return {"status": "success", "message": f"Profile data saved for user_id: {user_id}."}
        else:
            return {"status": "error", "message": f"Failed to retrieve data: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}

def get_groq_response(message, topic, objectives, skills, resources, conversation_context=[]):
    """
    Get an AI tutor response using Groq API
    
    Args:
        message (str): The user's message
        topic (str): The current topic being discussed
        objectives (list): Learning objectives for the current module
        skills (list): Skills for the current phase
        resources (dict): Resources for the current phase
        conversation_context (list): List of previous messages for context
        
    Returns:
        str: AI response
    """
    client = Groq(api_key=GROQ_API_KEY)
    
    # Format resources into a readable string
    resources_str = ""
    for category, items in resources.items():
        resources_str += f"{category}: {', '.join(items)}\n"
    
    # Prepare system prompt
    system_prompt = f"""You are an AI tutor specializing in {topic}. 
    
    You are currently helping the student with the following:
    - Topic: {topic}
    - Learning Objectives: {', '.join(objectives)}
    - Key Skills: {', '.join(skills)}
    
    Available Learning Resources:
    {resources_str}
    
    Your role is to:
    1. Answer questions about the topic in an educational manner
    2. Explain concepts clearly and thoroughly
    3. Provide practical examples and applications
    4. Suggest additional resources when appropriate
    5. Encourage critical thinking and problem-solving
    6. If the student seems to be struggling, break down complex topics into simpler components
    7. Maintain a supportive, patient, and encouraging tone
    
    Do not:
    - Provide incorrect information
    - Go off-topic from the learning objectives
    - Write extremely long responses (keep them concise but educational)
    
    Write in an engaging educational style that's friendly but professional.
    """
    
    # Prepare messages including conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation context (previous messages)
    if conversation_context:
        for msg in conversation_context:
            messages.append(msg)
    
    # Add the current user message
    messages.append({"role": "user", "content": message})
    
    # Get response from Groq
    response = client.chat.completions.create(
        messages=messages,
        model=MODEL,
        temperature=0.5,
        max_tokens=1000
    )
    
    return response.choices[0].message.content.strip()