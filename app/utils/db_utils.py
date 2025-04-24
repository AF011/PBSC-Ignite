from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import datetime
from bson import ObjectId
import bcrypt

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "PBSC-Ignite-db")

# MongoDB client initialization
def get_db():
    """Get database connection"""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

# Get initialized connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# User authentication functions
def check_existing_user(email, username):
    """Check if a user with the given email or username already exists"""
    return db.users.find_one({"$or": [{"email": email.lower()}, {"user_id": username.lower()}]})

def insert_user(user_data):
    """Insert a new user into the database"""
    return db.users.insert_one(user_data)

def find_user_by_credentials(email_or_user_id):
    """Find a user by email or user ID"""
    return db.users.find_one({"$or": [{"email": email_or_user_id}, {"user_id": email_or_user_id}]})

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(provided_password, stored_password):
    """Verify a password against stored hash"""
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

# User profile functions
def get_user_by_id(user_id):
    """Get user by user_id"""
    return db.users.find_one({"user_id": user_id})

def update_user_profile(user_id, update_data):
    """Update user profile with the provided data"""
    return db.users.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )

# Roadmap and learning plan functions
def get_user_roadmap(user_id):
    """Get user's roadmap data"""
    user = get_user_by_id(user_id)
    if user and "road_map" in user:
        return user["road_map"]
    return None

def update_learning_plan(user_id, phase_id, learning_plan):
    """Update or add a learning plan for a specific phase"""
    return db.users.update_one(
        {
            "user_id": user_id,
            "active_modules.phase_id": phase_id
        },
        {
            "$set": {
                "active_modules.$.learning_plan": learning_plan
            }
        }
    )

def add_module_to_user(user_id, module_data):
    """Add a new module to user's active modules"""
    return db.users.update_one(
        {"user_id": user_id},
        {"$addToSet": {"active_modules": module_data}}
    )

def update_task_completion(user_id, phase_id, week_num, day_num, completed, completion_date=None):
    """Update task completion status"""
    if completion_date is None:
        completion_date = datetime.datetime.now() if completed else None
        
    return db.users.update_one(
        {
            "user_id": user_id,
            "active_modules.phase_id": phase_id,
        },
        {
            "$set": {
                "active_modules.$.learning_plan.weekly_schedule.$[week].daily_tasks.$[day].completed": completed,
                "active_modules.$.learning_plan.weekly_schedule.$[week].daily_tasks.$[day].completed_date": completion_date
            }
        },
        array_filters=[
            {"week.week": int(week_num)},
            {"day.day": int(day_num)}
        ]
    )

# Notification functions
def add_notification(notification_data):
    """Add a new notification"""
    return db.notifications.insert_one(notification_data)

def get_user_notifications(user_id, limit=5, unread_only=True):
    """Get notifications for a user"""
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
        
    return list(db.notifications.find(query).sort("created_at", -1).limit(limit))

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    return db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"read": True}}
    )