// IntoTheCryptoverse Data Extractor
// Run this in the browser console on https://app.intothecryptoverse.com/crypto

(function extractCryptoverseData() {
    console.log("🔍 Starting IntoTheCryptoverse data extraction...");

    // Array to store extracted data
    const riskData = [];

    // Method 1: Try to find data in the React components
    const findReactData = () => {
        // Look for React fiber nodes
        const rootElement = document.getElementById('root') || document.querySelector('[id*="root"]');
        if (rootElement && rootElement._reactRootContainer) {
            console.log("Found React root");
            // Try to access React internal data
            const fiberRoot = rootElement._reactRootContainer._internalRoot;
            if (fiberRoot) {
                console.log("Exploring React fiber tree...");
            }
        }
    };

    // Method 2: Extract from table if visible
    const extractFromTable = () => {
        // Look for table with crypto data
        const tables = document.querySelectorAll('table');
        console.log(`Found ${tables.length} tables`);

        tables.forEach((table, index) => {
            console.log(`Checking table ${index + 1}`);
            const rows = table.querySelectorAll('tr');

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length > 0) {
                    // Try to find symbol, price, and risk columns
                    let symbol = '';
                    let price = null;
                    let risk = null;

                    // Look for symbol (usually first column or contains ticker)
                    cells.forEach((cell, i) => {
                        const text = cell.textContent.trim();

                        // Check for symbol patterns (BTC, ETH, etc.)
                        if (/^[A-Z]{2,6}$/.test(text)) {
                            symbol = text;
                        }

                        // Check for price (starts with $ or is a number)
                        if (text.startsWith('$') || /^\d+\.?\d*$/.test(text)) {
                            const numValue = parseFloat(text.replace(/[$,]/g, ''));
                            if (!isNaN(numValue) && numValue > 0) {
                                if (!price) price = numValue;
                            }
                        }

                        // Check for risk value (0-1 or 0-100)
                        if (/^0?\.\d+$/.test(text) || /^\d{1,2}(\.\d+)?%?$/.test(text)) {
                            const numValue = parseFloat(text.replace('%', ''));
                            if (!isNaN(numValue)) {
                                // Convert percentage to decimal if needed
                                risk = numValue > 1 ? numValue / 100 : numValue;
                            }
                        }
                    });

                    if (symbol && (price || risk)) {
                        riskData.push({
                            symbol: symbol,
                            price: price,
                            risk_value: risk,
                            source: 'intothecryptoverse',
                            timestamp: new Date().toISOString()
                        });
                    }
                }
            });
        });
    };

    // Method 3: Extract from divs and cards
    const extractFromCards = () => {
        // Look for card-like elements with crypto data
        const cards = document.querySelectorAll('[class*="card"], [class*="row"], [class*="item"]');
        console.log(`Found ${cards.length} potential data cards`);

        cards.forEach(card => {
            const text = card.textContent;

            // Look for patterns like "BTC $100,000 Risk: 0.85"
            const symbolMatch = text.match(/\b([A-Z]{2,6})\b/);
            const priceMatch = text.match(/\$?([\d,]+\.?\d*)/);
            const riskMatch = text.match(/(?:risk|Risk|RISK)[:\s]*([\d.]+)/i);

            if (symbolMatch && (priceMatch || riskMatch)) {
                riskData.push({
                    symbol: symbolMatch[1],
                    price: priceMatch ? parseFloat(priceMatch[1].replace(/,/g, '')) : null,
                    risk_value: riskMatch ? parseFloat(riskMatch[1]) : null,
                    source: 'intothecryptoverse',
                    timestamp: new Date().toISOString()
                });
            }
        });
    };

    // Method 4: Check for API data in window object
    const checkWindowData = () => {
        // Common places where data might be stored
        const possibleKeys = ['__INITIAL_STATE__', '__DATA__', 'cryptoData', 'riskData', 'tableData'];

        possibleKeys.forEach(key => {
            if (window[key]) {
                console.log(`Found window.${key}`);
                console.log(window[key]);
            }
        });

        // Check for Redux store
        if (window.store) {
            console.log("Found Redux store");
            const state = window.store.getState();
            console.log(state);
        }
    };

    // Method 5: Extract specific risk metric elements
    const extractRiskMetrics = () => {
        // Look for elements containing "risk" text
        const riskElements = Array.from(document.querySelectorAll('*')).filter(el =>
            el.textContent.toLowerCase().includes('risk') &&
            el.children.length === 0
        );

        console.log(`Found ${riskElements.length} elements with 'risk' text`);

        riskElements.forEach(el => {
            console.log(el.textContent);
        });
    };

    // Run all extraction methods
    console.log("Method 1: Checking React data...");
    findReactData();

    console.log("Method 2: Extracting from tables...");
    extractFromTable();

    console.log("Method 3: Extracting from cards...");
    extractFromCards();

    console.log("Method 4: Checking window object...");
    checkWindowData();

    console.log("Method 5: Extracting risk metrics...");
    extractRiskMetrics();

    // Display results
    console.log("=" * 60);
    console.log("📊 EXTRACTION RESULTS");
    console.log("=" * 60);
    console.log(`Found ${riskData.length} data points`);
    console.table(riskData);

    // Save to clipboard
    if (riskData.length > 0) {
        const jsonData = JSON.stringify(riskData, null, 2);
        navigator.clipboard.writeText(jsonData).then(() => {
            console.log("✅ Data copied to clipboard!");
            console.log("Paste it into a file and run:");
            console.log("python3 sync_intothecryptoverse_direct.py --load your_file.json");
        });
    }

    // Return data for manual inspection
    return riskData;
})();

// Additional helper to get all text content
function getAllText() {
    const allText = document.body.innerText;
    console.log("Full page text (first 1000 chars):");
    console.log(allText.substring(0, 1000));
    return allText;
}

// Helper to find specific patterns
function findPatterns() {
    const patterns = {
        btc: /BTC.*?(\d+\.?\d*)/gi,
        eth: /ETH.*?(\d+\.?\d*)/gi,
        risk: /risk.*?(\d+\.?\d*)/gi
    };

    const text = document.body.innerText;

    Object.entries(patterns).forEach(([name, pattern]) => {
        const matches = text.match(pattern);
        if (matches) {
            console.log(`${name} patterns found:`, matches.slice(0, 5));
        }
    });
}