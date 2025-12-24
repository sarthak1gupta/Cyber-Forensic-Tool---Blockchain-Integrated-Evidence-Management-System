# 📚 API Documentation

Complete REST API reference for the Cyber Forensic Tool.

**Base URL:** `http://localhost:5000/api`

---

## 🔍 Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/check-tools` | GET | Check available forensic tools |
| `/api/validate-config` | GET | Validate configuration |
| `/api/start-forensics` | POST | Start forensic investigation |
| `/api/register-blockchain` | POST | Register evidence on blockchain |
| `/api/generate-report` | POST | Generate AI forensic report |
| `/api/session-status` | GET | Get current session status |
| `/api/blockchain-balance` | GET | Get wallet balance |
| `/api/verify-evidence` | POST | Verify evidence integrity |
| `/api/download-report/:type` | GET | Download generated report |

---

## 📋 Detailed API Reference

### 1. Check Available Tools

**Endpoint:** `GET /api/check-tools`

**Description:** Returns list of available forensic tools on the system.

**Request:**
```bash
curl http://localhost:5000/api/check-tools
```

**Response:**
```json
{
  "status": "success",
  "tools": {
    "disk": ["fls", "icat", "mmls"],
    "memory": ["psutil"],
    "network": ["netstat"],
    "log": ["grep", "cat"]
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - System error

---

### 2. Validate Configuration

**Endpoint:** `GET /api/validate-config`

**Description:** Validates environment configuration and API keys.

**Request:**
```bash
curl http://localhost:5000/api/validate-config
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Configuration is valid"
}
```

**Response (Warning):**
```json
{
  "status": "warning",
  "errors": [
    "CONTRACT_ADDRESS not set in .env",
    "GROQ_API_KEY_1 not set in .env"
  ],
  "message": "Some configuration values are missing"
}
```

**Status Codes:**
- `200 OK` - Configuration valid or warnings
- `500 Internal Server Error` - Critical error

---

### 3. Start Forensic Investigation

**Endpoint:** `POST /api/start-forensics`

**Description:** Initiates forensic analysis on the system.

**Request Body:**
```json
{
  "forensic_types": ["disk", "memory", "network", "log"]
}
```

Or for all forensics:
```json
{
  "forensic_types": ["all"]
}
```

**Request:**
```bash
curl -X POST http://localhost:5000/api/start-forensics \
  -H "Content-Type: application/json" \
  -d '{"forensic_types": ["all"]}'
```

**Response:**
```json
{
  "status": "success",
  "session_id": "20240101_120000",
  "session_dir": "/path/to/evidence_output/session_20240101_120000",
  "evidence_hash": "abc123...def789",
  "forensics_completed": ["disk", "memory", "network", "log"]
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Error message description"
}
```

**Status Codes:**
- `200 OK` - Forensics completed successfully
- `500 Internal Server Error` - Forensic execution failed

**Execution Time:** 30-120 seconds depending on system size

---

### 4. Register Evidence on Blockchain

**Endpoint:** `POST /api/register-blockchain`

**Description:** Registers evidence on Ethereum Sepolia testnet.

**Prerequisites:**
- Active session from `/api/start-forensics`
- Sufficient Sepolia ETH in wallet

**Request:**
```bash
curl -X POST http://localhost:5000/api/register-blockchain
```

**Response:**
```json
{
  "status": "success",
  "evidence_id": "EVD_20240101_120000",
  "blockchain_data": {
    "status": "success",
    "transaction_hash": "0xabc123...def789",
    "block_number": 12345678,
    "gas_used": 234567,
    "timestamp": 1704110400
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "No active session. Run forensics first."
}
```

**Status Codes:**
- `200 OK` - Evidence registered successfully
- `400 Bad Request` - No active session
- `500 Internal Server Error` - Blockchain error

**Execution Time:** 15-30 seconds (blockchain confirmation)

---

### 5. Generate Forensic Report

**Endpoint:** `POST /api/generate-report`

**Description:** Generates comprehensive AI-powered forensic report.

**Prerequisites:**
- Active session with forensics completed
- Evidence registered on blockchain

**Request:**
```bash
curl -X POST http://localhost:5000/api/generate-report
```

**Response:**
```json
{
  "status": "success",
  "report": {
    "report_metadata": {
      "generated_at": "2024-01-01T12:00:00",
      "session_id": "20240101_120000",
      "investigator": "INV001",
      "organization": "Cyber Forensics Lab",
      "evidence_hash": "abc123...def789",
      "blockchain_tx": "0xabc...def"
    },
    "executive_summary": "...",
    "detailed_findings": "...",
    "legal_compliance": "...",
    "chain_of_custody": {...}
  },
  "report_paths": {
    "json_report": "/path/to/forensic_report.json",
    "text_report": "/path/to/forensic_report.txt"
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Blockchain registration required before report generation."
}
```

**Status Codes:**
- `200 OK` - Report generated successfully
- `400 Bad Request` - Prerequisites not met
- `500 Internal Server Error` - Report generation failed

**Execution Time:** 60-120 seconds (3 LLM API calls)

---

### 6. Get Session Status

**Endpoint:** `GET /api/session-status`

**Description:** Returns current investigation session status.

**Request:**
```bash
curl http://localhost:5000/api/session-status
```

**Response (Active Session):**
```json
{
  "status": "active",
  "session_id": "20240101_120000",
  "timestamp": "2024-01-01T12:00:00",
  "evidence_hash": "abc123...def789",
  "blockchain_registered": true,
  "report_generated": true
}
```

**Response (No Session):**
```json
{
  "status": "no_session",
  "message": "No active session"
}
```

**Status Codes:**
- `200 OK` - Status returned

---

### 7. Get Blockchain Balance

**Endpoint:** `GET /api/blockchain-balance`

**Description:** Returns wallet balance on Sepolia testnet.

**Request:**
```bash
curl http://localhost:5000/api/blockchain-balance
```

**Response:**
```json
{
  "status": "success",
  "balance": {
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb5",
    "balance_wei": 100000000000000000,
    "balance_eth": 0.1
  }
}
```

**Status Codes:**
- `200 OK` - Balance retrieved
- `500 Internal Server Error` - Blockchain connection failed

---

### 8. Verify Evidence Integrity

**Endpoint:** `POST /api/verify-evidence`

**Description:** Verifies evidence hash against blockchain record.

**Request Body:**
```json
{
  "evidence_id": "EVD_20240101_120000",
  "hash": "abc123...def789"
}
```

**Request:**
```bash
curl -X POST http://localhost:5000/api/verify-evidence \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "EVD_20240101_120000",
    "hash": "abc123...def789"
  }'
```

**Response (Valid):**
```json
{
  "status": "success",
  "is_valid": true,
  "message": "Hash verified successfully"
}
```

**Response (Invalid):**
```json
{
  "status": "success",
  "is_valid": false,
  "message": "Hash mismatch"
}
```

**Status Codes:**
- `200 OK` - Verification completed
- `500 Internal Server Error` - Verification failed

---

### 9. Download Report

**Endpoint:** `GET /api/download-report/:type`

**Description:** Downloads generated forensic report.

**Parameters:**
- `type` - Report type: `json` or `text`

**Request:**
```bash
# Download JSON report
curl http://localhost:5000/api/download-report/json -O

# Download text report
curl http://localhost:5000/api/download-report/text -O
```

**Response:** File download

**Status Codes:**
- `200 OK` - File download started
- `404 Not Found` - No report available
- `400 Bad Request` - Invalid report type

---

## 🔄 Typical Workflow

### Complete Investigation Flow

```bash
# 1. Check configuration
curl http://localhost:5000/api/validate-config

# 2. Check available tools
curl http://localhost:5000/api/check-tools

# 3. Start forensics
curl -X POST http://localhost:5000/api/start-forensics \
  -H "Content-Type: application/json" \
  -d '{"forensic_types": ["all"]}'

# 4. Check wallet balance
curl http://localhost:5000/api/blockchain-balance

# 5. Register on blockchain
curl -X POST http://localhost:5000/api/register-blockchain

# 6. Generate report
curl -X POST http://localhost:5000/api/generate-report

# 7. Download reports
curl http://localhost:5000/api/download-report/json -O
curl http://localhost:5000/api/download-report/text -O

# 8. Verify evidence (optional)
curl -X POST http://localhost:5000/api/verify-evidence \
  -H "Content-Type: application/json" \
  -d '{"evidence_id": "EVD_...", "hash": "..."}'
```

---

## 🔐 Authentication

Currently, the API does not require authentication. For production deployment:

### Recommended Authentication Methods

1. **API Key Authentication**
```python
# Add to app.py
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != Config.API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
```

2. **JWT Token Authentication**
```python
from flask_jwt_extended import JWTManager, jwt_required

app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET
jwt = JWTManager(app)

@app.route('/api/protected')
@jwt_required()
def protected():
    return jsonify({'message': 'Protected route'})
```

---

## 🚦 Rate Limiting

Recommended rate limits for production:

| Endpoint | Rate Limit | Reason |
|----------|-----------|--------|
| `/api/start-forensics` | 5/hour | Resource intensive |
| `/api/register-blockchain` | 10/hour | Gas costs |
| `/api/generate-report` | 10/hour | LLM API costs |
| Other endpoints | 100/hour | General protection |

**Implementation:**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr
)

@app.route('/api/start-forensics')
@limiter.limit("5 per hour")
def start_forensics():
    ...
```

---

## 📊 Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 🐛 Error Handling

All API endpoints return consistent error format:

```json
{
  "status": "error",
  "error": "Detailed error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `NO_SESSION` | No active forensic session | Run `/api/start-forensics` first |
| `BLOCKCHAIN_ERROR` | Blockchain connection failed | Check Infura key and network |
| `INSUFFICIENT_FUNDS` | Not enough ETH for gas | Get Sepolia ETH from faucet |
| `LLM_ERROR` | LLM API error | Check Groq API keys |
| `CONFIG_ERROR` | Configuration missing | Validate `.env` file |

---

## 📝 Example Integration

### Python Client

```python
import requests
import json

class ForensicClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session_id = None
    
    def start_investigation(self, forensic_types=["all"]):
        response = requests.post(
            f"{self.base_url}/api/start-forensics",
            json={"forensic_types": forensic_types}
        )
        data = response.json()
        if data['status'] == 'success':
            self.session_id = data['session_id']
        return data
    
    def register_blockchain(self):
        response = requests.post(
            f"{self.base_url}/api/register-blockchain"
        )
        return response.json()
    
    def generate_report(self):
        response = requests.post(
            f"{self.base_url}/api/generate-report"
        )
        return response.json()

# Usage
client = ForensicClient()
result = client.start_investigation()
print(f"Session: {result['session_id']}")
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class ForensicClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.sessionId = null;
    }
    
    async startInvestigation(forensicTypes = ['all']) {
        const response = await axios.post(
            `${this.baseURL}/api/start-forensics`,
            { forensic_types: forensicTypes }
        );
        
        if (response.data.status === 'success') {
            this.sessionId = response.data.session_id;
        }
        
        return response.data;
    }
    
    async registerBlockchain() {
        const response = await axios.post(
            `${this.baseURL}/api/register-blockchain`
        );
        return response.data;
    }
    
    async generateReport() {
        const response = await axios.post(
            `${this.baseURL}/api/generate-report`
        );
        return response.data;
    }
}

// Usage
const client = new ForensicClient();
const result = await client.startInvestigation();
console.log(`Session: ${result.session_id}`);
```

---

## 🧪 Testing Endpoints

### Using cURL

```bash
# Test all endpoints
./test_api.sh
```

### Using Postman

Import collection: `postman_collection.json`

### Using Python

```bash
python test_api.py
```

---

**API Version:** 1.0.0  
**Last Updated:** 2024-01-01