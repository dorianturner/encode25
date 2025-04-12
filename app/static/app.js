document.addEventListener('DOMContentLoaded', function() {
    // Adjust portfolio height dynamically based on content
    function adjustPortfolioHeight() {
        const getElementHeight = (selector) => 
            document.querySelector(selector)?.clientHeight || 0;
    
        const portfolioList = document.querySelector('.portfolio-list');
        if (!portfolioList) return;
    
        const walletHeight = getElementHeight('.wallet-section');
        const formHeight = getElementHeight('#ethereum-form');
        const headerHeight = getElementHeight('.portfolio-header');
        const padding = 56; // 28px top + 28px bottom
    
        const minHeight = 100;
        const calculatedHeight = walletHeight - formHeight - headerHeight - padding - 16;
        
        portfolioList.style.maxHeight = `${Math.max(minHeight, calculatedHeight)}px`;
    }

    // Theme toggle functionality
    const ThemeManager = (() => {
        const htmlElement = document.documentElement;
        const themeToggle = document.getElementById('theme-toggle');
        const themeToggleIcon = document.getElementById('theme-toggle-icon');
        
        const setTheme = (theme) => {
            htmlElement.classList.remove('light', 'dark');
            htmlElement.classList.add(theme);
            localStorage.setItem('theme', theme);
        };
    
        const toggleTheme = () => {
            const isLight = htmlElement.classList.contains('light');
            setTheme(isLight ? 'dark' : 'light');
        };
    
        const init = () => {
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
            
            setTheme(initialTheme);
            themeToggle.addEventListener('click', toggleTheme);
        };
    
        return { init };
    })();
    
    ThemeManager.init();

    // Handle Ethereum address form submission
    const ethereumForm = document.getElementById('ethereum-form');
    const portfolioList = document.querySelector('.portfolio-list');
    const portfolioValue = document.querySelector('.portfolio-value');
    const portfolioSection = document.querySelector('.portfolio'); 

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
                portfolioSection.classList.remove('hidden');
                portfolioSection.classList.add('revealed');

                // Store the current address in session storage for use with questions
                sessionStorage.setItem('current_address', address);
            })
            .catch(error => {
                showError('Failed to fetch wallet data. Please try again.');
                console.error('Error:', error);
            });
        });
    }

   // Updated portfolio reveal functionality
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
            console.log(tokenBalances);

            // Create a mapping of addresses to token names
            const addressToName = {};
            for (const [name, address] of Object.entries(TOKEN_ADDRESSES)) {
                addressToName[address] = name;
            }

            for (const [address, [balance, name, logo]] of Object.entries(tokenBalances)) {
                console.log(balance + " " + name + " " + logo);
                const tokenName = name;
                const tokenSymbol = name;

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
                        <div class="asset-amount">${parseFloat(balance).toFixed(2)}</div>
                    </div>
                `;
            }
        }

        // Update the DOM
        portfolioList.innerHTML = portfolioHTML;
        
        // For smoother animation, update the text after a brief delay
        setTimeout(() => {
            // Use a counter animation for the total value
            animateCounter(0, totalValue, 1500, value => {
                portfolioValue.textContent = `Total: $${value.toFixed(2)}`;
            });
        }, 100);
        
        // Adjust portfolio height before showing
        adjustPortfolioHeight();
        
        // Remove hidden class first
        portfolioSection.classList.remove('hidden');
        
        // Force a reflow before adding the revealed class
        void portfolioSection.offsetWidth;
        
        // Then add revealed class to trigger animation
        portfolioSection.classList.add('revealed');
    }

    // Counter animation function
    function animateCounter(start, end, duration, callback) {
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            // Use easeOutExpo for smoother animation
            const easing = 1 - Math.pow(2, -10 * progress);
            const currentValue = start + (end - start) * easing;
            
            callback(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
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

    // Handle question submission
    document.getElementById('question-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const questionInput = document.getElementById('question-input');
        const answerBox = document.getElementById('answer-box');
        const question = questionInput.value.trim();
        
        if (!question) return;
        
        // Show loading state
        answerBox.innerHTML = '<div class="loading-spinner"></div>';
        
        try {
            // Send to backend
            const response = await fetch('/ask_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    address: sessionStorage.getItem('current_address') || ''
                })
            });
        
            console.log("Raw response object:", response);
        
            if (!response.ok) {
                const errorText = await response.text(); // Read raw error
                throw new Error(`Request failed (${response.status}): ${errorText}`);
            }
        
            const data = await response.json();
            console.log("Received data:", data);
            
            answerBox.innerHTML = `<div class="answer-text">${data.response}</div>`;

        
      
            
        } catch (error) {
            console.log('Error:', error);
            answerBox.innerHTML = '<div class="error">Failed to get response. Please try again.</div>';
            console.error('Error:', error);
        }
    });

    // Add global TOKEN_ADDRESSES for use in the JavaScript

    let TOKEN_ADDRESSES;

    fetch("static/tokens.json")
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(json => {
        TOKEN_ADDRESSES = json;
        console.log('TOKEN_ADDRESSES:', TOKEN_ADDRESSES);
      })
      .catch(error => {
        console.error('Error loading TOKEN_ADDRESSES:', error);
      });

    // Add event listener for window resize to adjust heights
    window.addEventListener('resize', adjustPortfolioHeight);

    // Call adjustPortfolioHeight on page load
    window.addEventListener('load', adjustPortfolioHeight);
});
