import re
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, PcapFile
from app.schemas import ResultResponse

router = APIRouter()

def _parse_port_and_service(value):
    # Accept int, numeric string, or labeled like "80 (HTTP)"
    if value is None:
        return None, None
    if isinstance(value, int):
        return value, None
    if isinstance(value, str):
        # extract leading digits
        m = re.match(r"\s*(\d+)", value)
        port = int(m.group(1)) if m else None
        # optional service in parentheses
        m2 = re.search(r"\(([^)]+)\)", value)
        service = m2.group(1).strip() if m2 else None
        return port, service
    # unknown type -> None
    return None, None

@router.get("/result/{job_id}", response_model=ResultResponse)
def get_job_result(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the analysis result for a completed PCAP file"""
    pcap_file = db.query(PcapFile).filter(
        PcapFile.id == job_id,
        PcapFile.user_id == user.id
    ).first()

    if not pcap_file:
        raise HTTPException(status_code=404, detail="Job not found")

    if pcap_file.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed yet. Current status: {pcap_file.status}"
        )

    # Parse result JSON
    try:
        result_data = json.loads(pcap_file.result)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse result data")

    raw_threats = result_data.get("threats", [])

    sanitized_threats = []
    for t in raw_threats:
        t = dict(t) if isinstance(t, dict) else {}
        port_val, service_val = _parse_port_and_service(t.get("port"))
        # enforce types expected by ThreatDetail in schemas.py
        sanitized = {
            "id": t.get("id"),
            "type": t.get("type"),
            "severity": t.get("severity"),
            "description": t.get("description"),
            "confidence": t.get("confidence"),
            "sourceIP": t.get("sourceIP"),
            "destinationIP": t.get("destinationIP"),
            "port": port_val,            # must be int or None
        }
        # keep a UI-friendly field if present; schemas.py doesn’t declare it, so
        # include it only in result_data passthroughs or ignore for strict model.
        if service_val:
            sanitized["service"] = service_val  # optional extra for clients that read it

        sanitized_threats.append(sanitized)

    return ResultResponse(
        job_id=pcap_file.id,
        filename=pcap_file.filename,
        status=pcap_file.status,
        threats=sanitized_threats,
        summary=result_data.get("summary", {
            "totalThreats": 0,
            "riskScore": 0,
            "recommendation": "No analysis available"
        })
    )
