import os
import json
import subprocess
import psutil
import socket
from datetime import datetime

class NetworkForensics:
    """
    Network Forensics Module
    Tools: psutil, netstat, tshark/tcpdump (if available)
    """
    
    def __init__(self, session_dir):
        self.session_dir = session_dir
        self.output_dir = os.path.join(session_dir, 'network')
        self.tools_used = []
        
    def execute(self):
        """Execute all network forensic operations"""
        print("[*] Starting Network Forensics...")
        
        results = {
            'forensic_type': 'network',
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'tools_used': [],
            'findings': {},
            'raw_outputs': {}
        }
        
        try:
            # 1. Get network interfaces
            results['findings']['network_interfaces'] = self._get_network_interfaces()
            results['tools_used'].append('psutil')
            
            # 2. Get active connections
            results['findings']['active_connections'] = self._get_active_connections()
            
            # 3. Get listening ports
            results['findings']['listening_ports'] = self._get_listening_ports()
            
            # 4. Get routing table
            results['findings']['routing_table'] = self._get_routing_table()
            
            # 5. Get ARP cache
            results['findings']['arp_cache'] = self._get_arp_cache()
            
            # 6. Detect suspicious connections
            results['findings']['suspicious_connections'] = self._detect_suspicious_connections()
            
            # 7. Get DNS cache (if available)
            results['findings']['dns_cache'] = self._get_dns_cache()
            
            # 8. Check firewall rules
            results['findings']['firewall_rules'] = self._get_firewall_rules()
            
            # 9. Get network statistics
            results['findings']['network_stats'] = self._get_network_stats()
            
            results['status'] = 'completed'
            results['tools_used'] = list(set(results['tools_used']))
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        # Save individual forensic JSON
        self._save_json(results, 'network_forensics.json')
        
        return results
    
    def _get_network_interfaces(self):
        """Get network interface information"""
        interfaces = []
        
        try:
            # Get interface addresses
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface, addr_list in addrs.items():
                iface_info = {
                    'name': interface,
                    'addresses': [],
                    'stats': {}
                }
                
                for addr in addr_list:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    iface_info['addresses'].append(addr_info)
                
                # Add interface statistics
                if interface in stats:
                    iface_info['stats'] = {
                        'isup': stats[interface].isup,
                        'speed': stats[interface].speed,
                        'mtu': stats[interface].mtu
                    }
                
                interfaces.append(iface_info)
            
            self.tools_used.append('psutil')
            
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
                    'local_addr': None,
                    'remote_addr': None,
                    'status': conn.status,
                    'pid': conn.pid,
                    'process': None
                }
                
                # Format addresses
                if conn.laddr:
                    conn_info['local_addr'] = f"{conn.laddr.ip}:{conn.laddr.port}"
                
                if conn.raddr:
                    conn_info['remote_addr'] = f"{conn.raddr.ip}:{conn.raddr.port}"
                
                # Get process information
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        conn_info['process'] = {
                            'name': proc.name(),
                            'exe': proc.exe(),
                            'cmdline': ' '.join(proc.cmdline())
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                connections.append(conn_info)
        
        except (psutil.AccessDenied, PermissionError) as e:
            connections.append({
                'error': 'Access denied',
                'note': 'May require root/admin privileges',
                'detail': str(e)
            })
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
            listening.append({'error': 'Access denied', 'note': 'Requires elevated privileges'})
        except Exception as e:
            listening.append({'error': str(e)})
        
        return listening
    
    def _get_routing_table(self):
        """Get routing table"""
        routing = []
        
        try:
            if os.name == 'posix':  # Linux/Mac
                result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
                if result.returncode == 0:
                    routing = result.stdout.split('\n')
                    self.tools_used.append('ip route')
                else:
                    # Fallback to route
                    result = subprocess.run(['route', '-n'], capture_output=True, text=True)
                    if result.returncode == 0:
                        routing = result.stdout.split('\n')
                        self.tools_used.append('route')
            
            else:  # Windows
                result = subprocess.run(['route', 'print'], capture_output=True, text=True)
                if result.returncode == 0:
                    routing = result.stdout.split('\n')
                    self.tools_used.append('route')
        
        except Exception as e:
            routing.append(f"Error: {str(e)}")
        
        return [r for r in routing if r.strip()]
    
    def _get_arp_cache(self):
        """Get ARP cache"""
        arp = []
        
        try:
            if os.name == 'posix':
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
                if result.returncode == 0:
                    arp = result.stdout.split('\n')
                    self.tools_used.append('arp')
            
            else:  # Windows
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    arp = result.stdout.split('\n')
                    self.tools_used.append('arp')
        
        except Exception as e:
            arp.append(f"Error: {str(e)}")
        
        return [a for a in arp if a.strip()]
    
    def _detect_suspicious_connections(self):
        """Detect suspicious network connections"""
        suspicious = []
        
        # Known suspicious ports and IPs
        suspicious_ports = [
            4444,  # Metasploit default
            31337,  # Back Orifice
            12345, 12346,  # NetBus
            1234, 6667, 6668, 6669,  # IRC
            27374,  # SubSeven
        ]
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                flags = []
                
                # Check for suspicious ports
                if conn.laddr and conn.laddr.port in suspicious_ports:
                    flags.append(f"Suspicious local port: {conn.laddr.port}")
                
                if conn.raddr and conn.raddr.port in suspicious_ports:
                    flags.append(f"Suspicious remote port: {conn.raddr.port}")
                
                # Check for non-standard HTTP/HTTPS ports
                if conn.raddr and conn.raddr.port not in [80, 443, 8080, 8443]:
                    if conn.status == 'ESTABLISHED':
                        flags.append(f"Non-standard port connection: {conn.raddr.port}")
                
                # Check for connections to private IPs from unusual processes
                if conn.raddr and conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        proc_name = proc.name().lower()
                        
                        # Flag if non-browser making external connections
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
    
    def _get_dns_cache(self):
        """Get DNS cache"""
        dns_cache = []
        
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ipconfig', '/displaydns'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    dns_cache = result.stdout.split('\n')[:100]  # Limit output
                    self.tools_used.append('ipconfig')
            
            else:  # Linux - DNS cache not readily available without additional tools
                dns_cache.append("DNS cache not readily available on this system")
                dns_cache.append("Consider using: sudo systemd-resolve --statistics")
        
        except Exception as e:
            dns_cache.append(f"Error: {str(e)}")
        
        return [d for d in dns_cache if d.strip()]
    
    def _get_firewall_rules(self):
        """Get firewall rules"""
        firewall = []
        
        try:
            if os.name == 'posix':
                # Try iptables (Linux)
                result = subprocess.run(['sudo', 'iptables', '-L', '-n'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    firewall = result.stdout.split('\n')
                    self.tools_used.append('iptables')
                else:
                    firewall.append("Requires root privileges to view iptables")
            
            else:  # Windows
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    firewall = result.stdout.split('\n')
                    self.tools_used.append('netsh')
        
        except subprocess.TimeoutExpired:
            firewall.append("Command timed out - may require elevated privileges")
        except Exception as e:
            firewall.append(f"Error: {str(e)}")
        
        return [f for f in firewall if f.strip()][:50]  # Limit output
    
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
    
    def _save_json(self, data, filename):
        """Save JSON output"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"[+] Network forensics saved: {filepath}")