from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, PcapFile
from app.schemas import StatusResponse

router = APIRouter()

@router.get("/status/{job_id}", response_model=StatusResponse)
def get_job_status(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current status of a PCAP file processing job"""
    
    pcap_file = db.query(PcapFile).filter(
        PcapFile.id == job_id,
        PcapFile.user_id == user.id
    ).first()
    
    if not pcap_file:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return StatusResponse(
        job_id=pcap_file.id,
        status=pcap_file.status,
        filename=pcap_file.filename
    )
