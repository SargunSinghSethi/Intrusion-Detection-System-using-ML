from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app.models import User, PcapFile
from app.schemas import HistoryItem
import json

router = APIRouter()

@router.get("/history", response_model=List[HistoryItem])
def get_user_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all PCAP analysis history for the current user"""
    
    pcap_files = db.query(PcapFile).filter(
        PcapFile.user_id == user.id
    ).order_by(PcapFile.created_at.desc()).all()
    
    history = []
    for pcap in pcap_files:
        threats_detected = 0
        severity = "Low"
        
        # Parse result to get threat info
        if pcap.result:
            try:
                result_data = json.loads(pcap.result)
                threats_detected = result_data.get("summary", {}).get("totalThreats", 0)
                
                # Determine severity based on risk score
                risk_score = result_data.get("summary", {}).get("riskScore", 0)
                if risk_score >= 70:
                    severity = "High"
                elif risk_score >= 40:
                    severity = "Medium"
                else:
                    severity = "Low"
            except:
                pass
        
        history.append(HistoryItem(
            pcap_id=pcap.id,
            filename=pcap.filename,
            status=pcap.status,
            threats_detected=threats_detected,
            severity=severity,
            timestamp=pcap.created_at
        ))
    
    return history
