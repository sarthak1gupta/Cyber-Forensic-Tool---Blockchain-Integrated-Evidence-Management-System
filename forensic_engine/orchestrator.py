import os
import json
import hashlib
from datetime import datetime
from config import Config

class ForensicOrchestrator:
    """
    Main orchestrator for coordinating forensic operations
    """
    
    def __init__(self, session_dir, session_id, use_advanced_tools=False):
        self.session_dir = session_dir
        self.session_id = session_id
        self.use_advanced_tools = use_advanced_tools
        self.evidence_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'investigator': Config.INVESTIGATOR_ID,
            'os_source': self._detect_os(),
            'advanced_tools_enabled': use_advanced_tools,
            'forensics': {},
            'tools_summary': {
                'core_tools_used': [],
                'advanced_tools_used': [],
                'commands_executed': []
            }
        }
        
    def _detect_os(self):
        """Detect operating system"""
        import platform
        return f"{platform.system()} {platform.release()}"
    
    def execute_forensics(self, forensic_types):
        """
        Execute selected forensic types
        
        Args:
            forensic_types (list): List of forensic types to execute
                                   ['disk', 'memory', 'network', 'log', 'all']
        """
        if 'all' in forensic_types:
            forensic_types = ['disk', 'memory', 'network', 'log']
        
        results = {}
        
        for forensic_type in forensic_types:
            print(f"[*] Starting {forensic_type} forensics...")
            
            try:
                if forensic_type == 'disk':
                    from forensic_engine.disk_forensics import DiskForensics
                    df = DiskForensics(self.session_dir, self.use_advanced_tools)
                    results['disk'] = df.execute()
                    self._update_tools_summary(results['disk'])
                    
                elif forensic_type == 'memory':
                    from forensic_engine.memory_forensics import MemoryForensics
                    mf = MemoryForensics(self.session_dir, self.use_advanced_tools)
                    results['memory'] = mf.execute()
                    self._update_tools_summary(results['memory'])
                    
                elif forensic_type == 'network':
                    from forensic_engine.network_forensics import NetworkForensics
                    nf = NetworkForensics(self.session_dir, self.use_advanced_tools)
                    results['network'] = nf.execute()
                    self._update_tools_summary(results['network'])
                    
                elif forensic_type == 'log':
                    from forensic_engine.log_forensics import LogForensics
                    lf = LogForensics(self.session_dir, self.use_advanced_tools)
                    results['log'] = lf.execute()
                    self._update_tools_summary(results['log'])
                
                print(f"[+] {forensic_type} forensics completed")
                
            except Exception as e:
                print(f"[!] Error in {forensic_type} forensics: {str(e)}")
                import traceback
                traceback.print_exc()
                results[forensic_type] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.evidence_data['forensics'] = results
        return self.evidence_data
    
    def _update_tools_summary(self, forensic_result):
        """Update tools summary with what was used"""
        if isinstance(forensic_result, dict):
            # Add core tools
            core_tools = forensic_result.get('tools_used', [])
            self.evidence_data['tools_summary']['core_tools_used'].extend(core_tools)
            
            # Add advanced tools
            advanced_tools = forensic_result.get('advanced_tools_used', [])
            self.evidence_data['tools_summary']['advanced_tools_used'].extend(advanced_tools)
            
            # Add commands
            commands = forensic_result.get('commands_executed', [])
            self.evidence_data['tools_summary']['commands_executed'].extend(commands)
        
        # Remove duplicates
        self.evidence_data['tools_summary']['core_tools_used'] = list(set(
            self.evidence_data['tools_summary']['core_tools_used']
        ))
        self.evidence_data['tools_summary']['advanced_tools_used'] = list(set(
            self.evidence_data['tools_summary']['advanced_tools_used']
        ))
    
    def save_master_json(self):
        """Save master JSON with all forensic data"""
        master_file = os.path.join(self.session_dir, 'master_evidence.json')
        
        with open(master_file, 'w') as f:
            json.dump(self.evidence_data, f, indent=4)
        
        print(f"[+] Master evidence JSON saved: {master_file}")
        return master_file
    
    def calculate_evidence_hash(self):
        """Calculate SHA-256 hash of master evidence"""
        master_file = os.path.join(self.session_dir, 'master_evidence.json')
        
        if not os.path.exists(master_file):
            self.save_master_json()
        
        sha256_hash = hashlib.sha256()
        with open(master_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        evidence_hash = sha256_hash.hexdigest()
        
        # Add hash to evidence data
        self.evidence_data['evidence_hash'] = evidence_hash
        self.save_master_json()
        
        return evidence_hash
    
    def get_evidence_summary(self):
        """Generate summary for blockchain registration"""
        summary = {
            'evidence_id': self.session_id,
            'evidence_hash': self.evidence_data.get('evidence_hash', ''),
            'timestamp': self.evidence_data['timestamp'],
            'os_source': self.evidence_data['os_source'],
            'investigator_id': self.evidence_data['investigator'],
            'forensic_types': list(self.evidence_data['forensics'].keys()),
            'tools_used': self._get_tools_used()
        }
        return summary
    
    def _get_tools_used(self):
        """Get list of all tools used across forensics"""
        tools = []
        for forensic_type, data in self.evidence_data['forensics'].items():
            if isinstance(data, dict) and 'tools_used' in data:
                tools.extend(data['tools_used'])
        return list(set(tools))
    
    @staticmethod
    def list_available_tools():
        """List all available forensic tools on system"""
        import shutil
        
        available = {
            'core_tools': {
                'python_libraries': Config.CORE_TOOLS['python_libraries'],
                'system_commands': []
            },
            'advanced_tools': {
                'disk': [],
                'memory': [],
                'network': [],
                'available': False
            }
        }
        
        # Check system commands for current OS
        os_commands = Config.CORE_TOOLS['system_commands'].get(Config.OS_TYPE, [])
        for cmd in os_commands:
            if shutil.which(cmd) or Config.get_tool_path(cmd):
                available['core_tools']['system_commands'].append(cmd)
        
        # Check advanced tools
        for category, tools_dict in Config.OPTIONAL_TOOLS.items():
            for tool_suite, tool_info in tools_dict.items():
                for tool_name in tool_info['tools']:
                    tool_path = Config.get_tool_path(tool_name)
                    if tool_path or shutil.which(tool_name):
                        available['advanced_tools'][category].append({
                            'name': tool_name,
                            'suite': tool_suite,
                            'path': tool_path or shutil.which(tool_name),
                            'description': tool_info['description']
                        })
                        available['advanced_tools']['available'] = True
        
        return available