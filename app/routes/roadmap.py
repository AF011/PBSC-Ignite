from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import json
from datetime import datetime
from app.utils.db_utils import get_db, get_user_by_id
from app.utils.llm_utils import generate_learning_plan

# Create a blueprint for roadmap routes
roadmap_bp = Blueprint('roadmap_bp', __name__)

@roadmap_bp.route('/road-map')
def roadmap():
    """Render the roadmap page for the user"""
    if "user_id" not in session:
        return redirect(url_for("auth_bp.sign_in"))
    
    # Get user data
    user = get_user_by_id(session["user_id"])
    if not user:
        return redirect(url_for("auth_bp.sign_in"))
    
    # Get roadmap data
    roadmap_data = json.loads(user.get('road_map', '{}'))
    
    # Check if roadmap exists
    if not roadmap_data or 'phases' not in roadmap_data:
        return redirect(url_for("main_bp.student_profile"))
    
    # Add the user object to the template context
    return render_template('road_map.html', roadmap_data=roadmap_data, user=user)

@roadmap_bp.route('/generate-plan/<string:phase_id>', methods=['POST'])
def generate_plan(phase_id):
    """Generate a learning plan for a specific phase"""
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    # Get user data
    user = get_user_by_id(session["user_id"])
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    # Get roadmap data
    roadmap_data = json.loads(user.get('road_map', '{}'))
    
    # Check if phase exists
    try:
        phase_id_int = int(phase_id)
        if phase_id_int < 0 or phase_id_int >= len(roadmap_data.get('phases', [])):
            return jsonify({"status": "error", "message": "Invalid phase ID"}), 400
        
        phase = roadmap_data['phases'][phase_id_int]
    except (ValueError, IndexError, KeyError):
        return jsonify({"status": "error", "message": "Invalid phase ID"}), 400
    
    # Check if the learning plan already exists
    if phase.get('learning_plan'):
        return jsonify({"status": "exists", "message": "Learning plan already exists"})
    
    # Get phase name and skills
    phase_name = phase.get('name', '')
    skills = phase.get('skills', [])
    
    if not phase_name or not skills:
        return jsonify({"status": "error", "message": "Missing phase name or skills"}), 400
    
    try:
        # Generate the learning plan
        learning_plan = generate_learning_plan(phase_name, skills)
        
        # Add the learning plan to the phase
        phase['learning_plan'] = learning_plan
        
        # Mark all tasks as not completed
        for week in learning_plan.get('weekly_schedule', []):
            for task in week.get('daily_tasks', []):
                task['completed'] = False
        
        # Update the user's roadmap in the database
        db = get_db()
        db.users.update_one(
            {"user_id": session["user_id"]},
            {"$set": {"road_map": json.dumps(roadmap_data)}}
        )
        
        return jsonify({"status": "success", "message": "Learning plan generated"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@roadmap_bp.route('/learning-plan/<string:phase_id>')
def learning_plan(phase_id):
    """Render the learning plan page for a specific phase"""
    if "user_id" not in session:
        return redirect(url_for("auth_bp.sign_in"))
    
    # Get user data
    user = get_user_by_id(session["user_id"])
    if not user:
        return redirect(url_for("auth_bp.sign_in"))
    
    # Get roadmap data
    roadmap_data = json.loads(user.get('road_map', '{}'))
    
    # Check if phase exists
    try:
        phase_id_int = int(phase_id)
        if phase_id_int < 0 or phase_id_int >= len(roadmap_data.get('phases', [])):
            return redirect(url_for("roadmap_bp.roadmap"))
        
        phase = roadmap_data['phases'][phase_id_int]
    except (ValueError, IndexError, KeyError):
        return redirect(url_for("roadmap.roadmap"))
    
    # Check if learning plan exists
    if not phase.get('learning_plan'):
        # Generate learning plan
        return redirect(url_for("roadmap_bp.generate_plan", phase_id=phase_id))
    
    # Add the user object and phase ID to the template context
    return render_template('learning_plan.html', phase=phase, user=user, phase_id=phase_id)

@roadmap_bp.route('/complete-task', methods=['POST'])
def complete_task():
    """Mark a task as completed or not completed"""
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    data = request.json
    phase_id = data.get('phase_id')
    week_index = data.get('week_index')
    day_index = data.get('day_index')
    completed = data.get('completed', False)
    
    if not all([phase_id, week_index, day_index]):
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    
    try:
        # Get user data
        user = get_user_by_id(session["user_id"])
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        # Get roadmap data
        roadmap_data = json.loads(user.get('road_map', '{}'))
        
        # Update the task completion status
        phase = roadmap_data['phases'][int(phase_id)]
        weekly_schedule = phase['learning_plan']['weekly_schedule']
        task = weekly_schedule[int(week_index)]['daily_tasks'][int(day_index)]
        task['completed'] = completed
        
        # Update the database
        db = get_db()
        db.users.update_one(
            {"user_id": session["user_id"]},
            {"$set": {"road_map": json.dumps(roadmap_data)}}
        )
        
        return jsonify({"status": "success", "message": "Task updated"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500