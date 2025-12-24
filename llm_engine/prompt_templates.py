"""
LLM Prompt Templates for Forensic Report Generation
These templates guide the AI to generate professional, legal-ready reports
"""

# System prompts for different parts of the report
SYSTEM_PROMPTS = {
    'executive_summary': """You are a professional cyber forensic analyst with expertise in digital evidence analysis and legal reporting. You specialize in creating executive summaries that are clear, concise, and suitable for both technical and non-technical audiences including law enforcement and legal professionals.""",
    
    'detailed_findings': """You are a cyber forensic analyst providing detailed technical analysis of digital evidence. Your analysis should be thorough, methodical, and focus on actionable findings. You understand various forensic tools and techniques and can interpret their outputs accurately.""",
    
    'legal_compliance': """You are a forensic analyst with expertise in cyber law and legal compliance, specializing in IT Act 2000 (India), ISO/IEC 27037, and international digital evidence standards. You understand the legal requirements for evidence admissibility in court."""
}


# Template for Executive Summary
EXECUTIVE_SUMMARY_TEMPLATE = """You are generating an executive summary for a digital forensic investigation which must be legally accepted.

**Evidence Overview:**
{evidence_summary}

**Your Task:**
Generate a comprehensive yet concise executive summary that includes:

1. **Incident Overview** (2-3 sentences)
   - What was examined
   - When the investigation occurred
   - Scope of the investigation

2. **Investigation Scope**
   - Types of forensic analysis performed
   - Operating system examined
   - Data sources analyzed

3. **Key Findings Summary**
   - Most critical discoveries (3-5 bullet points)
   - Security concerns identified
   - Evidence integrity status

4. **Evidence Integrity Status**
   - Hash verification
   - Blockchain registration status
   - Chain of custody maintenance

5. **Critical Observations**
   - Any immediate security concerns
   - Suspicious activities detected
   - Recommendations priority level

**Guidelines:**
- Write in clear, professional language
- Avoid excessive technical jargon
- Be objective and fact-based
- Suitable for executives and legal professionals
- 300-500 words

**Format:**
Use clear section headers and bullet points where appropriate."""


# Template for Detailed Findings
DETAILED_FINDINGS_TEMPLATE = """You are continuing a forensic analysis report with the following context:

**Previous Section (Executive Summary):**
{previous_context}

**Forensic Data Collected:**
{findings_data}

**Your Task:**
Provide a detailed analysis of the forensic findings for each category. For each forensic type, generate:

### 1. Disk Forensics Analysis
- **Data Examined:** Summarize what was analyzed (filesystems, files, partitions)
- **Key Discoveries:** Notable files, suspicious activities, deleted data
- **Security Concerns:** Any risks or anomalies identified
- **Important Artifacts:** Specific files or data of interest

### 2. Memory Forensics Analysis
- **Processes Analyzed:** Summary of running processes examined
- **Suspicious Activities:** Unusual processes or behaviors
- **Network Connections:** Active connections and their significance
- **Security Indicators:** Signs of compromise or malware

### 3. Network Forensics Analysis
- **Network Activity:** Summary of network connections and traffic
- **Suspicious Connections:** Unusual or unauthorized connections
- **Port Analysis:** Open ports and their services
- **Security Risks:** Potential vulnerabilities or intrusions

### 4. Log Analysis
- **Log Sources:** Types of logs examined
- **Security Events:** Failed logins, unauthorized access attempts
- **User Activity:** Notable user actions
- **Anomalies:** Unusual patterns or events

**Guidelines:**
- Be specific but concise
- Focus on actionable findings
- Identify patterns and correlations
- Highlight security implications
- Use technical terms accurately
- 600-900 words total

**Format:**
Use clear headings, subheadings, and bullet points for readability."""


# Template for Legal Compliance
LEGAL_COMPLIANCE_TEMPLATE = """You are completing a forensic investigation report with the following context:

**Executive Summary:**
{part1}

**Detailed Findings:**
{part2}

**Evidence Metadata:**
- Session ID: {session_id}
- Timestamp: {timestamp}
- Evidence Hash: {evidence_hash}
- Blockchain Transaction: {blockchain_tx}

**Your Task:**
Generate the final section covering legal compliance and recommendations:

## 1. Legal Compliance Assessment

### IT Act 2000 (India) Compliance
- **Section 43** (Penalty for damage to computer systems): Analyze if relevant
- **Section 65B** (Admissibility of electronic records): Compliance status
  - Electronic record requirements met: Yes/No
  - Certificate requirements: Details
  - Chain of custody: Verified

### ISO/IEC 27037 Compliance
- **Evidence Collection:** Procedures followed
- **Evidence Acquisition:** Methods used
- **Evidence Preservation:** Integrity maintained
- **Documentation:** Complete and accurate

### Chain of Custody Verification
- **Blockchain Registration:** Confirmed/Pending
- **Hash Verification:** Status
- **Timestamp Integrity:** Verified
- **Access Control:** Documented

## 2. Evidence Integrity Assessment
- **Hash Verification Status:** [Pass/Fail]
- **Blockchain Timestamp:** {timestamp}
- **Evidence Hash:** {evidence_hash}
- **Integrity Status:** [Intact/Compromised]

## 3. Evidence Admissibility Opinion
Provide professional opinion on:
- Likelihood of court admissibility
- Strengths of the evidence
- Any weaknesses or concerns
- Additional steps recommended

## 4. Recommendations

### Immediate Actions Required
(Priority 1 - Within 24 hours)
- List 2-3 immediate actions

### Short-term Improvements
(Priority 2 - Within 1 week)
- List 3-4 short-term actions

### Long-term Security Enhancements
(Priority 3 - Within 1 month)
- List 3-4 long-term improvements

### Policy Recommendations
- Security policy updates
- Training requirements
- Monitoring improvements

## 5. Conclusion
- Summary of investigation
- Evidence strength assessment
- Overall security posture
- Next steps recommended

**Guidelines:**
- Be authoritative and legally sound
- Reference specific laws and standards
- Provide clear, actionable recommendations
- Maintain professional tone
- 500-700 words

**Format:**
Use clear section headers and numbered/bulleted lists."""


# Template for simplified analysis (if data is limited)
SIMPLIFIED_ANALYSIS_TEMPLATE = """Based on the forensic data collected:

**System Analyzed:** {os_source}
**Analysis Types:** {forensic_types}
**Evidence Hash:** {evidence_hash}

Generate a brief forensic report covering:
1. What was examined
2. Key findings (3-5 points)
3. Security concerns identified
4. Basic recommendations

Keep it under 300 words, professional, and actionable."""


# Template for incident timeline generation
TIMELINE_TEMPLATE = """Based on the forensic evidence and log data:

{evidence_data}

Create a chronological incident timeline showing:
- Date/Time
- Event Type
- Description
- Significance

Include only notable security events, not routine system activities.
Maximum 15 events, most to least significant."""


# Template for threat assessment
THREAT_ASSESSMENT_TEMPLATE = """Analyze the forensic findings for potential threats:

**Findings:**
{findings_summary}

**Suspicious Indicators:**
{suspicious_items}

Provide:
1. **Threat Level:** (Low/Medium/High/Critical)
2. **Threat Type:** (External attack/Internal misuse/Malware/etc.)
3. **Indicators of Compromise:** List any IOCs found
4. **Potential Impact:** What could happen
5. **Mitigation Priority:** What to fix first

Be specific and actionable. 200-300 words."""


# Template for compliance mapping
COMPLIANCE_MAPPING_TEMPLATE = """Map the forensic investigation to compliance standards:

**Investigation Details:**
{investigation_summary}

**Standards to Check:**
1. IT Act 2000 (India) - Sections 43, 65B, 66, 67
2. ISO/IEC 27037:2012 - Digital Evidence Guidelines
3. NIST SP 800-86 - Integration of Forensic Techniques
4. RFC 3227 - Evidence Collection and Archiving

For each standard:
- **Requirement:** What the standard requires
- **Status:** Met/Partially Met/Not Met
- **Evidence:** How we comply
- **Gaps:** What's missing (if any)

Be specific about compliance status."""


# Helper function to format evidence summary for LLM
def format_evidence_summary(evidence_data):
    """Format evidence data into a concise summary for LLM consumption"""
    summary = {
        'session_id': evidence_data.get('session_id', 'Unknown'),
        'timestamp': evidence_data.get('timestamp', 'Unknown'),
        'os_source': evidence_data.get('os_source', 'Unknown'),
        'forensic_types': list(evidence_data.get('forensics', {}).keys()),
        'evidence_hash': evidence_data.get('evidence_hash', 'Not calculated'),
    }
    
    # Add counts from each forensic type
    forensics = evidence_data.get('forensics', {})
    
    if 'disk' in forensics:
        disk_data = forensics['disk'].get('findings', {})
        summary['disk'] = {
            'filesystems': len(disk_data.get('filesystems', [])),
            'recent_files': len(disk_data.get('recent_files', [])),
            'suspicious_files': len(disk_data.get('suspicious_files', {}).get('files_found', []))
        }
    
    if 'memory' in forensics:
        mem_data = forensics['memory'].get('findings', {})
        summary['memory'] = {
            'processes': len(mem_data.get('running_processes', [])),
            'connections': len(mem_data.get('network_connections', [])),
            'suspicious': len(mem_data.get('suspicious_processes', []))
        }
    
    if 'network' in forensics:
        net_data = forensics['network'].get('findings', {})
        summary['network'] = {
            'interfaces': len(net_data.get('network_interfaces', [])),
            'connections': len(net_data.get('active_connections', [])),
            'suspicious': len(net_data.get('suspicious_connections', []))
        }
    
    if 'log' in forensics:
        log_data = forensics['log'].get('findings', {})
        summary['log'] = {
            'failed_logins': len(log_data.get('failed_logins', [])),
            'sudo_commands': len(log_data.get('sudo_commands', [])),
        }
    
    return summary


# Export all templates
__all__ = [
    'SYSTEM_PROMPTS',
    'EXECUTIVE_SUMMARY_TEMPLATE',
    'DETAILED_FINDINGS_TEMPLATE',
    'LEGAL_COMPLIANCE_TEMPLATE',
    'SIMPLIFIED_ANALYSIS_TEMPLATE',
    'TIMELINE_TEMPLATE',
    'THREAT_ASSESSMENT_TEMPLATE',
    'COMPLIANCE_MAPPING_TEMPLATE',
    'format_evidence_summary'
]