import os
import json
import psutil
from datetime import datetime
from config import Config

class MemoryForensics:
    """
    Enhanced Memory Forensics Module
    Core Tools: psutil
    Advanced Tools: Volatility (for memory dumps)
    """
    
    def __init__(self, session_dir, use_advanced_tools=False):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'memory')
        self.use_advanced_tools = use_advanced_tools
        self.tools_used = []
        self.advanced_tools_used = []
        self.commands_executed = []
        
    def execute(self):
        """Execute all memory forensic operations"""
        print("[*] Starting Memory Forensics...")
        print(f"    Advanced Tools: {'ENABLED' if self.use_advanced_tools else 'DISABLED'}")
        
        results = {
            'forensic_type': 'memory',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'advanced_tools_enabled': self.use_advanced_tools,
            'tools_used': [],
            'advanced_tools_used': [],
            'commands_executed': [],
            'findings': {}
        }
        
        try:
            # CORE FORENSICS (Always Execute)
            print("    [Core] Analyzing running processes...")
            self._log_command("psutil.process_iter()", "Enumerate all running processes")
            results['findings']['running_processes'] = self._get_running_processes()
            self.tools_used.append('psutil')
            
            print("    [Core] Analyzing network connections...")
            self._log_command("psutil.net_connections()", "Get active network connections")
            results['findings']['network_connections'] = self._get_network_connections()
            
            print("    [Core] Analyzing loaded modules...")
            self._log_command("psutil.Process.memory_maps()", "Get loaded modules per process")
            results['findings']['loaded_modules'] = self._get_loaded_modules()
            
            print("    [Core] Getting memory statistics...")
            self._log_command("psutil.virtual_memory()", "Get memory usage statistics")
            results['findings']['memory_stats'] = self._get_memory_stats()
            
            print("    [Core] Detecting suspicious processes...")
            self._log_command("Custom anomaly detection", "Identify suspicious process patterns")
            results['findings']['suspicious_processes'] = self._detect_suspicious_processes()
            
            print("    [Core] Analyzing open files...")
            self._log_command("psutil.Process.open_files()", "Get files opened by processes")
            results['findings']['open_files'] = self._get_open_files()
            
            print("    [Core] Getting environment variables...")
            self._log_command("os.environ", "Capture relevant environment variables")
            results['findings']['env_variables'] = self._get_env_variables()
            
            # ADVANCED FORENSICS (If Enabled)
            if self.use_advanced_tools:
                print("\n    [Advanced] Checking for Volatility...")
                vol_path = Config.get_tool_path('volatility3') or Config.get_tool_path('vol.py')
                if vol_path:
                    print("    [Volatility] Advanced memory analysis available...")
                    results['findings']['volatility_info'] = self._volatility_analysis_info()
                    self.advanced_tools_used.append('volatility3')
                else:
                    results['findings']['volatility_info'] = {
                        'status': 'not_available',
                        'note': 'Volatility not found - live analysis only'
                    }
            
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
        self._save_json(results, 'memory_forensics.json')
        
        return results
    
    def _log_command(self, command, description):
        """Log command execution"""
        self.commands_executed.append({
            'command': command,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
    
    def _get_running_processes(self):
        """Get all running processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time', 
                                            'cpu_percent', 'memory_percent', 'status', 
                                            'cmdline', 'exe']):
                try:
                    pinfo = proc.info
                    pinfo['create_time_formatted'] = datetime.fromtimestamp(
                        pinfo['create_time']
                    ).isoformat() if pinfo['create_time'] else None
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
        except Exception as e:
            processes.append({'error': str(e)})
        
        return processes
    
    def _get_network_connections(self):
        """Get active network connections"""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                conn_info = {
                    'fd': conn.fd,
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                }
                
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        conn_info['process_name'] = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        conn_info['process_name'] = 'Unknown'
                
                connections.append(conn_info)
            
        except (psutil.AccessDenied, PermissionError) as e:
            connections.append({'error': f'Access denied: {str(e)}'})
        except Exception as e:
            connections.append({'error': str(e)})
        
        return connections
    
    def _get_loaded_modules(self):
        """Get loaded modules for top processes"""
        modules = []
        
        try:
            for proc in list(psutil.process_iter(['pid', 'name']))[:10]:
                try:
                    process = psutil.Process(proc.info['pid'])
                    proc_modules = []
                    
                    for module in process.memory_maps():
                        proc_modules.append({
                            'path': module.path,
                            'size': module.rss
                        })
                    
                    if proc_modules:
                        modules.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'modules': proc_modules[:10]
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        except Exception as e:
            modules.append({'error': str(e)})
        
        return modules
    
    def _get_memory_stats(self):
        """Get memory usage statistics"""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            return {
                'virtual_memory': {
                    'total': virtual_mem.total,
                    'available': virtual_mem.available,
                    'used': virtual_mem.used,
                    'percent': virtual_mem.percent,
                    'free': virtual_mem.free
                },
                'swap_memory': {
                    'total': swap_mem.total,
                    'used': swap_mem.used,
                    'free': swap_mem.free,
                    'percent': swap_mem.percent
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_suspicious_processes(self):
        """Detect potentially suspicious processes"""
        suspicious = []
        
        suspicious_indicators = {
            'high_cpu': 80.0,
            'high_memory': 50.0,
            'suspicious_names': ['nc', 'netcat', 'ncat', 'powershell', 'cmd', 'bash', 'python'],
            'suspicious_paths': ['/tmp', 'C:\\Temp', 'C:\\Windows\\Temp', 'AppData\\Local\\Temp']
        }
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'exe', 
                                            'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    flags = []
                    
                    if pinfo['cpu_percent'] and pinfo['cpu_percent'] > suspicious_indicators['high_cpu']:
                        flags.append(f"High CPU: {pinfo['cpu_percent']}%")
                    
                    if pinfo['memory_percent'] and pinfo['memory_percent'] > suspicious_indicators['high_memory']:
                        flags.append(f"High Memory: {pinfo['memory_percent']:.2f}%")
                    
                    if pinfo['name']:
                        for sus_name in suspicious_indicators['suspicious_names']:
                            if sus_name.lower() in pinfo['name'].lower():
                                flags.append(f"Suspicious name: {pinfo['name']}")
                                break
                    
                    if pinfo['exe']:
                        for sus_path in suspicious_indicators['suspicious_paths']:
                            if sus_path.lower() in pinfo['exe'].lower():
                                flags.append(f"Suspicious path: {pinfo['exe']}")
                                break
                    
                    if flags:
                        suspicious.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'user': pinfo['username'],
                            'exe': pinfo['exe'],
                            'flags': flags
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        except Exception as e:
            suspicious.append({'error': str(e)})
        
        return suspicious
    
    def _get_open_files(self):
        """Get open files by processes"""
        open_files = []
        
        try:
            for proc in list(psutil.process_iter(['pid', 'name']))[:20]:
                try:
                    process = psutil.Process(proc.info['pid'])
                    files = process.open_files()
                    
                    if files:
                        open_files.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'files': [{'path': f.path, 'fd': f.fd} for f in files[:5]]
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        except Exception as e:
            open_files.append({'error': str(e)})
        
        return open_files
    
    def _get_env_variables(self):
        """Get environment variables"""
        try:
            env_vars = dict(os.environ)
            relevant_keys = ['PATH', 'USER', 'HOME', 'SHELL', 'TEMP', 'TMP', 
                           'USERNAME', 'COMPUTERNAME', 'USERDOMAIN']
            return {k: v for k, v in env_vars.items() if k in relevant_keys}
        except Exception as e:
            return {'error': str(e)}
    
    def _volatility_analysis_info(self):
        """Provide Volatility analysis information"""
        return {
            'tool': 'Volatility 3',
            'status': 'configured',
            'note': 'Advanced memory dump analysis available',
            'capabilities': [
                'Analyze memory dumps for hidden processes',
                'Detect malware and rootkits',
                'Extract process memory',
                'Analyze network connections from memory',
                'Recover encryption keys',
                'Timeline analysis'
            ],
            'usage': 'Requires memory dump file for deep analysis'
        }
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Memory forensics saved: {filepath}")