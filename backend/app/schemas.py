from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UploadResponse(BaseModel):
    job_id: int
    message: str

class StatusResponse(BaseModel):
    job_id: int
    status: str
    filename: str

class ThreatDetail(BaseModel):
    id: int
    type: str
    severity: str
    description: str
    confidence: float
    sourceIP: Optional[str] = None
    destinationIP: Optional[str] = None
    port: Optional[int] = None

class ResultSummary(BaseModel):
    totalThreats: int
    riskScore: int
    recommendation: str

class ResultResponse(BaseModel):
    job_id: int
    filename: str
    status: str
    threats: List[ThreatDetail]
    summary: ResultSummary

class HistoryItem(BaseModel):
    pcap_id: int
    filename: str
    status: str
    threats_detected: int
    severity: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
