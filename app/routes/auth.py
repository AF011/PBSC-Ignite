from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.utils.db_utils import (
    check_existing_user,
    insert_user,
    find_user_by_credentials,
    hash_password,
    verify_password
)

# Account creation
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            error = "Passwords do not match. Please try again."
            return render_template("sign_up.html", error=error)
        
        # Hash the password for security        
        hashed_password = hash_password(password)
        
        # Check if the email or username already exists
        existing_user = check_existing_user(email, username)
        
        if existing_user:
            error = "Email or username already exists. Please use a different one."
            return render_template("sign_up.html", error=error)
        
        # Insert the new user into the MongoDB collection
        new_user = {
            "user_id": username.lower(),
            "name": name,
            "phone": phone,
            "dob": dob,
            "email": email.lower(),
            "password": hashed_password,
            "joining_date": request.form.get("startdate", None),
            "career_goal": request.form.get("career_goal", None),
            "entrepreneurship_interest": request.form.get("entrepreneurship_interest", None),
            "key_interests": request.form.get("interested_industries", "").split(", "),  # Split into list
            "dream_company": request.form.get("dream_company", None),
            "company_preference": request.form.get("company_preference", None),
            "preferred_company": request.form.get("preferred_company", None),
            "personal_statement": request.form.get("personal_statement", None),
            "github_profile": request.form.get("githubProfile", None),
            "linkedin_profile": request.form.get("linkedinProfile", None),
        }
        
        try:
            insert_user(new_user)  # Insert new user using db_utils function
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('auth_bp.sign_in'))
        except Exception as e:
            error = f"An error occurred: {e}"
            return render_template("sign_up.html", error=error)
    else:
        return render_template("sign_up.html")


@auth_bp.route("/sign_in", methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        email_or_user_id = request.form['username']
        password = request.form['password']
        
        # Query to find the user by email or user ID from MongoDB
        user = find_user_by_credentials(email_or_user_id)
        
        if user:                        
            # Verify the password using function from db_utils
            if verify_password(password, user['password']):
                # Store user info in the session
                session['user_id'] = user['user_id']  # Save user ID in session
                session['name'] = user['name']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('main_bp.home'))
            else:
                error = "Incorrect password. Please try again."
                return render_template("sign_in.html", error=error)
        else:
            error = "No account found with the provided email or user ID."
            return render_template("sign_in.html", error=error)
    else:
        return render_template("sign_in.html")
    
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth_bp.sign_in"))