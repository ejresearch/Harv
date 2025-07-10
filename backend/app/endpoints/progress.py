"""
Complete Progress Tracking Endpoints for Primer Initiative
Drop this file as: app/endpoints/progress.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app.schemas import (
    ProgressUpdateRequest, ProgressResponse, UserStatsResponse,
    MessageResponse
)
from app.models import User, UserProgress, Module

router = APIRouter(prefix="/user", tags=["Progress"])

# ===== PROGRESS ENDPOINTS =====

@router.get("/progress", response_model=List[ProgressResponse])
async def get_user_progress(
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Get user's progress across all modules"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()
    
    return [ProgressResponse.from_orm(p) for p in progress]

@router.get("/progress/{module_id}", response_model=ProgressResponse)
async def get_module_progress(
    module_id: int,
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Get user's progress for a specific module"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.module_id == module_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this module"
        )
    
    return ProgressResponse.from_orm(progress)

@router.put("/progress", response_model=ProgressResponse)
async def update_user_progress(
    request: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Update user's progress for a module"""
    # Check if module exists
    module = db.query(Module).filter(Module.id == request.module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Get or create progress record
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.module_id == request.module_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            module_id=request.module_id,
            completed=False,
            time_spent=0,
            attempts=0,
            created_at=datetime.utcnow()
        )
        db.add(progress)
    
    # Update progress
    progress.completed = request.completed
    progress.grade = request.grade
    progress.updated_at = datetime.utcnow()
    
    if request.completed and not progress.completion_date:
        progress.completion_date = datetime.utcnow()
    
    progress.attempts += 1
    
    db.commit()
    db.refresh(progress)
    
    return ProgressResponse.from_orm(progress)

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Get comprehensive user statistics"""
    # Get total modules
    total_modules = db.query(Module).count()
    
    # Get user progress
    progress_query = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    )
    
    all_progress = progress_query.all()
    completed_progress = progress_query.filter(
        UserProgress.completed == True
    ).all()
    
    # Calculate stats
    completed_modules = len(completed_progress)
    completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    total_time_spent = sum(p.time_spent for p in all_progress)
    
    # Calculate average grade (simplified)
    grades_with_values = []
    for p in completed_progress:
        if p.grade:
            grade_value = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}.get(p.grade, 0)
            grades_with_values.append(grade_value)
    
    average_grade = None
    if grades_with_values:
        avg_val = sum(grades_with_values) / len(grades_with_values)
        grade_map = {4: 'A', 3: 'B', 2: 'C', 1: 'D', 0: 'F'}
        average_grade = grade_map.get(round(avg_val), 'C')
    
    return UserStatsResponse(
        total_modules=total_modules,
        completed_modules=completed_modules,
        completion_rate=round(completion_rate, 2),
        average_grade=average_grade,
        total_time_spent=total_time_spent,
        progress=[ProgressResponse.from_orm(p) for p in all_progress]
    )

@router.post("/progress/{module_id}/time", response_model=MessageResponse)
async def update_time_spent(
    module_id: int,
    time_spent: int,
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Update time spent on a module"""
    # Get or create progress record
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.module_id == module_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            module_id=module_id,
            completed=False,
            time_spent=0,
            attempts=0,
            created_at=datetime.utcnow()
        )
        db.add(progress)
    
    # Update time spent
    progress.time_spent += time_spent
    progress.updated_at = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(
        message=f"Time updated: {time_spent} seconds added",
        success=True
    )

@router.delete("/progress/{module_id}", response_model=MessageResponse)
async def reset_module_progress(
    module_id: int,
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Reset progress for a specific module"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.module_id == module_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this module"
        )
    
    # Reset progress
    progress.completed = False
    progress.grade = None
    progress.completion_date = None
    progress.time_spent = 0
    progress.attempts = 0
    progress.updated_at = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(
        message="Module progress reset successfully",
        success=True
    )
