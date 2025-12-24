import json
import os
from groq import Groq
from config import Config
from datetime import datetime

class ReportGenerator:
    """
    LLM-powered forensic report generator using 3 API keys for better token distribution
    """
    
    def __init__(self):
        # Initialize 3 Groq clients with different API keys
        self.client1 = Groq(api_key=Config.GROQ_API_KEY_1)
        self.client2 = Groq(api_key=Config.GROQ_API_KEY_2)
        self.client3 = Groq(api_key=Config.GROQ_API_KEY_3)
        
        self.model = Config.LLM_MODEL
        self.conversation_context = []
    
    def generate_comprehensive_report(self, evidence_data, blockchain_data):
        """
        Generate comprehensive forensic report using all 3 API keys
        
        Args:
            evidence_data (dict): Master evidence JSON data
            blockchain_data (dict): Blockchain registration data
        
        Returns:
            dict: Complete forensic report
        """
        print("[*] Generating comprehensive forensic report...")
        
        # Split the report generation into 3 parts across 3 API keys
        
        # Part 1: Executive Summary & Evidence Overview (API Key 1)
        print("[*] Generating Part 1: Executive Summary...")
        part1 = self._generate_executive_summary(evidence_data, blockchain_data)
        
        # Part 2: Detailed Findings & Analysis (API Key 2)
        print("[*] Generating Part 2: Detailed Findings...")
        part2 = self._generate_detailed_findings(evidence_data, part1)
        
        # Part 3: Legal Compliance & Recommendations (API Key 3)
        print("[*] Generating Part 3: Legal Compliance...")
        part3 = self._generate_legal_compliance(evidence_data, part1, part2)
        
        # Combine all parts
        complete_report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'session_id': evidence_data.get('session_id'),
                'investigator': Config.INVESTIGATOR_ID,
                'organization': Config.ORGANIZATION,
                'evidence_hash': evidence_data.get('evidence_hash'),
                'blockchain_tx': blockchain_data.get('transaction_hash')
            },
            'executive_summary': part1,
            'detailed_findings': part2,
            'legal_compliance': part3,
            'chain_of_custody': self._format_chain_of_custody(blockchain_data)
        }
        
        print("[+] Report generation completed!")
        
        return complete_report
    
    def _generate_executive_summary(self, evidence_data, blockchain_data):
        """Generate executive summary using API Key 1"""
        
        # Prepare concise evidence overview
        evidence_summary = {
            'session_id': evidence_data.get('session_id'),
            'timestamp': evidence_data.get('timestamp'),
            'os_source': evidence_data.get('os_source'),
            'forensic_types': list(evidence_data.get('forensics', {}).keys()),
            'evidence_hash': evidence_data.get('evidence_hash'),
            'blockchain_verified': blockchain_data.get('status') == 'success'
        }
        
        prompt = f"""You are a professional cyber forensic analyst. Generate an executive summary for a digital forensic investigation.

Evidence Overview:
{json.dumps(evidence_summary, indent=2)}

Generate a comprehensive executive summary including:
1. Incident Overview (2-3 sentences)
2. Investigation Scope
3. Key Findings Summary
4. Evidence Integrity Status
5. Critical Observations

Format the response as structured sections. Be professional and concise."""

        try:
            response = self.client1.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional cyber forensic analyst specializing in digital evidence analysis and legal reporting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content
            self.conversation_context.append({
                'role': 'part1',
                'content': summary
            })
            
            return summary
        
        except Exception as e:
            return f"Error generating executive summary: {str(e)}"
    
    def _generate_detailed_findings(self, evidence_data, previous_context):
        """Generate detailed findings using API Key 2"""
        
        forensics = evidence_data.get('forensics', {})
        
        # Prepare detailed forensic data for each type
        findings_summary = {}
        
        for forensic_type, data in forensics.items():
            if isinstance(data, dict) and 'findings' in data:
                findings_summary[forensic_type] = self._summarize_findings(
                    forensic_type, 
                    data['findings']
                )
        
        prompt = f"""You are continuing a forensic analysis report. Here's the context from the executive summary:

{previous_context}

Now, provide a detailed analysis of the forensic findings:

Forensic Data:
{json.dumps(findings_summary, indent=2)}

Generate detailed findings for each forensic category:
1. Disk Forensics Analysis
2. Memory Forensics Analysis
3. Network Forensics Analysis
4. Log Analysis

For each category:
- Summarize key discoveries
- Identify suspicious or anomalous activity
- Highlight security concerns
- Note important artifacts

Be specific but concise. Focus on actionable findings."""

        try:
            response = self.client2.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cyber forensic analyst providing detailed technical analysis of digital evidence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            findings = response.choices[0].message.content
            self.conversation_context.append({
                'role': 'part2',
                'content': findings
            })
            
            return findings
        
        except Exception as e:
            return f"Error generating detailed findings: {str(e)}"
    
    def _generate_legal_compliance(self, evidence_data, part1, part2):
        """Generate legal compliance section using API Key 3"""
        
        prompt = f"""You are completing a forensic investigation report. You have the context from previous sections:

EXECUTIVE SUMMARY:
{part1}

DETAILED FINDINGS:
{part2}

Now generate the legal compliance and recommendations section:

1. **Legal Compliance**:
   - IT Act 2000 (India) - Sections 43, 65B compliance
   - ISO/IEC 27037 compliance
   - Chain of custody verification
   - Evidence admissibility assessment

2. **Evidence Integrity**:
   - Hash verification status
   - Blockchain timestamp: {evidence_data.get('timestamp')}
   - Evidence hash: {evidence_data.get('evidence_hash', 'N/A')[:16]}...

3. **Recommendations**:
   - Immediate actions required
   - Long-term security improvements
   - Policy recommendations

4. **Conclusion**:
   - Summary of investigation
   - Evidence strength assessment
   - Next steps

Be authoritative and legally sound. Reference specific sections of laws where applicable."""

        try:
            response = self.client3.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a forensic analyst with expertise in cyber law and legal compliance, specializing in IT Act 2000 (India) and international standards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            compliance = response.choices[0].message.content
            
            return compliance
        
        except Exception as e:
            return f"Error generating legal compliance: {str(e)}"
    
    def _summarize_findings(self, forensic_type, findings_data):
        """Summarize findings data for LLM consumption"""
        
        summary = {
            'forensic_type': forensic_type,
            'data_points': {}
        }
        
        # Extract key information based on forensic type
        if forensic_type == 'disk':
            summary['data_points'] = {
                'filesystems': len(findings_data.get('filesystems', [])),
                'recent_files_count': len(findings_data.get('recent_files', [])),
                'suspicious_files': len(findings_data.get('suspicious_files', {}).get('files_found', []))
            }
        
        elif forensic_type == 'memory':
            summary['data_points'] = {
                'processes_count': len(findings_data.get('running_processes', [])),
                'connections_count': len(findings_data.get('network_connections', [])),
                'suspicious_processes': len(findings_data.get('suspicious_processes', []))
            }
        
        elif forensic_type == 'network':
            summary['data_points'] = {
                'interfaces_count': len(findings_data.get('network_interfaces', [])),
                'active_connections': len(findings_data.get('active_connections', [])),
                'listening_ports': len(findings_data.get('listening_ports', [])),
                'suspicious_connections': len(findings_data.get('suspicious_connections', []))
            }
        
        elif forensic_type == 'log':
            summary['data_points'] = {
                'os_type': findings_data.get('os_type', 'Unknown'),
                'auth_events': 'present' if findings_data.get('auth_events') else 'none',
                'failed_logins': len(findings_data.get('failed_logins', [])),
                'ssh_attempts': 'analyzed' if findings_data.get('ssh_attempts') else 'none'
            }
        
        return summary
    
    def _format_chain_of_custody(self, blockchain_data):
        """Format chain of custody section"""
        
        custody = {
            'blockchain_verified': blockchain_data.get('status') == 'success',
            'transaction_hash': blockchain_data.get('transaction_hash'),
            'block_number': blockchain_data.get('block_number'),
            'timestamp': blockchain_data.get('timestamp'),
            'investigator': Config.INVESTIGATOR_ID,
            'organization': Config.ORGANIZATION,
            'integrity_status': 'VERIFIED' if blockchain_data.get('status') == 'success' else 'PENDING'
        }
        
        return custody
    
    def save_report(self, report, output_dir):
        """Save report to files"""
        
        # Save JSON report
        json_path = os.path.join(output_dir, 'forensic_report.json')
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"[+] JSON report saved: {json_path}")
        
        # Save formatted text report
        text_path = os.path.join(output_dir, 'forensic_report.txt')
        with open(text_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DIGITAL FORENSIC INVESTIGATION REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Report Generated: {report['report_metadata']['generated_at']}\n")
            f.write(f"Session ID: {report['report_metadata']['session_id']}\n")
            f.write(f"Investigator: {report['report_metadata']['investigator']}\n")
            f.write(f"Organization: {report['report_metadata']['organization']}\n")
            f.write(f"Evidence Hash: {report['report_metadata']['evidence_hash']}\n")
            f.write(f"Blockchain TX: {report['report_metadata']['blockchain_tx']}\n")
            f.write("\n" + "="*80 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-"*80 + "\n")
            f.write(report['executive_summary'])
            f.write("\n\n")
            
            f.write("DETAILED FINDINGS\n")
            f.write("-"*80 + "\n")
            f.write(report['detailed_findings'])
            f.write("\n\n")
            
            f.write("LEGAL COMPLIANCE & RECOMMENDATIONS\n")
            f.write("-"*80 + "\n")
            f.write(report['legal_compliance'])
            f.write("\n\n")
            
            f.write("CHAIN OF CUSTODY\n")
            f.write("-"*80 + "\n")
            f.write(json.dumps(report['chain_of_custody'], indent=2))
            f.write("\n\n")
            
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"[+] Text report saved: {text_path}")
        
        return {
            'json_report': json_path,
            'text_report': text_path
        }