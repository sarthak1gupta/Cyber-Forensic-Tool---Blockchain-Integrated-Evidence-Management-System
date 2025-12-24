import os
import json
import subprocess
import psutil
from datetime import datetime

class MemoryForensics:
    """
    Memory Forensics Module
    Tools: psutil (live), Volatility (for memory dumps)
    """
    
    def __init__(self, session_dir):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'memory')
        self.tools_used = []
        
    def execute(self):
        """Execute all memory forensic operations"""
        print("[*] Starting Memory Forensics...")
        
        results = {
            'forensic_type': 'memory',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'tools_used': [],
            'findings': {},
            'raw_outputs': {}
        }
        
        try:
            # 1. Get running processes
            results['findings']['running_processes'] = self._get_running_processes()
            results['tools_used'].append('psutil')
            
            # 2. Get network connections
            results['findings']['network_connections'] = self._get_network_connections()
            
            # 3. Get loaded modules/DLLs
            results['findings']['loaded_modules'] = self._get_loaded_modules()
            
            # 4. Get memory usage statistics
            results['findings']['memory_stats'] = self._get_memory_stats()
            
            # 5. Detect suspicious processes
            results['findings']['suspicious_processes'] = self._detect_suspicious_processes()
            
            # 6. Get open files by processes
            results['findings']['open_files'] = self._get_open_files()
            
            # 7. Get environment variables
            results['findings']['env_variables'] = self._get_env_variables()
            
            results['status'] = 'completed'
            results['tools_used'] = list(set(results['tools_used']))
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        # Save individual forensic JSON
        self._save_json(results, 'memory_forensics.json')
        
        return results
    
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
            
            self.tools_used.append('psutil')
            
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
                
                # Get process name for this connection
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        conn_info['process_name'] = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        conn_info['process_name'] = 'Unknown'
                
                connections.append(conn_info)
            
        except (psutil.AccessDenied, PermissionError) as e:
            connections.append({'error': f'Access denied: {str(e)}', 
                              'note': 'May require root/admin privileges'})
        except Exception as e:
            connections.append({'error': str(e)})
        
        return connections
    
    def _get_loaded_modules(self):
        """Get loaded modules/DLLs for suspicious processes"""
        modules = []
        suspicious_process_count = 0
        
        try:
            # Check first 10 processes
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
                            'modules': proc_modules[:10]  # Limit to 10 modules per process
                        })
                    
                    suspicious_process_count += 1
                    if suspicious_process_count >= 10:
                        break
                        
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
            
            stats = {
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
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_suspicious_processes(self):
        """Detect potentially suspicious processes"""
        suspicious = []
        
        suspicious_indicators = {
            'high_cpu': 80.0,  # CPU usage > 80%
            'high_memory': 50.0,  # Memory usage > 50%
            'suspicious_names': ['nc', 'netcat', 'ncat', 'powershell', 'cmd', 'bash'],
            'suspicious_paths': ['/tmp', 'C:\\Temp', 'C:\\Windows\\Temp']
        }
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'exe', 
                                            'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    flags = []
                    
                    # Check CPU usage
                    if pinfo['cpu_percent'] and pinfo['cpu_percent'] > suspicious_indicators['high_cpu']:
                        flags.append(f"High CPU: {pinfo['cpu_percent']}%")
                    
                    # Check memory usage
                    if pinfo['memory_percent'] and pinfo['memory_percent'] > suspicious_indicators['high_memory']:
                        flags.append(f"High Memory: {pinfo['memory_percent']:.2f}%")
                    
                    # Check suspicious names
                    if pinfo['name']:
                        for sus_name in suspicious_indicators['suspicious_names']:
                            if sus_name.lower() in pinfo['name'].lower():
                                flags.append(f"Suspicious name: {pinfo['name']}")
                                break
                    
                    # Check suspicious paths
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
        process_count = 0
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    process = psutil.Process(proc.info['pid'])
                    files = process.open_files()
                    
                    if files:
                        open_files.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'files': [{'path': f.path, 'fd': f.fd} for f in files[:5]]  # Limit to 5
                        })
                    
                    process_count += 1
                    if process_count >= 20:  # Limit to 20 processes
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        except Exception as e:
            open_files.append({'error': str(e)})
        
        return open_files
    
    def _get_env_variables(self):
        """Get environment variables (limited for privacy)"""
        try:
            env_vars = dict(os.environ)
            
            # Only include relevant forensic variables
            relevant_keys = ['PATH', 'USER', 'HOME', 'SHELL', 'TEMP', 'TMP', 
                           'USERNAME', 'COMPUTERNAME', 'USERDOMAIN']
            
            filtered_env = {k: v for k, v in env_vars.items() if k in relevant_keys}
            
            return filtered_env
            
        except Exception as e:
            return {'error': str(e)}
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Memory forensics saved: {filepath}")