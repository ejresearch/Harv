# Add this to the end of app/auth.py
def get_current_user_optional():
    """Simple optional user dependency that actually works"""
    def dependency(
        db: Session = Depends(get_db),
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ):
        if not credentials:
            return None
        
        token_data = verify_token(credentials.credentials)
        if not token_data:
            return None
        
        return get_user_by_id(db, token_data["user_id"])
    
    return dependency
