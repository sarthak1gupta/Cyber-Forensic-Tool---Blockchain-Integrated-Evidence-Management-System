from web3 import Web3
from eth_account import Account
import json
import os
from config import Config

class BlockchainHandler:
    """
    Handles all blockchain interactions for evidence chain of custody
    """
    
    def __init__(self):
        # Connect to Sepolia testnet
        self.w3 = Web3(Web3.HTTPProvider(Config.BLOCKCHAIN_PROVIDER))
        
        # Check connection
        if not self.w3.is_connected():
            raise Exception("Failed to connect to blockchain network")
        
        print(f"[+] Connected to blockchain: {self.w3.is_connected()}")
        
        # Load contract ABI
        self.contract_address = Config.CONTRACT_ADDRESS
        self.contract_abi = self._load_contract_abi()
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.contract_abi
        )
        
        # Load investigator account
        self.account = Account.from_key(Config.PRIVATE_KEY)
        self.investigator_address = self.account.address
        
        print(f"[+] Investigator address: {self.investigator_address}")
        print(f"[+] Contract address: {self.contract_address}")
    
    def _load_contract_abi(self):
        """Load contract ABI from file"""
        abi_path = os.path.join('contracts', 'contract_abi.json')
        
        if not os.path.exists(abi_path):
            raise Exception(f"Contract ABI not found at {abi_path}")
        
        with open(abi_path, 'r') as f:
            abi = json.load(f)
        
        return abi
    
    def register_evidence(self, evidence_id, evidence_hash, os_source, 
                         forensic_type, tools_used):
        """
        Register new evidence on blockchain
        
        Args:
            evidence_id (str): Unique evidence identifier
            evidence_hash (str): SHA-256 hash of evidence
            os_source (str): Operating system source
            forensic_type (str): Type of forensic (disk/memory/network/log)
            tools_used (str): Comma-separated list of tools used
        
        Returns:
            dict: Transaction receipt and details
        """
        try:
            print(f"[*] Registering evidence on blockchain: {evidence_id}")
            
            # Prepare transaction
            nonce = self.w3.eth.get_transaction_count(self.investigator_address)
            
            # Build transaction
            transaction = self.contract.functions.registerEvidence(
                evidence_id,
                evidence_hash,
                os_source,
                Config.INVESTIGATOR_ID,
                "Collected",  # Initial action
                forensic_type,
                tools_used
            ).build_transaction({
                'from': self.investigator_address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"[*] Transaction sent: {tx_hash.hex()}")
            print("[*] Waiting for confirmation...")
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            result = {
                'status': 'success' if tx_receipt['status'] == 1 else 'failed',
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'gas_used': tx_receipt['gasUsed'],
                'evidence_id': evidence_id,
                'timestamp': self.w3.eth.get_block(tx_receipt['blockNumber'])['timestamp']
            }
            
            print(f"[+] Evidence registered successfully!")
            print(f"    Transaction: {result['transaction_hash']}")
            print(f"    Block: {result['block_number']}")
            
            return result
        
        except Exception as e:
            print(f"[!] Error registering evidence: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def add_custody_event(self, evidence_id, action, remarks):
        """
        Add custody event to evidence chain
        
        Args:
            evidence_id (str): Evidence identifier
            action (str): Action performed (Accessed/Analyzed/Transferred)
            remarks (str): Additional remarks
        
        Returns:
            dict: Transaction receipt and details
        """
        try:
            print(f"[*] Adding custody event for evidence: {evidence_id}")
            
            nonce = self.w3.eth.get_transaction_count(self.investigator_address)
            
            transaction = self.contract.functions.addCustodyEvent(
                evidence_id,
                Config.INVESTIGATOR_ID,
                action,
                remarks
            ).build_transaction({
                'from': self.investigator_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            result = {
                'status': 'success' if tx_receipt['status'] == 1 else 'failed',
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'gas_used': tx_receipt['gasUsed']
            }
            
            print(f"[+] Custody event added successfully!")
            
            return result
        
        except Exception as e:
            print(f"[!] Error adding custody event: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_evidence(self, evidence_id):
        """
        Retrieve evidence details from blockchain
        
        Args:
            evidence_id (str): Evidence identifier
        
        Returns:
            dict: Evidence details
        """
        try:
            evidence = self.contract.functions.getEvidence(evidence_id).call()
            
            return {
                'evidence_hash': evidence[0],
                'timestamp': evidence[1],
                'os_source': evidence[2],
                'investigator_id': evidence[3],
                'action': evidence[4],
                'forensic_type': evidence[5],
                'tools_used': evidence[6]
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_custody_chain(self, evidence_id):
        """
        Retrieve complete custody chain for evidence
        
        Args:
            evidence_id (str): Evidence identifier
        
        Returns:
            list: List of custody events
        """
        try:
            chain_length = self.contract.functions.getCustodyChainLength(evidence_id).call()
            
            custody_chain = []
            for i in range(chain_length):
                event = self.contract.functions.getCustodyEvent(evidence_id, i).call()
                custody_chain.append({
                    'timestamp': event[0],
                    'investigator_id': event[1],
                    'action': event[2],
                    'remarks': event[3]
                })
            
            return custody_chain
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def verify_evidence_hash(self, evidence_id, hash_to_verify):
        """
        Verify evidence hash matches blockchain record
        
        Args:
            evidence_id (str): Evidence identifier
            hash_to_verify (str): Hash to verify
        
        Returns:
            bool: True if hash matches
        """
        try:
            is_valid = self.contract.functions.verifyEvidenceHash(
                evidence_id, 
                hash_to_verify
            ).call()
            
            return is_valid
        
        except Exception as e:
            print(f"[!] Error verifying hash: {str(e)}")
            return False
    
    def get_account_balance(self):
        """Get investigator account balance"""
        try:
            balance_wei = self.w3.eth.get_balance(self.investigator_address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return {
                'address': self.investigator_address,
                'balance_wei': balance_wei,
                'balance_eth': float(balance_eth)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @staticmethod
    def generate_evidence_id(session_id):
        """Generate evidence ID from session ID"""
        return f"EVD_{session_id}"