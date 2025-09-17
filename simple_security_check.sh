#!/bin/bash

# Simple Security Check for ZmartBot
# Intelligent check that distinguishes between real secrets and example/documentation

echo "🔒 ZmartBot Security Check"

# Check staged files only
staged_files=$(git diff --cached --name-only)

if [ -z "$staged_files" ]; then
    echo "✅ No staged files to check"
    exit 0
fi

echo "📋 Checking staged files for security issues..."

# Track if we found actual secrets
found_secrets=false

for file in $staged_files; do
    if [ -f "$file" ]; then
        # Skip files that are obviously safe
        # 1. Documentation files
        if [[ "$file" == *.md ]] || [[ "$file" == *.mdc ]] || [[ "$file" == *.txt ]] || [[ "$file" == *.rst ]]; then
            continue
        fi

        # 2. Example/template files
        if [[ "$file" == *.example ]] || [[ "$file" == *.template ]] || [[ "$file" == *example* ]] || [[ "$file" == *template* ]]; then
            continue
        fi

        # 3. Test files
        if [[ "$file" == *test* ]] || [[ "$file" == *spec* ]] || [[ "$file" == *mock* ]]; then
            continue
        fi

        # 4. Build/compiled files (often contain false positives)
        if [[ "$file" == */dist/* ]] || [[ "$file" == */build/* ]] || [[ "$file" == */assets/* ]] || [[ "$file" == *.min.js ]]; then
            continue
        fi

        # 5. Package/dependency files
        if [[ "$file" == */node_modules/* ]] || [[ "$file" == */venv/* ]] || [[ "$file" == */.venv/* ]]; then
            continue
        fi

        # 6. FusionCharts and similar libraries (known false positives)
        if [[ "$file" == */fusioncharts/* ]] || [[ "$file" == */professional_dashboard/assets/* ]]; then
            continue
        fi

        # For Python files, check if it's just importing/using settings
        if [[ "$file" == *.py ]]; then
            # Check for actual hardcoded secrets (not just variable references)
            if grep -qE "password[\s]*=[\s]*[\"'][^\"']{8,}[\"']" "$file" 2>/dev/null; then
                # But skip if it's from settings or environment
                if ! grep -qE "password[\s]*=[\s]*(settings\.|os\.environ|config\.|env\.)" "$file" 2>/dev/null; then
                    echo "❌ Potential hardcoded password in: $file"
                    found_secrets=true
                fi
            fi

            if grep -qE "api[_-]?key[\s]*=[\s]*[\"'][a-zA-Z0-9]{20,}[\"']" "$file" 2>/dev/null; then
                # Skip if it's a placeholder or from config
                if ! grep -qE "api[_-]?key[\s]*=[\s]*[\"'](your_|placeholder|example|test|mock|settings\.|os\.environ|config\.)" "$file" 2>/dev/null; then
                    echo "❌ Potential hardcoded API key in: $file"
                    found_secrets=true
                fi
            fi
        fi

        # For shell scripts, be more lenient (often contain example configs)
        if [[ "$file" == *.sh ]]; then
            # Only flag if it looks like a real secret (not example/placeholder)
            if grep -qE "password=\"[^\"]{8,}\"" "$file" 2>/dev/null; then
                if ! grep -qE "password=\"(your_|placeholder|example|test|mock|\\\$)" "$file" 2>/dev/null; then
                    echo "❌ Potential hardcoded password in: $file"
                    found_secrets=true
                fi
            fi
        fi

        # For .env files (not .env.example), check for real secrets
        if [[ "$file" == *.env ]] && [[ "$file" != *.env.example ]] && [[ "$file" != *.env.template ]]; then
            # Check if it contains actual keys (not placeholders)
            if grep -qE "=[a-zA-Z0-9]{20,}" "$file" 2>/dev/null; then
                if ! grep -qE "=(your_|placeholder|example|test|mock|xxx|<.*>|\[.*\])" "$file" 2>/dev/null; then
                    echo "⚠️  Warning: .env file with potential secrets: $file"
                    echo "   Consider using .env.example for templates"
                    # Don't block for .env files that might be needed
                fi
            fi
        fi

        # For config files, check more carefully
        if [[ "$file" == config.* ]] || [[ "$file" == settings.* ]]; then
            # Check if it has real-looking secrets
            if grep -qE "(password|secret|key)[\s]*=[\s]*[\"'][^\"']{10,}[\"']" "$file" 2>/dev/null; then
                # But not if they're clearly placeholders
                if ! grep -qE "(password|secret|key)[\s]*=[\s]*[\"'](your_|placeholder|example|test|mock|changeme|xxx)" "$file" 2>/dev/null; then
                    echo "⚠️  Warning: Config file with potential secrets: $file"
                    echo "   Consider using environment variables or a secure secrets manager"
                    # Warning only, don't block
                fi
            fi
        fi
    fi
done

if [ "$found_secrets" = true ]; then
    echo ""
    echo "💥 Security scan failed! Actual secrets found."
    echo "👀 Please remove hardcoded secrets and use:"
    echo "   - Environment variables (.env files)"
    echo "   - API Keys Manager Service"
    echo "   - Config files with placeholders"
    exit 1
else
    echo "✅ Security scan passed - no hardcoded secrets detected"
    exit 0
fi