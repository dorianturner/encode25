let myChart = null;
let pieChart = null;

document.addEventListener('DOMContentLoaded', function() {

    // Function to adjust chart container dimensions dynamically
    function adjustChartContainer() {
        const newsSection = document.querySelector('.news-section');
        const graphSection = document.querySelector('.graph-section');
        const performanceChart = document.querySelector('.performance-chart');
        const distributionChart = document.querySelector('.distribution-chart');

        if (graphSection && newsSection) {
            const newsWidth = newsSection.offsetWidth;
            graphSection.style.width = `${newsWidth}px`;
            const graphHeight = graphSection.offsetHeight;
            if (performanceChart) performanceChart.style.height = `${graphHeight*0.7}px`;
            if (distributionChart) distributionChart.style.height = `${graphHeight*0.7}px`;
        }
    }

    // Call adjustChartContainer on DOMContentLoaded
    adjustChartContainer();



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

        const setTheme = (theme) => {
            htmlElement.classList.remove('light', 'dark');
            htmlElement.classList.add(theme);
            localStorage.setItem('theme', theme);
            updateChartTheme();
        };

        const updateChartTheme = () => {
            const style = getComputedStyle(document.documentElement);
            
            if (myChart) {
                myChart.options.scales.x.ticks.color = style.getPropertyValue('--text-muted');
                myChart.options.scales.y.ticks.color = style.getPropertyValue('--text-muted');
                myChart.options.scales.y.grid.color = style.getPropertyValue('--portfolio-border');
                myChart.options.plugins.tooltip.backgroundColor = style.getPropertyValue('--card-bg');
                myChart.options.plugins.tooltip.titleColor = style.getPropertyValue('--text-color');
                myChart.options.plugins.tooltip.bodyColor = style.getPropertyValue('--text-color');
                myChart.options.plugins.tooltip.borderColor = style.getPropertyValue('--input-border');
                myChart.data.datasets[0].borderColor = style.getPropertyValue('--primary');
                myChart.update();
            }
            
            if (pieChart) {
                pieChart.options.plugins.legend.labels.color = style.getPropertyValue('--text-color');
                pieChart.options.plugins.tooltip.backgroundColor = style.getPropertyValue('--card-bg');
                pieChart.options.plugins.tooltip.titleColor = style.getPropertyValue('--text-color');
                pieChart.options.plugins.tooltip.bodyColor = style.getPropertyValue('--text-color');
                pieChart.options.plugins.tooltip.borderColor = style.getPropertyValue('--input-border');
                pieChart.options.plugins.title.color = style.getPropertyValue('--text-color');
                pieChart.update();
            }
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

        return { init, updateChartTheme, setChart: (chart) => { myChart = chart; }, setPieChart: (chart) => { pieChart = chart; } };
    })();

    ThemeManager.init();

    // Handle tab switching
    function setupGraphTabs() {
        const tabs = document.querySelectorAll('.graph-tab');
        const chartContainers = document.querySelectorAll('.chart-placeholder');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs and containers
                tabs.forEach(t => t.classList.remove('active'));
                chartContainers.forEach(c => c.classList.remove('active'));

                // Add active class to clicked tab
                tab.classList.add('active');

                // Show corresponding chart
                const tabName = tab.dataset.tab;
                document.querySelector(`.${tabName}-chart`).classList.add('active');
            });
        });
    }

    // Handle Ethereum address form submission
    const ethereumForm = document.getElementById('ethereum-form');
    const portfolioList = document.querySelector('.portfolio-list');
    const portfolioValue = document.querySelector('.portfolio-value');
    const portfolioSection = document.querySelector('.portfolio');

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

        // Create HTML for portfolio items
        let portfolioHTML = '';

        let ethPrice = walletData['ETH'] || 0;
        totalValue += ethValue * ethPrice;

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
                <div>
                    <div class="asset-amount">${ethValue.toFixed(4)} ETH</div>
                    <div class="asset-price">\$${(ethValue * ethPrice).toFixed(2)}</div>
                </div>
            </div>
        `;

        // Add ERC-20 tokens if available
        if (walletData['ERC-20 Token Balances']) {
            const tokenBalances = walletData['ERC-20 Token Balances'];

            for (const [address, balance, tokenName, tokenSymbol, logoURL, price] of tokenBalances) {
                totalValue += parseFloat(price);

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
                        <div>
                            <div class="asset-amount">${parseFloat(balance).toFixed(2)} ${tokenSymbol}</div>
                            <div class="asset-price">\$${parseFloat(price).toFixed(2)}</div>
                        </div>
                    </div>
                `;
            }
        }

        // Update the DOM
        portfolioList.innerHTML = portfolioHTML;

        // For smoother animation, update the text after a brief delay
        setTimeout(() => {
            animateCounter(0, totalValue, 1500, value => {
                portfolioValue.textContent = `Total: $${totalValue.toFixed(2)}`;
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

        // Destroy existing charts if they exist
        if (myChart) {
            myChart.destroy();
            myChart = null;
        }
        if (pieChart) {
            pieChart.destroy();
            pieChart = null;
        }

        // Prepare data for both charts
        const historicalData = walletData['historical_data'] || [];
        const filteredHistoricalData = historicalData.filter(item => item.value >= 1);
        const dates = filteredHistoricalData.map(item => item.date);
        const values = filteredHistoricalData.map(item => item.value);

        // Prepare pie chart data
        const tokens = [];
        const amounts = [];
        let pieTotalValue = 0;

        // Add ETH data if available
        if (walletData['ETH Balance'] && walletData['ETH']) {
            const ethValue = walletData['ETH Balance'] * walletData['ETH'];
            tokens.push('ETH');
            amounts.push(ethValue);
            pieTotalValue += ethValue;
        }

        // Add ERC-20 tokens if available
        if (walletData['ERC-20 Token Balances']) {
            for (const token of walletData['ERC-20 Token Balances']) {
                // Skip tokens with zero or negative value
                if (token[5] <= 0) continue;
                
                tokens.push(token[3]); // Symbol
                amounts.push(token[5]); // USD value
                pieTotalValue += token[5];
            }
        }

        // Group small tokens into "Others" if there are more than 8 tokens
        const MAX_TOKENS_TO_DISPLAY = 8;
        if (tokens.length > MAX_TOKENS_TO_DISPLAY) {
            const threshold = pieTotalValue * 0.01; // 1% threshold
            const mainTokens = [];
            const mainAmounts = [];
            let othersSum = 0;

            for (let i = 0; i < tokens.length; i++) {
                if (amounts[i] >= threshold) {
                    mainTokens.push(tokens[i]);
                    mainAmounts.push(amounts[i]);
                } else {
                    othersSum += amounts[i];
                }
            }

            // Add "Others" if there are small tokens
            if (othersSum > 0) {
                mainTokens.push('Others');
                mainAmounts.push(othersSum);
            }

            // Use the filtered data
            tokens.length = 0;
            amounts.length = 0;
            tokens.push(...mainTokens);
            amounts.push(...mainAmounts);
        }

        // Create line chart
        const ctx = document.getElementById('myChart').getContext('2d');

        var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
        gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
        gradientStroke.addColorStop(0.01, 'rgba(72,72,176,0.0)');
        gradientStroke.addColorStop(0, 'rgba(119,52,169,0)');

        myChart = new Chart(ctx, {
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
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted'),
                            callback: function(value, index) {
                                const date = new Date(this.getLabelForValue(value));
                                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                            }
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

        // Create pie chart
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        pieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: tokens,
                datasets: [{
                    data: amounts,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',   // Indigo
                        'rgba(239, 68, 68, 0.7)',    // Red
                        'rgba(16, 185, 129, 0.7)',   // Green
                        'rgba(245, 158, 11, 0.7)',   // Yellow
                        'rgba(139, 92, 246, 0.7)',   // Purple
                        'rgba(20, 184, 166, 0.7)',   // Teal
                        'rgba(249, 115, 22, 0.7)',   // Orange
                        'rgba(236, 72, 153, 0.7)',   // Pink
                        'rgba(6, 182, 212, 0.7)',    // Cyan
                        'rgba(156, 163, 175, 0.7)'   // Gray
                    ],
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--card-bg'),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                            font: {
                                size: 12
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--card-bg'),
                        titleColor: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                        bodyColor: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--input-border'),
                        bodyFont: {
                            size: 14
                        },
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = parseFloat(context.raw || 0).toFixed(2);
                                return `${label}: $${value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                            }
                        }
                    },
                    // title: {
                    //     align: 'center',
                    //     display: true,
                    //     text: 'Token Distribution',
                    //     color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                    //     font: {
                    //         size: 16
                    //     }
                    // }
                },
                cutout: '60%'
            }
        });

        // Set charts in ThemeManager
        ThemeManager.setChart(myChart);
        ThemeManager.setPieChart(pieChart);
        
        // Initialize the tabs
        setupGraphTabs();
        ThemeManager.updateChartTheme();
    }

    // Counter animation function
    function animateCounter(start, end, duration, callback) {
        const startTime = performance.now();

        function update(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
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

    document.getElementById('question-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const questionInput = document.getElementById('question-input');
        const answerBox = document.getElementById('answer-box');
        const question = questionInput.value.trim();
        if (!question) return;
    
        // Show loading state
        answerBox.innerHTML = '<div class="spinner loading"></div>';
    
        try {
            const response = await fetch('/api/ask_question_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    address: sessionStorage.getItem('current_address') || ''
                })
            });
    
            if (!response.ok || !response.body) {
                const errorText = await response.text();
                throw new Error(`Request failed (${response.status}): ${errorText}`);
            }
    
            const ensureMarkedLoaded = () => {
                return new Promise((resolve) => {
                    if (typeof marked !== 'undefined') {
                        resolve();
                    } else {
                        const script = document.createElement('script');
                        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.2/marked.min.js';
                        script.onload = () => resolve();
                        document.head.appendChild(script);
                    }
                });
            };
    
            await ensureMarkedLoaded();
    
            answerBox.innerHTML = '<div class="answer-text markdown-content"></div>';
            const answerText = answerBox.querySelector('.answer-text');
    
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedText = '';
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                accumulatedText += chunk;
                
                answerText.innerHTML = marked.parse(accumulatedText);
                
                if (typeof hljs !== 'undefined') {
                    answerText.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                }
                
                answerText.scrollTop = answerText.scrollHeight;
            }
    
        } catch (error) {
            console.log('Error:', error);
            answerBox.innerHTML = '<div class="error">Failed to get response. Please try again.</div>';
        }
    });


    window.addEventListener('resize', adjustChartContainer);
    document.addEventListener('DOMContentLoaded', adjustChartContainer);

    // Add event listener for window resize to adjust heights
    window.addEventListener('resize', adjustPortfolioHeight);

    // Call adjustPortfolioHeight on page load
    window.addEventListener('load', adjustPortfolioHeight);
});
