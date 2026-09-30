# AuraVisual

AuraVisual is a Flask-based website deployed on Google Cloud Run, with a Firestore-backed contact pipeline and SMTP notifications.

The project is structured for low operational overhead, production safety, and fast iteration.

## Table of Contents

- [Overview](#overview)
- [Your Card product page](#your-card-product-page)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Run Locally](#run-locally)
- [Environment Variables](#environment-variables)
- [Contact Form Flow](#contact-form-flow)
- [Security Controls](#security-controls)
- [Deployment](#deployment)
- [Cloud Run Cost Optimization](#cloud-run-cost-optimization)
- [Container Size Notes](#container-size-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

AuraVisual is a modular Flask web application designed for:

- serving a marketing site and product pages
- collecting contact leads safely
- storing requests in Google Firestore
- sending internal notification emails over SMTP
- deploying on Google Cloud Run through Cloud Build
- promoting digital product offers such as the NFC business card landing page

The codebase follows a factory pattern with Blueprints, making it easy to extend and maintain.

## Your Card product page

The project includes a dedicated sales page for the NFC card product under the `/your-card/` route. The page is designed to explain the actual business value of the product:

- replace the traditional paper card with a digital first impression
- redirect customers to the relevant page with a single tap
- direct clients to the company website, portfolio, CV, or campaign destination
- improve engagement during networking, sales meetings, and events

The page is implemented as a separate Flask blueprint and stays consistent with the existing marketing site structure and shared navbar.

Navigation behavior is route-aware:

- homepage (`/`) uses the original section navigation (`#hero`, `#mission`, `#about`, `#team`, `#portfolio`, `#plan`, `#contact`)
- card page (`/your-card/`) uses product-focused anchors (`#hero`, `#benefits`, `#how-it-works`) and still includes a `Home` link back to the homepage

## Key Features

- Flask app factory and Blueprint-based routing
- Contact form with WTForms validation and CSRF protection
- Google reCAPTCHA (standard/free) verification on the backend
- Rate limiting for abuse prevention on form submission
- Firestore persistence for contact requests
- SMTP notification emails with timeout-based sending
- Cloud Run-friendly container setup with Gunicorn
- Static and SEO endpoint cache headers (robots.txt, sitemap.xml)

## Architecture

High-level request flow:

1. User submits the contact form from the frontend.
2. Frontend JavaScript posts the form payload asynchronously.
3. Flask validates CSRF and form fields.
4. Backend verifies reCAPTCHA token with Google.
5. Rate limiter enforces request limits on submission endpoint.
6. Valid payload is saved in Firestore.
7. Notification email is sent through SMTP.
8. JSON response is returned to the frontend.

## Tech Stack

- Python 3.11
- Flask 3.1.1
- Flask-WTF (forms + CSRF)
- Flask-Limiter (rate limiting)
- Google Cloud Firestore (NoSQL)
- Gunicorn (production WSGI server)
- Docker + Cloud Build + Cloud Run

## Project Structure

```text
app.py
aura_visual/
   __init__.py
   config.py
   forms.py
   repositories/
      contact_repository.py
   routes/
      main.py
      your_card.py
   services/
      db.py
   utils/
      email_service.py
   templates/
   static/
cloudbuild.yaml
Dockerfile
requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.11
- pip
- Google Cloud project with Firestore enabled
- SMTP credentials for outgoing mail

### Installation

```bash
git clone <your-repository-url>
cd aura-visual
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Locally

Load environment variables from your shell, then start the app:

```bash
set -a && source .env && set +a
python app.py
```

Alternative (Gunicorn):

```bash
set -a && source .env && set +a
gunicorn --bind :5000 'aura_visual:create_app("production")' --workers 1 --threads 4 --timeout 60
```

## Environment Variables

The application is environment-driven. Do not hardcode secrets.

### Required in Production

- FLASK_SECRET_KEY
- GOOGLE_CLOUD_PROJECT
- MAIL_USERNAME
- MAIL_PASSWORD
- RECAPTCHA_SITE_KEY
- RECAPTCHA_SECRET_KEY

### Common Mail and Runtime Variables

- MAIL_SERVER (default: smtp.zoho.eu)
- MAIL_PORT (default: 587)
- MAIL_USE_TLS (default: True)
- MAIL_USE_SSL (default: False)
- MAIL_DEFAULT_SENDER

### Optional Product Variables

- YOUR_CARD_PRODUCT_NAME
- YOUR_CARD_PRODUCT_DESCRIPTION
- YOUR_CARD_PRODUCT_PRICE
- YOUR_CARD_PRODUCT_CURRENCY

## Contact Form Flow

The contact pipeline includes both user experience and backend safety controls:

- frontend asynchronous submission via fetch
- field-level validation feedback in the UI
- CSRF protection for POST requests
- server-side form validation with WTForms
- backend reCAPTCHA verification against Google API
- endpoint rate limit (currently 5 submissions per hour per client IP)
- Firestore persistence into the contact_requests collection
- SMTP notification email to internal recipients

## Security Controls

- CSRF protection enabled globally
- Input validation and length constraints on all critical fields
- reCAPTCHA verification on the server side
- Rate limiting to reduce spam and abuse cost
- Minimal operational logging for email workflow
- Environment-based secret loading

Important:

- Keep all credentials out of source control.
- Use environment variables or a secrets manager.
- Rotate any key immediately if it is accidentally exposed.

## Deployment

This repository includes a Cloud Build pipeline in cloudbuild.yaml that:

1. Builds the Docker image.
2. Pushes the image to Container Registry.
3. Deploys the service to Cloud Run.

Current Cloud Run tuning in pipeline:

- min instances: 0
- max instances: 3
- concurrency: 20
- memory: 256Mi
- cpu: 1

Deploy command (manual example):

```bash
gcloud run deploy aura-visual \
   --image gcr.io/PROJECT_ID/aura-visual \
   --region europe-north1 \
   --platform managed \
   --allow-unauthenticated
```

## Cloud Run Cost Optimization

For this architecture, the main cost drivers are request volume and compute time, not just image size.

Recommended controls:

- keep min instances at 0 for scale-to-zero
- cap max instances to expected traffic profile
- tune concurrency to reduce cold start pressure and over-scaling
- keep request handlers lightweight and timeout-bounded
- throttle abusive endpoints (already applied to contact form)

When to add GCS/CDN:

- If static traffic grows significantly, serve static assets through Cloud Storage + CDN.
- At low traffic levels, current setup may already be cost-efficient enough.

## Container Size Notes

The current image size is already relatively small for a Python + Flask + Google SDK stack.

You can still reduce it further by:

- removing unused dependencies from requirements.txt
- pinning only required Google client libraries
- reviewing optional packages pulled indirectly

However, a smaller image mostly impacts cold start and transfer time; steady-state Cloud Run cost is usually dominated by CPU/memory usage time and request count.

## Troubleshooting

If contact form submissions fail:

- verify RECAPTCHA_SITE_KEY and RECAPTCHA_SECRET_KEY are set correctly
- verify MAIL_USERNAME and MAIL_PASSWORD are present in runtime env
- verify Firestore permissions for the runtime identity
- inspect Cloud Run logs for validation or connectivity errors

If app startup fails in production:

- ensure FLASK_SECRET_KEY is set (required by production config)
- ensure GOOGLE_CLOUD_PROJECT is configured for Firestore client

## License

This project is distributed under the terms defined in the LICENSE file.