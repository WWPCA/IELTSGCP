### Overview

IELTS AI Prep is an AI-powered platform designed for IELTS test preparation. It offers comprehensive assessment services for both Academic and General Training IELTS exams. The platform utilizes a cost-optimized hybrid architecture, combining AWS infrastructure with Google AI services for optimal performance and cost efficiency. Key features include QR code authentication for a seamless mobile-to-web user experience and AI-driven detailed feedback generation. The project aims to provide accessible and consistent IELTS preparation, leveraging the best of AWS and Google Cloud AI to enhance the learning experience.

### User Preferences

Preferred communication style: Simple, everyday language.

### System Architecture

**System Design & Core Technologies:**
The platform uses a **hybrid AWS-Google Cloud architecture** featuring:
-   **AWS Lambda Deployment:** Serverless Flask application with automatic scaling and pay-per-use pricing.
-   **AWS DynamoDB:** NoSQL database for user data, sessions, assessments, and QR tokens with global tables support.
-   **API Gateway:** RESTful API management with custom domain support and request throttling.
-   **CloudFront CDN:** Global content delivery with edge caching and custom header-based access control.
-   **Frontend:** Progressive Web App (PWA) optimized for mobile and desktop, with Capacitor-based native iOS/Android applications.
-   **QR Code Authentication:** Facilitates seamless user transitions between mobile and web platforms.

**AI Services Integration (Hybrid Architecture with Global Regional Optimization):**
-   **AWS Bedrock Nova Micro:** Cost-effective text assessment evaluation for writing essays and reading/listening comprehension. Provides detailed scoring against official IELTS band descriptors. (~$0.003 per writing assessment)
-   **Google Gemini 2.5 Flash Lite & Flash (Regional Smart Selection with DSQ):** Powers real-time speech-to-speech conversations with an AI examiner (Maya) through 21 global regions with Dynamic Shared Quota:
    -   **Global Coverage:** 77 countries mapped to optimal regions for minimal latency
    -   **Smart Model Selection:** Dynamically switches between Flash Lite (Part 1) and Flash (Parts 2-3)
    -   **Regional Endpoints:** Africa (1), Asia (6), Australia (1), Europe (8), Middle East (2), Americas (3)
    -   **Dynamic Shared Quota (DSQ):** Automatic capacity distribution across regions without manual quota management
    -   **Latency Optimization:** 50-70% latency reduction for Asian users, 30-40% for European users
    -   **Health Monitoring:** Automatic failover to healthy regions with real-time health checks
    -   **Cost:** ~$0.025 per complete speaking assessment (no additional infrastructure costs)
-   **Comprehensive IELTS Assessment Prompts:** Incorporates official IELTS band descriptors for all four criteria (Speaking: Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation; Writing: Task Achievement/Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy).
-   **Personalized Improvement Plans:** Provides evidence-based feedback, specific improvement examples, focus areas, actionable steps, practice schedules, and progress tracking.
-   **AI-Powered Helpdesk System:** Utilizes Gemini 2.5 Flash for automated ticket analysis, intelligent categorization, confidence scoring for auto-resolution (targeting 60-80%), and smart escalation for complex issues.

**Key Features & Components:**
-   **Authentication System:** Mobile-first registration, cross-platform login, QR code bridge, and App Store/Google Play receipt validation.
-   **Assessment Engine:** Supports four AI-powered, multi-modal assessment types (Academic/General Speaking and Writing).
-   **Advanced Real-time Content Moderation:** Audio content filtering during speaking assessments to maintain appropriate content standards while preserving the examination experience.
-   **Mobile App Integration:** In-app purchases, regional API routing, and native platform features via Capacitor.

**Deployment Strategy:**
-   **AWS Lambda Deployment:** Serverless compute with automatic scaling, packaged with all dependencies in `/deployment` folder.
-   **DynamoDB Tables:** User data, sessions, assessments, QR tokens with on-demand billing and point-in-time recovery.
-   **CloudFormation Templates:** Infrastructure as Code for reproducible AWS deployments.
-   **CI/CD Pipeline:** Includes comprehensive testing (integration, security scanning), automated builds for mobile apps, and deployment automation.
-   **Route 53 DNS:** Custom domain management with health checks and failover support.

**UI/UX Decisions:**
-   Professional, clean interface with simplified user messaging.
-   Responsive design with Bootstrap styling, blue gradient backgrounds (#2c3e50 to #3498db), and modern card layouts.
-   Authentic IELTS examination format with specific layouts, timers, and word counters.
-   Brand colors: Primary #2c3e50 (dark blue-gray), Secondary #3498db (bright blue), Accent #e74c3c (red).
-   Typography: Inter font family for consistency across platforms.

**Security Guidelines:**
-   Environment variables for sensitive configurations (AWS credentials, API keys, session secrets).
-   CloudFront-based access control with custom header validation.
-   Google reCAPTCHA v2 for bot protection.
-   Email confirmation system with secure token generation via AWS SES.
-   Real-time content moderation with graduated response system.
-   DynamoDB encryption at rest and in transit.

**Payment Integration:**
-   **Mobile-Only Purchase Model:** All payments exclusively processed via Apple App Store and Google Play Store with distinct product tiers (Writing, Speaking, Full-Length Mock Tests).
-   **QR Code Bridge:** Seamless transition from mobile purchase to web platform access with secure token validation.

### External Dependencies

**AWS Services:**
-   **Lambda:** Serverless compute for application logic.
-   **DynamoDB:** NoSQL database for user data, sessions, assessments.
-   **Bedrock:** Access to Nova Micro model for text assessment (~$0.15 per 1M input tokens, $0.60 per 1M output tokens).
-   **SES (Simple Email Service):** Email delivery for verification and notifications.
-   **CloudFront:** Global CDN and edge security.
-   **Route 53:** DNS management and routing policies.
-   **S3:** Static asset storage and audio/image files for tests.
-   **CloudWatch:** Logging, monitoring, and alerting.
-   **Systems Manager:** Parameter store for configuration.
-   **WAF:** Web Application Firewall for bot protection (replaces Google reCAPTCHA).

**Google Cloud Services (Single Service Only):**
-   **Vertex AI:** EXCLUSIVELY for Gemini 2.5 Flash Lite and Flash models via Google GenAI SDK with Dynamic Shared Quota (DSQ) across 21 regions. This is the ONLY Google service used in the architecture.

**Third-Party Integrations:**
-   **Apple App Store:** In-app purchase processing and receipt validation.
-   **Google Play Store:** Android purchase verification.
-   **Capacitor:** Mobile app framework for iOS/Android native features.

**Development Tools:**
-   **AWS SAM/CloudFormation:** Infrastructure as Code for AWS.
-   **AWS CLI:** AWS resource management and deployment.
-   **boto3:** AWS SDK for Python integration.
-   **Google GenAI SDK:** Integration with Gemini models.

### Recent Architecture Changes (October 2025)

**Migration from GCP to AWS (October 2025):**
-   Transitioned from Cloud Run to AWS Lambda for serverless compute with better cold start performance.
-   Migrated from Firestore to DynamoDB for improved single-digit millisecond latency and simpler pricing.
-   Consolidated infrastructure to AWS for unified billing and management.
-   Retained Google Gemini models for speaking assessment due to superior audio processing capabilities.
-   Smart Selection optimization reduces Gemini costs by 58% through dynamic model switching.

**Key Files & Components:**
-   `/deployment/` - Complete AWS Lambda deployment package with all dependencies
-   `/deployment/lambda_handler.py` - Lambda entry point using awsgi
-   `/deployment/app.py` - Main Flask application configured for Lambda (2,051 lines)
-   `/deployment/bedrock_service.py` - AWS Bedrock Nova Micro integration (484 lines)
-   `/deployment/dynamodb_dal.py` - DynamoDB data access layer (371 lines)
-   `gemini_live_audio_service_smart.py` - Gemini smart selection for speaking (444 lines)
-   `ielts_workflow_manager.py` - IELTS part-based workflow orchestration

**DynamoDB Tables:**
-   `ielts-genai-prep-users` - User accounts with email as primary key
-   `ielts-genai-prep-sessions` - Active sessions with TTL for auto-cleanup
-   `ielts-genai-prep-assessments` - Assessment results with user_id GSI
-   `ielts-genai-prep-qr-tokens` - QR authentication tokens with 5-min TTL
-   `ielts-genai-prep-entitlements` - User purchase and subscription data
-   `ielts-assessment-questions` - Question bank for all assessment types
-   `ielts-assessment-rubrics` - Official IELTS scoring rubrics
-   `ielts-ai-safety-logs` - AI content moderation logs
-   `ielts-content-reports` - User-reported content tracking
