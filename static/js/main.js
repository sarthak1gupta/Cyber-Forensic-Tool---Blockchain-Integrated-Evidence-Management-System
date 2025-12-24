// Global state
let currentSession = null;

// API Base URL
const API_BASE = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkSessionStatus();
});

// Toggle All Forensics checkbox
function toggleAllForensics(checkbox) {
    const forensicCheckboxes = document.querySelectorAll('.forensic-type');
    forensicCheckboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        cb.disabled = checkbox.checked;
    });
}

// Check Configuration
async function checkConfiguration() {
    const resultDiv = document.getElementById('configResult');
    resultDiv.className = 'result-box info';
    resultDiv.innerHTML = '<p>Checking configuration...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/validate-config`);
        const data = await response.json();
        
        if (data.status === 'success') {
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = `
                <h3>✅ Configuration Valid</h3>
                <p>${data.message}</p>
            `;
        } else if (data.status === 'warning') {
            resultDiv.className = 'result-box warning';
            resultDiv.innerHTML = `
                <h3>⚠️ Configuration Warnings</h3>
                <p>Some configuration values are missing:</p>
                <ul>
                    ${data.errors.map(err => `<li>${err}</li>`).join('')}
                </ul>
                <p><strong>Note:</strong> Some features may not work properly.</p>
            `;
        }
    } catch (error) {
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    }
}

// Check Available Tools
async function checkTools() {
    const resultDiv = document.getElementById('configResult');
    resultDiv.className = 'result-box info';
    resultDiv.innerHTML = '<p>Checking available tools...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/check-tools`);
        const data = await response.json();
        
        if (data.status === 'success') {
            let html = '<h3>🔧 Available Forensic Tools</h3>';
            
            for (const [category, tools] of Object.entries(data.tools)) {
                html += `<h4>${category.toUpperCase()}</h4>`;
                if (tools.length > 0) {
                    html += `<ul>${tools.map(tool => `<li>✅ ${tool}</li>`).join('')}</ul>`;
                } else {
                    html += '<p>⚠️ No tools available for this category</p>';
                }
            }
            
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = html;
        }
    } catch (error) {
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    }
}

// Start Forensics
async function startForensics() {
    // Get selected forensic types
    const allCheckbox = document.getElementById('forensic_all');
    const forensicCheckboxes = document.querySelectorAll('.forensic-type:checked');
    
    let forensicTypes = [];
    if (allCheckbox.checked) {
        forensicTypes = ['all'];
    } else {
        forensicTypes = Array.from(forensicCheckboxes).map(cb => cb.value);
    }
    
    if (forensicTypes.length === 0) {
        alert('Please select at least one forensic type');
        return;
    }
    
    // Disable button and show progress
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="loading"></span> Running...';
    
    const progressDiv = document.getElementById('forensicProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const resultDiv = document.getElementById('forensicResult');
    
    progressDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    
    // Animate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
        progressFill.style.width = progress + '%';
    }, 500);
    
    progressText.textContent = 'Executing forensic analysis...';
    
    try {
        const response = await fetch(`${API_BASE}/api/start-forensics`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ forensic_types: forensicTypes })
        });
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Forensics completed!';
        
        if (data.status === 'success') {
            currentSession = data;
            
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = `
                <h3>✅ Forensic Investigation Completed</h3>
                <p><strong>Session ID:</strong> ${data.session_id}</p>
                <p><strong>Evidence Hash:</strong> <code>${data.evidence_hash}</code></p>
                <p><strong>Forensics Completed:</strong></p>
                <ul>
                    ${data.forensics_completed.map(f => `<li>✅ ${f.toUpperCase()}</li>`).join('')}
                </ul>
                <p class="mt-20"><strong>Next Steps:</strong></p>
                <ul>
                    <li>Register evidence on blockchain</li>
                    <li>Generate forensic report</li>
                </ul>
            `;
            
            // Enable blockchain button
            document.getElementById('blockchainBtn').disabled = false;
            
            // Update session status
            updateSessionStatus(data);
            
        } else {
            resultDiv.className = 'result-box error';
            resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
        }
    } catch (error) {
        clearInterval(progressInterval);
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    } finally {
        startBtn.disabled = false;
        startBtn.innerHTML = '🚀 Start Investigation';
        setTimeout(() => {
            progressDiv.style.display = 'none';
        }, 2000);
    }
}

// Check Blockchain Balance
async function checkBalance() {
    const resultDiv = document.getElementById('blockchainResult');
    resultDiv.className = 'result-box info';
    resultDiv.innerHTML = '<p>Checking wallet balance...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/blockchain-balance`);
        const data = await response.json();
        
        if (data.status === 'success') {
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = `
                <h3>💰 Wallet Balance</h3>
                <p><strong>Address:</strong> <code>${data.balance.address}</code></p>
                <p><strong>Balance:</strong> ${data.balance.balance_eth.toFixed(6)} ETH</p>
                <p class="small">${data.balance.balance_wei} wei</p>
            `;
        } else {
            resultDiv.className = 'result-box error';
            resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
        }
    } catch (error) {
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    }
}

// Register on Blockchain
async function registerBlockchain() {
    if (!currentSession) {
        alert('Please run forensics first');
        return;
    }
    
    const btn = document.getElementById('blockchainBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Registering...';
    
    const resultDiv = document.getElementById('blockchainResult');
    resultDiv.className = 'result-box info';
    resultDiv.innerHTML = '<p>Registering evidence on blockchain... This may take 10-30 seconds.</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/register-blockchain`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = `
                <h3>✅ Blockchain Registration Successful</h3>
                <p><strong>Evidence ID:</strong> <code>${data.evidence_id}</code></p>
                <p><strong>Transaction Hash:</strong> <code>${data.blockchain_data.transaction_hash}</code></p>
                <p><strong>Block Number:</strong> ${data.blockchain_data.block_number}</p>
                <p><strong>Gas Used:</strong> ${data.blockchain_data.gas_used}</p>
                <p class="mt-20">
                    <a href="https://sepolia.etherscan.io/tx/${data.blockchain_data.transaction_hash}" 
                       target="_blank" class="btn btn-secondary">
                        🔍 View on Etherscan
                    </a>
                </p>
            `;
            
            // Enable report button
            document.getElementById('reportBtn').disabled = false;
            
        } else {
            resultDiv.className = 'result-box error';
            resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
        }
    } catch (error) {
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📝 Register on Blockchain';
    }
}

// Generate Report
async function generateReport() {
    const btn = document.getElementById('reportBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Generating...';
    
    const progressDiv = document.getElementById('reportProgress');
    const progressFill = document.getElementById('reportProgressFill');
    const progressText = document.getElementById('reportProgressText');
    const resultDiv = document.getElementById('reportResult');
    
    progressDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    
    // Animate progress (report generation takes time)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 3;
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
        progressFill.style.width = progress + '%';
        
        if (progress < 30) {
            progressText.textContent = 'Generating executive summary...';
        } else if (progress < 60) {
            progressText.textContent = 'Analyzing detailed findings...';
        } else {
            progressText.textContent = 'Preparing legal compliance report...';
        }
    }, 1000);
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-report`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Report generated!';
        
        if (data.status === 'success') {
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = `
                <h3>✅ Report Generated Successfully</h3>
                <p>Comprehensive forensic report has been generated with AI analysis.</p>
                <div class="mt-20">
                    <h4>Report Contents:</h4>
                    <ul>
                        <li>✅ Executive Summary</li>
                        <li>✅ Detailed Forensic Findings</li>
                        <li>✅ Legal Compliance Assessment</li>
                        <li>✅ Chain of Custody Verification</li>
                        <li>✅ Recommendations</li>
                    </ul>
                </div>
            `;
            
            // Show download buttons
            document.getElementById('downloadSection').style.display = 'block';
            
        } else {
            resultDiv.className = 'result-box error';
            resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
        }
    } catch (error) {
        clearInterval(progressInterval);
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📊 Generate Report';
        setTimeout(() => {
            progressDiv.style.display = 'none';
        }, 2000);
    }
}

// Download Report
function downloadReport(type) {
    window.location.href = `${API_BASE}/api/download-report/${type}`;
}

// Verify Evidence
async function verifyEvidence() {
    const evidenceId = document.getElementById('evidenceId').value.trim();
    const evidenceHash = document.getElementById('evidenceHash').value.trim();
    const resultDiv = document.getElementById('verifyResult');
    
    if (!evidenceId || !evidenceHash) {
        resultDiv.className = 'result-box warning';
        resultDiv.innerHTML = '<p>⚠️ Please enter both Evidence ID and Hash</p>';
        return;
    }
    
    resultDiv.className = 'result-box info';
    resultDiv.innerHTML = '<p>Verifying evidence...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/verify-evidence`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                evidence_id: evidenceId,
                hash: evidenceHash
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (data.is_valid) {
                resultDiv.className = 'result-box success';
                resultDiv.innerHTML = `
                    <h3>✅ Evidence Verified</h3>
                    <p>${data.message}</p>
                    <p>The evidence hash matches the blockchain record.</p>
                `;
            } else {
                resultDiv.className = 'result-box error';
                resultDiv.innerHTML = `
                    <h3>❌ Verification Failed</h3>
                    <p>${data.message}</p>
                    <p>The evidence hash does NOT match the blockchain record.</p>
                `;
            }
        } else {
            resultDiv.className = 'result-box error';
            resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
        }
    } catch (error) {
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    }
}

// Check Session Status
async function checkSessionStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/session-status`);
        const data = await response.json();
        
        if (data.status === 'active') {
            updateSessionStatus(data);
            
            // Enable appropriate buttons
            if (data.blockchain_registered) {
                document.getElementById('blockchainBtn').disabled = false;
                document.getElementById('reportBtn').disabled = false;
            }
            
            if (data.report_generated) {
                document.getElementById('downloadSection').style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Session check error:', error);
    }
}

// Update Session Status Display
function updateSessionStatus(data) {
    const statusDiv = document.getElementById('sessionStatus');
    
    statusDiv.innerHTML = `
        <p><strong>Session ID:</strong> ${data.session_id}</p>
        <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
        <p><strong>Evidence Hash:</strong> <code>${data.evidence_hash ? data.evidence_hash.substring(0, 32) + '...' : 'N/A'}</code></p>
        <p><strong>Blockchain Registered:</strong> ${data.blockchain_registered ? '✅ Yes' : '⏳ Pending'}</p>
        <p><strong>Report Generated:</strong> ${data.report_generated ? '✅ Yes' : '⏳ Pending'}</p>
    `;
}