"""
Utility functions for forensic operations
Common functions used across different forensic modules
"""

import os
import json
import hashlib
import subprocess
import platform
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


def calculate_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (sha256, md5, sha1)
    
    Returns:
        Hex digest of file hash
    """
    hash_func = getattr(hashlib, algorithm)()
    
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"


def calculate_string_hash(data: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a string
    
    Args:
        data: String data
        algorithm: Hash algorithm
    
    Returns:
        Hex digest of hash
    """
    hash_func = getattr(hashlib, algorithm)()
    hash_func.update(data.encode('utf-8'))
    return hash_func.hexdigest()


def check_tool_available(tool_name: str) -> bool:
    """
    Check if a forensic tool is available on the system
    
    Args:
        tool_name: Name of the tool/command
    
    Returns:
        True if tool is available, False otherwise
    """
    return shutil.which(tool_name) is not None


def run_command(command: List[str], timeout: int = 30) -> Dict[str, Any]:
    """
    Run a system command safely with timeout
    
    Args:
        command: Command as list of strings
        timeout: Timeout in seconds
    
    Returns:
        Dict with returncode, stdout, stderr
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def get_system_info() -> Dict[str, str]:
    """
    Get system information
    
    Returns:
        Dict with OS, version, architecture, hostname
    """
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'os_release': platform.release(),
        'architecture': platform.machine(),
        'hostname': platform.node(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes into human-readable format
    
    Args:
        bytes_size: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to readable format
    
    Args:
        timestamp: Unix timestamp
    
    Returns:
        Formatted datetime string
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return 'Invalid timestamp'


def get_file_metadata(filepath: str) -> Dict[str, Any]:
    """
    Get file metadata
    
    Args:
        filepath: Path to file
    
    Returns:
        Dict with file metadata
    """
    try:
        stat = os.stat(filepath)
        return {
            'path': filepath,
            'size': stat.st_size,
            'size_formatted': format_bytes(stat.st_size),
            'created': format_timestamp(stat.st_ctime),
            'modified': format_timestamp(stat.st_mtime),
            'accessed': format_timestamp(stat.st_atime),
            'permissions': oct(stat.st_mode)[-3:],
            'owner_uid': stat.st_uid,
            'group_gid': stat.st_gid
        }
    except Exception as e:
        return {'error': str(e)}


def search_files(directory: str, pattern: str = '*', 
                 max_results: int = 100) -> List[str]:
    """
    Search for files matching pattern
    
    Args:
        directory: Directory to search
        pattern: File pattern (e.g., '*.exe')
        max_results: Maximum number of results
    
    Returns:
        List of file paths
    """
    import fnmatch
    
    results = []
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    results.append(os.path.join(root, filename))
                    if len(results) >= max_results:
                        return results
    except Exception as e:
        print(f"Error searching files: {e}")
    
    return results


def is_suspicious_file(filepath: str) -> Dict[str, Any]:
    """
    Check if a file is potentially suspicious
    
    Args:
        filepath: Path to file
    
    Returns:
        Dict with suspicious indicators
    """
    suspicious = {
        'is_suspicious': False,
        'reasons': []
    }
    
    # Suspicious extensions
    suspicious_extensions = [
        '.exe', '.bat', '.cmd', '.vbs', '.ps1', '.sh',
        '.dll', '.scr', '.pif', '.com', '.jar'
    ]
    
    # Suspicious locations
    suspicious_locations = [
        '/tmp', '/var/tmp', 'C:\\Temp', 'C:\\Windows\\Temp',
        '/dev/shm', 'AppData\\Local\\Temp'
    ]
    
    # Check extension
    ext = os.path.splitext(filepath)[1].lower()
    if ext in suspicious_extensions:
        suspicious['is_suspicious'] = True
        suspicious['reasons'].append(f'Executable extension: {ext}')
    
    # Check location
    for loc in suspicious_locations:
        if loc in filepath:
            suspicious['is_suspicious'] = True
            suspicious['reasons'].append(f'Suspicious location: {loc}')
    
    # Check if hidden file (Unix)
    if os.name == 'posix':
        filename = os.path.basename(filepath)
        if filename.startswith('.') and len(filename) > 1:
            suspicious['is_suspicious'] = True
            suspicious['reasons'].append('Hidden file')
    
    return suspicious


def parse_log_entry(log_line: str) -> Dict[str, str]:
    """
    Parse a log entry into components
    
    Args:
        log_line: Single line from log file
    
    Returns:
        Dict with parsed components
    """
    # Basic parsing - can be enhanced for specific log formats
    parts = log_line.split(None, 4)
    
    if len(parts) >= 5:
        return {
            'timestamp': f"{parts[0]} {parts[1]} {parts[2]}",
            'hostname': parts[3],
            'message': parts[4] if len(parts) > 4 else ''
        }
    else:
        return {
            'raw': log_line
        }


def detect_anomalies(values: List[float], threshold: float = 2.0) -> List[int]:
    """
    Detect anomalies using simple statistical method
    
    Args:
        values: List of numerical values
        threshold: Number of standard deviations for anomaly
    
    Returns:
        List of indices where anomalies detected
    """
    if len(values) < 3:
        return []
    
    import statistics
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    
    anomalies = []
    for i, value in enumerate(values):
        if abs(value - mean) > threshold * stdev:
            anomalies.append(i)
    
    return anomalies


def sanitize_output(data: str, max_length: int = 10000) -> str:
    """
    Sanitize command output for JSON storage
    
    Args:
        data: Output string
        max_length: Maximum length to keep
    
    Returns:
        Sanitized string
    """
    if not data:
        return ""
    
    # Remove null bytes
    data = data.replace('\x00', '')
    
    # Truncate if too long
    if len(data) > max_length:
        data = data[:max_length] + "\n... (truncated)"
    
    return data


def create_evidence_id(prefix: str = 'EVD') -> str:
    """
    Create unique evidence ID
    
    Args:
        prefix: Prefix for evidence ID
    
    Returns:
        Unique evidence ID
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}"


def validate_hash(hash_string: str, algorithm: str = 'sha256') -> bool:
    """
    Validate if string is a valid hash
    
    Args:
        hash_string: Hash string to validate
        algorithm: Hash algorithm
    
    Returns:
        True if valid hash format
    """
    expected_lengths = {
        'md5': 32,
        'sha1': 40,
        'sha256': 64,
        'sha512': 128
    }
    
    if algorithm not in expected_lengths:
        return False
    
    if len(hash_string) != expected_lengths[algorithm]:
        return False
    
    # Check if hexadecimal
    try:
        int(hash_string, 16)
        return True
    except ValueError:
        return False


def get_recent_files(directory: str, days: int = 7, 
                     max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Get files modified in the last N days
    
    Args:
        directory: Directory to search
        days: Number of days to look back
        max_results: Maximum results to return
    
    Returns:
        List of file info dicts
    """
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = cutoff_time.timestamp()
    
    recent_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    stat = os.stat(filepath)
                    if stat.st_mtime > cutoff_timestamp:
                        recent_files.append({
                            'path': filepath,
                            'modified': format_timestamp(stat.st_mtime),
                            'size': format_bytes(stat.st_size)
                        })
                        
                        if len(recent_files) >= max_results:
                            return recent_files
                except:
                    continue
    except Exception as e:
        print(f"Error getting recent files: {e}")
    
    return recent_files


def merge_json_files(json_files: List[str]) -> Dict[str, Any]:
    """
    Merge multiple JSON files into one dict
    
    Args:
        json_files: List of JSON file paths
    
    Returns:
        Merged dictionary
    """
    merged = {}
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                # Use filename (without extension) as key
                key = os.path.splitext(os.path.basename(json_file))[0]
                merged[key] = data
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            merged[key] = {'error': str(e)}
    
    return merged


def save_json_safe(data: Dict, filepath: str, indent: int = 4) -> bool:
    """
    Safely save JSON data to file
    
    Args:
        data: Data to save
        filepath: Output file path
        indent: JSON indentation
    
    Returns:
        True if successful
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write to temporary file first
        temp_file = filepath + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        
        # Rename to final file (atomic operation)
        os.replace(temp_file, filepath)
        
        return True
    except Exception as e:
        print(f"Error saving JSON to {filepath}: {e}")
        return False


def load_json_safe(filepath: str) -> Optional[Dict]:
    """
    Safely load JSON data from file
    
    Args:
        filepath: JSON file path
    
    Returns:
        Dict with data or None if error
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {filepath}: {e}")
        return None


# Export commonly used functions
__all__ = [
    'calculate_file_hash',
    'calculate_string_hash',
    'check_tool_available',
    'run_command',
    'get_system_info',
    'format_bytes',
    'format_timestamp',
    'get_file_metadata',
    'search_files',
    'is_suspicious_file',
    'parse_log_entry',
    'detect_anomalies',
    'sanitize_output',
    'create_evidence_id',
    'validate_hash',
    'get_recent_files',
    'merge_json_files',
    'save_json_safe',
    'load_json_safe'
]