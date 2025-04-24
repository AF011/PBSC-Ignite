from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from datetime import datetime
import json
import os
from app.utils.db_utils import get_user_by_id
from app.utils.llm_utils import get_roadmap_from_groq

# Main blueprint
main_bp = Blueprint('main_bp', __name__)

@main_bp.route("/")
@main_bp.route("/home")
def home():
    if "user_id" in session:
        # Categories for the top section
        categories = [
            "Blockchain", "JavaScript", "Education", "Coding", "Books", "Web Development",
            "Marketing", "Deep Learning", "Social Media", "Software Development",
            "Artificial Intelligence", "Culture", "React", "UX", "Software Engineering",
            "Design", "Science", "Health", "Python", "Productivity", "Machine Learning",
            "Writing", "Self Improvement", "Technology", "Data Science", "Programming"
        ]

        # Fetch companies from database
        from app.utils.db_utils import get_db
        db = get_db()
        companies_collection = db.companies
        companies = companies_collection.find().sort("visit_date", 1).limit(5)
        selected_companies = list(companies)

        # Fetch articles from Medium API
        query = "technology"
        page = 0
        url = "https://medium16.p.rapidapi.com/search/stories"
        headers = {
            "x-rapidapi-key": os.getenv('MEDIUM_API_KEY', 'a9d206afa9msh1a3192fce899677p15fbaajsn6ccdd156cb0e'),
            "x-rapidapi-host": "medium16.p.rapidapi.com",
        }
        querystring = {"q": query, "limit": "5", "page": str(page)}
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            articles = response.json().get("data", []) if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching articles: {e}")
            articles = []

        return render_template(
            "home.html", categories=categories, stories=articles, companies=selected_companies
        )
    else:
        return redirect(url_for("auth_bp.sign_in"))

@main_bp.route("/news-articles")
def news_article():
    if "user_id" in session:
        # Categories for the top section
        categories = [
            "Blockchain", "JavaScript", "Education", "Coding", "Books", "Web Development",
            "Marketing", "Deep Learning", "Social Media", "Software Development",
            "Artificial Intelligence", "Culture", "React", "UX", "Software Engineering",
            "Design", "Science", "Health", "Python", "Productivity", "Machine Learning",
            "Writing", "Self Improvement", "Technology", "Data Science", "Programming"
        ]

        # Get query parameters for topic and pagination
        query = request.args.get("q", "technology")
        page = int(request.args.get("page", 0))

        # API Request
        url = "https://medium16.p.rapidapi.com/search/stories"
        headers = {
            "x-rapidapi-key": os.getenv('MEDIUM_API_KEY', 'a9d206afa9msh1a3192fce899677p15fbaajsn6ccdd156cb0e'),
            "x-rapidapi-host": "medium16.p.rapidapi.com",
        }
        querystring = {"q": query, "limit": "10", "page": str(page)}
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            stories = response.json().get("data", []) if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching stories: {e}")
            stories = []

        return render_template(
            "news_articles.html", stories=stories, query=query, page=page, categories=categories
        )
    else:
        return redirect(url_for("auth_bp.sign_in"))

@main_bp.route('/mentorship')
def mentorship():
    if "user_id" in session:
        return render_template('mentorship.html')
    else:
        return redirect(url_for("auth_bp.sign_in"))

@main_bp.route('/get_notifications')
def get_notifications():
    if "user_id" not in session:
        return jsonify([])
    
    from app.utils.db_utils import get_db
    db = get_db()
    notifications = list(db.notifications.find(
        {"user_id": session["user_id"], "read": False}
    ).sort("created_at", -1).limit(5))
    
    for n in notifications:
        n["_id"] = str(n["_id"])
        
    return jsonify(notifications)

@main_bp.route('/student_profile', methods=['POST', 'GET'])
def student_profile():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.sign_in"))

    from app.utils.db_utils import get_db
    db = get_db()
    user_collection = db.users
    linkedin_data_collection = db.linkedin_data

    if request.method == 'POST':
        user_id = session['user_id']
        existing_profile = user_collection.find_one({"user_id": user_id})
        if not existing_profile:
            return "Profile not found", 404

        # Check if key fields were updated
        key_fields = ['career_goal', 'dream_company', 'personal_statement', 'company_preference']
        key_fields_updated = any(
            request.form.get(field, '').strip() != existing_profile.get(field, '')
            for field in key_fields
        )

        updated_profile = {
            key: value.strip() if value.strip() else existing_profile.get(key, '')
            for key, value in request.form.items() if key != 'user_id'
        }

        # Fetch LinkedIn data
        linkedin_profile = existing_profile.get('linkedinProfile')
        if linkedin_profile:
            linkedin_data = linkedin_data_collection.find_one({"user_id": user_id})
            if linkedin_data:
                updated_profile['linkedin_data'] = {
                    "name": f"{linkedin_data.get('firstName', '')} {linkedin_data.get('lastName', '')}",
                    "headline": linkedin_data.get("headline", ""),
                    "summary": linkedin_data.get("summary", ""),
                    "skills": linkedin_data.get("skills", []),
                    "educations": linkedin_data.get("educations", []),
                    "positions": linkedin_data.get("fullPositions", []),
                    "certifications": linkedin_data.get("certifications", []),
                    "languages": linkedin_data.get("languages", []),
                }

        try:
            desired_role = updated_profile.get('career_goal', 'Software Developer')
            roadmap_data = get_roadmap_from_groq(desired_role)
            updated_profile['road_map'] = json.dumps(roadmap_data)

            update_operation = {"$set": updated_profile}
            if key_fields_updated:
                update_operation["$unset"] = {"active_modules": ""}

            user_collection.update_one(
                {"user_id": user_id}, 
                update_operation
            )
            return redirect(url_for('main_bp.student_profile'))

        except Exception as e:
            print(f"Error generating roadmap: {str(e)}")
            flash("Error updating profile. Please try again.")
            return redirect(url_for('main_bp.student_profile'))

    profile = user_collection.find_one({"user_id": session['user_id']}) or {}
    return render_template('student_profile.html', profile=profile, user=profile)