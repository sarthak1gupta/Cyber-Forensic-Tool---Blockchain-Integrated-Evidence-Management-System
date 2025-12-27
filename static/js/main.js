// Global state
let currentSession = null;
let systemInfo = null;
let availableTools = null;

// API Base URL
const API_BASE = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadSystemInfo();
    checkSessionStatus();
});

// Load system information
async function loadSystemInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/system-info`);
        const data = await response.json();
        
        if (data.status === 'success') {
            systemInfo = data.system;
            displaySystemInfo(systemInfo);
        }
    } catch (error) {
        console.error('Error loading system info:', error);
    }
}

// Display system information
function displaySystemInfo(info) {
    const infoDiv = document.getElementById('systemInfo');
    infoDiv.innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Operating System:</span>
                <span class="info-value"><strong>${info.os} ${info.os_release}</strong></span>
            </div>
            <div class="info-item">
                <span class="info-label">Architecture:</span>
                <span class="info-value">${info.architecture}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Hostname:</span>
                <span class="info-value">${info.hostname}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Python Version:</span>
                <span class="info-value">${info.python_version}</span>
            </div>
        </div>
    `;
}

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
            availableTools = data.tools;
            displayToolsInfo(data.tools);
            
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = '<h3>✅ Tools Check Complete</h3><p>Check "Available Tools" section above for details.</p>';
            
            return data.tools;
        }
    } catch (error) {
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    }
}

// Display Tools Information
function displayToolsInfo(tools) {
    // Core Tools
    const coreDiv = document.getElementById('coreTools');
    let coreHTML = '';
    
    coreHTML += '<div class="tool-category">';
    coreHTML += '<h4>🐍 Python Libraries</h4><ul>';
    tools.core_tools.python_libraries.forEach(lib => {
        coreHTML += `<li>✅ <strong>${lib}</strong></li>`;
    });
    coreHTML += '</ul></div>';
    
    coreHTML += '<div class="tool-category">';
    coreHTML += '<h4>💻 System Commands</h4><ul>';
    if (tools.core_tools.system_commands.length > 0) {
        tools.core_tools.system_commands.forEach(cmd => {
            coreHTML += `<li>✅ ${cmd}</li>`;
        });
    } else {
        coreHTML += '<li class="text-muted">No system commands detected</li>';
    }
    coreHTML += '</ul></div>';
    coreDiv.innerHTML = coreHTML;
    
    // Advanced Tools
    const advDiv = document.getElementById('advancedTools');
    if (tools.advanced_tools.available) {
        let advHTML = '';
        let toolCount = 0;
        
        for (const [category, toolList] of Object.entries(tools.advanced_tools)) {
            if (category !== 'available' && Array.isArray(toolList) && toolList.length > 0) {
                advHTML += `<div class="tool-category">`;
                advHTML += `<h4>🔧 ${category.toUpperCase()} Tools</h4><ul>`;
                toolList.forEach(tool => {
                    advHTML += `<li>✅ <strong>${tool.name}</strong> (${tool.suite})<br>`;
                    advHTML += `<span class="small text-muted">${tool.description}</span></li>`;
                    toolCount++;
                });
                advHTML += '</ul></div>';
            }
        }
        
        if (toolCount > 0) {
            advDiv.innerHTML = `
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #28a745;">
                    <strong>🎉 ${toolCount} Advanced Tool(s) Detected!</strong>
                    <p class="small" style="margin-top: 5px;">These tools will provide enhanced forensic capabilities when enabled.</p>
                </div>
                ${advHTML}
            `;
        } else {
            showNoAdvancedTools(advDiv);
        }
    } else {
        showNoAdvancedTools(advDiv);
    }
}

function showNoAdvancedTools(advDiv) {
    advDiv.innerHTML = `
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <p><strong>⚠️ No Advanced Tools Detected</strong></p>
            <p class="small">The system will use core tools only. For enhanced analysis, install:</p>
            <ul class="small">
                <li><strong>The Sleuth Kit</strong> - Deleted file recovery, timeline analysis</li>
                <li><strong>Foremost</strong> - File carving and data recovery</li>
                <li><strong>Wireshark</strong> - Deep packet analysis</li>
            </ul>
            <p class="small">Configure tool paths in your .env file.</p>
        </div>
    `;
}

// Start Forensics
async function startForensics() {
    const allCheckbox = document.getElementById('forensic_all');
    const forensicCheckboxes = document.querySelectorAll('.forensic-type:checked');
    const useAdvancedTools = document.getElementById('useAdvancedTools').checked;
    
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
    
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="loading"></span> Running...';
    
    const progressDiv = document.getElementById('forensicProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const resultDiv = document.getElementById('forensicResult');
    const commandLogDiv = document.getElementById('commandLog');
    const commandLogContent = document.getElementById('commandLogContent');
    
    progressDiv.style.display = 'block';
    commandLogDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    
    // Clear previous command log
    commandLogContent.innerHTML = '<p style="color: #00ff00;">Starting forensic investigation...</p>';
    
    // Simulate real-time command logging
    let commandCount = 0;
    const commandSimulator = setInterval(() => {
        commandCount++;
        const commands = [
            'Initializing forensic modules...',
            'Detecting operating system...',
            'Enumerating processes...',
            'Analyzing network connections...',
            'Scanning disk information...',
            'Checking system logs...',
            'Collecting evidence...'
        ];
        if (commandCount < commands.length) {
            commandLogContent.innerHTML += `<p style="color: #888;">[${ new Date().toLocaleTimeString()}] ${commands[commandCount]}</p>`;
            commandLogDiv.scrollTop = commandLogDiv.scrollHeight;
        }
    }, 1500);
    
    // Animate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 3;
        if (progress >= 95) {
            progress = 95;
        }
        progressFill.style.width = progress + '%';
        progressFill.textContent = progress + '%';
    }, 800);
    
    progressText.textContent = `Executing forensic analysis... ${useAdvancedTools ? '(Advanced Tools Enabled)' : ''}`;
    
    try {
        const response = await fetch(`${API_BASE}/api/start-forensics`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                forensic_types: forensicTypes,
                use_advanced_tools: useAdvancedTools
            })
        });
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        clearInterval(commandSimulator);
        progressFill.style.width = '100%';
        progressFill.textContent = '100%';
        progressText.textContent = 'Forensics completed!';
        
        commandLogContent.innerHTML += '<p style="color: #00ff00; font-weight: bold;">✓ Investigation completed successfully!</p>';
        
        if (data.status === 'success') {
            currentSession = data;
            
            resultDiv.className = 'result-box success';
            resultDiv.innerHTML = `
                <h3>✅ Forensic Investigation Completed</h3>
                <p><strong>Session ID:</strong> ${data.session_id}</p>
                <p><strong>Evidence Hash:</strong> <code>${data.evidence_hash}</code></p>
                <p><strong>Advanced Tools:</strong> ${data.advanced_tools_used ? '✅ Enabled' : '❌ Disabled'}</p>
                <p><strong>Forensics Completed:</strong></p>
                <ul>
                    ${data.forensics_completed.map(f => `<li>✅ ${f.toUpperCase()}</li>`).join('')}
                </ul>
                <p class="mt-20"><strong>Next Steps:</strong></p>
                <ul>
                    <li>Register evidence on blockchain for immutable chain of custody</li>
                    <li>Generate AI-powered forensic report</li>
                </ul>
            `;
            
            // Display tools summary
            if (data.tools_summary) {
                displayToolsSummary(data.tools_summary);
            }
            
            // Enable blockchain button
            document.getElementById('blockchainBtn').disabled = false;
            
            // Update session status
            updateSessionStatus(data);
            
        } else {
            resultDiv.className = 'result-box error';
            resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
            commandLogContent.innerHTML += `<p style="color: #ff0000;">✗ Error: ${data.error}</p>`;
        }
    } catch (error) {
        clearInterval(progressInterval);
        clearInterval(commandSimulator);
        resultDiv.className = 'result-box error';
        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
        commandLogContent.innerHTML += `<p style="color: #ff0000;">✗ Error: ${error.message}</p>`;
    } finally {
        startBtn.disabled = false;
        startBtn.innerHTML = '🚀 Start Investigation';
    }
}

// Display Tools Summary
function displayToolsSummary(summary) {
    const findingsDiv = document.getElementById('detailedFindings');
    findingsDiv.style.display = 'block';
    
    let html = '<h3>🔍 Tools & Commands Used</h3>';
    
    html += '<div class="findings-section">';
    html += '<h4>Core Tools</h4>';
    html += '<p>' + summary.core_tools_used.join(', ') + '</p>';
    html += '</div>';
    
    if (summary.advanced_tools_used.length > 0) {
        html += '<div class="findings-section">';
        html += '<h4>🚀 Advanced Tools</h4>';
        html += '<p>' + summary.advanced_tools_used.join(', ') + '</p>';
        html += '</div>';
    }
    
    if (summary.commands_executed.length > 0) {
        html += '<div class="findings-section">';
        html += '<h4>Commands Executed</h4>';
        html += '<div class="command-list">';
        summary.commands_executed.slice(0, 10).forEach(cmd => {
            html += `<div class="command-item">`;
            html += `<code>${cmd.command}</code>`;
            if (cmd.description) {
                html += `<p class="small text-muted">${cmd.description}</p>`;
            }
            html += `</div>`;
        });
        if (summary.commands_executed.length > 10) {
            html += `<p class="small">... and ${summary.commands_executed.length - 10} more commands</p>`;
        }
        html += '</div></div>';
    }
    
    findingsDiv.innerHTML = html;
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
                `;
            } else {
                resultDiv.className = 'result-box error';
                resultDiv.innerHTML = `
                    <h3>❌ Verification Failed</h3>
                    <p>${data.message}</p>
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