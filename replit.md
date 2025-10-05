### Overview

IELTS GenAI Prep is an AI-powered platform for IELTS test preparation. It offers assessment services for Academic and General Training IELTS. The platform is **migrating from AWS to Google Cloud Platform (GCP)**, transitioning from AWS Lambda to Cloud Run, DynamoDB to Firestore, and AWS Bedrock Nova to Google Gemini 2.5 Flash. The system supports QR code authentication for a seamless mobile-to-web user experience and utilizes AI for comprehensive evaluation across all IELTS criteria. The platform aims to provide high-quality, AI-driven assessment and feedback to help users prepare for the IELTS exam, with a focus on ease of access and consistent user experience across devices.

### GCP Migration Status

**Migration Phase:** Infrastructure Build Complete ✅ - Ready to Deploy
- **Target Go-Live:** TBD (pending UI/pricing testing on test.ieltsaiprep.com)
- **Test Environment:** test.ieltsaiprep.com (isolated data via Firestore collection prefixing)
- **Migration Type:** Direct migration (no live users, full cutover)
- **Cost Savings:** ~23% reduction (~$218/month)
- **Documentation:** 
  - `gcp/QUICK_START.md` - Fast deployment guide
  - `gcp/ISOLATION_GUIDE.md` - Test/production data separation
  - `gcp/GCP_MIGRATION_GUIDE.md` - Comprehensive migration guide
- **Deployment Scripts:**
  - `gcp/deploy_test.sh` - Deploy test environment only
  - `gcp/deploy.sh` - Full production deployment

### User Preferences

Preferred communication style: Simple, everyday language.

### System Architecture

**🚀 NEW: GCP Architecture (Target)**

**Backend Infrastructure:**
- **Cloud Run Multi-Region Deployment** - Flask app on Cloud Run with native WebSocket support across `us-central1`, `europe-west1`, and `asia-southeast1`.
- **Global HTTPS Load Balancer** - Automatic traffic distribution with Cloud CDN, session affinity for WebSocket connections.
- **Hybrid Compute Strategy:**
  - **Cloud Run**: Main Flask application (full features, 60-minute timeout)
  - **Cloud Functions**: Simple tasks (receipt validation, QR codes, session cleanup)
- **Firestore Multi-Region Database** - `nam5` multi-region (US) with automatic replication, 99.999% SLA.
- **No Cold Start Issues** - Minimum 1 instance per region ensures instant response.

**🔧 LEGACY: AWS Architecture (Current - Will be Decommissioned)**

**Backend Infrastructure:**
- **Pure Lambda Handler Architecture** - Eliminated Flask + Gunicorn overhead for maximum serverless performance and minimal cold start latency.
- **Direct API Gateway Integration** - Pure Lambda functions handle requests directly without web framework abstraction layers.
- Multi-region deployment across `us-east-1`, `eu-west-1`, and `ap-southeast-1`.
- API Gateway for regional endpoints and automatic routing.
- WebSocket API for real-time bi-directional communication, especially for Nova Sonic streaming.

**Frontend Architecture:**
- Progressive Web App (PWA) optimized for mobile and desktop.
- Capacitor-based native iOS/Android mobile applications.
- QR Code Authentication for seamless transitions between mobile and web.

**AI Services Integration:**

**🚀 NEW: Google Gemini (GCP)**
- **Gemini 2.5 Flash Live API** for true bidirectional speech-to-speech conversations with AI examiner Maya.
- Direct audio-to-audio processing (16-bit PCM, 16kHz input / 24kHz output) via WebSocket.
- **Gemini 2.5 Flash** for text processing, writing assessment evaluation, and feedback generation.
- Real-time content moderation using Google Cloud Natural Language API.
- Advanced moderation with graduated response system (guidance → redirection → termination).
- Native multilingual support with improved speech recognition.

**🔧 LEGACY: AWS Bedrock (Current)**
- Amazon Nova Sonic for bidirectional speech-to-speech conversations (primarily `us-east-1`).
- Amazon Nova Micro for text processing and assessment evaluation.
- Real-time streaming via WebSockets for speaking assessments.

**Key Components:**
- **Authentication System:** Mobile-first registration and purchase, cross-platform login, 1-hour web session management, and App Store/Google Play receipt validation.
- **Assessment Engine:** Supports four assessment types (Academic/General Speaking and Writing) with AI-powered, multi-modal evaluation.
- **Advanced Speech-to-Speech Content Moderation:** Real-time audio content filtering using Nova Sonic bidirectional streaming, with seamless conversation flow that maintains authentic IELTS examination experience while ensuring appropriate content standards. Features direct audio-to-audio processing without text intermediary.
- **Mobile App Integration:** In-app purchases ($36 per assessment product), regional API routing, native platform features via Capacitor, and flexible dual-platform access.

**Data Flow:**
- **Purchase-to-Assessment:** User purchases in mobile app, receipt is validated, and assessment can be completed on mobile or web.
- **Enhanced Speech Assessment:** Web-based initiation, WebSocket connection to `us-east-1`, true bidirectional audio streaming with Nova Sonic, real-time speech-to-speech content moderation, seamless conversation flow with Maya AI examiner, and detailed feedback generation.

**Deployment Strategy:**

**🚀 NEW: GCP Deployment**
- **Multi-Region Cloud Run** with `us-central1` as primary and `europe-west1`, `asia-southeast1` as secondary.
- **Firestore Multi-Region** (`nam5`) for automatic data replication across all US regions.
- **Terraform Infrastructure as Code** for reproducible deployments.
- **Cloud Build** for containerized deployments with multi-region rollout.
- **Global Load Balancer** with health checks and automatic failover.
- **Cloud DNS** for domain management (migrating from Route 53).
- **Managed SSL Certificates** with auto-renewal.
- **No Cold Starts** - Minimum instances ensure instant response (vs Lambda cold starts).

**🔧 LEGACY: AWS Deployment (Current)**
- Multi-Region Serverless Deployment with `us-east-1` as primary and `eu-west-1`, `ap-southeast-1` as secondary regions.
- DynamoDB Global Tables for cross-region data replication.
- Mobile App Distribution via Apple App Store and Google Play Store, with automated Capacitor build pipeline.
- Development environment integrates Replit with AWS mock services and pure Lambda handler testing.

**CI/CD Pipeline:**
- **Comprehensive Testing**: Integration tests with AWS LocalStack (DynamoDB, Bedrock, Secrets Manager)
- **Security Scanning**: SAST (Bandit), dependency scanning (pip-audit, npm audit), secret scanning (TruffleHog)
- **Test Coverage**: User lifecycle, Nova AI services (Sonic/Micro), WebSocket streaming, receipt validation, multi-region configuration
- **Automated Builds**: Android APK and iOS IPA with production signing
- **Release Approval**: Manual approval gates with GitHub Environments for production releases (draft-by-default)
- **Compliance**: Security checks before release, artifact retention policies, audit trail

**UI/UX Decisions:**
- Professional, clean interface with simplified user messages (e.g., "Maya" as examiner, no technical AWS references).
- Responsive design with professional Bootstrap styling, purple gradient backgrounds, and modern card layouts.
- Authentic IELTS examination format with two-column layouts for writing assessments, timers, and word counters.
- Clear call-to-action buttons, glassmorphism-styled benefit icons, and smooth sequential animations.

**Security Guidelines:**
- Environment variables for all sensitive configuration values.
- CloudFront-based blocking with custom header validation to prevent direct API Gateway access.
- Google reCAPTCHA v2 integration for secure authentication.
- AWS SES email confirmation system for registration and account deletion.
- Real-time content moderation for speaking assessments with graduated response system (mild guidance, redirection, or assessment termination for severe violations).

**Payment Integration:**
- **Mobile-Only Purchase Model:** All payments processed exclusively through Apple App Store and Google Play Store ($36 per assessment package).
- **QR Code Bridge:** Seamless transition from mobile purchase to web platform access via QR code authentication.  
- **No Web Payments:** Zero integration with web-based payment processors - maintaining strict mobile app store compliance.
- **Repurchase Workflow:** Full support for users to repurchase assessments after completion or purchase additional attempts during active assessments, with automatic eligibility checking and purchase history tracking.

### External Dependencies

**🚀 NEW: GCP Services**
- **Cloud Run:** Container-based compute with auto-scaling.
- **Firestore:** Multi-region NoSQL database with automatic replication.
- **Vertex AI:** Access to Gemini 2.5 Flash and Gemini Live API models.
- **Cloud Functions:** Serverless functions for simple tasks.
- **Secret Manager:** Encrypted secret storage with automatic replication.
- **Cloud Build:** Container image building and deployment.
- **Cloud Storage:** Object storage for static assets.
- **Cloud CDN:** Content Delivery Network integrated with Load Balancer.
- **Cloud DNS:** Managed DNS service (migrating from Route 53).
- **Cloud Logging & Monitoring:** Observability and alerting.
- **Cloud Natural Language API:** Content moderation and sentiment analysis.
- **SendGrid (via API):** Email delivery service.

**🔧 LEGACY: AWS Services (Current - Will be Decommissioned)**
- **Lambda:** Serverless compute.
- **DynamoDB Global Tables:** Data storage and replication.
- **Bedrock:** Access to Nova Sonic and Nova Micro models.
- **API Gateway:** REST and WebSocket API management.
- **SES:** Email services.
- **CloudFront:** Content Delivery Network.
- **Route 53:** DNS management.

**Third-Party Integrations (Unchanged):**
- **Apple App Store:** In-app purchase processing and receipt validation.
- **Google Play Store:** Android purchase verification.
- **Capacitor:** Mobile app framework for native device access.
- **Google reCAPTCHA:** Bot detection and security.

**Development Tools:**
- **🚀 NEW: Terraform** - Infrastructure as Code for GCP.
- **🚀 NEW: gcloud CLI** - GCP resource management.
- **Docker** - Container image building for Cloud Run.
- **🔧 LEGACY: Serverless Framework** - AWS infrastructure (will be removed).
- **🔧 LEGACY: AWS CLI** - AWS resource management (will be removed).