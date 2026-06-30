# ClarityDoc

> **ClarityDoc is an offline-first, CPU-powered AI application that transforms complex documents such as insurance policies, medical reports, government notices, legal letters, and official documents into simple, easy-to-understand language while extracting actionable information for users.**

---

# 📖 Overview

Every day, millions of people receive important documents filled with technical terminology and lengthy explanations. Insurance policies, medical reports, legal notices, government letters, and banking documents are often difficult for ordinary people to understand. This problem becomes even more challenging for elderly people, individuals with low digital literacy, and people with limited education.

ClarityDoc solves this problem by allowing users to upload a document or image. The application processes the document completely offline using CPU-optimized AI models, extracts the important information, simplifies the language into plain English, highlights deadlines and actions, and generates an easy-to-read summary without sending any data to the cloud.

---

# 🚨 Problem Statement

People frequently struggle to understand complex official documents because they contain technical, legal, or medical terminology. Misunderstanding these documents can lead to missed deadlines, incorrect decisions, financial losses, and unnecessary stress.

Existing AI-powered document assistants usually rely on cloud-based APIs, raising privacy concerns since sensitive documents such as medical records and insurance policies are uploaded to external servers.

The challenge is to create an intelligent solution that works completely offline while preserving user privacy and making complex documents understandable for everyone.

---

# 💡 Proposed Solution

ClarityDoc is an AI-powered document simplification assistant that works entirely offline.

The application accepts scanned documents, PDFs, or images, extracts text using OCR, processes the content with a lightweight local language model, and produces:

- Plain-language summary
- Important action items
- Deadlines
- Amounts due
- Contact information
- Priority level
- Easy explanation for elderly users

All processing happens locally on the user's device without requiring an internet connection.

---

# 🎯 Objectives

- Simplify complex documents into plain language.
- Improve accessibility for elderly and non-technical users.
- Protect sensitive information through offline processing.
- Automatically extract important information from documents.
- Reduce time spent understanding official documents.
- Provide an easy and user-friendly interface.

---

# 👥 Target Users

- Elderly people
- Patients
- Insurance policy holders
- Students
- Government service users
- Citizens receiving official notices
- People with low literacy
- Individuals concerned about document privacy

---

# ✨ Features

- Completely Offline Processing
- CPU-Optimized AI Models
- OCR-based Document Reading
- Plain Language Conversion
- Important Information Extraction
- Action Checklist Generation
- Deadline Detection
- Contact Information Extraction
- Amount Due Identification
- Priority Detection
- Privacy-First Design
- Local SQLite Storage
- User-Friendly Interface
- Fast Processing
- Secure Local Data Handling

---

# ⚙️ Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

## Backend

- Python
- Flask

## AI & Machine Learning

- Local Small Language Model (SLM)
- llama.cpp
- ONNX Runtime (CPU)

## OCR

- Tesseract OCR

## Database

- SQLite

## Other Tools

- Git
- GitLab
- Python Virtual Environment

---

# 🏗️ System Architecture

```
                User Uploads Document
                        │
                        ▼
              Image / PDF Processing
                        │
                        ▼
                OCR Text Extraction
                        │
                        ▼
          Text Cleaning & Preprocessing
                        │
                        ▼
      Local AI Language Model Processing
                        │
                        ▼
      Structured Information Extraction
                        │
                        ▼
       Plain Language Simplification
                        │
                        ▼
        Action Items & Summary Generation
                        │
                        ▼
            Store Results in SQLite
                        │
                        ▼
             Display Results to User
```

---

# 🔄 Workflow

### Step 1

User uploads a PDF, scanned document, or image.

### Step 2

The application extracts text using OCR.

### Step 3

The extracted text is cleaned and preprocessed.

### Step 4

A lightweight local AI model analyzes the document.

### Step 5

The AI identifies:

- Document type
- Important information
- Deadlines
- Contact details
- Required actions
- Important amounts

### Step 6

The AI rewrites the content into simple everyday language.

### Step 7

A structured summary is generated.

### Step 8

Results are stored locally and shown to the user.

---

# 📊 Expected Output

For every uploaded document, ClarityDoc provides:

- Plain Language Summary
- Document Category
- Important Dates
- Action Required
- Deadline
- Contact Details
- Amount Due
- Urgency Level
- Key Highlights
- Easy Explanation for Elderly Users

---

# 🧠 AI Components

- Optical Character Recognition (OCR)
- Natural Language Processing (NLP)
- Text Simplification
- Named Entity Recognition
- Information Extraction
- Local Small Language Models
- Structured JSON Generation
- Rule-Based Validation

---

# 🔒 Privacy & Security

ClarityDoc follows a privacy-first approach.

- No internet connection required.
- No cloud storage.
- No external API usage.
- All AI inference runs locally.
- Documents never leave the user's device.
- Sensitive information remains secure.
- Local SQLite database for storage.

---

# 🚀 Future Enhancements

- Voice Explanation for Elderly Users
- Regional Language Support
- Document Translation
- Mobile Application
- Smart Search
- Document History
- PDF Export
- Reminder Notifications
- Accessibility Mode
- AI Chat Assistant for Documents

---

# 📅 Development Roadmap

## Phase 1

- Project Planning
- Repository Setup
- README Documentation
- System Architecture
- Specification Design

## Phase 2

- OCR Integration
- AI Model Integration
- Backend Development
- Frontend Development
- Database Design

## Phase 3

- Testing
- Performance Optimization
- Documentation
- Deployment
- User Feedback
- Final Presentation

---

# 📂 Project Structure

```
ClarityDoc/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── database/
│   └── claritydoc.db
│
├── models/
│
├── uploads/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── upload.html
│   └── result.html
│
├── utils/
│   ├── ocr.py
│   ├── preprocess.py
│   ├── summarizer.py
│   └── extractor.py
│
└── docs/
```

---

# 🌟 Key Benefits

- Works completely offline
- Protects user privacy
- No cloud dependency
- Fast CPU-based inference
- Easy for elderly users
- Supports multiple document types
- Reduces confusion caused by technical language
- Improves accessibility
- Saves time
- Helps users make informed decisions

---

# 🎯 Hackathon Requirements Covered

✅ Offline-First Application

✅ CPU-Optimized AI

✅ Local AI Inference

✅ OCR-Based Document Processing

✅ Structured Data Extraction

✅ SQLite Local Storage

✅ No External APIs

✅ Privacy-Preserving Design

✅ Open Source Ready

---

# 🛠️ Getting Started

## Prerequisites

- Python 3.10 or higher
- Tesseract OCR installed on your system
  - **Windows:** [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - **macOS:** `brew install tesseract`
  - **Linux:** `sudo apt install tesseract-ocr`

## Installation

```bash
# Clone the repository
git clone https://code.swecha.org/Amanmouriya/clarity_doc.git
cd clarity_doc

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

# 👨‍💻 Team

**Team Name:** Code Crackers

Project Members:

- Aman Kumar
- Dhruvika

---

# 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [LICENSE](LICENSE) for details.

---

# 🙏 Acknowledgements

We thank the organizers of the CPU-First Offline AI Hackathon for encouraging privacy-preserving, offline, and efficient AI applications that solve real-world problems while ensuring user data remains secure.

---

# 📬 Repository

GitLab Repository: [https://code.swecha.org/Amanmouriya/clarity_doc](https://code.swecha.org/Amanmouriya/clarity_doc)

---

## One-Line Project Description

**ClarityDoc is an offline AI-powered document assistant that converts complex insurance, medical, legal, and government documents into simple language while extracting actionable insights securely on the user's device.**
