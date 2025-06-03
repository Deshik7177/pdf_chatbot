from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
from typing import List
import uuid
from datetime import datetime

from .database import get_db, create_tables
from .models import Document, Question
from .pdf_processor import PDFProcessor
from .qa_engine import SimpleQAEngine

app = FastAPI(title="PDF Q&A API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_processor = PDFProcessor()
qa_engines = {}  # Store QA engines per document

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "PDF Q&A API is running!"}

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process PDF file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(pdf_processor.upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        text_content = pdf_processor.extract_text_from_pdf(file_path)
        
        # Save to database
        db_document = Document(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            text_content=text_content
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Create and build QA engine
        qa_engine = SimpleQAEngine()
        text_chunks = pdf_processor.chunk_text(text_content)
        qa_engine.build_index(text_chunks)
        qa_engines[db_document.id] = qa_engine
        
        return {
            "message": "File uploaded successfully",
            "document_id": db_document.id,
            "filename": file.filename,
            "text_length": len(text_content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/ask")
async def ask_question(
    document_id: int = Form(...),
    question: str = Form(...),
    db: Session = Depends(get_db)
):
    """Ask question about uploaded document"""
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get QA engine
        qa_engine = qa_engines.get(document_id)
        if not qa_engine:
            # Rebuild QA engine if not in memory
            qa_engine = SimpleQAEngine()
            text_chunks = pdf_processor.chunk_text(document.text_content)
            qa_engine.build_index(text_chunks)
            qa_engines[document_id] = qa_engine
        
        # Get answer
        answer = qa_engine.ask_question(question)
        
        # Save question and answer
        db_question = Question(
            document_id=document_id,
            question_text=question,
            answer_text=answer
        )
        db.add(db_question)
        db.commit()
        
        return {
            "question": question,
            "answer": answer,
            "document_filename": document.original_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    """Get list of uploaded documents"""
    documents = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "filename": doc.original_filename,
            "upload_date": doc.upload_date,
            "text_length": len(doc.text_content) if doc.text_content else 0
        }
        for doc in documents
    ]

@app.get("/documents/{document_id}/questions")
def get_document_questions(document_id: int, db: Session = Depends(get_db)):
    """Get questions asked for a specific document"""
    questions = db.query(Question).filter(Question.document_id == document_id).all()
    return [
        {
            "id": q.id,
            "question": q.question_text,
            "answer": q.answer_text,
            "created_date": q.created_date
        }
        for q in questions
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)