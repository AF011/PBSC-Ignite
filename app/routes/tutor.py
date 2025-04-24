from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
import json
import os
from app.utils.db_utils import get_db, get_user_by_id
from app.utils.resource_utils import (
    fetch_youtube_videos,
    fetch_google_scholar_papers,
    fetch_google_search_results
)
from app.utils.llm_utils import get_groq_response

# Create a Blueprint for the tutor routes
tutor_bp = Blueprint('tutor_bp', __name__)

@tutor_bp.route('/tutor/<string:phase_id>/<string:module_id>', methods=['GET'])
def tutor_page(phase_id, module_id):
    """
    Render the AI Tutor page for a specific phase and module
    
    Args:
        phase_id (str): The ID of the phase
        module_id (str): The ID of the module
    """
    if "user_id" not in session:
        return redirect(url_for("auth_bp.sign_in"))
    
    # Get user data
    user = get_user_by_id(session["user_id"])
    if not user:
        return redirect(url_for("auth_bp.sign_in"))
    
    # Get roadmap data
    roadmap_data = json.loads(user.get('road_map', '{}'))
    
    # Get specific phase data
    phase = None
    try:
        phase = roadmap_data['phases'][int(phase_id)]
    except (IndexError, KeyError, ValueError):
        return redirect(url_for("roadmap_bp.roadmap"))
    
    # Get learning plan data if available
    learning_plan = phase.get('learning_plan', {})
    
    # Get the specific module (weekly schedule)
    module = None
    try:
        module = learning_plan['weekly_schedule'][int(module_id) - 1]
    except (IndexError, KeyError, ValueError):
        # If module doesn't exist, redirect to roadmap
        return redirect(url_for("roadmap_bp.roadmap"))
    
    # Prepare initial resources
    topic = f"{phase['name']} - Week {module['week']}: {', '.join(module['learning_objectives'])}"
    
    # Get chat history if exists - use the new nested structure
    db = get_db()
    chat_history_doc = db.user_chat_histories.find_one({
        "user_id": session["user_id"]
    })
    
    chat_history = []
    if chat_history_doc:
        # Get the specific module history from the nested structure
        module_key = f"{phase_id}_{module_id}"
        if module_key in chat_history_doc.get('modules', {}):
            chat_history = chat_history_doc['modules'][module_key]
    
    return render_template(
        'tutor.html',
        user=user,
        phase=phase,
        module=module,
        phase_id=phase_id,
        module_id=module_id,
        topic=topic,
        chat_history=chat_history
    )

@tutor_bp.route('/api/tutor/chat', methods=['POST'])
def tutor_chat():
    """API endpoint for the tutor chat functionality"""
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    data = request.json
    message = data.get('message')
    phase_id = data.get('phase_id')
    module_id = data.get('module_id')
    
    if not all([message, phase_id, module_id]):
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    
    # Get user data
    user = get_user_by_id(session["user_id"])
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    # Get roadmap data to provide context
    roadmap_data = json.loads(user.get('road_map', '{}'))
    
    try:
        # Get phase and module data
        phase = roadmap_data['phases'][int(phase_id)]
        learning_plan = phase.get('learning_plan', {})
        module = learning_plan['weekly_schedule'][int(module_id) - 1]
        
        # Create module key for storage
        module_key = f"{phase_id}_{module_id}"
        
        # Get the current chat history for this module
        db = get_db()
        chat_history_doc = db.user_chat_histories.find_one({
            "user_id": session["user_id"]
        })
        
        # Initialize chat history structure if it doesn't exist
        if not chat_history_doc:
            chat_history_doc = {
                "user_id": session["user_id"],
                "modules": {}
            }
        
        # Initialize module chat history if it doesn't exist
        if 'modules' not in chat_history_doc:
            chat_history_doc['modules'] = {}
            
        if module_key not in chat_history_doc['modules']:
            chat_history_doc['modules'][module_key] = []
        
        # Create user message object
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        }
        
        # Add user message to history
        chat_history_doc['modules'][module_key].append(user_message)
        
        # Get previous messages for context (last 10)
        previous_messages = chat_history_doc['modules'][module_key][-10:] if len(chat_history_doc['modules'][module_key]) > 0 else []
        
        # Create conversation context
        conversation_context = []
        for msg in previous_messages:
            conversation_context.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Prepare context for the AI
        topic = f"{phase['name']} - Week {module['week']}"
        objectives = module['learning_objectives']
        skills = phase.get('skills', [])
        resources = phase.get('resources', {})
        
        # Get response from Groq
        ai_response = get_groq_response(
            message=message,
            topic=topic,
            objectives=objectives,
            skills=skills,
            resources=resources,
            conversation_context=conversation_context
        )
        
        # Create AI response object
        assistant_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now()
        }
        
        # Add assistant message to history
        chat_history_doc['modules'][module_key].append(assistant_message)
        
        # Update the database
        db.user_chat_histories.update_one(
            {"user_id": session["user_id"]},
            {"$set": chat_history_doc},
            upsert=True
        )
        
        return jsonify({
            "status": "success",
            "response": ai_response
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@tutor_bp.route('/api/tutor/resources', methods=['GET'])
def get_resources():
    """API endpoint to get resources for a specific topic"""
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    topic = request.args.get('topic')
    resource_type = request.args.get('type', 'all')
    
    if not topic:
        return jsonify({"status": "error", "message": "Missing topic parameter"}), 400
    
    try:
        results = {}
        
        if resource_type in ['all', 'youtube']:
            # Fetch YouTube videos
            youtube_results = fetch_youtube_videos(topic, max_results=5)
            results['youtube'] = youtube_results
        
        if resource_type in ['all', 'papers']:
            # Fetch Google Scholar papers
            papers = fetch_google_scholar_papers(topic, max_results=5)
            results['papers'] = papers
        
        if resource_type in ['all', 'web']:
            # Fetch general web resources
            web_resources = fetch_google_search_results(topic, max_results=5)
            results['web'] = web_resources
        
        return jsonify({
            "status": "success",
            "resources": results
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Import at the top
from datetime import datetime

@tutor_bp.route('/api/tutor/clear-history', methods=['POST'])
def clear_chat_history():
    """Clear the chat history for a specific module"""
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    data = request.json
    phase_id = data.get('phase_id')
    module_id = data.get('module_id')
    
    if not all([phase_id, module_id]):
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    
    try:
        # Create module key
        module_key = f"{phase_id}_{module_id}"
        
        # Clear chat history for this module
        db = get_db()
        
        result = db.user_chat_histories.update_one(
            {"user_id": session["user_id"]},
            {"$set": {f"modules.{module_key}": []}}
        )
        
        return jsonify({
            "status": "success",
            "message": "Chat history cleared successfully"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500