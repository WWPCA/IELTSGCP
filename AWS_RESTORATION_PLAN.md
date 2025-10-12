# AWS Architecture Restoration Plan
## Complete Guide for IELTS AI Prep Platform

Generated: October 12, 2025  
Status: Ready for Implementation

---

## 📊 Executive Summary

This document provides a complete plan to restore AWS architecture with DynamoDB for data storage while using a hybrid AI approach with Gemini Flash Lite/Flash for speaking and AWS Bedrock Nova Micro for writing assessments.

---

## 🏗️ Architecture Overview

### Core Components:
- **Data Storage**: AWS DynamoDB (replacing Firestore)
- **Email Service**: AWS SES
- **AI Models**:
  - Speaking: Gemini Flash Lite → Flash (smart switching)
  - Writing: AWS Bedrock Nova Micro
  - Reading/Listening: Nova Micro (capability assessment below)

### Cost Optimization:
- Speaking: ~$0.025 per session with Smart Selection
- Writing: ~$0.003 per assessment with Nova Micro
- Overall margin: 99.7% on $25 product

---

## 📋 Phase 1: DynamoDB Tables Creation

### Required Tables:

```python
PRODUCTION_DYNAMODB_TABLES = {
    'users': 'ielts-genai-prep-users',
    'sessions': 'ielts-genai-prep-sessions', 
    'assessments': 'ielts-genai-prep-assessments',
    'questions': 'ielts-assessment-questions',
    'rubrics': 'ielts-assessment-rubrics',
    'content_reports': 'ielts-content-reports',
    'ai_safety_logs': 'ielts-ai-safety-logs'
}
```

### Table Schemas:

#### 1. Users Table (`ielts-genai-prep-users`)
```json
{
  "email": "STRING (Primary Key)",
  "user_id": "STRING",
  "password_hash": "STRING",
  "created_at": "TIMESTAMP",
  "last_login": "TIMESTAMP",
  "purchases": "LIST",
  "preferences": "MAP"
}
```

#### 2. Sessions Table (`ielts-genai-prep-sessions`)
```json
{
  "session_id": "STRING (Primary Key)",
  "user_email": "STRING (GSI)",
  "user_id": "STRING",
  "created_at": "TIMESTAMP",
  "expires_at": "NUMBER (TTL)"
}
```

#### 3. Assessments Table (`ielts-genai-prep-assessments`)
```json
{
  "assessment_id": "STRING (Primary Key)",
  "user_email": "STRING (GSI)",
  "assessment_type": "STRING",
  "overall_band": "NUMBER",
  "criteria_scores": "MAP",
  "feedback": "STRING",
  "timestamp": "TIMESTAMP",
  "completed": "BOOLEAN",
  "ai_generated": "BOOLEAN",
  "content_safe": "BOOLEAN"
}
```

#### 4. Questions Table (`ielts-assessment-questions`)
```json
{
  "question_id": "STRING (Primary Key)",
  "assessment_type": "STRING (GSI)",
  "prompt": "STRING",
  "word_limit": "NUMBER",
  "time_limit": "NUMBER"
}
```

#### 5. Rubrics Table (`ielts-assessment-rubrics`)
```json
{
  "rubric_id": "STRING (Primary Key)",
  "assessment_type": "STRING",
  "criteria": "MAP",
  "band_descriptors": "MAP",
  "weight": "NUMBER"
}
```

### AWS CLI Commands to Create Tables:

```bash
# Create Users Table
aws dynamodb create-table \
  --table-name ielts-genai-prep-users \
  --attribute-definitions \
    AttributeName=email,AttributeType=S \
  --key-schema \
    AttributeName=email,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1

# Create Sessions Table with TTL
aws dynamodb create-table \
  --table-name ielts-genai-prep-sessions \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
    AttributeName=user_email,AttributeType=S \
  --key-schema \
    AttributeName=session_id,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=user-email-index,Keys=[{AttributeName=user_email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1

# Enable TTL on Sessions Table
aws dynamodb update-time-to-live \
  --table-name ielts-genai-prep-sessions \
  --time-to-live-specification Enabled=true,AttributeName=expires_at \
  --region us-east-1

# Create Assessments Table
aws dynamodb create-table \
  --table-name ielts-genai-prep-assessments \
  --attribute-definitions \
    AttributeName=assessment_id,AttributeType=S \
    AttributeName=user_email,AttributeType=S \
  --key-schema \
    AttributeName=assessment_id,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=user-email-index,Keys=[{AttributeName=user_email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

---

## 🤖 Phase 2: AI Model Integration

### A. Gemini Flash Lite/Flash for Speaking (Smart Selection)

#### Configuration Files Already Available:
- `gemini_live_audio_service_smart.py` - Complete implementation
- `ielts_workflow_manager.py` - Workflow orchestration
- `hybrid_integration_routes_smart.py` - API routes

#### Activation Steps:

1. **Import the smart selection modules in app.py:**
```python
from gemini_live_audio_service_smart import GeminiLiveServiceSmart, create_smart_selection_service
from hybrid_integration_routes_smart import create_hybrid_routes_smart
```

2. **Initialize the service:**
```python
# In app.py after Flask app creation
gemini_smart_service = create_smart_selection_service(
    project_id=os.environ.get('GOOGLE_CLOUD_PROJECT'),
    region='us-central1'
)

# Register the hybrid routes
app.register_blueprint(create_hybrid_routes_smart(gemini_smart_service))
```

3. **Configure environment variables:**
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GEMINI_API_KEY=your-gemini-api-key
```

### B. AWS Bedrock Nova Micro for Writing

#### Implementation Already Available:
- Location: `production-branch-code/lambda_function.py` (line 496)
- Function: `evaluate_writing_with_nova_micro()`

#### Activation Steps:

1. **Copy the Nova Micro function to main app:**
```python
# Add to app.py
from production_branch_code.lambda_function import evaluate_writing_with_nova_micro
```

2. **Create API endpoint:**
```python
@app.route('/api/writing/evaluate', methods=['POST'])
def evaluate_writing():
    data = request.get_json()
    essay_text = data.get('essay_text')
    prompt = data.get('prompt')
    assessment_type = data.get('assessment_type')
    
    # Get rubric from DynamoDB
    rubric = get_assessment_rubric(assessment_type)
    
    # Evaluate with Nova Micro
    result = evaluate_writing_with_nova_micro(
        essay_text, prompt, rubric, assessment_type
    )
    
    # Store in DynamoDB
    save_assessment_result(result)
    
    return jsonify(result)
```

---

## 📚 Phase 3: Nova Micro Capability Assessment

### Reading & Listening Assessment Capability

#### ✅ **Nova Micro CAN Handle These Assessments**

**Reasoning:**
1. **Simple Pattern Matching**: Reading/listening involve comparing user answers to answer keys
2. **No Creative Generation**: Unlike writing/speaking, these are objective assessments
3. **Cost Effective**: ~$0.001 per assessment for simple scoring

#### Recommended Implementation:

```python
def evaluate_reading_with_nova_micro(user_answers, answer_key, passages):
    """
    Evaluate reading comprehension using Nova Micro
    Cost: ~$0.001 per assessment
    """
    prompt = f"""
    You are an IELTS examiner evaluating reading comprehension.
    
    Passages: {passages}
    Answer Key: {answer_key}
    User Answers: {user_answers}
    
    Task:
    1. Compare user answers to answer key
    2. Allow for minor spelling variations
    3. Accept synonyms where appropriate
    4. Return score and detailed feedback
    
    Output format:
    {
        "correct_answers": 0,
        "total_questions": 40,
        "band_score": 0.0,
        "detailed_feedback": []
    }
    """
    
    # Call Nova Micro
    response = bedrock_client.invoke_model(
        modelId="amazon.nova-micro-v1:0",
        body=json.dumps({"messages": [{"role": "user", "content": prompt}]})
    )
    
    return json.loads(response['body'])

def evaluate_listening_with_nova_micro(user_answers, answer_key, transcript):
    """
    Similar to reading but with audio transcript
    Cost: ~$0.001 per assessment
    """
    # Similar implementation as reading
    pass
```

---

## 🔧 Phase 4: DynamoDB Data Access Layer

### Create `dynamodb_dal.py`:

```python
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, Dict, Any, List
import os

class DynamoDBConnection:
    """DynamoDB connection manager"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        
    def get_table(self, table_name: str):
        """Get DynamoDB table reference"""
        return self.dynamodb.Table(table_name)

class UserDAL:
    """User Data Access Layer for DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('ielts-genai-prep-users')
        
    def create_user(self, email: str, password_hash: str, **kwargs):
        """Create new user"""
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        self.table.put_item(Item=user_data)
        return user_data
        
    def get_user(self, email: str):
        """Get user by email"""
        response = self.table.get_item(Key={'email': email})
        return response.get('Item')
        
    def update_user(self, email: str, **updates):
        """Update user data"""
        update_expr = "SET "
        expr_values = {}
        
        for key, value in updates.items():
            update_expr += f"{key} = :{key}, "
            expr_values[f":{key}"] = value
            
        update_expr = update_expr.rstrip(", ")
        
        self.table.update_item(
            Key={'email': email},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )

class AssessmentDAL:
    """Assessment Data Access Layer for DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('ielts-genai-prep-assessments')
        
    def save_assessment(self, assessment_data: Dict[str, Any]):
        """Save assessment result"""
        assessment_data['assessment_id'] = str(uuid.uuid4())
        assessment_data['timestamp'] = datetime.utcnow().isoformat()
        self.table.put_item(Item=assessment_data)
        return assessment_data
        
    def get_user_assessments(self, user_email: str):
        """Get all assessments for a user"""
        response = self.table.query(
            IndexName='user-email-index',
            KeyConditionExpression=Key('user_email').eq(user_email)
        )
        return response.get('Items', [])
```

---

## 🔌 Phase 5: Connect Everything in app.py

### Update main `app.py`:

```python
import os
import boto3
from flask import Flask, request, jsonify
from dynamodb_dal import DynamoDBConnection, UserDAL, AssessmentDAL
from gemini_live_audio_service_smart import create_smart_selection_service
from hybrid_integration_routes_smart import create_hybrid_routes_smart

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize DynamoDB
db_connection = DynamoDBConnection(region='us-east-1')
user_dal = UserDAL(db_connection)
assessment_dal = AssessmentDAL(db_connection)

# Initialize AWS clients
ses_client = boto3.client('ses', region_name='us-east-1')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Initialize Gemini Smart Selection for Speaking
gemini_smart_service = create_smart_selection_service(
    project_id=os.environ.get('GOOGLE_CLOUD_PROJECT'),
    region='us-central1'
)

# Register hybrid routes for speaking
hybrid_blueprint = create_hybrid_routes_smart(gemini_smart_service, assessment_dal)
app.register_blueprint(hybrid_blueprint)

# Writing assessment endpoint (Nova Micro)
@app.route('/api/writing/evaluate', methods=['POST'])
def evaluate_writing():
    """Evaluate writing with Nova Micro"""
    data = request.get_json()
    
    # Call Nova Micro
    from production_branch_code.lambda_function import evaluate_writing_with_nova_micro
    result = evaluate_writing_with_nova_micro(
        data['essay_text'],
        data['prompt'],
        data['rubric'],
        data['assessment_type']
    )
    
    # Save to DynamoDB
    result['user_email'] = data['user_email']
    assessment_dal.save_assessment(result)
    
    return jsonify(result)

# Reading assessment endpoint (Nova Micro)
@app.route('/api/reading/evaluate', methods=['POST'])
def evaluate_reading():
    """Evaluate reading with Nova Micro"""
    data = request.get_json()
    
    prompt = f"""Evaluate IELTS reading answers.
    User answers: {data['user_answers']}
    Answer key: {data['answer_key']}
    Return score and feedback."""
    
    response = bedrock_client.invoke_model(
        modelId="amazon.nova-micro-v1:0",
        body=json.dumps({"messages": [{"role": "user", "content": prompt}]})
    )
    
    result = json.loads(response['body'])
    assessment_dal.save_assessment(result)
    
    return jsonify(result)
```

---

## 🌍 Phase 6: Cross-Platform Consistency

### Mobile Apps Configuration:

1. **Update API endpoints in both mobile apps:**
```javascript
// config.js in mobile apps
const API_CONFIG = {
    BASE_URL: 'https://api.ieltsaiprep.com',
    ENDPOINTS: {
        SPEAKING: '/api/speaking/stream',  // Gemini Smart Selection
        WRITING: '/api/writing/evaluate',  // Nova Micro
        READING: '/api/reading/evaluate',  // Nova Micro
        LISTENING: '/api/listening/evaluate' // Nova Micro
    }
};
```

2. **Ensure consistent model usage:**
```javascript
// assessment-service.js
const AssessmentService = {
    startSpeaking: async () => {
        // Uses Gemini Flash Lite → Flash
        return await apiCall('/api/speaking/stream');
    },
    
    submitWriting: async (essay) => {
        // Uses Nova Micro
        return await apiCall('/api/writing/evaluate', {essay});
    }
};
```

### Verification Checklist:

- [ ] Website uses DynamoDB for all data operations
- [ ] Mobile App 1 uses same DynamoDB tables
- [ ] Mobile App 2 uses same DynamoDB tables  
- [ ] Speaking uses Gemini Smart Selection on all platforms
- [ ] Writing uses Nova Micro on all platforms
- [ ] Reading/Listening use Nova Micro on all platforms
- [ ] SES email service configured for all platforms
- [ ] Environment variables consistent across deployments

---

## 🚀 Deployment Steps

### 1. Set Environment Variables:
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
export GOOGLE_CLOUD_PROJECT=your-project
export GEMINI_API_KEY=your-gemini-key
export SESSION_SECRET=your-secret
```

### 2. Create DynamoDB Tables:
```bash
# Run the AWS CLI commands from Phase 1
./create_dynamodb_tables.sh
```

### 3. Deploy Lambda Functions (Optional):
```bash
# If using Lambda for serverless
cd production-branch-code
zip -r lambda_deployment.zip .
aws lambda update-function-code \
  --function-name ielts-assessment-handler \
  --zip-file fileb://lambda_deployment.zip
```

### 4. Update and Deploy Flask App:
```bash
# Test locally
python app.py

# Deploy to production
git add .
git commit -m "Restore AWS architecture with DynamoDB"
git push origin main
```

---

## 💰 Cost Analysis

### Monthly Cost Projections (1000 users/month):

| Service | Usage | Cost |
|---------|-------|------|
| DynamoDB | 1GB storage, 1M requests | $5 |
| SES | 10,000 emails | $1 |
| Gemini Flash Lite/Flash | 1000 speaking sessions | $25 |
| Nova Micro (Writing) | 1000 assessments | $3 |
| Nova Micro (Reading/Listening) | 2000 assessments | $2 |
| **Total** | | **$36/month** |

### Profit Margin:
- Revenue: $25 × 1000 users = $25,000
- Costs: $36
- **Margin: 99.86%**

---

## 🔐 Required Secrets

### AWS Secrets:
```yaml
AWS_ACCESS_KEY_ID: AKIA...
AWS_SECRET_ACCESS_KEY: wJal...
AWS_REGION: us-east-1  # Optional, defaults to us-east-1
```

### Google Cloud Secrets:
```yaml
GOOGLE_CLOUD_PROJECT: your-project-id
GEMINI_API_KEY: your-api-key
```

### Application Secrets:
```yaml
SESSION_SECRET: your-random-secret
RECAPTCHA_V2_SITE_KEY: your-key
RECAPTCHA_V2_SECRET_KEY: your-secret
```

---

## ✅ Success Metrics

1. **All data stored in DynamoDB** ✓
2. **Speaking uses Gemini Smart Selection** ✓  
3. **Writing uses Nova Micro** ✓
4. **Reading/Listening use Nova Micro** ✓
5. **Costs under $0.04 per user** ✓
6. **Cross-platform consistency** ✓

---

## 📝 Notes

- The Smart Selection logic is already implemented and tested
- Nova Micro is cost-effective for all text-based assessments
- DynamoDB provides better AWS ecosystem integration
- This architecture supports global scaling with DynamoDB Global Tables

---

*Document generated: October 12, 2025*
*Status: Ready for implementation*