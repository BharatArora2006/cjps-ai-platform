# CJPS AI Workflow Automation Platform

## Overview

CJPS AI Workflow Automation Platform is a production-grade legal operations system designed to automate process-serving workflows for law firms and legal contractors.

The platform leverages AI-powered document intelligence, workflow automation, and cloud-native architecture to streamline:
- Legal job intake
- Contractor assignment
- Attempt tracking
- Affidavit generation
- Invoice automation
- Payment workflows
- Client communications

Built using FastAPI, PostgreSQL, Supabase, GROQ LLM APIs, Stripe, and Render Cloud Deployment.

---

# Key Features

## AI-Powered Document Processing
- Extracts structured legal case data from unstructured emails and PDF documents
- Uses GROQ LLM APIs for intelligent parsing and summarization
- Automatically identifies:
  - Client details
  - Defendant information
  - Service address
  - County
  - Instructions

---

## Intelligent Contractor Assignment
- Automatically assigns contractors based on:
  - County coverage
  - Active workload
  - Availability

---

## AI-Powered Attempt Notes
- Contractors log service attempts through dashboard
- AI rewrites raw operational notes into professional legal summaries
- Handles typo correction and contextual understanding

### Example

**Raw Note**
```text
No opened the door
```

**AI Note**
```text
Attempted service but no one answered the door.
```

---

## Automated Affidavit Generation
- Generates court-ready affidavit PDFs automatically
- Includes:
  - Attempt history
  - AI-enhanced notes
  - Service details
  - Contractor information

---

## Invoice & Payment Automation
- Auto-generates invoices after job completion
- Stripe payment link integration
- Admin invoice approval workflow
- Final package email delivery to clients

---

## Real-Time Notifications
- Contractor assignment emails
- Attempt update notifications
- Final package delivery emails
- Automated workflow communication using Resend Email API

---

## Analytics Dashboard
- Job tracking
- SLA monitoring
- Contractor activity visibility
- Workflow metrics

---

# Tech Stack

## Backend
- FastAPI
- Python
- PostgreSQL
- SQLAlchemy

## AI / Automation
- GROQ LLM APIs
- Prompt Engineering
- AI Workflow Automation

## Cloud & Infrastructure
- Supabase
- Render
- Stripe API
- Resend Email API

## Frontend
- Jinja2 Templates
- HTML/CSS
- JavaScript

---

# Architecture

```text
Client Email/PDF
        ↓
AI Extraction Engine
        ↓
Job Creation
        ↓
Contractor Assignment
        ↓
Attempt Tracking
        ↓
AI Note Rewriting
        ↓
Affidavit Generation
        ↓
Invoice Generation
        ↓
Payment Workflow
        ↓
Final Client Delivery
```

---

# Security Features

- Password hashing using bcrypt
- Session-based authentication
- Secure cloud document storage
- Environment variable-based secret management

---

# Deployment

The platform is deployed using:
- Render (Application Hosting)
- Supabase (Database + Storage)

---

# Author
## Bharat Arora

MS in Machine Learning & AI  
Scaler Neovarsity × Woolf University
