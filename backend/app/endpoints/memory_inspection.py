# Memory Inspection Endpoint
# Save as: backend/app/endpoints/memory_inspection.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.database import get_db
from app.memory_context_enhanced import DynamicMemoryAssembler

router = APIRouter()

class MemoryInspectionRequest(BaseModel):
    user_id: int
    module_id: int
    current_message: Optional[str] = ""
    conversation_id: Optional[str] = None

@router.post("/memory/inspect")
async def inspect_memory(request: MemoryInspectionRequest, db: Session = Depends(get_db)):
    """Inspect assembled memory context for debugging"""
    
    try:
        memory_assembler = DynamicMemoryAssembler(db)
        
        memory_context = memory_assembler.assemble_dynamic_context(
            user_id=request.user_id,
            module_id=request.module_id,
            current_message=request.current_message,
            conversation_id=request.conversation_id
        )
        
        return {
            "assembled_prompt": memory_context['assembled_prompt'],
            "context_metrics": memory_context['context_metrics'],
            "memory_layers": memory_context['memory_layers'],
            "database_status": memory_context['database_status'],
            "conversation_id": memory_context['conversation_id']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory inspection failed: {str(e)}")

@router.get("/memory/stats/{user_id}")
async def get_memory_stats(user_id: int, db: Session = Depends(get_db)):
    """Get memory statistics for a user"""
    
    try:
        memory_assembler = DynamicMemoryAssembler(db)
        
        # Get stats for all modules
        stats = []
        for module_id in range(1, 16):  # Your 15 modules
            context = memory_assembler.assemble_dynamic_context(
                user_id=user_id,
                module_id=module_id
            )
            
            stats.append({
                "module_id": module_id,
                "context_length": context['context_metrics']['total_chars'],
                "optimization_score": context['context_metrics']['optimization_score'],
                "layers_active": sum(1 for status in context['database_status'].values() if status)
            })
        
        return {
            "user_id": user_id,
            "total_modules": 15,
            "module_stats": stats,
            "average_context_length": sum(s['context_length'] for s in stats) / len(stats),
            "average_optimization": sum(s['optimization_score'] for s in stats) / len(stats)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory stats failed: {str(e)}")

@router.get('/enhanced/{module_id}')
async def get_enhanced_memory(module_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """Get enhanced memory status for GUI"""
    try:
        from app.memory_context_enhanced import DynamicMemoryAssembler
        assembler = DynamicMemoryAssembler(db)
        context = assembler.assemble_dynamic_context(user_id=user_id, module_id=module_id)
        return {
            'status': 'available',
            'context_length': context['context_metrics']['total_chars'],
            'layers_active': sum(1 for status in context['database_status'].values() if status),
            'optimization_score': context['context_metrics']['optimization_score']
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
