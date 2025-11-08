import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, FastAPI, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, PcapFile
from app.schemas import UploadResponse
from app.utils.pcap_converter import convert_pcap_to_csv
from app.utils.model_predictor import predict_from_csv
from app.utils.gemini_formatter import format_with_gemini
from datetime import datetime
import shutil, os, uuid, json
import json



router = APIRouter()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
CSV_FOLDER = os.getenv("CSV_FOLDER", "csv_files")
MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")
SCALAR_PATH = os.getenv("SCALAR_PATH", "scalar.joblib")
CHUNK_DIR = "upload_chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)

def process_pcap_file(pcap_id: int, pcap_path: str, filename: str):
    """Background task to process PCAP file"""
    db = next(get_db())
    
    try:
        # Get PCAP record
        pcap_file = db.query(PcapFile).filter(PcapFile.id == pcap_id).first()
        if not pcap_file:
            return
        
        # Update status to processing
        pcap_file.status = "processing"
        db.commit()
        
        # Step 1: Convert PCAP to CSV
        print("Converting PCAP to CSV")
        csv_path = convert_pcap_to_csv(pcap_path, CSV_FOLDER)
        pcap_file.csv_path = csv_path
        db.commit()
        
        print("Successfully Converted to CSV: ${csv_path}")
        # Step 2: Run model prediction
        print("SENT FOR MODEL EVALUATION")
        model_output = predict_from_csv(csv_path, MODEL_PATH, SCALAR_PATH)
        print(model_output)
        # Step 3: Format with Gemini
        gemini_result = format_with_gemini(model_output, filename)
        
        # Step 4: Store result
        pcap_file.result = json.dumps(gemini_result)
        pcap_file.status = "completed"
        pcap_file.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # Handle errors
        pcap_file = db.query(PcapFile).filter(PcapFile.id == pcap_id).first()
        if pcap_file:
            pcap_file.status = "failed"
            pcap_file.error = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/upload", response_model=UploadResponse)
async def upload_pcap(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PCAP file for analysis"""
    
    # Validate file extension
    if not file.filename.endswith(('.pcap', '.pcapng')):
        raise HTTPException(status_code=400, detail="Only PCAP files are allowed")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    
    # Save file
    try:
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record
    pcap_file = PcapFile(
        user_id=user.id,
        filename=file.filename,
        filepath=save_path,
        status="pending"
    )
    db.add(pcap_file)
    db.commit()
    db.refresh(pcap_file)
    
    # Start background processing
    background_tasks.add_task(process_pcap_file, pcap_file.id, save_path, file.filename)
    
    return UploadResponse(
        job_id=pcap_file.id,
        message="File uploaded successfully. Processing started."
    )


@router.post("/upload-chunk")
async def upload_chunk(
    chunk: UploadFile = File(...),
    filename: str = Form(...),
    chunkIndex: int = Form(...),
    totalChunks: int = Form(...),
    uploadId: str = Form(...),
    user: User = Depends(get_current_user)
):
    """Receive a file chunk"""
    user_dir = os.path.join(CHUNK_DIR, uploadId)
    os.makedirs(user_dir, exist_ok=True)
    chunk_path = os.path.join(user_dir, f"chunk_{chunkIndex:05d}")
    with open(chunk_path, "wb") as buffer:
        shutil.copyfileobj(chunk.file, buffer)
    return {"status": "ok", "chunk": chunkIndex}

@router.post("/merge-chunks", response_model=UploadResponse)
async def merge_chunks(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """Merge chunks and start background processing"""
    filename = payload.get("filename")
    uploadId = payload.get("uploadId")
    if not filename or not uploadId:
        raise HTTPException(status_code=400, detail="Missing filename or uploadId")

    user_dir = os.path.join(CHUNK_DIR, uploadId)
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="Chunks not found")

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    final_path = os.path.join(UPLOAD_FOLDER, unique_name)

    with open(final_path, "wb") as merged:
        for chunk_file in sorted(os.listdir(user_dir)):
            with open(os.path.join(user_dir, chunk_file), "rb") as cf:
                shutil.copyfileobj(cf, merged)

    shutil.rmtree(user_dir)

    # Create DB record
    pcap_file = PcapFile(
        user_id=user.id,
        filename=filename,
        filepath=final_path,
        status="pending"
    )
    db.add(pcap_file)
    db.commit()
    db.refresh(pcap_file)

    # Start background processing
    background_tasks.add_task(process_pcap_file, pcap_file.id, final_path, filename)

    return UploadResponse(job_id=pcap_file.id, message="File uploaded successfully and processing started.")