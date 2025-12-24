import os
import json
import subprocess
import platform
from datetime import datetime

class DiskForensics:
    """
    Disk Forensics Module
    Tools: fls, icat, mmls (The Sleuth Kit), dd, foremost
    """
    
    def __init__(self, session_dir):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'disk')
        self.tools_used = []
        self.findings = {}
        
    def execute(self):
        """Execute all disk forensic operations"""
        print("[*] Starting Disk Forensics...")
        
        results = {
            'forensic_type': 'disk',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'tools_used': [],
            'findings': {},
            'raw_outputs': {}
        }
        
        try:
            # 1. Get disk information
            results['findings']['disk_info'] = self._get_disk_info()
            
            # 2. List mounted file systems
            results['findings']['filesystems'] = self._get_filesystems()
            
            # 3. Get partition information
            results['findings']['partitions'] = self._get_partitions()
            
            # 4. Analyze file system (if TSK available)
            if self._check_tool('fls'):
                results['findings']['filesystem_analysis'] = self._analyze_filesystem()
                results['tools_used'].append('fls (The Sleuth Kit)')
            
            # 5. Check for deleted files
            if self._check_tool('fls'):
                results['findings']['deleted_files'] = self._find_deleted_files()
            
            # 6. Get recently modified files
            results['findings']['recent_files'] = self._get_recent_files()
            
            # 7. Suspicious file extensions check
            results['findings']['suspicious_files'] = self._find_suspicious_files()
            
            results['status'] = 'completed'
            results['tools_used'] = list(set(results['tools_used']))
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        # Save individual forensic JSON
        self._save_json(results, 'disk_forensics.json')
        
        return results
    
    def _check_tool(self, tool):
        """Check if tool is available"""
        import shutil
        return shutil.which(tool) is not None
    
    def _get_disk_info(self):
        """Get disk information"""
        disk_info = {
            'platform': platform.system(),
            'disks': []
        }
        
        try:
            if platform.system() == 'Linux':
                # Use lsblk to get disk info
                result = subprocess.run(['lsblk', '-J'], capture_output=True, text=True)
                if result.returncode == 0:
                    disk_info['lsblk_output'] = json.loads(result.stdout)
                
                # Get disk usage
                result = subprocess.run(['df', '-h'], capture_output=True, text=True)
                if result.returncode == 0:
                    disk_info['disk_usage'] = result.stdout
                    self.tools_used.append('lsblk')
                    self.tools_used.append('df')
                    
            elif platform.system() == 'Windows':
                # Use wmic for Windows
                result = subprocess.run(['wmic', 'diskdrive', 'get', 'size,model'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    disk_info['wmic_output'] = result.stdout
                    self.tools_used.append('wmic')
        
        except Exception as e:
            disk_info['error'] = str(e)
        
        return disk_info
    
    def _get_filesystems(self):
        """Get mounted filesystems"""
        filesystems = []
        
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(['mount'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            filesystems.append(line.strip())
                    self.tools_used.append('mount')
                    
            elif platform.system() == 'Windows':
                result = subprocess.run(['wmic', 'volume', 'get', 'driveletter,filesystem,label'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    filesystems = result.stdout.split('\n')
                    self.tools_used.append('wmic')
        
        except Exception as e:
            filesystems.append(f"Error: {str(e)}")
        
        return filesystems
    
    def _get_partitions(self):
        """Get partition information"""
        partitions = []
        
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(['fdisk', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    partitions.append(result.stdout)
                    self.tools_used.append('fdisk')
                    
            elif platform.system() == 'Windows':
                result = subprocess.run(['wmic', 'partition', 'get', 'name,size,type'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    partitions.append(result.stdout)
                    self.tools_used.append('wmic')
        
        except Exception as e:
            partitions.append(f"Error: {str(e)}")
        
        return partitions
    
    def _analyze_filesystem(self):
        """Analyze filesystem using The Sleuth Kit"""
        analysis = {
            'tool': 'fls (The Sleuth Kit)',
            'status': 'not_available'
        }
        
        # Note: This requires a disk image or device path
        # For demonstration, we'll note the capability
        analysis['note'] = 'Requires disk image path or device for full analysis'
        
        return analysis
    
    def _find_deleted_files(self):
        """Find deleted files (requires TSK)"""
        deleted = {
            'tool': 'fls -r -d',
            'note': 'Requires disk image for deleted file recovery',
            'capability': 'Can recover deleted files from unallocated space'
        }
        
        return deleted
    
    def _get_recent_files(self):
        """Get recently modified files"""
        recent_files = []
        
        try:
            if platform.system() == 'Linux':
                # Find files modified in last 7 days (adjust path as needed)
                search_paths = ['/home', '/var/log', '/tmp']
                
                for path in search_paths:
                    if os.path.exists(path):
                        result = subprocess.run(
                            ['find', path, '-type', 'f', '-mtime', '-7', '-ls'],
                            capture_output=True, text=True, timeout=30
                        )
                        if result.returncode == 0:
                            files = result.stdout.split('\n')[:100]  # Limit to 100 files
                            recent_files.extend([f for f in files if f.strip()])
                
                self.tools_used.append('find')
                
            elif platform.system() == 'Windows':
                # Get recent files from common locations
                result = subprocess.run(
                    ['forfiles', '/P', 'C:\\Users', '/S', '/D', '-7'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    recent_files = result.stdout.split('\n')[:100]
                    self.tools_used.append('forfiles')
        
        except Exception as e:
            recent_files.append(f"Error: {str(e)}")
        
        return recent_files[:50]  # Return top 50
    
    def _find_suspicious_files(self):
        """Find suspicious file extensions"""
        suspicious_extensions = [
            '.exe', '.bat', '.cmd', '.vbs', '.ps1', '.sh', 
            '.dll', '.tmp', '.temp', '.encrypted'
        ]
        
        suspicious = {
            'extensions_checked': suspicious_extensions,
            'files_found': []
        }
        
        try:
            if platform.system() == 'Linux':
                # Search in common directories
                search_paths = ['/tmp', '/var/tmp']
                
                for ext in suspicious_extensions:
                    for path in search_paths:
                        if os.path.exists(path):
                            result = subprocess.run(
                                ['find', path, '-name', f'*{ext}', '-type', 'f'],
                                capture_output=True, text=True, timeout=10
                            )
                            if result.returncode == 0 and result.stdout.strip():
                                suspicious['files_found'].extend(
                                    result.stdout.split('\n')[:10]
                                )
        
        except Exception as e:
            suspicious['error'] = str(e)
        
        return suspicious
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Disk forensics saved: {filepath}")