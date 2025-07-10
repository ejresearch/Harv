# Add this to fix the /me endpoint
@router.get("/me", response_model=None)
def get_current_user_profile(current_user: User = Depends(get_current_user_dependency)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at
    }
