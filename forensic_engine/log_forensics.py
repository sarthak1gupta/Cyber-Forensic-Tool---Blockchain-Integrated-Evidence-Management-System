import os
import json
import subprocess
import platform
import re
from datetime import datetime, timedelta

class LogForensics:
    """
    Log Analysis Forensics Module
    Analyzes system logs for security events
    """
    
    def __init__(self, session_dir):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'logs')
        self.tools_used = []
        self.os_type = platform.system()
        
    def execute(self):
        """Execute all log forensic operations"""
        print("[*] Starting Log Forensics...")
        
        results = {
            'forensic_type': 'log',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'os_type': self.os_type,
            'tools_used': [],
            'findings': {},
            'raw_outputs': {}
        }
        
        try:
            if self.os_type == 'Linux':
                results['findings'] = self._analyze_linux_logs()
            elif self.os_type == 'Windows':
                results['findings'] = self._analyze_windows_logs()
            else:
                results['findings'] = {'error': f'Unsupported OS: {self.os_type}'}
            
            results['status'] = 'completed'
            results['tools_used'] = list(set(self.tools_used))
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        # Save individual forensic JSON
        self._save_json(results, 'log_forensics.json')
        
        return results
    
    def _analyze_linux_logs(self):
        """Analyze Linux system logs"""
        findings = {
            'auth_events': self._analyze_auth_log(),
            'syslog_events': self._analyze_syslog(),
            'failed_logins': self._get_failed_logins(),
            'sudo_commands': self._get_sudo_commands(),
            'ssh_attempts': self._get_ssh_attempts(),
            'cron_jobs': self._get_cron_jobs(),
            'recent_user_activity': self._get_recent_user_activity()
        }
        
        return findings
    
    def _analyze_auth_log(self):
        """Analyze authentication logs"""
        auth_events = {
            'successful_logins': [],
            'failed_attempts': [],
            'suspicious_activity': []
        }
        
        auth_log_paths = [
            '/var/log/auth.log',
            '/var/log/secure',
        ]
        
        for log_path in auth_log_paths:
            if os.path.exists(log_path):
                try:
                    # Get last 100 lines
                    result = subprocess.run(['tail', '-n', '100', log_path],
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        
                        for line in lines:
                            if 'Accepted' in line and 'ssh' in line.lower():
                                auth_events['successful_logins'].append(line)
                            elif 'Failed password' in line:
                                auth_events['failed_attempts'].append(line)
                            elif 'POSSIBLE BREAK-IN ATTEMPT' in line:
                                auth_events['suspicious_activity'].append(line)
                        
                        self.tools_used.append('tail')
                        break  # Found a valid log
                
                except Exception as e:
                    auth_events['error'] = str(e)
        
        return auth_events
    
    def _analyze_syslog(self):
        """Analyze system logs"""
        syslog_events = {
            'errors': [],
            'warnings': [],
            'critical': []
        }
        
        syslog_paths = [
            '/var/log/syslog',
            '/var/log/messages'
        ]
        
        for log_path in syslog_paths:
            if os.path.exists(log_path):
                try:
                    # Get last 100 lines
                    result = subprocess.run(['tail', '-n', '100', log_path],
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        
                        for line in lines:
                            lower_line = line.lower()
                            if 'error' in lower_line:
                                syslog_events['errors'].append(line)
                            elif 'warning' in lower_line or 'warn' in lower_line:
                                syslog_events['warnings'].append(line)
                            elif 'critical' in lower_line or 'crit' in lower_line:
                                syslog_events['critical'].append(line)
                        
                        break  # Found a valid log
                
                except Exception as e:
                    syslog_events['error'] = str(e)
        
        return syslog_events
    
    def _get_failed_logins(self):
        """Get failed login attempts"""
        failed = []
        
        try:
            result = subprocess.run(['grep', 'Failed password', '/var/log/auth.log'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')[-50:]  # Last 50
                failed = [line for line in lines if line.strip()]
                self.tools_used.append('grep')
        
        except Exception as e:
            failed.append(f"Error: {str(e)}")
        
        return failed
    
    def _get_sudo_commands(self):
        """Get sudo command history"""
        sudo_cmds = []
        
        auth_log_paths = ['/var/log/auth.log', '/var/log/secure']
        
        for log_path in auth_log_paths:
            if os.path.exists(log_path):
                try:
                    result = subprocess.run(['grep', 'sudo', log_path],
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')[-30:]  # Last 30
                        sudo_cmds = [line for line in lines if line.strip() and 'COMMAND=' in line]
                        self.tools_used.append('grep')
                        break
                
                except Exception as e:
                    sudo_cmds.append(f"Error: {str(e)}")
        
        return sudo_cmds
    
    def _get_ssh_attempts(self):
        """Get SSH connection attempts"""
        ssh_attempts = {
            'successful': [],
            'failed': []
        }
        
        auth_log_paths = ['/var/log/auth.log', '/var/log/secure']
        
        for log_path in auth_log_paths:
            if os.path.exists(log_path):
                try:
                    # Successful SSH
                    result = subprocess.run(['grep', 'sshd.*Accepted', log_path],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        ssh_attempts['successful'] = result.stdout.split('\n')[-20:]
                    
                    # Failed SSH
                    result = subprocess.run(['grep', 'sshd.*Failed', log_path],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        ssh_attempts['failed'] = result.stdout.split('\n')[-20:]
                    
                    self.tools_used.append('grep')
                    break
                
                except Exception as e:
                    ssh_attempts['error'] = str(e)
        
        return ssh_attempts
    
    def _get_cron_jobs(self):
        """Get scheduled cron jobs"""
        cron_jobs = []
        
        try:
            # System crontab
            if os.path.exists('/etc/crontab'):
                with open('/etc/crontab', 'r') as f:
                    cron_jobs.append({
                        'file': '/etc/crontab',
                        'content': f.read()
                    })
            
            # User crontabs
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                cron_jobs.append({
                    'file': 'user crontab',
                    'content': result.stdout
                })
                self.tools_used.append('crontab')
        
        except Exception as e:
            cron_jobs.append({'error': str(e)})
        
        return cron_jobs
    
    def _get_recent_user_activity(self):
        """Get recent user login activity"""
        activity = {
            'last_logins': [],
            'who_logged_in': []
        }
        
        try:
            # Last command - show recent logins
            result = subprocess.run(['last', '-20'], capture_output=True, text=True)
            if result.returncode == 0:
                activity['last_logins'] = result.stdout.split('\n')
                self.tools_used.append('last')
            
            # Who command - currently logged in users
            result = subprocess.run(['who'], capture_output=True, text=True)
            if result.returncode == 0:
                activity['who_logged_in'] = result.stdout.split('\n')
                self.tools_used.append('who')
        
        except Exception as e:
            activity['error'] = str(e)
        
        return activity
    
    def _analyze_windows_logs(self):
        """Analyze Windows event logs"""
        findings = {
            'security_events': self._get_windows_security_events(),
            'system_events': self._get_windows_system_events(),
            'application_events': self._get_windows_application_events(),
            'failed_logins': self._get_windows_failed_logins(),
            'powershell_history': self._get_powershell_history()
        }
        
        return findings
    
    def _get_windows_security_events(self):
        """Get Windows security events"""
        events = []
        
        try:
            # Get last 50 security events
            cmd = [
                'wevtutil', 'qe', 'Security', '/c:50', '/rd:true', '/f:text'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                events = result.stdout.split('\n')
                self.tools_used.append('wevtutil')
        
        except Exception as e:
            events.append(f"Error: {str(e)}")
        
        return events
    
    def _get_windows_system_events(self):
        """Get Windows system events"""
        events = []
        
        try:
            cmd = [
                'wevtutil', 'qe', 'System', '/c:50', '/rd:true', '/f:text'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                events = result.stdout.split('\n')
                self.tools_used.append('wevtutil')
        
        except Exception as e:
            events.append(f"Error: {str(e)}")
        
        return events
    
    def _get_windows_application_events(self):
        """Get Windows application events"""
        events = []
        
        try:
            cmd = [
                'wevtutil', 'qe', 'Application', '/c:50', '/rd:true', '/f:text'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                events = result.stdout.split('\n')
                self.tools_used.append('wevtutil')
        
        except Exception as e:
            events.append(f"Error: {str(e)}")
        
        return events
    
    def _get_windows_failed_logins(self):
        """Get failed login attempts on Windows"""
        failed = []
        
        try:
            # Event ID 4625 is failed logon
            cmd = [
                'wevtutil', 'qe', 'Security', 
                '/q:*[System[(EventID=4625)]]', 
                '/c:20', '/rd:true', '/f:text'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                failed = result.stdout.split('\n')
                self.tools_used.append('wevtutil')
        
        except Exception as e:
            failed.append(f"Error: {str(e)}")
        
        return failed
    
    def _get_powershell_history(self):
        """Get PowerShell command history"""
        history = []
        
        try:
            # PowerShell history location
            history_path = os.path.expanduser(
                '~\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt'
            )
            
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    history = [line.strip() for line in lines[-50:]]  # Last 50 commands
        
        except Exception as e:
            history.append(f"Error: {str(e)}")
        
        return history
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Log forensics saved: {filepath}")