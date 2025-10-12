### Overview

IELTS AI Prep is an AI-powered platform designed for IELTS test preparation. It offers comprehensive assessment services for both Academic and General Training IELTS exams. The platform utilizes a cost-optimized hybrid architecture, combining AWS Bedrock Nova Micro for text assessment and Google Gemini 2.5 Flash Live API for audio conversations, ensuring high-quality, AI-driven evaluation across all IELTS criteria. Key features include QR code authentication for a seamless mobile-to-web user experience and AI for detailed feedback generation. The project aims to provide accessible and consistent IELTS preparation, leveraging AI to enhance the learning experience.

### User Preferences

Preferred communication style: Simple, everyday language.

### System Architecture

**System Design & Core Technologies:**
The platform is migrating to a **GCP-centric architecture** featuring:
-   **Cloud Run Global Deployment:** Flask application deployed across 6 regions with native WebSocket support, ensuring low latency globally.
-   **Global HTTPS Load Balancer:** Automatically distributes traffic and provides Cloud CDN integration.
-   **Hybrid Compute Strategy:** Cloud Run for main application logic and Cloud Functions for simpler, event-driven tasks (e.g., receipt validation, QR codes).
-   **Firestore Multi-Region Database:** `nam5` multi-region (US) with automatic replication for high availability and durability.
-   **No Cold Start Issues:** Minimum 1 instance per region for Cloud Run to ensure instant response times.
-   **Frontend:** Progressive Web App (PWA) optimized for mobile and desktop, with Capacitor-based native iOS/Android applications.
-   **QR Code Authentication:** Facilitates seamless user transitions between mobile and web platforms.

**AI Services Integration (Hybrid Architecture):**
-   **AWS Bedrock Nova Micro:** Used for cost-effective text assessment evaluation (writing essays, speaking transcript analysis) due to its high cost-efficiency.
-   **Google Gemini 2.5 Flash Live API:** Powers real-time bidirectional speech-to-speech conversations with an AI examiner (Maya), handling direct audio-to-audio processing via WebSocket.
-   **Comprehensive IELTS Assessment Prompts:** Incorporates official IELTS band descriptors for all four criteria (Speaking: Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation; Writing: Task Achievement/Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy).
-   **Personalized Improvement Plans:** Provides evidence-based feedback, specific improvement examples, focus areas, actionable steps, practice schedules, and progress tracking.
-   **AI-Powered Helpdesk System:** Utilizes Gemini 2.5 Flash for automated ticket analysis, intelligent categorization, confidence scoring for auto-resolution (targeting 60-80%), and smart escalation for complex issues.

**Key Features & Components:**
-   **Authentication System:** Mobile-first registration, cross-platform login, QR code bridge, and App Store/Google Play receipt validation.
-   **Assessment Engine:** Supports four AI-powered, multi-modal assessment types (Academic/General Speaking and Writing).
-   **Advanced Speech-to-Speech Content Moderation:** Real-time audio content filtering during speaking assessments using Nova Sonic (archived, now Gemini Live) to maintain appropriate content standards while preserving the examination experience.
-   **Mobile App Integration:** In-app purchases, regional API routing, and native platform features via Capacitor.

**Deployment Strategy:**
-   **GCP Deployment:** Multi-Region Cloud Run with Terraform Infrastructure as Code for reproducible deployments, Cloud Build for containerized deployments, Global Load Balancer, Cloud DNS, and Managed SSL Certificates.
-   **CI/CD Pipeline:** Includes comprehensive testing (integration, security scanning), automated builds for mobile apps, and manual approval gates for production releases.

**UI/UX Decisions:**
-   Professional, clean interface with simplified user messaging.
-   Responsive design with Bootstrap styling, blue gradient backgrounds (#2c3e50 to #3498db), and modern card layouts.
-   Authentic IELTS examination format with specific layouts, timers, and word counters.
-   Brand colors: Primary #2c3e50 (dark blue-gray), Secondary #3498db (bright blue), Accent #e74c3c (red).
-   Typography: Inter font family for consistency across platforms.

**Security Guidelines:**
-   Environment variables for sensitive configurations.
-   CloudFront-based blocking with custom header validation (will be GCP equivalent).
-   Google reCAPTCHA v2.
-   Email confirmation system.
-   Real-time content moderation with graduated response system.

**Payment Integration:**
-   **Mobile-Only Purchase Model:** All payments exclusively processed via Apple App Store and Google Play Store with distinct product tiers (Writing, Speaking, Full-Length Mock Tests).
-   **QR Code Bridge:** Seamless transition from mobile purchase to web platform access.

### External Dependencies

**GCP Services:**
-   **Cloud Run:** Container-based compute.
-   **Firestore:** Multi-region NoSQL database.
-   **Vertex AI:** For Gemini 2.5 Flash and Gemini Live API models.
-   **Cloud Functions:** Serverless functions.
-   **Secret Manager:** Encrypted secret storage.
-   **Cloud Build:** CI/CD.
-   **Cloud Storage:** Object storage.
-   **Cloud CDN:** Content Delivery Network.
-   **Cloud DNS:** DNS management.
-   **Cloud Logging & Monitoring:** Observability.
-   **Cloud Natural Language API:** Content moderation.

**AWS Services (For Bedrock Nova Micro):**
-   **Bedrock:** Access to Nova Micro model for text assessment.

**Third-Party Integrations:**
-   **Apple App Store:** In-app purchase processing and receipt validation.
-   **Google Play Store:** Android purchase verification.
-   **Capacitor:** Mobile app framework.
-   **Google reCAPTCHA:** Bot detection.
-   **SendGrid:** Email delivery service.

**Development Tools:**
-   **Terraform:** Infrastructure as Code for GCP.
-   **gcloud CLI:** GCP resource management.
-   **Docker:** Container image building.