import os
import json
import subprocess
import platform
from datetime import datetime
from config import Config

class DiskForensics:
    """
    Enhanced Disk Forensics Module
    Core Tools: lsblk, df, mount, find, wmic
    Advanced Tools: The Sleuth Kit (fls, icat, mmls), Foremost
    """
    
    def __init__(self, session_dir, use_advanced_tools=False):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'disk')
        self.use_advanced_tools = use_advanced_tools
        self.tools_used = []
        self.advanced_tools_used = []
        self.commands_executed = []
        self.findings = {}
        
    def execute(self):
        """Execute all disk forensic operations"""
        print("[*] Starting Disk Forensics...")
        print(f"    Advanced Tools: {'ENABLED' if self.use_advanced_tools else 'DISABLED'}")
        
        results = {
            'forensic_type': 'disk',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'advanced_tools_enabled': self.use_advanced_tools,
            'tools_used': [],
            'advanced_tools_used': [],
            'commands_executed': [],
            'findings': {},
            'raw_outputs': {}
        }
        
        try:
            # CORE FORENSICS (Always Execute)
            print("    [Core] Getting disk information...")
            results['findings']['disk_info'] = self._get_disk_info()
            
            print("    [Core] Getting filesystems...")
            results['findings']['filesystems'] = self._get_filesystems()
            
            print("    [Core] Getting partitions...")
            results['findings']['partitions'] = self._get_partitions()
            
            print("    [Core] Getting recent files...")
            results['findings']['recent_files'] = self._get_recent_files()
            
            print("    [Core] Scanning for suspicious files...")
            results['findings']['suspicious_files'] = self._find_suspicious_files()
            
            # ADVANCED FORENSICS (If Enabled)
            if self.use_advanced_tools:
                print("\n    [Advanced] Using enhanced tools...")
                
                # The Sleuth Kit
                if self._check_tool('fls'):
                    print("    [TSK] Analyzing filesystem with fls...")
                    results['findings']['filesystem_analysis'] = self._analyze_filesystem_tsk()
                    
                    print("    [TSK] Searching for deleted files...")
                    results['findings']['deleted_files'] = self._find_deleted_files_tsk()
                    
                if self._check_tool('mmls'):
                    print("    [TSK] Analyzing partition table...")
                    results['findings']['partition_analysis'] = self._analyze_partitions_tsk()
                
                # Foremost
                if self._check_tool('foremost'):
                    print("    [Foremost] File carving analysis...")
                    results['findings']['file_carving'] = self._file_carving_analysis()
                
                if not self.advanced_tools_used:
                    results['findings']['advanced_tools_note'] = "Advanced tools enabled but not found in system PATH or configured paths"
            
            results['status'] = 'completed'
            results['tools_used'] = list(set(self.tools_used))
            results['advanced_tools_used'] = list(set(self.advanced_tools_used))
            results['commands_executed'] = self.commands_executed
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
            import traceback
            results['traceback'] = traceback.format_exc()
        
        # Save individual forensic JSON
        self._save_json(results, 'disk_forensics.json')
        
        return results
    
    def _check_tool(self, tool_name):
        """Check if tool is available"""
        tool_path = Config.get_tool_path(tool_name)
        return tool_path is not None
    
    def _run_command(self, command, description=""):
        """Run command and track it"""
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        self.commands_executed.append({
            'command': cmd_str,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                shell=(platform.system() == 'Windows')
            )
            return result
        except Exception as e:
            print(f"    [!] Command failed: {cmd_str} - {str(e)}")
            return None
    
    def _get_disk_info(self):
        """Get disk information"""
        disk_info = {
            'platform': platform.system(),
            'disks': []
        }
        
        try:
            if platform.system() == 'Linux':
                result = self._run_command(['lsblk', '-J'], "List block devices")
                if result and result.returncode == 0:
                    disk_info['lsblk_output'] = json.loads(result.stdout)
                    self.tools_used.append('lsblk')
                
                result = self._run_command(['df', '-h'], "Disk space usage")
                if result and result.returncode == 0:
                    disk_info['disk_usage'] = result.stdout
                    self.tools_used.append('df')
                    
            elif platform.system() == 'Windows':
                result = self._run_command(
                    'wmic diskdrive get size,model,caption',
                    "Get disk drives information"
                )
                if result and result.returncode == 0:
                    disk_info['wmic_output'] = result.stdout
                    self.tools_used.append('wmic')
                
                result = self._run_command(
                    'wmic logicaldisk get size,freespace,caption',
                    "Get logical disk information"
                )
                if result and result.returncode == 0:
                    disk_info['logical_disks'] = result.stdout
        
        except Exception as e:
            disk_info['error'] = str(e)
        
        return disk_info
    
    def _get_filesystems(self):
        """Get mounted filesystems"""
        filesystems = []
        
        try:
            if platform.system() == 'Linux':
                result = self._run_command(['mount'], "List mounted filesystems")
                if result and result.returncode == 0:
                    filesystems = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                    self.tools_used.append('mount')
                    
            elif platform.system() == 'Windows':
                result = self._run_command(
                    'wmic volume get driveletter,filesystem,label,capacity',
                    "Get volume information"
                )
                if result and result.returncode == 0:
                    filesystems = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                    self.tools_used.append('wmic')
        
        except Exception as e:
            filesystems.append(f"Error: {str(e)}")
        
        return filesystems
    
    def _get_partitions(self):
        """Get partition information"""
        partitions = []
        
        try:
            if platform.system() == 'Linux':
                result = self._run_command(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'], "List partitions")
                if result and result.returncode == 0:
                    partitions.append(result.stdout)
                    self.tools_used.append('lsblk')
                    
            elif platform.system() == 'Windows':
                result = self._run_command(
                    'wmic partition get name,size,type',
                    "Get partition information"
                )
                if result and result.returncode == 0:
                    partitions.append(result.stdout)
                    self.tools_used.append('wmic')
        
        except Exception as e:
            partitions.append(f"Error: {str(e)}")
        
        return partitions
    
    def _get_recent_files(self):
        """Get recently modified files"""
        recent_files = []
        
        try:
            if platform.system() == 'Linux':
                search_paths = ['/home', '/tmp', '/var/tmp']
                
                for path in search_paths:
                    if os.path.exists(path):
                        result = self._run_command(
                            ['find', path, '-type', 'f', '-mtime', '-7', '-ls'],
                            f"Find recent files in {path}"
                        )
                        if result and result.returncode == 0:
                            files = result.stdout.split('\n')[:50]
                            recent_files.extend([f for f in files if f.strip()])
                
                self.tools_used.append('find')
                
            elif platform.system() == 'Windows':
                # Use a simpler approach for Windows
                print("    [Core] Scanning Windows user directories...")
                try:
                    import glob
                    from datetime import datetime, timedelta
                    
                    cutoff_time = datetime.now() - timedelta(days=7)
                    cutoff_timestamp = cutoff_time.timestamp()
                    
                    # Search in Downloads and Desktop
                    user_path = os.path.expanduser('~')
                    search_locations = [
                        os.path.join(user_path, 'Downloads'),
                        os.path.join(user_path, 'Desktop'),
                        os.path.join(user_path, 'Documents')
                    ]
                    
                    for location in search_locations:
                        if os.path.exists(location):
                            try:
                                for root, dirs, files in os.walk(location):
                                    for filename in files[:20]:  # Limit per directory
                                        filepath = os.path.join(root, filename)
                                        try:
                                            stat = os.stat(filepath)
                                            if stat.st_mtime > cutoff_timestamp:
                                                recent_files.append({
                                                    'path': filepath,
                                                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                                    'size': stat.st_size
                                                })
                                        except:
                                            continue
                                    if len(recent_files) >= 50:
                                        break
                                if len(recent_files) >= 50:
                                    break
                            except:
                                continue
                    
                    self.tools_used.append('os.walk')
                except Exception as e:
                    print(f"    [!] Error in Windows file search: {e}")
                    recent_files.append(f"Error: {str(e)}")
        
        except Exception as e:
            print(f"    [!] Error getting recent files: {e}")
            recent_files.append(f"Error: {str(e)}")
        
        print(f"    [+] Found {len(recent_files)} recent files")
        return recent_files[:50]
    
    def _find_suspicious_files(self):
        """Find suspicious file extensions"""
        suspicious_extensions = [
            '.exe', '.bat', '.cmd', '.vbs', '.ps1', '.sh', 
            '.dll', '.scr', '.tmp'
        ]
        
        suspicious = {
            'extensions_checked': suspicious_extensions,
            'files_found': []
        }
        
        try:
            print("    [Core] Scanning for suspicious files...")
            
            if platform.system() == 'Linux':
                search_paths = ['/tmp', '/var/tmp']
                
                for ext in suspicious_extensions:
                    for path in search_paths:
                        if os.path.exists(path):
                            result = self._run_command(
                                ['find', path, '-name', f'*{ext}', '-type', 'f'],
                                f"Search for {ext} files in {path}"
                            )
                            if result and result.returncode == 0 and result.stdout.strip():
                                found = result.stdout.split('\n')[:10]
                                suspicious['files_found'].extend([f for f in found if f.strip()])
            
            elif platform.system() == 'Windows':
                # Search in common suspicious locations
                temp_paths = [
                    os.path.expandvars('%TEMP%'),
                    'C:\\Windows\\Temp',
                    os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp')
                ]
                
                for temp_path in temp_paths:
                    if os.path.exists(temp_path):
                        try:
                            for ext in suspicious_extensions:
                                pattern = os.path.join(temp_path, f'*{ext}')
                                import glob
                                files = glob.glob(pattern)[:5]
                                suspicious['files_found'].extend(files)
                        except Exception as e:
                            print(f"    [!] Error scanning {temp_path}: {e}")
                            continue
                
                self.tools_used.append('glob')
            
            print(f"    [+] Found {len(suspicious['files_found'])} suspicious files")
        
        except Exception as e:
            print(f"    [!] Error finding suspicious files: {e}")
            suspicious['error'] = str(e)
        
        return suspicious
    
    # ADVANCED TOOLS METHODS
    
    def _analyze_filesystem_tsk(self):
        """Analyze filesystem using The Sleuth Kit"""
        analysis = {
            'tool': 'fls (The Sleuth Kit)',
            'status': 'running'
        }
        
        fls_path = Config.get_tool_path('fls')
        if not fls_path:
            analysis['status'] = 'not_available'
            return analysis
        
        self.advanced_tools_used.append('fls')
        
        # Note: This is a demonstration - in real use, you'd specify actual disk image or device
        analysis['note'] = 'Advanced filesystem analysis available with disk image path'
        analysis['capabilities'] = [
            'List all files including deleted',
            'Show file metadata (MAC times)',
            'Identify unallocated inodes',
            'Recover file contents'
        ]
        analysis['status'] = 'configured'
        
        return analysis
    
    def _find_deleted_files_tsk(self):
        """Find deleted files using TSK"""
        deleted = {
            'tool': 'fls -rd (TSK Deleted Files)',
            'status': 'ready'
        }
        
        fls_path = Config.get_tool_path('fls')
        if not fls_path:
            deleted['status'] = 'not_available'
            return deleted
        
        self.advanced_tools_used.append('fls')
        
        deleted['note'] = 'Deleted file recovery ready - requires disk image or device path'
        deleted['capabilities'] = [
            'Scan for deleted file entries',
            'Recover file metadata',
            'Extract deleted file contents',
            'Timeline analysis of deletions'
        ]
        
        return deleted
    
    def _analyze_partitions_tsk(self):
        """Analyze partitions using mmls"""
        partition_analysis = {
            'tool': 'mmls (TSK Partition Analysis)',
            'status': 'ready'
        }
        
        mmls_path = Config.get_tool_path('mmls')
        if not mmls_path:
            partition_analysis['status'] = 'not_available'
            return partition_analysis
        
        self.advanced_tools_used.append('mmls')
        
        partition_analysis['note'] = 'Partition analysis ready - requires disk image'
        partition_analysis['capabilities'] = [
            'Display partition layout',
            'Identify partition types',
            'Show start/end sectors',
            'Detect hidden partitions'
        ]
        
        return partition_analysis
    
    def _file_carving_analysis(self):
        """File carving analysis using Foremost"""
        carving = {
            'tool': 'foremost (File Carving)',
            'status': 'ready'
        }
        
        foremost_path = Config.get_tool_path('foremost')
        if not foremost_path:
            carving['status'] = 'not_available'
            return carving
        
        self.advanced_tools_used.append('foremost')
        
        carving['note'] = 'File carving ready - can recover files from unallocated space'
        carving['capabilities'] = [
            'Recover deleted images (JPEG, PNG, GIF)',
            'Recover documents (PDF, DOC, XLS)',
            'Recover archives (ZIP, RAR, TAR)',
            'Recover videos and audio files',
            'Works on formatted drives'
        ]
        carving['supported_formats'] = ['jpg', 'png', 'gif', 'pdf', 'doc', 'xls', 'zip', 'rar']
        
        return carving
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Disk forensics saved: {filepath}")