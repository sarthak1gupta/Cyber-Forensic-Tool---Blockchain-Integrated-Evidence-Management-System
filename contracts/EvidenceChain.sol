// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EvidenceChain
 * @dev Smart contract for maintaining immutable chain of custody for digital evidence
 */
contract EvidenceChain {
    
    // Evidence structure
    struct Evidence {
        string evidenceId;
        string evidenceHash; // SHA-256 hash
        uint256 timestamp;
        string osSource;
        string investigatorId;
        string action; // Collected/Accessed/Analyzed
        string forensicType; // disk/memory/network/log
        string toolsUsed;
        bool exists;
    }
    
    // Chain of custody event
    struct CustodyEvent {
        uint256 timestamp;
        string investigatorId;
        string action;
        string remarks;
    }
    
    // Mappings
    mapping(string => Evidence) public evidences;
    mapping(string => CustodyEvent[]) public custodyChain;
    mapping(string => bool) public evidenceExists;
    
    // Events
    event EvidenceRegistered(
        string indexed evidenceId,
        string evidenceHash,
        uint256 timestamp,
        string investigatorId
    );
    
    event CustodyTransferred(
        string indexed evidenceId,
        string investigatorId,
        string action,
        uint256 timestamp
    );
    
    // Modifiers
    modifier evidenceExistsModifier(string memory _evidenceId) {
        require(evidenceExists[_evidenceId], "Evidence does not exist");
        _;
    }
    
    /**
     * @dev Register new evidence on blockchain
     */
    function registerEvidence(
        string memory _evidenceId,
        string memory _evidenceHash,
        string memory _osSource,
        string memory _investigatorId,
        string memory _action,
        string memory _forensicType,
        string memory _toolsUsed
    ) public {
        require(!evidenceExists[_evidenceId], "Evidence already registered");
        require(bytes(_evidenceId).length > 0, "Evidence ID cannot be empty");
        require(bytes(_evidenceHash).length == 64, "Invalid SHA-256 hash");
        
        Evidence memory newEvidence = Evidence({
            evidenceId: _evidenceId,
            evidenceHash: _evidenceHash,
            timestamp: block.timestamp,
            osSource: _osSource,
            investigatorId: _investigatorId,
            action: _action,
            forensicType: _forensicType,
            toolsUsed: _toolsUsed,
            exists: true
        });
        
        evidences[_evidenceId] = newEvidence;
        evidenceExists[_evidenceId] = true;
        
        // Initial custody event
        custodyChain[_evidenceId].push(CustodyEvent({
            timestamp: block.timestamp,
            investigatorId: _investigatorId,
            action: _action,
            remarks: "Evidence registered"
        }));
        
        emit EvidenceRegistered(_evidenceId, _evidenceHash, block.timestamp, _investigatorId);
    }
    
    /**
     * @dev Add custody event to evidence chain
     */
    function addCustodyEvent(
        string memory _evidenceId,
        string memory _investigatorId,
        string memory _action,
        string memory _remarks
    ) public evidenceExistsModifier(_evidenceId) {
        require(bytes(_investigatorId).length > 0, "Investigator ID cannot be empty");
        require(bytes(_action).length > 0, "Action cannot be empty");
        
        custodyChain[_evidenceId].push(CustodyEvent({
            timestamp: block.timestamp,
            investigatorId: _investigatorId,
            action: _action,
            remarks: _remarks
        }));
        
        emit CustodyTransferred(_evidenceId, _investigatorId, _action, block.timestamp);
    }
    
    /**
     * @dev Get evidence details
     */
    function getEvidence(string memory _evidenceId) 
        public 
        view 
        evidenceExistsModifier(_evidenceId)
        returns (
            string memory evidenceHash,
            uint256 timestamp,
            string memory osSource,
            string memory investigatorId,
            string memory action,
            string memory forensicType,
            string memory toolsUsed
        ) 
    {
        Evidence memory evidence = evidences[_evidenceId];
        return (
            evidence.evidenceHash,
            evidence.timestamp,
            evidence.osSource,
            evidence.investigatorId,
            evidence.action,
            evidence.forensicType,
            evidence.toolsUsed
        );
    }
    
    /**
     * @dev Get custody chain length
     */
    function getCustodyChainLength(string memory _evidenceId) 
        public 
        view 
        evidenceExistsModifier(_evidenceId)
        returns (uint256) 
    {
        return custodyChain[_evidenceId].length;
    }
    
    /**
     * @dev Get specific custody event
     */
    function getCustodyEvent(string memory _evidenceId, uint256 _index)
        public
        view
        evidenceExistsModifier(_evidenceId)
        returns (
            uint256 timestamp,
            string memory investigatorId,
            string memory action,
            string memory remarks
        )
    {
        require(_index < custodyChain[_evidenceId].length, "Index out of bounds");
        CustodyEvent memory custodyEvent = custodyChain[_evidenceId][_index];
        return (
            custodyEvent.timestamp,
            custodyEvent.investigatorId,
            custodyEvent.action,
            custodyEvent.remarks
        );
    }
    
    /**
     * @dev Verify evidence hash matches
     */
    function verifyEvidenceHash(string memory _evidenceId, string memory _hash)
        public
        view
        evidenceExistsModifier(_evidenceId)
        returns (bool)
    {
        return keccak256(abi.encodePacked(evidences[_evidenceId].evidenceHash)) == 
               keccak256(abi.encodePacked(_hash));
    }
}