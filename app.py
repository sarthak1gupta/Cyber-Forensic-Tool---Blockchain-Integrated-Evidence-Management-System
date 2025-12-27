from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime

from config import Config
from forensic_engine.orchestrator import ForensicOrchestrator
from blockchain.blockchain_handler import BlockchainHandler
from llm_engine.report_generator import ReportGenerator

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Global variables
current_session = None
blockchain_handler = None

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', 
                         investigator=Config.INVESTIGATOR_ID,
                         organization=Config.ORGANIZATION)

@app.route('/api/check-tools', methods=['GET'])
def check_tools():
    """Check available forensic tools"""
    try:
        available_tools = ForensicOrchestrator.list_available_tools()
        return jsonify({
            'status': 'success',
            'tools': available_tools,
            'system_info': Config.get_system_info()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/system-info', methods=['GET'])
def system_info():
    """Get system information"""
    try:
        return jsonify({
            'status': 'success',
            'system': Config.get_system_info(),
            'core_tools': Config.CORE_TOOLS,
            'optional_tools': Config.OPTIONAL_TOOLS
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/validate-config', methods=['GET'])
def validate_config():
    """Validate configuration"""
    try:
        errors = Config.validate_config()
        
        if errors:
            return jsonify({
                'status': 'warning',
                'errors': errors,
                'message': 'Some configuration values are missing'
            })
        
        return jsonify({
            'status': 'success',
            'message': 'Configuration is valid'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/start-forensics', methods=['POST'])
def start_forensics():
    """Start forensic investigation"""
    global current_session
    
    try:
        data = request.json
        forensic_types = data.get('forensic_types', ['all'])
        use_advanced_tools = data.get('use_advanced_tools', False)
        
        # Create session directory
        session_dir, session_id = Config.create_session_directory()
        
        print(f"\n{'='*60}")
        print(f"FORENSIC INVESTIGATION STARTED")
        print(f"Session ID: {session_id}")
        print(f"Session Directory: {session_dir}")
        print(f"Forensic Types: {', '.join(forensic_types)}")
        print(f"Advanced Tools: {'ENABLED' if use_advanced_tools else 'DISABLED'}")
        print(f"{'='*60}\n")
        
        # Initialize orchestrator
        orchestrator = ForensicOrchestrator(session_dir, session_id, use_advanced_tools)
        
        # Execute forensics
        evidence_data = orchestrator.execute_forensics(forensic_types)
        
        # Save master JSON
        orchestrator.save_master_json()
        
        # Calculate evidence hash
        evidence_hash = orchestrator.calculate_evidence_hash()
        
        print(f"\n[+] Evidence hash calculated: {evidence_hash}")
        
        current_session = {
            'session_id': session_id,
            'session_dir': session_dir,
            'evidence_data': evidence_data,
            'evidence_hash': evidence_hash,
            'timestamp': datetime.now().isoformat(),
            'use_advanced_tools': use_advanced_tools
        }
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'session_dir': session_dir,
            'evidence_hash': evidence_hash,
            'forensics_completed': list(evidence_data['forensics'].keys()),
            'advanced_tools_used': use_advanced_tools,
            'tools_summary': evidence_data.get('tools_summary', {})
        })
    
    except Exception as e:
        print(f"\n[!] Error in forensic execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/register-blockchain', methods=['POST'])
def register_blockchain():
    """Register evidence on blockchain"""
    global blockchain_handler, current_session
    
    try:
        if not current_session:
            return jsonify({
                'status': 'error',
                'error': 'No active session. Run forensics first.'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"BLOCKCHAIN REGISTRATION")
        print(f"{'='*60}\n")
        
        # Initialize blockchain handler
        if not blockchain_handler:
            blockchain_handler = BlockchainHandler()
        
        # Get evidence summary
        session_dir = current_session['session_dir']
        session_id = current_session['session_id']
        orchestrator = ForensicOrchestrator(session_dir, session_id)
        orchestrator.evidence_data = current_session['evidence_data']
        
        summary = orchestrator.get_evidence_summary()
        
        # Generate evidence ID
        evidence_id = BlockchainHandler.generate_evidence_id(session_id)
        
        # Register on blockchain
        blockchain_result = blockchain_handler.register_evidence(
            evidence_id=evidence_id,
            evidence_hash=summary['evidence_hash'],
            os_source=summary['os_source'],
            forensic_type=','.join(summary['forensic_types']),
            tools_used=','.join(summary['tools_used'][:5])  # Limit to 5 tools
        )
        
        if blockchain_result['status'] == 'success':
            print(f"\n[+] Evidence successfully registered on blockchain!")
            print(f"    Evidence ID: {evidence_id}")
            print(f"    Transaction: {blockchain_result['transaction_hash']}")
            print(f"    Block: {blockchain_result['block_number']}")
            
            current_session['blockchain_data'] = blockchain_result
            
            return jsonify({
                'status': 'success',
                'evidence_id': evidence_id,
                'blockchain_data': blockchain_result
            })
        else:
            return jsonify({
                'status': 'error',
                'error': blockchain_result.get('error', 'Unknown error')
            }), 500
    
    except Exception as e:
        print(f"\n[!] Blockchain registration error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate forensic report using LLM"""
    global current_session
    
    try:
        if not current_session:
            return jsonify({
                'status': 'error',
                'error': 'No active session. Run forensics first.'
            }), 400
        
        if 'blockchain_data' not in current_session:
            return jsonify({
                'status': 'error',
                'error': 'Blockchain registration required before report generation.'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"REPORT GENERATION")
        print(f"{'='*60}\n")
        
        # Initialize report generator
        report_gen = ReportGenerator()
        
        # Generate comprehensive report
        report = report_gen.generate_comprehensive_report(
            evidence_data=current_session['evidence_data'],
            blockchain_data=current_session['blockchain_data']
        )
        
        # Save report
        report_paths = report_gen.save_report(
            report, 
            current_session['session_dir']
        )
        
        print(f"\n[+] Report generation completed!")
        print(f"    JSON Report: {report_paths['json_report']}")
        print(f"    Text Report: {report_paths['text_report']}")
        
        current_session['report'] = report
        current_session['report_paths'] = report_paths
        
        return jsonify({
            'status': 'success',
            'report': report,
            'report_paths': report_paths
        })
    
    except Exception as e:
        print(f"\n[!] Report generation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/session-status', methods=['GET'])
def session_status():
    """Get current session status"""
    if not current_session:
        return jsonify({
            'status': 'no_session',
            'message': 'No active session'
        })
    
    return jsonify({
        'status': 'active',
        'session_id': current_session.get('session_id'),
        'timestamp': current_session.get('timestamp'),
        'evidence_hash': current_session.get('evidence_hash'),
        'blockchain_registered': 'blockchain_data' in current_session,
        'report_generated': 'report' in current_session
    })

@app.route('/api/download-report/<report_type>', methods=['GET'])
def download_report(report_type):
    """Download generated report"""
    try:
        if not current_session or 'report_paths' not in current_session:
            return jsonify({
                'status': 'error',
                'error': 'No report available'
            }), 404
        
        report_paths = current_session['report_paths']
        
        if report_type == 'json':
            filepath = report_paths['json_report']
            mimetype = 'application/json'
        elif report_type == 'text':
            filepath = report_paths['text_report']
            mimetype = 'text/plain'
        else:
            return jsonify({
                'status': 'error',
                'error': 'Invalid report type'
            }), 400
        
        return send_file(
            filepath,
            mimetype=mimetype,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/blockchain-balance', methods=['GET'])
def blockchain_balance():
    """Get blockchain account balance"""
    global blockchain_handler
    
    try:
        if not blockchain_handler:
            blockchain_handler = BlockchainHandler()
        
        balance = blockchain_handler.get_account_balance()
        return jsonify({
            'status': 'success',
            'balance': balance
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/verify-evidence', methods=['POST'])
def verify_evidence():
    """Verify evidence hash against blockchain"""
    global blockchain_handler
    
    try:
        data = request.json
        evidence_id = data.get('evidence_id')
        hash_to_verify = data.get('hash')
        
        if not blockchain_handler:
            blockchain_handler = BlockchainHandler()
        
        is_valid = blockchain_handler.verify_evidence_hash(evidence_id, hash_to_verify)
        
        return jsonify({
            'status': 'success',
            'is_valid': is_valid,
            'message': 'Hash verified successfully' if is_valid else 'Hash mismatch'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create base evidence directory
    os.makedirs(Config.BASE_EVIDENCE_DIR, exist_ok=True)
    
    # Validate configuration
    errors = Config.validate_config()
    if errors:
        print("\n" + "="*60)
        print("CONFIGURATION WARNINGS:")
        for error in errors:
            print(f"  ⚠️  {error}")
        print("="*60 + "\n")
        print("Some features may not work without proper configuration.")
        print("Please check your .env file.\n")
    
    print("\n" + "="*60)
    print("CYBER FORENSIC TOOL")
    print("="*60)
    print(f"Investigator: {Config.INVESTIGATOR_ID}")
    print(f"Organization: {Config.ORGANIZATION}")
    print(f"Evidence Directory: {Config.BASE_EVIDENCE_DIR}")
    print("="*60 + "\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )