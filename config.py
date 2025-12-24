import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Blockchain Configuration
    BLOCKCHAIN_PROVIDER = os.getenv('BLOCKCHAIN_PROVIDER', 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')  # Set after deployment
    PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')  # Investigator's wallet private key
    
    # LLM Configuration (3 API keys for token distribution)
    GROQ_API_KEY_1 = os.getenv('GROQ_API_KEY_1', '')
    GROQ_API_KEY_2 = os.getenv('GROQ_API_KEY_2', '')
    GROQ_API_KEY_3 = os.getenv('GROQ_API_KEY_3', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama-3.1-70b-versatile')
    
    # Evidence Storage Configuration
    BASE_EVIDENCE_DIR = os.getenv('BASE_EVIDENCE_DIR', 'evidence_output')
    
    # Investigator Information
    INVESTIGATOR_ID = os.getenv('INVESTIGATOR_ID', 'INV001')
    INVESTIGATOR_NAME = os.getenv('INVESTIGATOR_NAME', 'System Administrator')
    ORGANIZATION = os.getenv('ORGANIZATION', 'Forensic Lab')
    
    # Forensic Tools Paths (Auto-detect or specify)
    TOOLS = {
        'disk': {
            'fls': 'fls',  # The Sleuth Kit
            'icat': 'icat',
            'mmls': 'mmls',
            'dd': 'dd',
            'foremost': 'foremost',
        },
        'memory': {
            'volatility': 'vol.py',  # Volatility 3
            'lime': 'lime',
        },
        'network': {
            'tshark': 'tshark',
            'tcpdump': 'tcpdump',
        },
        'log': {
            'cat': 'cat',
            'grep': 'grep',
        }
    }
    
    # Operating System Detection
    OS_TYPE = os.name  # 'posix' for Linux/Mac, 'nt' for Windows
    
    # Log Paths
    LOG_PATHS = {
        'linux': [
            '/var/log/syslog',
            '/var/log/auth.log',
            '/var/log/kern.log',
            '/var/log/apache2/access.log',
            '/var/log/apache2/error.log',
        ],
        'windows': [
            'Application',
            'Security',
            'System',
        ]
    }
    
    # Legal Compliance Standards
    LEGAL_STANDARDS = {
        'india': ['IT Act 2000 Section 43', 'IT Act 2000 Section 65B', 'ISO/IEC 27037'],
        'international': ['ISO/IEC 27037', 'NIST SP 800-86', 'RFC 3227']
    }
    
    @staticmethod
    def create_session_directory():
        """Create timestamped session directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_dir = os.path.join(Config.BASE_EVIDENCE_DIR, f'session_{timestamp}')
        os.makedirs(session_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['disk', 'memory', 'network', 'logs', 'reports']
        for subdir in subdirs:
            os.makedirs(os.path.join(session_dir, subdir), exist_ok=True)
        
        return session_dir, timestamp
    
    @staticmethod
    def validate_config():
        """Validate critical configuration"""
        errors = []
        
        if not Config.CONTRACT_ADDRESS:
            errors.append("CONTRACT_ADDRESS not set in .env")
        
        if not Config.GROQ_API_KEY_1:
            errors.append("GROQ_API_KEY_1 not set in .env")
        
        if not Config.PRIVATE_KEY:
            errors.append("PRIVATE_KEY not set in .env")
        
        return errors