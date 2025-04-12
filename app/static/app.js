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

        const minHeight = 1000;
        const calculatedHeight = walletHeight - formHeight - headerHeight - padding - 16;

        portfolioList.style.maxHeight = `${Math.max(minHeight, calculatedHeight)}px`;
    }

    // Theme toggle functionality
    const ThemeManager = (() => {
        const htmlElement = document.documentElement;
        const themeToggle = document.getElementById('theme-toggle');
        const themeToggleIcon = document.getElementById('theme-toggle-icon');
        let myChart = null;

        const setTheme = (theme) => {
            htmlElement.classList.remove('light', 'dark');
            htmlElement.classList.add(theme);
            localStorage.setItem('theme', theme);
            updateChartTheme();
        };

        const updateChartTheme = () => {
            if (!myChart) return;
            
            const style = getComputedStyle(document.documentElement);
            myChart.options.scales.x.ticks.color = style.getPropertyValue('--text-muted');
            myChart.options.scales.y.ticks.color = style.getPropertyValue('--text-muted');
            myChart.options.scales.y.grid.color = style.getPropertyValue('--portfolio-border');
            myChart.options.plugins.tooltip.backgroundColor = style.getPropertyValue('--card-bg');
            myChart.options.plugins.tooltip.titleColor = style.getPropertyValue('--text-color');
            myChart.options.plugins.tooltip.bodyColor = style.getPropertyValue('--text-color');
            myChart.options.plugins.tooltip.borderColor = style.getPropertyValue('--input-border');
            
            myChart.data.datasets[0].borderColor = style.getPropertyValue('--primary');
            myChart.update();
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

        return { init, updateChartTheme, setChart: (chart) => { myChart = chart; } };
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
            portfolioSection.classList.remove('hidden');
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

        const historicalData = walletData['historical_data'];
        const filteredHistoricalData = historicalData.filter(item => item.value !== 0);

        const dates = filteredHistoricalData.map(item => item.date);
        const values = filteredHistoricalData.map(item => item.value);

        const ctx = document.getElementById('myChart').getContext('2d');

        var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

        gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
        gradientStroke.addColorStop(0.01, 'rgba(72,72,176,0.0)');
        gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

        const myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Portfolio Value',
                    data: values,
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--primary'),
                    backgroundColor: gradientStroke,
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--card-bg'),
                        titleColor: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                        bodyColor: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--input-border'),
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted')
                        }
                    },
                    y: {
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--portfolio-border'),
                            drawBorder: false
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted'),
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });

        ThemeManager.setChart(myChart);

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

            for (const [address, balance, tokenName, tokenSymbol, logoURL] of tokenBalances) {
                const tokenValue = balance * (mockPrices[address] || 0);
                totalValue += tokenValue;

                portfolioHTML += `
                    <div class="portfolio-item">
                        <div class="asset-info">
                            <div class="asset-icon">
                                <img src="${logoURL}" onerror="this.src='static/images/generic-token.png'" alt="${tokenSymbol}">
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

        // For smoother animation, update the text after a brief delay
        setTimeout(() => {
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

    // Rest of the file remains the same (animateCounter, showError, question form handling, etc.)
    // ...
});
