# 🔍 Cyber Forensic Tool - Blockchain Integrated Evidence Management System

A comprehensive digital forensic investigation platform that integrates multiple forensic tools, maintains evidence integrity using blockchain technology (Ethereum Sepolia), and generates legal-ready reports using AI (Groq/Llama).

## 🎯 Problem Statement

Current cyber forensic investigations suffer from:
- ❌ Manual evidence collection across different tools
- ❌ Weak or manual chain-of-custody documentation
- ❌ Time-consuming legal report preparation
- ❌ Risk of evidence tampering or poor audit trails

## ✨ Solution

This platform provides:
- ✅ **Automated Forensic Tool Integration** - Disk, Memory, Network, and Log forensics
- ✅ **Blockchain Chain of Custody** - Immutable evidence tracking on Ethereum
- ✅ **AI-Powered Legal Reports** - Automated compliance and legal documentation
- ✅ **Evidence Integrity** - Cryptographic hash verification

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Application                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend: HTML/CSS/JS → Backend: Flask → Forensic Engine   │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────────┐                 ┌─────────────────┐
│ Forensic Tools    │                 │ Blockchain      │
│ Execution Engine  │←───────────────→│ (Sepolia)       │
└───────────────────┘                 └─────────────────┘
        ↓                                       ↓
┌───────────────────┐                 ┌─────────────────┐
│ Evidence Storage  │                 │ LLM Report Gen  │
│ (JSON + Raw)      │────────────────→│ (Groq/Llama)    │
└───────────────────┘                 └─────────────────┘
```

---

## 🔧 Forensic Tools Mapping

### 1. **Disk Forensics**
- **The Sleuth Kit (TSK)** - File system analysis
  - `fls` - List files/directories
  - `icat` - Extract file contents
  - `mmls` - Partition table analysis
- **foremost** - File carving
- **dd/dcfldd** - Disk imaging

### 2. **Memory Forensics**
- **psutil** - Live process and memory analysis
- **Volatility 3** - Memory dump analysis (optional)

### 3. **Network Forensics**
- **psutil** - Network connections
- **netstat** - Network statistics
- **tshark/tcpdump** - Packet capture (optional)

### 4. **Log Analysis**
- **System Logs** - auth.log, syslog, secure
- **Windows Event Logs** - wevtutil
- **Custom parsers** - Application logs

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu/Debian recommended) or Windows 10+
- **Python**: 3.8 or higher
- **Node.js**: Not required (pure Flask/JS)
- **RAM**: Minimum 4GB
- **Disk Space**: 2GB free space

### Required Accounts
1. **Infura** - Ethereum API provider
   - Sign up: https://infura.io
   
2. **MetaMask** - Ethereum wallet
   - Install: https://metamask.io
   - Switch to Sepolia testnet
   
3. **Groq** - LLM API
   - Sign up: https://console.groq.com
   - Get 3 API keys

4. **Sepolia Testnet ETH**
   - Faucet: https://sepoliafaucet.com

### Optional Tools (for enhanced forensics)
```bash
# Ubuntu/Debian
sudo apt-get install sleuthkit foremost volatility3 wireshark-cli

# macOS
brew install sleuthkit foremost

# Windows
# Download tools from respective websites
```

---

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/cyber-forensic-tool.git
cd cyber-forensic-tool
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.template .env
nano .env  # Edit with your values
```

Required `.env` values:
```bash
BLOCKCHAIN_PROVIDER=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
CONTRACT_ADDRESS=0xYourContractAddress
PRIVATE_KEY=0xYourPrivateKey
GROQ_API_KEY_1=gsk_your_key_1
GROQ_API_KEY_2=gsk_your_key_2
GROQ_API_KEY_3=gsk_your_key_3
```

### 5. Deploy Smart Contract

#### Using Remix IDE:
1. Go to https://remix.ethereum.org
2. Create new file: `EvidenceChain.sol`
3. Copy contract code from `contracts/EvidenceChain.sol`
4. Compile with Solidity 0.8.0+
5. Deploy to Sepolia testnet:
   - Environment: Injected Provider - MetaMask
   - Network: Sepolia
   - Click Deploy
6. Copy contract address to `.env`
7. Copy ABI to `contracts/contract_abi.json`

---

## 🎮 Usage

### 1. Start Application
```bash
python app.py
```

Application will start on: http://localhost:5000

### 2. Web Interface Workflow

#### Step 1: Configuration Check
- Click "Check Configuration"
- Click "Check Available Tools"
- Verify all tools are installed

#### Step 2: Start Forensic Investigation
- Select forensic types:
  - All Forensics (recommended)
  - OR individual: Disk, Memory, Network, Log
- Click "Start Investigation"
- Wait for completion (30-120 seconds)

#### Step 3: Register on Blockchain
- Click "Check Wallet Balance" (ensure you have Sepolia ETH)
- Click "Register on Blockchain"
- Wait for transaction confirmation (10-30 seconds)
- View transaction on Etherscan

#### Step 4: Generate Report
- Click "Generate Report"
- Wait for AI analysis (60-90 seconds)
- Download JSON or Text report

#### Step 5: Verify Evidence (Optional)
- Enter Evidence ID from report
- Enter Evidence Hash
- Click "Verify"

---

## 📂 Project Structure

```
cyber-forensic-tool/
├── app.py                          # Main Flask application
├── config.py                       # Configuration
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this)
├── README.md                       # This file
│
├── contracts/
│   ├── EvidenceChain.sol          # Smart contract
│   └── contract_abi.json          # Contract ABI
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   └── index.html
│
├── forensic_engine/
│   ├── __init__.py
│   ├── orchestrator.py            # Main coordinator
│   ├── disk_forensics.py
│   ├── memory_forensics.py
│   ├── network_forensics.py
│   └── log_forensics.py
│
├── blockchain/
│   ├── __init__.py
│   └── blockchain_handler.py
│
├── llm_engine/
│   ├── __init__.py
│   └── report_generator.py
│
└── evidence_output/               # Auto-generated
    └── session_YYYYMMDD_HHMMSS/
        ├── disk/
        ├── memory/
        ├── network/
        ├── logs/
        ├── reports/
        ├── master_evidence.json
        ├── forensic_report.json
        └── forensic_report.txt
```

---

## 🔐 Security Considerations

### Private Key Security
- ⚠️ **NEVER commit `.env` file to Git**
- ⚠️ **NEVER share your private key**
- ⚠️ Use test accounts only for Sepolia
- ⚠️ Store private keys securely

### Evidence Integrity
- ✅ All evidence is hashed (SHA-256)
- ✅ Hashes are stored on blockchain
- ✅ Timestamps are immutable
- ✅ Chain of custody is verifiable

### Permissions
- Some tools require root/admin privileges
- Run with minimum necessary permissions
- Review forensic_engine modules before execution

---

## 📊 Output Files

### Per-Forensic Type
- `disk/disk_forensics.json` - Disk analysis results
- `memory/memory_forensics.json` - Memory analysis
- `network/network_forensics.json` - Network analysis
- `logs/log_forensics.json` - Log analysis

### Master Files
- `master_evidence.json` - Combined forensic data
- `forensic_report.json` - AI-generated report (structured)
- `forensic_report.txt` - Human-readable report

### Blockchain Data
- Transaction hash
- Block number
- Evidence ID
- Timestamp

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Failed to connect to blockchain"
```bash
# Check Infura key
curl "https://sepolia.infura.io/v3/YOUR_KEY" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

#### 2. "Insufficient funds for gas"
- Get Sepolia ETH from faucet
- Check balance: https://sepolia.etherscan.io

#### 3. "Tool not found"
```bash
# Install missing tools
sudo apt-get install sleuthkit foremost
```

#### 4. "LLM API error"
- Verify Groq API keys
- Check API quota: https://console.groq.com

---

## 📚 Legal Compliance

### Supported Standards
- **IT Act 2000 (India)** - Sections 43, 65B
- **ISO/IEC 27037** - Digital evidence guidelines
- **NIST SP 800-86** - Integration guides

### Evidence Admissibility
- ✅ Hash verification
- ✅ Chain of custody
- ✅ Timestamp verification
- ✅ Investigator identification

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Authors

- Your Name - Initial work - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- **The Sleuth Kit** - Forensic tools
- **Anthropic** - Claude AI assistance
- **Groq** - LLM API
- **Ethereum** - Blockchain platform
- **Web3.py** - Ethereum integration

---

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/cyber-forensic-tool/issues
- Email: your.email@example.com

---

## 🔮 Future Enhancements

- [ ] Mobile app support
- [ ] Real-time monitoring
- [ ] Multi-investigator support
- [ ] Advanced analytics dashboard
- [ ] Integration with more forensic tools
- [ ] IPFS storage for large evidence files
- [ ] Automated alert system

---

## ⚖️ Disclaimer

This tool is intended for legitimate forensic investigations and educational purposes only. Users are responsible for ensuring compliance with applicable laws and regulations in their jurisdiction. The authors assume no liability for misuse of this software.

---

**Built with ❤️ for the Cyber Security Community**