#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('MCP Server Connection Test');
console.log('===========================\n');

const configPath = path.join(__dirname, 'claude_desktop_config.json');

try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const servers = config.mcpServers;

    console.log(`Found ${Object.keys(servers).length} MCP servers in configuration:\n`);

    const testServer = (name, serverConfig) => {
        return new Promise((resolve) => {
            console.log(`Testing: ${name}`);
            console.log(`Command: ${serverConfig.command} ${(serverConfig.args || []).join(' ')}`);

            const timeout = setTimeout(() => {
                console.log(`⏱️  ${name}: Timeout - Server took too long to respond`);
                resolve({ name, status: 'timeout' });
            }, 5000);

            try {
                const childProcess = spawn(serverConfig.command, serverConfig.args || [], {
                    env: { ...process.env, ...serverConfig.env },
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                let output = '';
                let errorOutput = '';

                childProcess.stdout.on('data', (data) => {
                    output += data.toString();
                });

                childProcess.stderr.on('data', (data) => {
                    errorOutput += data.toString();
                });

                setTimeout(() => {
                    if (childProcess.pid) {
                        childProcess.stdin.write(JSON.stringify({
                            jsonrpc: "2.0",
                            method: "initialize",
                            params: {
                                protocolVersion: "1.0",
                                capabilities: {}
                            },
                            id: 1
                        }) + '\n');
                    }
                }, 100);

                setTimeout(() => {
                    clearTimeout(timeout);
                    if (childProcess.pid) {
                        childProcess.kill();
                        if (output || errorOutput.includes('MCP')) {
                            console.log(`✅ ${name}: Server responds correctly`);
                            resolve({ name, status: 'working' });
                        } else if (errorOutput.includes('not found') || errorOutput.includes('command not found')) {
                            console.log(`❌ ${name}: Command not found - needs installation`);
                            resolve({ name, status: 'not_installed' });
                        } else {
                            console.log(`⚠️  ${name}: Server started but response unclear`);
                            resolve({ name, status: 'unclear' });
                        }
                    }
                }, 2000);

                childProcess.on('error', (err) => {
                    clearTimeout(timeout);
                    if (err.code === 'ENOENT') {
                        console.log(`❌ ${name}: Command not found - ${serverConfig.command}`);
                        resolve({ name, status: 'not_installed' });
                    } else {
                        console.log(`❌ ${name}: Error - ${err.message}`);
                        resolve({ name, status: 'error', error: err.message });
                    }
                });

            } catch (err) {
                clearTimeout(timeout);
                console.log(`❌ ${name}: Failed to test - ${err.message}`);
                resolve({ name, status: 'error', error: err.message });
            }

            console.log('');
        });
    };

    const runTests = async () => {
        const results = [];

        for (const [name, config] of Object.entries(servers)) {
            const result = await testServer(name, config);
            results.push(result);
        }

        console.log('\n\nTest Summary:');
        console.log('=============');

        const working = results.filter(r => r.status === 'working');
        const notInstalled = results.filter(r => r.status === 'not_installed');
        const errors = results.filter(r => r.status === 'error' || r.status === 'unclear' || r.status === 'timeout');

        console.log(`✅ Working: ${working.length}`);
        working.forEach(r => console.log(`   - ${r.name}`));

        if (notInstalled.length > 0) {
            console.log(`\n❌ Not Installed: ${notInstalled.length}`);
            notInstalled.forEach(r => console.log(`   - ${r.name}`));
            console.log('\n   Run: ./install-mcp-servers.sh to install missing servers');
        }

        if (errors.length > 0) {
            console.log(`\n⚠️  Issues: ${errors.length}`);
            errors.forEach(r => console.log(`   - ${r.name}: ${r.status}`));
        }

        console.log('\n\nNext Steps:');
        console.log('===========');
        console.log('1. If any servers are not installed, run: ./install-mcp-servers.sh');
        console.log('2. Restart Claude Desktop application');
        console.log('3. Check MCP status in Claude Desktop settings');
    };

    runTests();

} catch (err) {
    console.error('Error reading config file:', err.message);
    console.error('Make sure claude_desktop_config.json exists in the current directory');
}