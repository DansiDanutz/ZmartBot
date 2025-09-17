// Complete IntoTheCryptoverse Risk Grid Extractor
// This script extracts the FULL risk database for each symbol
// Run this in the browser console on https://app.intothecryptoverse.com/crypto

(async function extractCompleteRiskGrid() {
    console.log("🚀 Starting COMPLETE risk grid extraction...");
    console.log("This will click on each symbol to get the full risk database");

    const completeRiskData = {
        symbols: {},
        metadata: {
            source: "IntoTheCryptoverse",
            extracted_at: new Date().toISOString(),
            url: window.location.href
        }
    };

    // Function to wait
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Function to extract data from current view
    const extractCurrentData = () => {
        const data = [];

        // Look for all tables
        const tables = document.querySelectorAll('table');

        tables.forEach(table => {
            const rows = table.querySelectorAll('tr');

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 2) {
                    const priceText = cells[0]?.textContent || '';
                    const riskText = cells[1]?.textContent || '';

                    // Parse price (remove $ and commas)
                    const price = parseFloat(priceText.replace(/[$,]/g, ''));

                    // Parse risk value
                    const risk = parseFloat(riskText);

                    if (!isNaN(price) && !isNaN(risk)) {
                        data.push({
                            price: price,
                            risk_value: risk
                        });
                    }
                }
            });
        });

        return data;
    };

    // Function to click on a symbol and extract its full risk grid
    const extractSymbolGrid = async (symbol) => {
        console.log(`\n📊 Extracting risk grid for ${symbol}...`);

        // Find and click the symbol in the Fiat Risks table
        const symbolElements = Array.from(document.querySelectorAll('td, div, span')).filter(
            el => el.textContent.trim() === symbol
        );

        if (symbolElements.length > 0) {
            // Click on the symbol
            symbolElements[0].click();

            // Wait for data to load
            await wait(2000);

            // Extract the risk grid data
            const gridData = extractCurrentData();

            if (gridData.length > 0) {
                console.log(`   ✅ Found ${gridData.length} price points for ${symbol}`);
                completeRiskData.symbols[symbol] = {
                    grid: gridData,
                    count: gridData.length,
                    min_price: Math.min(...gridData.map(d => d.price)),
                    max_price: Math.max(...gridData.map(d => d.price)),
                    min_risk: Math.min(...gridData.map(d => d.risk_value)),
                    max_risk: Math.max(...gridData.map(d => d.risk_value))
                };
            } else {
                console.log(`   ⚠️ No grid data found for ${symbol}`);
            }

            // Go back to main view
            const backButton = document.querySelector('[aria-label*="back"], button:has-text("Back"), button:has-text("←")');
            if (backButton) {
                backButton.click();
                await wait(1000);
            }
        } else {
            console.log(`   ❌ Could not find ${symbol} in the table`);
        }
    };

    // List of symbols to extract (from Fiat Risks table)
    const symbols = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE',
        'TRX', 'DOT', 'MATIC', 'SHIB', 'LINK', 'BCH', 'UNI', 'LTC',
        'ATOM', 'ETC', 'XLM', 'ICP', 'FIL', 'HBAR', 'CRO', 'MKR',
        'RNDR', 'XMR', 'ARB', 'VET', 'AAVE', 'QNT', 'OP', 'ALGO',
        'FTM', 'EGLD', 'XTZ', 'SAND', 'MANA', 'AXS', 'APE', 'GALA',
        'CHZ', 'STX'
    ];

    // Extract data for each symbol
    console.log(`\n📋 Will extract risk grids for ${symbols.length} symbols`);
    console.log("This may take a few minutes...\n");

    for (const symbol of symbols.slice(0, 5)) { // Start with first 5 for testing
        await extractSymbolGrid(symbol);
    }

    // Summary
    console.log("\n" + "=".repeat(60));
    console.log("📊 EXTRACTION COMPLETE");
    console.log("=".repeat(60));

    const extractedSymbols = Object.keys(completeRiskData.symbols);
    console.log(`Extracted ${extractedSymbols.length} symbol grids:`);

    extractedSymbols.forEach(symbol => {
        const data = completeRiskData.symbols[symbol];
        console.log(`  ${symbol}: ${data.count} price points (${data.min_price.toFixed(2)} - ${data.max_price.toFixed(2)})`);
    });

    // Save to file
    const jsonData = JSON.stringify(completeRiskData, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cryptoverse_complete_risk_grid.json';
    a.click();

    console.log("\n✅ Data saved to cryptoverse_complete_risk_grid.json");
    console.log("📌 Use this file to sync all risk grids to your database");

    // Also copy to clipboard
    navigator.clipboard.writeText(jsonData).then(() => {
        console.log("📋 Data also copied to clipboard!");
    });

    return completeRiskData;
})();

// Manual extraction helper for a single symbol
function extractSingleSymbolGrid(symbol) {
    console.log(`Extracting grid for ${symbol}...`);
    console.log("1. Click on", symbol, "in the Fiat Risks table");
    console.log("2. Wait for the grid to load");
    console.log("3. Run: extractVisibleGrid()");
}

// Extract the currently visible grid
function extractVisibleGrid() {
    const grid = [];
    const tables = document.querySelectorAll('table');

    tables.forEach(table => {
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                const price = parseFloat(cells[0].textContent.replace(/[$,]/g, ''));
                const risk = parseFloat(cells[1].textContent);
                if (!isNaN(price) && !isNaN(risk)) {
                    grid.push({ price, risk_value: risk });
                }
            }
        });
    });

    console.table(grid);
    console.log(`Found ${grid.length} price points`);

    // Copy to clipboard
    const jsonData = JSON.stringify(grid, null, 2);
    navigator.clipboard.writeText(jsonData);
    console.log("✅ Grid data copied to clipboard!");

    return grid;
}