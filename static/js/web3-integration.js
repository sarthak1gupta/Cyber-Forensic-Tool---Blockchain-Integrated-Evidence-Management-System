// Web3 Integration for Blockchain Interactions
// This file provides client-side blockchain verification capabilities

// Check if MetaMask is installed
function isMetaMaskInstalled() {
    return typeof window.ethereum !== 'undefined';
}

// Connect to MetaMask
async function connectMetaMask() {
    if (!isMetaMaskInstalled()) {
        alert('MetaMask is not installed. Please install MetaMask to interact with the blockchain.');
        return null;
    }

    try {
        // Request account access
        const accounts = await window.ethereum.request({ 
            method: 'eth_requestAccounts' 
        });
        
        console.log('Connected to MetaMask:', accounts[0]);
        return accounts[0];
    } catch (error) {
        console.error('Error connecting to MetaMask:', error);
        alert('Failed to connect to MetaMask: ' + error.message);
        return null;
    }
}

// Get current network
async function getCurrentNetwork() {
    if (!isMetaMaskInstalled()) {
        return null;
    }

    try {
        const chainId = await window.ethereum.request({ 
            method: 'eth_chainId' 
        });
        
        // Convert hex to decimal
        const networkId = parseInt(chainId, 16);
        
        const networks = {
            1: 'Mainnet',
            5: 'Goerli',
            11155111: 'Sepolia',
            137: 'Polygon',
            80001: 'Mumbai'
        };
        
        return {
            chainId: networkId,
            name: networks[networkId] || 'Unknown Network'
        };
    } catch (error) {
        console.error('Error getting network:', error);
        return null;
    }
}

// Switch to Sepolia testnet
async function switchToSepolia() {
    if (!isMetaMaskInstalled()) {
        return false;
    }

    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0xaa36a7' }], // Sepolia chainId in hex
        });
        
        console.log('Switched to Sepolia testnet');
        return true;
    } catch (error) {
        // This error code indicates that the chain has not been added to MetaMask
        if (error.code === 4902) {
            try {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: '0xaa36a7',
                        chainName: 'Sepolia Testnet',
                        nativeCurrency: {
                            name: 'Sepolia ETH',
                            symbol: 'ETH',
                            decimals: 18
                        },
                        rpcUrls: ['https://sepolia.infura.io/v3/'],
                        blockExplorerUrls: ['https://sepolia.etherscan.io/']
                    }]
                });
                
                console.log('Sepolia network added');
                return true;
            } catch (addError) {
                console.error('Error adding Sepolia network:', addError);
                return false;
            }
        }
        
        console.error('Error switching network:', error);
        return false;
    }
}

// Get account balance
async function getAccountBalance(address) {
    if (!isMetaMaskInstalled()) {
        return null;
    }

    try {
        const balance = await window.ethereum.request({
            method: 'eth_getBalance',
            params: [address, 'latest']
        });
        
        // Convert from Wei to ETH
        const ethBalance = parseInt(balance, 16) / 1e18;
        
        return {
            wei: balance,
            eth: ethBalance.toFixed(6)
        };
    } catch (error) {
        console.error('Error getting balance:', error);
        return null;
    }
}

// Verify transaction on blockchain
async function verifyTransaction(txHash) {
    if (!isMetaMaskInstalled()) {
        return null;
    }

    try {
        const receipt = await window.ethereum.request({
            method: 'eth_getTransactionReceipt',
            params: [txHash]
        });
        
        if (!receipt) {
            return {
                status: 'pending',
                message: 'Transaction is still pending'
            };
        }
        
        return {
            status: receipt.status === '0x1' ? 'success' : 'failed',
            blockNumber: parseInt(receipt.blockNumber, 16),
            gasUsed: parseInt(receipt.gasUsed, 16),
            from: receipt.from,
            to: receipt.to
        };
    } catch (error) {
        console.error('Error verifying transaction:', error);
        return {
            status: 'error',
            message: error.message
        };
    }
}

// Initialize Web3 UI components
function initWeb3UI() {
    if (!isMetaMaskInstalled()) {
        // Show warning that MetaMask is not installed
        const warning = document.createElement('div');
        warning.className = 'result-box warning';
        warning.innerHTML = `
            <h3>⚠️ MetaMask Not Detected</h3>
            <p>MetaMask is not installed. While you can still use the backend blockchain features, 
               client-side verification requires MetaMask.</p>
            <p><a href="https://metamask.io" target="_blank" class="btn btn-secondary">Install MetaMask</a></p>
        `;
        
        // Insert warning at top of page
        const container = document.querySelector('.main-content');
        if (container) {
            container.insertBefore(warning, container.firstChild);
        }
        
        return;
    }

    // Add MetaMask status to header
    const headerInfo = document.querySelector('.header-info');
    if (headerInfo) {
        const metaMaskStatus = document.createElement('span');
        metaMaskStatus.innerHTML = '🦊 MetaMask: <strong id="metaMaskStatus">Checking...</strong>';
        headerInfo.appendChild(metaMaskStatus);
    }

    // Check initial connection status
    checkMetaMaskStatus();
}

// Check MetaMask connection status
async function checkMetaMaskStatus() {
    const statusElement = document.getElementById('metaMaskStatus');
    if (!statusElement) return;

    try {
        const accounts = await window.ethereum.request({ 
            method: 'eth_accounts' 
        });
        
        if (accounts.length > 0) {
            statusElement.textContent = 'Connected';
            statusElement.style.color = '#28a745';
            
            // Check if on Sepolia
            const network = await getCurrentNetwork();
            if (network && network.chainId !== 11155111) {
                statusElement.textContent = `Connected (${network.name})`;
                statusElement.style.color = '#ffc107';
            }
        } else {
            statusElement.textContent = 'Not Connected';
            statusElement.style.color = '#dc3545';
        }
    } catch (error) {
        statusElement.textContent = 'Error';
        statusElement.style.color = '#dc3545';
    }
}

// Listen for account changes
if (typeof window.ethereum !== 'undefined') {
    window.ethereum.on('accountsChanged', (accounts) => {
        console.log('Account changed:', accounts[0]);
        checkMetaMaskStatus();
        
        // Reload page on account change
        if (accounts.length === 0) {
            console.log('MetaMask disconnected');
        }
    });

    window.ethereum.on('chainChanged', (chainId) => {
        console.log('Network changed:', chainId);
        checkMetaMaskStatus();
        
        // Reload page on network change
        window.location.reload();
    });
}

// Client-side transaction verification
async function verifyEvidenceOnChain(contractAddress, contractABI, evidenceId) {
    if (!isMetaMaskInstalled()) {
        alert('MetaMask is required for client-side verification');
        return null;
    }

    try {
        // Connect to MetaMask
        const account = await connectMetaMask();
        if (!account) return null;

        // Check if on Sepolia
        const network = await getCurrentNetwork();
        if (network.chainId !== 11155111) {
            const switched = await switchToSepolia();
            if (!switched) {
                alert('Please switch to Sepolia testnet manually');
                return null;
            }
        }

        // Create contract instance
        const web3 = new Web3(window.ethereum);
        const contract = new web3.eth.Contract(contractABI, contractAddress);

        // Get evidence details
        const evidence = await contract.methods.getEvidence(evidenceId).call();

        return {
            evidenceHash: evidence[0],
            timestamp: evidence[1],
            osSource: evidence[2],
            investigatorId: evidence[3],
            action: evidence[4],
            forensicType: evidence[5],
            toolsUsed: evidence[6]
        };
    } catch (error) {
        console.error('Error verifying evidence:', error);
        alert('Error verifying evidence: ' + error.message);
        return null;
    }
}

// Add button to manually connect MetaMask
function addConnectButton() {
    const blockchainSection = document.querySelector('section.card h2');
    if (blockchainSection && blockchainSection.textContent.includes('Blockchain')) {
        const connectBtn = document.createElement('button');
        connectBtn.className = 'btn btn-secondary';
        connectBtn.textContent = '🦊 Connect MetaMask';
        connectBtn.onclick = async function() {
            const account = await connectMetaMask();
            if (account) {
                alert(`Connected to MetaMask: ${account.substring(0, 6)}...${account.substring(38)}`);
                checkMetaMaskStatus();
            }
        };
        
        blockchainSection.parentElement.insertBefore(connectBtn, blockchainSection.nextSibling);
    }
}

// View transaction on Etherscan
function viewOnEtherscan(txHash, network = 'sepolia') {
    const baseUrls = {
        'mainnet': 'https://etherscan.io',
        'sepolia': 'https://sepolia.etherscan.io',
        'goerli': 'https://goerli.etherscan.io'
    };
    
    const url = `${baseUrls[network]}/tx/${txHash}`;
    window.open(url, '_blank');
}

// View address on Etherscan
function viewAddressOnEtherscan(address, network = 'sepolia') {
    const baseUrls = {
        'mainnet': 'https://etherscan.io',
        'sepolia': 'https://sepolia.etherscan.io',
        'goerli': 'https://goerli.etherscan.io'
    };
    
    const url = `${baseUrls[network]}/address/${address}`;
    window.open(url, '_blank');
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWeb3UI);
} else {
    initWeb3UI();
}

// Export functions for use in other scripts
window.Web3Integration = {
    isMetaMaskInstalled,
    connectMetaMask,
    getCurrentNetwork,
    switchToSepolia,
    getAccountBalance,
    verifyTransaction,
    verifyEvidenceOnChain,
    viewOnEtherscan,
    viewAddressOnEtherscan,
    checkMetaMaskStatus
};