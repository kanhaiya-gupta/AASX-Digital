"""
Database interface for authentication
"""

import sqlite3
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import sys
import os

# Get the project root directory (3 levels up from this file)
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"

# Add the src directory to the Python path
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from shared.database_manager import DatabaseProjectManager
except ImportError as e:
    print(f"Error importing DatabaseProjectManager: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Looking for: {src_path}")
    raise

class AuthDatabase:
    """Database interface for authentication operations"""
    
    def __init__(self):
        self.db_manager = DatabaseProjectManager(
            projects_dir=Path("data/projects"),
            output_dir=Path("output")
        )
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        try:
            self.db_manager.cursor.execute("""
                SELECT user_id, username, email, password_hash, full_name, 
                       role, status, created_at, last_login
                FROM users 
                WHERE username = ?
            """, (username,))
            
            row = self.db_manager.cursor.fetchone()
            
            if row:
                return {
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "password_hash": row[3],
                    "full_name": row[4],
                    "role": row[5],
                    "status": row[6],
                    "created_at": row[7],
                    "last_login": row[8]
                }
            return None
            
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, email, password_hash, full_name, 
                       role, status, created_at, last_login
                FROM users 
                WHERE email = ?
            """, (email,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "password_hash": row[3],
                    "full_name": row[4],
                    "role": row[5],
                    "status": row[6],
                    "created_at": row[7],
                    "last_login": row[8]
                }
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def create_user(self, user_data: dict) -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (user_id, username, email, password_hash, full_name, 
                                 role, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data["user_id"],
                user_data["username"],
                user_data["email"],
                user_data["password_hash"],
                user_data["full_name"],
                user_data["role"],
                user_data["status"],
                user_data["created_at"]
            ))
            
            # Add user to default organization
            cursor.execute("""
                INSERT INTO user_organizations (user_id, org_id, role, joined_at)
                VALUES (?, ?, ?, ?)
            """, (
                user_data["user_id"],
                "default",
                "member",
                user_data["created_at"]
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET last_login = ? 
                WHERE user_id = ?
            """, (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    def update_user_profile(self, user_id: str, updates: dict) -> bool:
        """Update user profile information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ["full_name", "email", "password_hash"]:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if set_clauses:
                values.append(datetime.now().isoformat())  # updated_at
                values.append(user_id)
                
                query = f"""
                    UPDATE users 
                    SET {', '.join(set_clauses)}, updated_at = ?
                    WHERE user_id = ?
                """
                
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def get_all_users(self) -> List[dict]:
        """Get all users (admin only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, email, full_name, role, status, 
                       created_at, last_login
                FROM users 
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append({
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "full_name": row[3],
                    "role": row[4],
                    "status": row[5],
                    "created_at": row[6],
                    "last_login": row[7]
                })
            
            return users
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def log_user_activity(self, user_id: str, activity_type: str, 
                         resource_type: str, resource_id: str = None, 
                         details: dict = None) -> bool:
        """Log user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_activity_log 
                (user_id, activity_type, resource_type, resource_id, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                activity_type,
                resource_type,
                resource_id,
                str(details) if details else None,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging user activity: {e}")
            return False 