# ClarityDoc - Project Specification (SPEC KIT)

## Project Title

**ClarityDoc – Offline AI-Powered Document Simplification Assistant**

---

# Version

v1.0

---

# Problem Statement

Many official documents such as insurance policies, medical reports, legal notices, government letters, and banking documents contain complex terminology that is difficult for ordinary people to understand.

These documents often cause confusion, especially among elderly users, patients, and individuals with limited technical knowledge. Existing AI solutions usually require cloud services, which raise privacy concerns for sensitive personal documents.

ClarityDoc addresses this challenge by providing a completely offline, CPU-powered AI solution that simplifies complex documents into easy-to-understand language while extracting the most important information.

---

# Objective

The objective of ClarityDoc is to:

- Simplify difficult documents into plain language.
- Extract important information automatically.
- Generate actionable summaries.
- Ensure complete offline processing.
- Protect user privacy by avoiding cloud services.

---

# Target Users

- Elderly citizens
- Patients
- Insurance customers
- Government service users
- Students
- General public
- Privacy-conscious users

---

# Input Specification

Supported Input Types:

- PDF Documents
- Scanned Documents
- Images (JPG, PNG, JPEG)
- Printed Letters

Maximum File Size:

- 20 MB

---

# Output Specification

The application generates:

- Document Type
- Plain Language Summary
- Important Dates
- Deadlines
- Action Required
- Contact Information
- Amount Due (if available)
- Priority Level
- Key Highlights

---

# Functional Requirements

## FR-1 Document Upload

The user should be able to upload:

- PDF
- Image
- Scanned document

---

## FR-2 OCR Processing

The system shall extract text from uploaded documents using OCR.

---

## FR-3 Text Preprocessing

The extracted text shall be cleaned by removing unnecessary characters and formatting issues.

---

## FR-4 AI Processing

The local AI model shall analyze the extracted text and identify:

- Document category
- Important entities
- Required actions
- Deadlines
- Contact details

---

## FR-5 Text Simplification

The AI shall rewrite complex language into simple English that can be easily understood by non-technical users.

---

## FR-6 Summary Generation

The system shall generate a concise summary of the uploaded document.

---

## FR-7 Local Storage

All processed documents and summaries shall be stored locally using SQLite.

---

## FR-8 Offline Processing

The application shall work completely without internet connectivity.

---

# Non-Functional Requirements

## Performance

- Response time below 10 seconds for average documents.
- CPU-only execution.
- Low memory consumption.

---

## Security

- No external API usage.
- Local document processing.
- User data never leaves the device.

---

## Reliability

- Works without internet.
- Handles OCR failures gracefully.
- Supports multiple document formats.

---

## Usability

- Simple interface.
- Large readable summaries.
- Easy navigation.

---

# System Workflow

```
User Uploads Document
        │
        ▼
 OCR Text Extraction
        │
        ▼
 Text Cleaning
        │
        ▼
 Local AI Processing
        │
        ▼
 Information Extraction
        │
        ▼
 Plain Language Generation
        │
        ▼
 Summary Generation
        │
        ▼
 Save in SQLite
        │
        ▼
 Display Results
```

---

# AI Workflow

### Step 1

Receive document.

### Step 2

Extract text using OCR.

### Step 3

Preprocess extracted text.

### Step 4

Run local language model.

### Step 5

Extract structured information.

### Step 6

Simplify language.

### Step 7

Generate summary.

### Step 8

Store results locally.

---

# Technology Stack

## Frontend

- HTML
- CSS
- JavaScript
- Bootstrap

## Backend

- Python
- Flask

## OCR

- Tesseract OCR

## AI

- llama.cpp
- ONNX Runtime
- Local Small Language Models

## Database

- SQLite

## Version Control

- Git
- GitLab

---

# Database Schema

## Table: Documents

| Field | Type |
|--------|------|
| id | INTEGER |
| filename | TEXT |
| document_type | TEXT |
| upload_time | DATETIME |
| extracted_text | TEXT |

---

## Table: Summaries

| Field | Type |
|--------|------|
| id | INTEGER |
| document_id | INTEGER |
| summary | TEXT |
| action_required | TEXT |
| deadline | TEXT |
| contact_info | TEXT |
| amount_due | TEXT |
| priority | TEXT |

---

# Sample Input

Medical Report

```
Patient has been prescribed antibiotics for seven days.
Follow-up consultation is scheduled on 15 July 2026.
```

---

# Sample Output

```
Document Type:
Medical Report

Summary:
You need to take antibiotics for 7 days.

Action Required:
Complete medication and visit the doctor.

Deadline:
15 July 2026

Priority:
Medium
```

---

# Constraints

- Offline-first application.
- CPU-only AI inference.
- No cloud APIs.
- Open-source technologies only.
- Local database storage.

---

# Assumptions

- User uploads readable documents.
- OCR quality depends on image clarity.
- AI model is available locally.

---

# Future Scope

- Voice explanation for elderly users.
- Regional language support.
- Mobile application.
- Document translation.
- Smart reminders.
- Accessibility mode.
- AI chatbot for document queries.

---

# Deliverables

- Offline Web Application
- README
- SPEC Document
- Source Code
- SQLite Database
- Documentation
- GitLab Repository

---

# Success Criteria

The project will be considered successful if it:

- Works completely offline.
- Correctly extracts important information.
- Generates understandable summaries.
- Protects user privacy.
- Runs efficiently on CPU.
- Meets hackathon requirements.
