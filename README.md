# AI Catalog Maker Server

A FastAPI backend that turns raw business, product, or service information into an editable one-page catalog. It extracts text from uploads, refines messy input into structured catalog data with an LLM, renders polished HTML, exports a print-ready PDF, and stores generated catalogs in MongoDB.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Data Flow](#data-flow)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Development](#development)

## Overview

AI Catalog Maker Server is the backend for a catalog generation application. The client sends raw source text or extracted document content to the API. The server creates a generation job, runs the job in the background, asks an LLM to normalize the content into a structured catalog schema, renders a complete single-page HTML catalog, exports it as a PDF, and stores the result in MongoDB.

The generated HTML can be edited by the client and saved back to the server. Whenever edited HTML is saved, the backend sanitizes the HTML and re-renders the PDF so the HTML and PDF stay in sync.

## Features

- Document text extraction from PDF, DOCX, and TXT uploads
- Async FastAPI API with background catalog generation jobs
- MongoDB persistence for catalogs, templates, generated HTML, and PDF bytes
- Multiple LLM provider support: Gemini, OpenAI, Anthropic, etc.
- Structured catalog schema validation with Pydantic
- AI freestyle HTML rendering for one-page catalog layouts
- Built-in default template catalog and template previews
- Editable generated HTML workflow
- PDF export with WeasyPrint and optional Playwright Chromium fallback
- HTML sanitization before storing edited or generated HTML
- Saved catalog library endpoints
- CORS and basic security headers for frontend integration

## Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI Catalog Maker Architecture                       │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │   Client     │
                              │ React/Vite   │
                              └──────┬───────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   FastAPI    │
                              │   Server     │
                              └──────┬───────┘
                                     │
             ┌───────────────────────┼────────────────────────┐
             │                       │                        │
             ▼                       ▼                        ▼
     ┌──────────────┐        ┌──────────────┐         ┌──────────────┐
     │ /catalogs    │        │ /catalogs/   │         │ /templates   │
     │ create job   │        │ extract/save │         │ list/detail  │
     └──────┬───────┘        └──────┬───────┘         └──────┬───────┘
            │                       │                        │
            ▼                       ▼                        ▼
┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ Catalog Pipeline      │  │ Editing Pipeline     │  │ Template Service     │
│                       │  │                      │  │                      │
│ queued                │  │ edited HTML          │  │ default templates    │
│   │                   │  │   │                  │  │ seeded on demand     │
│ extracting            │  │ sanitize             │  │                      │
│   │                   │  │   │                  │  │ sample HTML          │
│ refining              │  │ render PDF           │  │ returned to client   │
│   │                   │  │   │                  │  │                      │
│ rendering             │  │ store HTML + PDF     │  │                      │
│   │                   │  └──────────┬───────────┘  └──────────┬───────────┘
│ exporting             │             │                         │
│   │                   │             ▼                         ▼
│ done / failed         │      ┌─────────────────────────────────────┐
└──────────┬────────────┘      │              MongoDB                │
           │                   │ catalogs, templates, HTML, PDF bytes│
           ▼                   └─────────────────────────────────────┘
┌───────────────────────┐
│ External AI Providers │
│ Gemini/OpenAI         │
│ Anthropic             │
└───────────────────────┘
```

## Data Flow

Catalog generation flow:

```text
Raw text -> Create job -> Refine with LLM -> Validate schema -> Render HTML
         -> Sanitize HTML -> Export PDF -> Store in MongoDB -> Return URLs
```

Upload extraction flow:

```text
PDF/DOCX/TXT upload -> Validate extension and size -> Extract text in memory
                    -> Trim to 100,000 chars -> Return plain text
```

Editing flow:

```text
Client edits HTML -> PUT /catalogs/{id}/html -> Sanitize HTML
                  -> Render new PDF -> Store updated catalog
```

Saved library flow:

```text
Generated or edited catalog -> POST /catalogs/{id}/save -> Mark saved
                            -> Appears in /catalogs/saved
```

## Tech Stack

| Component               | Technology                                |
| ----------------------- | ----------------------------------------- |
| Web framework           | FastAPI                                   |
| ASGI server             | Uvicorn                                   |
| Database                | MongoDB                                   |
| Async Mongo driver      | Motor                                     |
| Validation              | Pydantic                                  |
| LLM providers           | Gemini, OpenAI, Anthropic                 |
| HTML rendering          | AI freestyle renderer                     |
| Template previews       | Built-in template service                 |
| PDF export              | WeasyPrint                                |
| PDF fallback            | Playwright Chromium                       |
| PDF/DOCX/TXT extraction | PyMuPDF, python-docx, built-in TXT parser |
| Config                  | python-dotenv                             |

## Prerequisites

Before running the server, install:

- Python 3.10+
- MongoDB, local or Atlas
- At least one LLM provider:
  - Gemini API key, or
  - OpenAI API key, or
  - Anthropic API key

Optional:

- Playwright Chromium for the PDF fallback renderer
- Docker, if you prefer running supporting services in containers

## Installation

From the server folder:

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file inside the `server/` folder:

```env
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=catalog_maker
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEFAULT_LLM_PROVIDER=gemini
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Running the Application

Run the FastAPI server:

```bash
cd server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

Interactive API docs:

- Swagger UI: `http://localhost:8000/docs`

## API Reference

Base URL:

```text
http://localhost:8000
```

### Health

```http
GET /health
```

Returns server health.

## How It Works

### 1. API Request

The client creates a catalog by sending source text and generation options to `POST /api/v1/catalogs`.

The server creates a MongoDB catalog document with status `queued` and starts `catalog_service.run_pipeline` as a FastAPI background task.

### 2. Refinement

The pipeline moves to `refining` and calls the selected LLM provider:

```text
raw source text + style -> LLM provider -> Pydantic Catalog schema
```

The structured schema can contain:

- Brand name
- Hero content
- Overview
- Values and stats
- Products
- Features and benefits
- Specifications
- Pricing
- Testimonials
- FAQs
- Contact details
- Call to action

### 3. Rendering

The pipeline moves to `rendering`. The `FreestyleRenderer` asks the LLM provider to generate a complete one-page HTML catalog using:

- structured catalog data
- theme
- page size
- optional style hint from selected template

The current catalog creation endpoint stores catalogs as A4 pages.

### 4. Sanitization

Generated or edited HTML is passed through the sanitizer before storage. Editor-only attributes and client-side editing UI are expected to be stripped by the client before save, and server sanitization provides an additional safety layer.

### 5. PDF Export

The pipeline moves to `exporting`. `PdfExporter` injects print-fit CSS, renders the HTML to PDF with WeasyPrint, and stores the resulting PDF bytes in MongoDB.

If WeasyPrint fails and Playwright Chromium is installed, the exporter attempts the Chromium fallback.

### 6. Storage

The completed MongoDB catalog document stores:

- source text
- structured refined JSON
- generated or edited HTML
- PDF bytes
- status
- template/style/theme/provider metadata
- saved-library metadata
- timestamps

## Development

Run with auto reload:

```bash
uvicorn app.main:app --reload --port 8000
```

Useful local URLs:

- API health: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`
