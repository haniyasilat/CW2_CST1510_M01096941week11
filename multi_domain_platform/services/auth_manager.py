import bcrypt

class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def register_user_with_role(self, username, password, role="user"):
        """Register a new user with a specific role."""
        # Check if username exists
        existing = self.db.fetch_one("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if existing and existing[0] > 0:
            raise ValueError("Username already exists")
        
        # Validate role
        valid_roles = ["admin", "analyst", "researcher", "technician", "user"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Insert user with role
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash.decode('utf-8'), role)
        )
    
    def login_user_with_role(self, username, password):
        """Login user and return user data including role."""
        # Get user from database
        result = self.db.fetch_one(
            "SELECT password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        
        if result and result[0]:
            stored_hash = result[0].encode('utf-8')
            if bcrypt.checkpw(password.encode(), stored_hash):
                return {
                    'username': username,
                    'role': result[1] if result[1] else 'user'
                }
        return None
    
    # Keep original methods for backward compatibility
    def register_user(self, username, password):
        return self.register_user_with_role(username, password, "user")
    
    def login_user(self, username, password):
        user_data = self.login_user_with_role(username, password)
        return user_data is not None
    
    def get_user_role(self, username):
        """Get role of a specific user."""
        result = self.db.fetch_one(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        )
        return result[0] if result else None