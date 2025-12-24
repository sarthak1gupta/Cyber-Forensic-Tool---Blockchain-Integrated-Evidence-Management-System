"""
Evidence Logger Module
Handles logging of evidence actions and chain of custody events to blockchain
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
import os


class EvidenceLogger:
    """
    Manages evidence logging and chain of custody tracking
    """
    
    def __init__(self, blockchain_handler=None, log_file: str = None):
        """
        Initialize evidence logger
        
        Args:
            blockchain_handler: Instance of BlockchainHandler
            log_file: Path to local log file for backup
        """
        self.blockchain_handler = blockchain_handler
        self.log_file = log_file or 'evidence_custody_log.json'
        self.custody_events = []
        
        # Load existing logs if available
        self._load_logs()
    
    def _load_logs(self):
        """Load existing custody logs from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.custody_events = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing logs: {e}")
                self.custody_events = []
    
    def _save_logs(self):
        """Save custody logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.custody_events, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save logs: {e}")
    
    def log_evidence_collection(self, evidence_id: str, evidence_hash: str,
                                os_source: str, forensic_type: str,
                                tools_used: List[str], 
                                investigator_id: str) -> Dict:
        """
        Log initial evidence collection
        
        Args:
            evidence_id: Unique evidence identifier
            evidence_hash: SHA-256 hash of evidence
            os_source: Operating system source
            forensic_type: Type of forensic analysis
            tools_used: List of tools used
            investigator_id: Investigator ID
        
        Returns:
            Dict with logging result
        """
        event = {
            'event_type': 'COLLECTION',
            'evidence_id': evidence_id,
            'evidence_hash': evidence_hash,
            'timestamp': datetime.now().isoformat(),
            'os_source': os_source,
            'forensic_type': forensic_type,
            'tools_used': tools_used,
            'investigator_id': investigator_id,
            'action': 'Evidence Collected',
            'blockchain_registered': False
        }
        
        # Add to local log
        self.custody_events.append(event)
        self._save_logs()
        
        print(f"[+] Evidence collection logged: {evidence_id}")
        
        return event
    
    def log_blockchain_registration(self, evidence_id: str, 
                                    transaction_hash: str,
                                    block_number: int) -> Dict:
        """
        Log blockchain registration event
        
        Args:
            evidence_id: Evidence identifier
            transaction_hash: Blockchain transaction hash
            block_number: Block number
        
        Returns:
            Dict with logging result
        """
        event = {
            'event_type': 'BLOCKCHAIN_REGISTRATION',
            'evidence_id': evidence_id,
            'timestamp': datetime.now().isoformat(),
            'transaction_hash': transaction_hash,
            'block_number': block_number,
            'action': 'Registered on Blockchain',
            'blockchain_registered': True
        }
        
        # Add to local log
        self.custody_events.append(event)
        self._save_logs()
        
        # Update blockchain registration status in previous events
        for e in self.custody_events:
            if e.get('evidence_id') == evidence_id:
                e['blockchain_registered'] = True
        
        self._save_logs()
        
        print(f"[+] Blockchain registration logged: {transaction_hash}")
        
        return event
    
    def log_evidence_access(self, evidence_id: str, investigator_id: str,
                           action: str, remarks: str = "") -> Dict:
        """
        Log evidence access event
        
        Args:
            evidence_id: Evidence identifier
            investigator_id: Investigator accessing evidence
            action: Action performed (Accessed/Analyzed/Modified)
            remarks: Additional remarks
        
        Returns:
            Dict with logging result
        """
        event = {
            'event_type': 'ACCESS',
            'evidence_id': evidence_id,
            'timestamp': datetime.now().isoformat(),
            'investigator_id': investigator_id,
            'action': action,
            'remarks': remarks
        }
        
        # Add to local log
        self.custody_events.append(event)
        self._save_logs()
        
        # Log to blockchain if handler available
        if self.blockchain_handler:
            try:
                result = self.blockchain_handler.add_custody_event(
                    evidence_id, investigator_id, action, remarks
                )
                event['blockchain_tx'] = result.get('transaction_hash')
                event['blockchain_logged'] = True
            except Exception as e:
                print(f"[!] Could not log to blockchain: {e}")
                event['blockchain_logged'] = False
        
        print(f"[+] Evidence access logged: {action}")
        
        return event
    
    def log_report_generation(self, evidence_id: str, investigator_id: str,
                             report_path: str) -> Dict:
        """
        Log report generation event
        
        Args:
            evidence_id: Evidence identifier
            investigator_id: Investigator ID
            report_path: Path to generated report
        
        Returns:
            Dict with logging result
        """
        event = {
            'event_type': 'REPORT_GENERATION',
            'evidence_id': evidence_id,
            'timestamp': datetime.now().isoformat(),
            'investigator_id': investigator_id,
            'action': 'Report Generated',
            'report_path': report_path
        }
        
        # Add to local log
        self.custody_events.append(event)
        self._save_logs()
        
        # Log to blockchain if handler available
        if self.blockchain_handler:
            try:
                result = self.blockchain_handler.add_custody_event(
                    evidence_id, investigator_id, 
                    'Report Generated', f'Report: {report_path}'
                )
                event['blockchain_tx'] = result.get('transaction_hash')
            except Exception as e:
                print(f"[!] Could not log to blockchain: {e}")
        
        print(f"[+] Report generation logged")
        
        return event
    
    def log_evidence_transfer(self, evidence_id: str, from_investigator: str,
                             to_investigator: str, remarks: str = "") -> Dict:
        """
        Log evidence custody transfer
        
        Args:
            evidence_id: Evidence identifier
            from_investigator: Current custodian
            to_investigator: New custodian
            remarks: Transfer remarks
        
        Returns:
            Dict with logging result
        """
        event = {
            'event_type': 'CUSTODY_TRANSFER',
            'evidence_id': evidence_id,
            'timestamp': datetime.now().isoformat(),
            'from_investigator': from_investigator,
            'to_investigator': to_investigator,
            'action': 'Custody Transferred',
            'remarks': remarks
        }
        
        # Add to local log
        self.custody_events.append(event)
        self._save_logs()
        
        # Log to blockchain if handler available
        if self.blockchain_handler:
            try:
                result = self.blockchain_handler.add_custody_event(
                    evidence_id, to_investigator,
                    'Custody Transfer',
                    f'From: {from_investigator}, To: {to_investigator}. {remarks}'
                )
                event['blockchain_tx'] = result.get('transaction_hash')
            except Exception as e:
                print(f"[!] Could not log to blockchain: {e}")
        
        print(f"[+] Custody transfer logged: {from_investigator} → {to_investigator}")
        
        return event
    
    def get_custody_chain(self, evidence_id: str) -> List[Dict]:
        """
        Get complete custody chain for evidence
        
        Args:
            evidence_id: Evidence identifier
        
        Returns:
            List of custody events
        """
        # Get from local log
        local_events = [
            event for event in self.custody_events
            if event.get('evidence_id') == evidence_id
        ]
        
        # Get from blockchain if handler available
        blockchain_events = []
        if self.blockchain_handler:
            try:
                blockchain_events = self.blockchain_handler.get_custody_chain(evidence_id)
            except Exception as e:
                print(f"[!] Could not retrieve blockchain custody chain: {e}")
        
        return {
            'local_events': local_events,
            'blockchain_events': blockchain_events,
            'total_events': len(local_events)
        }
    
    def verify_evidence_integrity(self, evidence_id: str, 
                                  current_hash: str) -> Dict:
        """
        Verify evidence integrity by comparing hashes
        
        Args:
            evidence_id: Evidence identifier
            current_hash: Current hash to verify
        
        Returns:
            Dict with verification result
        """
        # Get original hash from logs
        original_hash = None
        for event in self.custody_events:
            if (event.get('evidence_id') == evidence_id and 
                event.get('event_type') == 'COLLECTION'):
                original_hash = event.get('evidence_hash')
                break
        
        if not original_hash:
            return {
                'verified': False,
                'reason': 'Original hash not found in logs'
            }
        
        # Compare hashes
        hashes_match = (original_hash == current_hash)
        
        # Verify with blockchain if handler available
        blockchain_verified = False
        if self.blockchain_handler and hashes_match:
            try:
                blockchain_verified = self.blockchain_handler.verify_evidence_hash(
                    evidence_id, current_hash
                )
            except Exception as e:
                print(f"[!] Blockchain verification failed: {e}")
        
        result = {
            'verified': hashes_match,
            'original_hash': original_hash,
            'current_hash': current_hash,
            'blockchain_verified': blockchain_verified,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log verification event
        self.custody_events.append({
            'event_type': 'VERIFICATION',
            'evidence_id': evidence_id,
            'timestamp': result['timestamp'],
            'result': 'PASS' if hashes_match else 'FAIL',
            'action': 'Integrity Verification'
        })
        self._save_logs()
        
        return result
    
    def generate_custody_report(self, evidence_id: str) -> Dict:
        """
        Generate chain of custody report
        
        Args:
            evidence_id: Evidence identifier
        
        Returns:
            Dict with custody report
        """
        custody_chain = self.get_custody_chain(evidence_id)
        
        report = {
            'evidence_id': evidence_id,
            'report_generated': datetime.now().isoformat(),
            'total_events': len(custody_chain['local_events']),
            'blockchain_events': len(custody_chain.get('blockchain_events', [])),
            'custody_timeline': []
        }
        
        # Sort events by timestamp
        events = sorted(
            custody_chain['local_events'],
            key=lambda x: x.get('timestamp', '')
        )
        
        for event in events:
            report['custody_timeline'].append({
                'timestamp': event.get('timestamp'),
                'event_type': event.get('event_type'),
                'action': event.get('action'),
                'investigator': event.get('investigator_id', 'System'),
                'blockchain_logged': event.get('blockchain_logged', False)
            })
        
        return report
    
    def export_custody_log(self, output_file: str) -> bool:
        """
        Export custody log to file
        
        Args:
            output_file: Output file path
        
        Returns:
            True if successful
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(self.custody_events, f, indent=4)
            print(f"[+] Custody log exported to: {output_file}")
            return True
        except Exception as e:
            print(f"[!] Error exporting custody log: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about logged events
        
        Returns:
            Dict with statistics
        """
        stats = {
            'total_events': len(self.custody_events),
            'evidence_items': len(set(
                e.get('evidence_id') for e in self.custody_events
                if e.get('evidence_id')
            )),
            'event_types': {},
            'blockchain_logged': 0,
            'investigators': set()
        }
        
        for event in self.custody_events:
            # Count event types
            event_type = event.get('event_type', 'UNKNOWN')
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
            
            # Count blockchain logged
            if event.get('blockchain_logged') or event.get('blockchain_registered'):
                stats['blockchain_logged'] += 1
            
            # Track investigators
            inv_id = event.get('investigator_id')
            if inv_id:
                stats['investigators'].add(inv_id)
        
        stats['investigators'] = list(stats['investigators'])
        
        return stats


# Export
__all__ = ['EvidenceLogger']