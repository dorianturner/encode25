document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');
    const questionInput = document.getElementById('question-input');
    const answerBox = document.getElementById('answer-box');
    const ethereumForm = document.getElementById('ethereum-form');
    
    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.className = savedTheme;
    updateThemeToggleIcon(savedTheme);
    
    // Theme toggle functionality
    themeToggle.addEventListener('click', function() {
        if (html.classList.contains('light')) {
            html.classList.remove('light');
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            updateThemeToggleIcon('dark');
        } else {
            html.classList.remove('dark');
            html.classList.add('light');
            localStorage.setItem('theme', 'light');
            updateThemeToggleIcon('light');
        }
    });
    
    function updateThemeToggleIcon(theme) {
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
    
    // Question handling
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const question = questionInput.value.toLowerCase();
            if (question.includes('risk')) {
                answerBox.innerHTML = `
                    <span class="badge badge-warning">Moderate Risk</span>
                    Your risk level on protocol X is moderate. Consider reallocating some assets to lower-risk options.
                    <div style="margin-top: 16px; display: flex; gap: 8px;">
                        <button class="btn btn-primary">Show recommendations</button>
                        <button class="btn">Learn more</button>
                    </div>
                `;
            } else if (question.includes('apy') || question.includes('yield')) {
                answerBox.innerHTML = `
                    <span class="badge" style="background-color: rgba(16, 185, 129, 0.1); color: #10b981;">Yield Analysis</span>
                    Based on your portfolio, you could earn an additional 3.2% APY by moving some USDC to Protocol Y's stablecoin pool.
                    <div style="margin-top: 16px; display: flex; gap: 8px;">
                        <button class="btn btn-primary">View details</button>
                        <button class="btn">Compare platforms</button>
                    </div>
                `;
            } else {
                answerBox.innerHTML = `
                    I can help you analyze your DeFi portfolio and provide insights. Please ask about your assets, risks, yields, or investment opportunities.
                    <div style="margin-top: 16px; display: flex; gap: 8px;">
                        <button class="btn">View suggestions</button>
                    </div>
                `;
            }
        }
    });
    
    // Ethereum form handling
    if (ethereumForm) {
        ethereumForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent the form from submitting traditionally
            
            const formData = new FormData(ethereumForm);
            
            fetch('/submit_address', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log(data.message);
                    
                    const portfolioSection = document.querySelector('.portfolio');
                    if (portfolioSection) {
                        const addressInfo = document.createElement('div');
                        addressInfo.className = 'portfolio-value';
                        addressInfo.textContent = `Address: ${data.address.substring(0, 6)}...${data.address.substring(data.address.length - 4)}`;
                        portfolioSection.querySelector('.portfolio-header').appendChild(addressInfo);
                    }
                } else {
                    console.error(data.message);
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }
    
    // else {
    //     document.querySelectorAll('.btn').forEach(button => {
    //         button.addEventListener('click', function() {
    //             alert('This is a demo interface. This button would normally trigger an action in the actual application.');
    //         });
    //     });
    // }
});