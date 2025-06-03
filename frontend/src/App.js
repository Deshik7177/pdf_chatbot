import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, MessageCircle, FileText, Send, Loader } from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchQuestions = async (documentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/${documentId}/questions`);
      setQuestions(response.data);
    } catch (error) {
      console.error('Error fetching questions:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Notice: No unused variable here — we don't store the response unless we want to use it
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      alert('File uploaded successfully!');
      fetchDocuments();
      event.target.value = '';
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDocumentSelect = (document) => {
    setSelectedDocument(document);
    fetchQuestions(document.id);
    setCurrentQuestion('');
  };

  const handleAskQuestion = async () => {
    if (!currentQuestion.trim() || !selectedDocument) return;

    const formData = new FormData();
    formData.append('document_id', selectedDocument.id);
    formData.append('question', currentQuestion);

    setIsAsking(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, formData);

      const newQuestion = {
        id: Date.now(),
        question: currentQuestion,
        answer: response.data.answer,
        created_date: new Date().toISOString(),
      };

      setQuestions([...questions, newQuestion]);
      setCurrentQuestion('');
    } catch (error) {
      console.error('Error asking question:', error);
      alert('Error processing question. Please try again.');
    } finally {
      setIsAsking(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleAskQuestion();
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>
          <FileText className="icon" />
          PDF Q&A Assistant
        </h1>
        <p>Upload PDF documents and ask questions about their content</p>
      </header>

      <div className="app-content">
        <div className="sidebar">
          <div className="upload-section">
            <h2>
              <Upload className="icon" />
              Upload PDF
            </h2>
            <div className="upload-area">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="file-input"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="upload-label">
                {isUploading ? (
                  <div className="upload-progress">
                    <Loader className="icon spinning" />
                    <span>Uploading... {uploadProgress}%</span>
                  </div>
                ) : (
                  <span>Choose PDF File</span>
                )}
              </label>
            </div>
          </div>

          <div className="documents-section">
            <h2>
              <FileText className="icon" />
              Documents ({documents.length})
            </h2>
            <div className="documents-list">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className={`document-item ${selectedDocument?.id === doc.id ? 'selected' : ''}`}
                  onClick={() => handleDocumentSelect(doc)}
                >
                  <div className="document-name">{doc.filename}</div>
                  <div className="document-info">
                    <span>{new Date(doc.upload_date).toLocaleDateString()}</span>
                    <span>{Math.round(doc.text_length / 1000)}k chars</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="main-content">
          {selectedDocument ? (
            <>
              <div className="document-header">
                <h2>{selectedDocument.filename}</h2>
                <p>Ask questions about this document</p>
              </div>

              <div className="questions-section">
                <div className="questions-list">
                  {questions.map((q) => (
                    <div key={q.id} className="question-item">
                      <div className="question">
                        <MessageCircle className="icon" />
                        <span>{q.question}</span>
                      </div>
                      <div className="answer">
                        <span>{q.answer}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="question-input">
                  <textarea
                    value={currentQuestion}
                    onChange={(e) => setCurrentQuestion(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about this document..."
                    disabled={isAsking}
                    rows="3"
                  />
                  <button
                    onClick={handleAskQuestion}
                    disabled={!currentQuestion.trim() || isAsking}
                    className="ask-button"
                  >
                    {isAsking ? (
                      <Loader className="icon spinning" />
                    ) : (
                      <Send className="icon" />
                    )}
                    {isAsking ? 'Processing...' : 'Ask'}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="no-document">
              <FileText className="icon large" />
              <h2>No Document Selected</h2>
              <p>Upload a PDF document or select one from the sidebar to start asking questions.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
