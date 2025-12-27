import os
from datetime import datetime
from dotenv import load_dotenv
import platform

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Blockchain Configuration
    BLOCKCHAIN_PROVIDER = os.getenv('BLOCKCHAIN_PROVIDER', '')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')
    
    # LLM Configuration (3 API keys for token distribution)
    GROQ_API_KEY_1 = os.getenv('GROQ_API_KEY_1', '')
    GROQ_API_KEY_2 = os.getenv('GROQ_API_KEY_2', '')
    GROQ_API_KEY_3 = os.getenv('GROQ_API_KEY_3', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')
    
    # Evidence Storage Configuration
    BASE_EVIDENCE_DIR = os.getenv('BASE_EVIDENCE_DIR', 'evidence_output')
    
    # Investigator Information
    INVESTIGATOR_ID = os.getenv('INVESTIGATOR_ID', 'INV001')
    INVESTIGATOR_NAME = os.getenv('INVESTIGATOR_NAME', 'System Administrator')
    ORGANIZATION = os.getenv('ORGANIZATION', 'Forensic Lab')
    
    # Operating System Detection
    OS_TYPE = platform.system()  # 'Windows', 'Linux', 'Darwin'
    OS_VERSION = platform.version()
    OS_RELEASE = platform.release()
    ARCHITECTURE = platform.machine()
    
    # Optional Tools Paths (from .env)
    SLEUTHKIT_BIN_PATH = os.getenv('SLEUTHKIT_BIN_PATH', '')
    SLEUTHKIT_LIB_PATH = os.getenv('SLEUTHKIT_LIB_PATH', '')
    FOREMOST_PATH = os.getenv('FOREMOST_PATH', '')
    WIRESHARK_PATH = os.getenv('WIRESHARK_PATH', '')
    VOLATILITY_PATH = os.getenv('VOLATILITY_PATH', '')
    
    # Core Tools (Always Available)
    CORE_TOOLS = {
        'python_libraries': ['psutil', 'subprocess', 'os', 'platform'],
        'system_commands': {
            'Windows': ['wmic', 'netstat', 'arp', 'route', 'wevtutil', 'ipconfig'],
            'Linux': ['lsblk', 'df', 'mount', 'netstat', 'arp', 'route', 'grep', 'tail', 'find'],
            'Darwin': ['diskutil', 'df', 'mount', 'netstat', 'arp', 'route', 'grep', 'tail', 'find']
        }
    }
    
    # Optional Tools (Enhanced Features)
    OPTIONAL_TOOLS = {
        'disk': {
            'sleuthkit': {
                'tools': ['fls', 'icat', 'mmls', 'fsstat'],
                'bin_path': SLEUTHKIT_BIN_PATH,
                'description': 'Advanced file system analysis and deleted file recovery'
            },
            'foremost': {
                'tools': ['foremost'],
                'path': FOREMOST_PATH,
                'description': 'File carving and data recovery from unallocated space'
            }
        },
        'network': {
            'wireshark': {
                'tools': ['tshark'],
                'path': WIRESHARK_PATH,
                'description': 'Deep packet analysis and network traffic capture'
            }
        },
        'memory': {
            'volatility': {
                'tools': ['vol.py', 'volatility3'],
                'path': VOLATILITY_PATH,
                'description': 'Advanced memory dump analysis and malware detection'
            }
        }
    }
    
    # Log Paths
    LOG_PATHS = {
        'Linux': [
            '/var/log/syslog',
            '/var/log/auth.log',
            '/var/log/kern.log',
            '/var/log/apache2/access.log',
            '/var/log/apache2/error.log',
        ],
        'Windows': [
            'Application',
            'Security',
            'System',
        ],
        'Darwin': [
            '/var/log/system.log',
            '/var/log/secure.log',
        ]
    }
    
    # Legal Compliance Standards
    LEGAL_STANDARDS = {
        'india': ['IT Act 2000 Section 43', 'IT Act 2000 Section 65B', 'ISO/IEC 27037'],
        'international': ['ISO/IEC 27037', 'NIST SP 800-86', 'RFC 3227']
    }
    
    @staticmethod
    def get_system_info():
        """Get detailed system information"""
        return {
            'os': Config.OS_TYPE,
            'os_version': Config.OS_VERSION,
            'os_release': Config.OS_RELEASE,
            'architecture': Config.ARCHITECTURE,
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
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
    
    @staticmethod
    def get_tool_path(tool_name):
        """Get full path for a tool"""
        # Check in PATH first
        import shutil
        tool = shutil.which(tool_name)
        if tool:
            return tool
        
        # Check in optional tool paths
        if Config.SLEUTHKIT_BIN_PATH and tool_name in ['fls', 'icat', 'mmls', 'fsstat']:
            tool_path = os.path.join(Config.SLEUTHKIT_BIN_PATH, f'{tool_name}.exe' if Config.OS_TYPE == 'Windows' else tool_name)
            if os.path.exists(tool_path):
                return tool_path
        
        if Config.FOREMOST_PATH and tool_name == 'foremost':
            tool_path = os.path.join(Config.FOREMOST_PATH, 'foremost.exe' if Config.OS_TYPE == 'Windows' else 'foremost')
            if os.path.exists(tool_path):
                return tool_path
        
        if Config.WIRESHARK_PATH and tool_name == 'tshark':
            tool_path = os.path.join(Config.WIRESHARK_PATH, 'tshark.exe' if Config.OS_TYPE == 'Windows' else 'tshark')
            if os.path.exists(tool_path):
                return tool_path
        
        return None