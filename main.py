from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import os
import shutil
from pydantic import BaseModel
from extractor import extract_lab_report
from agent import get_agent_response

from dotenv import load_dotenv
load_dotenv()

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Lab Report Intelligence Agent")

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    query: str

class UpdateResultRequest(BaseModel):
    result_id: int
    new_value: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/upload")
async def upload_report(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "/tmp/uploads" if os.environ.get("VERCEL") else "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Extract data using Gemini
        extracted_data = extract_lab_report(file_path, file.content_type)
        
        # Save report
        db_report = models.Report(
            report_date=extracted_data.report_date,
            file_path=file_path,
            raw_text="Extraction complete"
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        # Save results
        for res in extracted_data.results:
            db_res = models.TestResult(
                report_id=db_report.id,
                test_name=res.test_name,
                value=res.value,
                unit=res.unit,
                reference_range=res.reference_range,
                confidence=res.confidence,
                is_flagged=res.is_flagged
            )
            db.add(db_res)
        
        db.commit()
        return {"message": "Report uploaded and extracted successfully.", "report_id": db_report.id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports")
async def list_reports(db: Session = Depends(get_db)):
    reports = db.query(models.Report).all()
    results = []
    for r in reports:
        tests = db.query(models.TestResult).filter(models.TestResult.report_id == r.id).all()
        results.append({
            "id": r.id,
            "date": r.report_date,
            "tests": [{"id": t.id, "name": t.test_name, "value": t.value, "unit": t.unit, "flag": t.is_flagged, "confidence": t.confidence} for t in tests]
        })
    return {"reports": results}

@app.post("/chat")
async def chat_with_agent(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = get_agent_response(db, req.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_result")
async def update_result(req: UpdateResultRequest, db: Session = Depends(get_db)):
    result = db.query(models.TestResult).filter(models.TestResult.id == req.result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
        
    result.value = req.new_value
    db.commit()
    return {"message": "Result updated successfully"}
