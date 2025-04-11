document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const htmlElement = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');

    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        htmlElement.classList.add('dark');
        htmlElement.classList.remove('light');
        updateThemeIcon('dark');
    } else {
        htmlElement.classList.add('light');
        htmlElement.classList.remove('dark');
        updateThemeIcon('light');
    }

    // Update the theme icon based on current theme
    function updateThemeIcon(theme) {
        if (theme === 'dark') {
            themeToggleIcon.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
            `;
        } else {
            themeToggleIcon.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
            `;
        }
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        if (htmlElement.classList.contains('light')) {
            htmlElement.classList.remove('light');
            htmlElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            updateThemeIcon('dark');
        } else {
            htmlElement.classList.remove('dark');
            htmlElement.classList.add('light');
            localStorage.setItem('theme', 'light');
            updateThemeIcon('light');
        }
    });

    // Handle Ethereum address form submission
    const ethereumForm = document.getElementById('ethereum-form');
    const portfolioList = document.querySelector('.portfolio-list');
    const portfolioValue = document.querySelector('.portfolio-value');

    // Ethereum form handling
    if (ethereumForm) {
        ethereumForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(ethereumForm);
            const address = formData.get('ethereum_address');

            // Show loading state
            portfolioList.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            `;

            // Send request to backend
            fetch('/submit_address', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                    return;
                }

                updatePortfolio(data.wallet);

                // Store the current address in session storage for use with questions
                sessionStorage.setItem('current_address', address);
            })
            .catch(error => {
                showError('Failed to fetch wallet data. Please try again.');
                console.error('Error:', error);
            });
        });
    }

    function updatePortfolio(walletData) {
        if (!walletData || walletData.error) {
            showError('No wallet data available.');
            return;
        }

        let totalValue = 0;
        let ethValue = walletData['ETH Balance'] || 0;

        // For a real app, you would fetch current price data
        // This is a simplified calculation
        const mockPrices = {
            'ETH': 2000,
            '0xA0b86991C6218B36c1d19D4a2e9eb0ce3606eB48': 1, // USDC
            '0x6B175474E89094C44Da98b954EedeAC495271d0F': 1, // DAI
            '0x55d398326f99059fF775485246999027B3197955': 1, // USDT
            '0xC02aaA39b223FE8D0A0E5C4F27EAD9083C756Cc2': 2000 // WETH
        };

        // Calculate total value
        totalValue += ethValue * mockPrices['ETH'];

        // Create HTML for portfolio items
        let portfolioHTML = '';

        // Add ETH
        portfolioHTML += `
            <div class="portfolio-item">
                <div class="asset-info">
                    <div class="asset-icon">
                        <img src="static/images/ethereum-eth-logo-diamond-purple.svg" alt="ETH">
                    </div>
                    <div>
                        <div class="asset-name">Ethereum</div>
                        <div class="asset-symbol">ETH</div>
                    </div>
                </div>
                <div class="asset-amount">${ethValue.toFixed(4)} ETH</div>
            </div>
        `;

        // Add ERC-20 tokens if available
        if (walletData['ERC-20 Token Balances']) {
            const tokenBalances = walletData['ERC-20 Token Balances'];

            // Create a mapping of addresses to token names
            const addressToName = {};
            for (const [name, address] of Object.entries(TOKEN_ADDRESSES)) {
                addressToName[address] = name;
            }

            for (const [address, balance] of Object.entries(tokenBalances)) {
                const tokenName = addressToName[address] || 'Unknown Token';
                const tokenSymbol = addressToName[address] || 'UNKNOWN';

                const tokenValue = balance * (mockPrices[address] || 0);
                totalValue += tokenValue;

                portfolioHTML += `
                    <div class="portfolio-item">
                        <div class="asset-info">
                            <div class="asset-icon">
                                <img src="static/images/${tokenSymbol.toLowerCase()}-logo.svg" onerror="this.src='static/images/generic-token.svg'" alt="${tokenSymbol}">
                            </div>
                            <div>
                                <div class="asset-name">${tokenName}</div>
                                <div class="asset-symbol">${tokenSymbol}</div>
                            </div>
                        </div>
                        <div class="asset-amount">${parseFloat(balance).toFixed(2)} ${tokenSymbol}</div>
                    </div>
                `;
            }
        }

        // Update the DOM
        portfolioList.innerHTML = portfolioHTML;
        portfolioValue.textContent = `Total: $${totalValue.toFixed(2)}`;
    }

    function showError(message) {
        portfolioList.innerHTML = `
            <div style="padding: 20px; color: var(--danger);">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <p>${message}</p>
            </div>
        `;
    }

    // Handle AI Assistant questions
    const questionInput = document.getElementById('question-input');
    const answerBox = document.getElementById('answer-box');

    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const question = questionInput.value;
                const address = sessionStorage.getItem('current_address');

                // Show loading state
                answerBox.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                    </div>
                `;

                // Create form data to send to backend
                const formData = new FormData();
                formData.append('question', question);
                if (address) {
                    formData.append('address', address);
                }

                // Send to backend
                fetch('/ask_question', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Format the answer
                    let answerHTML = '';

                    if (data.badge) {
                        answerHTML += `<span class="badge ${data.badge}">${data.badge_text}</span>`;
                    }

                    answerHTML += data.text;

                    if (data.buttons && data.buttons.length > 0) {
                        answerHTML += `<div style="margin-top: 16px; display: flex; gap: 8px;">`;

                        data.buttons.forEach(button => {
                            const buttonClass = button.type === 'primary' ? 'btn btn-primary' : 'btn';
                            answerHTML += `<button class="${buttonClass}">${button.text}</button>`;
                        });

                        answerHTML += `</div>`;
                    }

                    answerBox.innerHTML = answerHTML;

                    // Add event listeners to the new buttons
                    document.querySelectorAll('.btn').forEach(button => {
                        button.addEventListener('click', function() {
                            alert('This is a demo interface. This button would normally trigger an action in the actual application.');
                        });
                    });
                })
                .catch(error => {
                    answerBox.innerHTML = `
                        <div style="color: var(--danger);">
                            Sorry, I couldn't process your question. Please try again.
                        </div>
                    `;
                    console.error('Error:', error);
                });
            }
        });
    }

    // Add global TOKEN_ADDRESSES for use in the JavaScript
    const TOKEN_ADDRESSES = {
        "USDT":"0xdac17f958d2ee523a2206206994597c13d831ec7",
        "USDC":"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "BUSD":"0x4fabb145d64652a948d72533023f6e7a623c7c53",
        "SHIB":"0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
        "DAI":"0x6b175474e89094c44da98b954eedeac495271d0f",
        "MATIC":"0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
        "STETH":"0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
        "UNI":"0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
        "WBTC":"0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        "OKB":"0x75231f58b43240c9718dd58b4967c5114342a86c",
        "LEO":"0x2af5d2ad76741191d15dfe7bf6ac92d4bd912ca3",
        "LINK":"0x514910771af9ca656af840dff83e8264ecf986ca",
        "CRO":"0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b",
        "QNT":"0x4a220e6096b25eadb88358cb44068a3248254675",
        "APE":"0x4d224452801aced8b2f0aebe155379bb5d594381",
        "XCN":"0xa2cd3d43c775978a96bdbf12d733d5a1ed94fb18",
        "FRAX":"0x853d955acef822db058eb8505911ed77f175b99e",
        "SAND":"0x3845badade8e6dff049820680d1f14bd3903a5d0",
        "MANA":"0x0f5d2fb29fb7d3cfee444a200298f468908cc942",
        "AXS":"0xbb0e17ef65f82ab018d8edd776e8dd940327b28b",
        "CHZ":"0x3506424f91fd33084466f402d5d97f05f8e3b4af",
        "AAVE":"0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9"
    };

    // Initialize buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            alert('This is a demo interface. This button would normally trigger an action in the actual application.');
        });
    });
});