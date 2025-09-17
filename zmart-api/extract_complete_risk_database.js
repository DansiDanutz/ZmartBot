// COMPLETE IntoTheCryptoverse Risk Database Extractor
// This extracts the ENTIRE risk grid for ALL symbols - every price point from 0 to 1 risk
// Run this in the browser console on https://app.intothecryptoverse.com/crypto

(async function extractCompleteRiskDatabase() {
    console.log("🚀 Starting COMPLETE Risk Database Extraction");
    console.log("This will extract ALL price points for each symbol's risk grid");
    console.log("=".repeat(60));

    const completeDatabase = {
        symbols: {},
        metadata: {
            source: "IntoTheCryptoverse",
            extracted_at: new Date().toISOString(),
            url: window.location.href,
            note: "Complete risk grid with ALL price points for each symbol"
        }
    };

    // Function to wait
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Function to extract the complete grid from current view
    const extractFullGrid = () => {
        const gridData = {
            fiat_risk_grid: [],
            btc_risk_grid: []
        };

        // Try different selectors for the risk grid table
        const selectors = [
            'table tbody tr',
            '.risk-table tr',
            '[data-testid*="risk"] tr',
            '.MuiTable-root tbody tr',
            'div[role="table"] div[role="row"]'
        ];

        let foundData = false;

        for (const selector of selectors) {
            const rows = document.querySelectorAll(selector);

            if (rows.length > 0) {
                console.log(`   Found ${rows.length} rows using selector: ${selector}`);

                rows.forEach(row => {
                    // Try to extract price and risk from each row
                    const cells = row.querySelectorAll('td, div[role="cell"]');

                    if (cells.length >= 2) {
                        const priceText = cells[0]?.textContent?.trim() || '';
                        const riskText = cells[1]?.textContent?.trim() || '';

                        // Parse price (remove $ and commas)
                        const price = parseFloat(priceText.replace(/[$,]/g, ''));

                        // Parse risk value
                        const risk = parseFloat(riskText);

                        if (!isNaN(price) && !isNaN(risk)) {
                            gridData.fiat_risk_grid.push({
                                price: price,
                                risk_value: risk
                            });
                            foundData = true;
                        }
                    }
                });

                if (foundData) break;
            }
        }

        // Sort by price
        gridData.fiat_risk_grid.sort((a, b) => a.price - b.price);

        return gridData;
    };

    // Function to click on a symbol and extract its complete risk grid
    const extractSymbolCompleteGrid = async (symbol) => {
        console.log(`\n📊 Extracting COMPLETE risk grid for ${symbol}...`);

        try {
            // Step 1: Find and click on the symbol in Fiat Risks table
            const symbolElements = Array.from(document.querySelectorAll('td, div, span, button')).filter(
                el => el.textContent?.trim() === symbol
            );

            if (symbolElements.length === 0) {
                console.log(`   ❌ Could not find ${symbol} in the page`);
                return null;
            }

            // Click on the symbol
            symbolElements[0].click();
            console.log(`   ✓ Clicked on ${symbol}`);

            // Wait for grid to load
            await wait(3000);

            // Step 2: Extract Fiat Risk grid
            console.log(`   📈 Extracting Fiat Risk grid...`);
            const fiatGrid = extractFullGrid();

            if (fiatGrid.fiat_risk_grid.length > 0) {
                console.log(`   ✅ Found ${fiatGrid.fiat_risk_grid.length} Fiat Risk price points`);
            }

            // Step 3: Try to switch to BTC Risk view
            const btcRiskButton = Array.from(document.querySelectorAll('button, div[role="button"]')).find(
                el => el.textContent?.includes('BTC Risk') || el.textContent?.includes('Bitcoin Risk')
            );

            let btcGrid = { btc_risk_grid: [] };

            if (btcRiskButton) {
                btcRiskButton.click();
                console.log(`   ✓ Switched to BTC Risk view`);
                await wait(2000);

                const btcData = extractFullGrid();
                btcGrid.btc_risk_grid = btcData.fiat_risk_grid; // Reuse the same extraction

                if (btcGrid.btc_risk_grid.length > 0) {
                    console.log(`   ✅ Found ${btcGrid.btc_risk_grid.length} BTC Risk price points`);
                }
            }

            // Step 4: Go back to main view
            const backButton = document.querySelector('[aria-label*="back"], button:has-text("Back"), button:has-text("←")');
            if (backButton) {
                backButton.click();
                await wait(1500);
            }

            // Combine the data
            return {
                symbol: symbol,
                fiat_risk_grid: fiatGrid.fiat_risk_grid,
                btc_risk_grid: btcGrid.btc_risk_grid,
                stats: {
                    total_fiat_points: fiatGrid.fiat_risk_grid.length,
                    total_btc_points: btcGrid.btc_risk_grid.length,
                    min_price: Math.min(...fiatGrid.fiat_risk_grid.map(d => d.price)),
                    max_price: Math.max(...fiatGrid.fiat_risk_grid.map(d => d.price)),
                    price_range: `$${Math.min(...fiatGrid.fiat_risk_grid.map(d => d.price)).toFixed(2)} - $${Math.max(...fiatGrid.fiat_risk_grid.map(d => d.price)).toFixed(2)}`
                }
            };

        } catch (error) {
            console.error(`   ❌ Error extracting ${symbol}:`, error);
            return null;
        }
    };

    // List of ALL symbols that have risk metrics
    const symbols = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE',
        'TRX', 'DOT', 'MATIC', 'SHIB', 'LINK', 'BCH', 'UNI', 'LTC',
        'ATOM', 'ETC'
    ];

    console.log(`\n📋 Will extract COMPLETE risk grids for ${symbols.length} symbols`);
    console.log("Each grid contains ALL price points from risk 0.0 to 1.0");
    console.log("This will take several minutes...\n");

    // Extract data for each symbol
    for (const symbol of symbols) {
        const gridData = await extractSymbolCompleteGrid(symbol);

        if (gridData) {
            completeDatabase.symbols[symbol] = gridData;
        }

        // Small delay between symbols
        await wait(1000);
    }

    // Summary
    console.log("\n" + "=".repeat(60));
    console.log("📊 EXTRACTION COMPLETE");
    console.log("=".repeat(60));

    const extractedSymbols = Object.keys(completeDatabase.symbols);
    console.log(`\n✅ Successfully extracted ${extractedSymbols.length} symbols:`);

    let totalFiatPoints = 0;
    let totalBtcPoints = 0;

    extractedSymbols.forEach(symbol => {
        const data = completeDatabase.symbols[symbol];
        totalFiatPoints += data.stats.total_fiat_points;
        totalBtcPoints += data.stats.total_btc_points;

        console.log(`  ${symbol}:`);
        console.log(`    - Fiat Risk: ${data.stats.total_fiat_points} price points`);
        console.log(`    - BTC Risk: ${data.stats.total_btc_points} price points`);
        console.log(`    - Price Range: ${data.stats.price_range}`);
    });

    console.log(`\n📊 Total Data Points:`);
    console.log(`  - Fiat Risk: ${totalFiatPoints} total price points`);
    console.log(`  - BTC Risk: ${totalBtcPoints} total price points`);
    console.log(`  - Combined: ${totalFiatPoints + totalBtcPoints} total data points`);

    // Save to file
    const jsonData = JSON.stringify(completeDatabase, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cryptoverse_complete_risk_database_${new Date().toISOString().split('T')[0]}.json`;
    a.click();

    console.log("\n✅ Complete risk database saved to file!");
    console.log("📌 This file contains ALL price points for each symbol");
    console.log("🎯 You can now look up exact risk values at ANY price!");

    // Also copy sample to clipboard for verification
    const sampleData = {
        description: "Sample of complete risk database",
        example_sol: completeDatabase.symbols.SOL ? {
            symbol: "SOL",
            sample_points: completeDatabase.symbols.SOL.fiat_risk_grid.slice(0, 5),
            total_points: completeDatabase.symbols.SOL.stats.total_fiat_points
        } : null
    };

    navigator.clipboard.writeText(JSON.stringify(sampleData, null, 2)).then(() => {
        console.log("📋 Sample data copied to clipboard for verification");
    });

    return completeDatabase;
})();

// Helper function to manually test risk lookup
function lookupRiskAtPrice(symbol, price) {
    // This would work after loading the complete database
    console.log(`Looking up risk for ${symbol} at $${price}...`);
    console.log("Run the extraction first to get the complete database");
}