import os
import json
import subprocess
import psutil
import platform
from datetime import datetime
from config import Config

class NetworkForensics:
    """
    Enhanced Network Forensics Module
    Core Tools: psutil, netstat, arp, route
    Advanced Tools: tshark (Wireshark CLI)
    """
    
    def __init__(self, session_dir, use_advanced_tools=False):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'network')
        self.use_advanced_tools = use_advanced_tools
        self.tools_used = []
        self.advanced_tools_used = []
        self.commands_executed = []
        
    def execute(self):
        """Execute all network forensic operations"""
        print("[*] Starting Network Forensics...")
        print(f"    Advanced Tools: {'ENABLED' if self.use_advanced_tools else 'DISABLED'}")
        
        results = {
            'forensic_type': 'network',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'advanced_tools_enabled': self.use_advanced_tools,
            'tools_used': [],
            'advanced_tools_used': [],
            'commands_executed': [],
            'findings': {}
        }
        
        try:
            # CORE FORENSICS
            print("    [Core] Getting network interfaces...")
            self._log_command("psutil.net_if_addrs()", "Enumerate network interfaces")
            results['findings']['network_interfaces'] = self._get_network_interfaces()
            self.tools_used.append('psutil')
            
            print("    [Core] Getting active connections...")
            self._log_command("psutil.net_connections()", "List active network connections")
            results['findings']['active_connections'] = self._get_active_connections()
            
            print("    [Core] Getting listening ports...")
            self._log_command("Filter LISTEN status", "Identify listening ports and services")
            results['findings']['listening_ports'] = self._get_listening_ports()
            
            print("    [Core] Getting routing table...")
            self._log_command(f"{'route print' if platform.system() == 'Windows' else 'ip route'}", "Display routing table")
            results['findings']['routing_table'] = self._get_routing_table()
            
            print("    [Core] Getting ARP cache...")
            self._log_command("arp -a", "Display ARP cache table")
            results['findings']['arp_cache'] = self._get_arp_cache()
            
            print("    [Core] Detecting suspicious connections...")
            self._log_command("Custom anomaly detection", "Identify suspicious network patterns")
            results['findings']['suspicious_connections'] = self._detect_suspicious_connections()
            
            print("    [Core] Getting network statistics...")
            self._log_command("psutil.net_io_counters()", "Gather network I/O statistics")
            results['findings']['network_stats'] = self._get_network_stats()
            
            # ADVANCED FORENSICS
            if self.use_advanced_tools:
                print("\n    [Advanced] Checking for tshark...")
                tshark_path = Config.get_tool_path('tshark')
                if tshark_path:
                    print("    [tshark] Deep packet analysis available...")
                    results['findings']['tshark_info'] = self._tshark_analysis_info()
                    self.advanced_tools_used.append('tshark')
                else:
                    results['findings']['tshark_info'] = {
                        'status': 'not_available',
                        'note': 'tshark not found - basic network analysis only'
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
        
        self._save_json(results, 'network_forensics.json')
        return results
    
    def _log_command(self, command, description):
        """Log command execution"""
        self.commands_executed.append({
            'command': command,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
    
    def _run_command(self, command, description=""):
        """Run system command"""
        if description:
            self._log_command(' '.join(command) if isinstance(command, list) else command, description)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=(platform.system() == 'Windows')
            )
            return result
        except Exception as e:
            return None
    
    def _get_network_interfaces(self):
        """Get network interface information"""
        interfaces = []
        
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface, addr_list in addrs.items():
                iface_info = {
                    'name': interface,
                    'addresses': [],
                    'stats': {}
                }
                
                for addr in addr_list:
                    iface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                if interface in stats:
                    iface_info['stats'] = {
                        'isup': stats[interface].isup,
                        'speed': stats[interface].speed,
                        'mtu': stats[interface].mtu
                    }
                
                interfaces.append(iface_info)
            
        except Exception as e:
            interfaces.append({'error': str(e)})
        
        return interfaces
    
    def _get_active_connections(self):
        """Get all active network connections"""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                conn_info = {
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid,
                    'process': None
                }
                
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        conn_info['process'] = {
                            'name': proc.name(),
                            'exe': proc.exe()
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                connections.append(conn_info)
        
        except (psutil.AccessDenied, PermissionError) as e:
            connections.append({'error': 'Access denied - requires elevated privileges'})
        except Exception as e:
            connections.append({'error': str(e)})
        
        return connections
    
    def _get_listening_ports(self):
        """Get listening ports"""
        listening = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    port_info = {
                        'port': conn.laddr.port if conn.laddr else None,
                        'address': conn.laddr.ip if conn.laddr else None,
                        'pid': conn.pid,
                        'process': None
                    }
                    
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            port_info['process'] = proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    listening.append(port_info)
        
        except (psutil.AccessDenied, PermissionError):
            listening.append({'error': 'Access denied'})
        except Exception as e:
            listening.append({'error': str(e)})
        
        return listening
    
    def _get_routing_table(self):
        """Get routing table"""
        routing = []
        
        try:
            if platform.system() == 'Windows':
                result = self._run_command('route print', "Get Windows routing table")
            else:
                result = self._run_command(['ip', 'route'], "Get Linux routing table")
                if not result or result.returncode != 0:
                    result = self._run_command(['route', '-n'], "Fallback to route command")
            
            if result and result.returncode == 0:
                routing = [r for r in result.stdout.split('\n') if r.strip()]
                self.tools_used.append('route' if platform.system() == 'Windows' else 'ip')
        
        except Exception as e:
            routing.append(f"Error: {str(e)}")
        
        return routing
    
    def _get_arp_cache(self):
        """Get ARP cache"""
        arp = []
        
        try:
            result = self._run_command(['arp', '-a'], "Display ARP cache")
            
            if result and result.returncode == 0:
                arp = [a for a in result.stdout.split('\n') if a.strip()]
                self.tools_used.append('arp')
        
        except Exception as e:
            arp.append(f"Error: {str(e)}")
        
        return arp
    
    def _detect_suspicious_connections(self):
        """Detect suspicious network connections"""
        suspicious = []
        suspicious_ports = [4444, 31337, 12345, 12346, 1234, 6667, 6668, 6669, 27374]
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                flags = []
                
                if conn.laddr and conn.laddr.port in suspicious_ports:
                    flags.append(f"Suspicious local port: {conn.laddr.port}")
                
                if conn.raddr and conn.raddr.port in suspicious_ports:
                    flags.append(f"Suspicious remote port: {conn.raddr.port}")
                
                if conn.raddr and conn.raddr.port not in [80, 443, 8080, 8443] and conn.status == 'ESTABLISHED':
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            proc_name = proc.name().lower()
                            if 'browser' not in proc_name and 'chrome' not in proc_name and 'firefox' not in proc_name:
                                if not conn.raddr.ip.startswith(('192.168.', '10.', '172.')):
                                    flags.append(f"Non-browser external connection: {proc_name}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                if flags:
                    suspicious.append({
                        'local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid,
                        'flags': flags
                    })
        
        except Exception as e:
            suspicious.append({'error': str(e)})
        
        return suspicious
    
    def _get_network_stats(self):
        """Get network I/O statistics"""
        try:
            io_counters = psutil.net_io_counters(pernic=True)
            stats = {}
            
            for interface, counters in io_counters.items():
                stats[interface] = {
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errin': counters.errin,
                    'errout': counters.errout,
                    'dropin': counters.dropin,
                    'dropout': counters.dropout
                }
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def _tshark_analysis_info(self):
        """Provide tshark analysis information"""
        return {
            'tool': 'tshark (Wireshark CLI)',
            'status': 'configured',
            'note': 'Deep packet analysis available',
            'capabilities': [
                'Capture live network traffic',
                'Analyze packet contents',
                'Extract HTTP requests/responses',
                'Decode protocols (DNS, TCP, UDP, HTTP, etc.)',
                'Follow TCP streams',
                'Extract files from network traffic',
                'Detect network anomalies'
            ],
            'usage': 'Can capture and analyze network packets for evidence'
        }
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Network forensics saved: {filepath}")