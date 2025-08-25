# GitHub Repository Security Audit & Cleanup Guide

## ⚠️ Important: Manual Steps Required

Since I cannot directly access your GitHub account, you'll need to:

1. **List your repositories** manually
2. **Clone each repository** locally
3. **Run the security audit** on each one
4. **Clean and re-push** if needed

## Step 1: Get List of All Your Repositories

### Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI if you haven't
brew install gh  # macOS
# or visit: https://cli.github.com/

# Authenticate
gh auth login

# List all your repositories
gh repo list DansiDanutz --limit 100 --json name,visibility,url > my_repos.json

# View the list
cat my_repos.json | jq '.'
```

### Using Git Command
```bash
# Clone all your repositories
curl -s "https://api.github.com/users/DansiDanutz/repos?per_page=100" | \
  grep -o 'git@[^"]*' | \
  xargs -L1 git clone
```

## Step 2: Create Security Scanner Script

Save this as `scan_secrets.sh`:

```bash
#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Scanning for exposed secrets in repositories..."
echo "================================================"

# Patterns to search for
PATTERNS=(
    # API Keys
    "api_key.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    "apikey.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    "API_KEY.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    
    # Secrets
    "secret.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    "SECRET.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    
    # Tokens
    "token.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    "TOKEN.*=.*[\"'][a-zA-Z0-9]{20,}[\"']"
    
    # Specific service patterns
    "sk-[a-zA-Z0-9]{48}"  # OpenAI
    "ghp_[a-zA-Z0-9]{36}"  # GitHub Personal Access Token
    "ghs_[a-zA-Z0-9]{36}"  # GitHub Secret
    "AKIA[0-9A-Z]{16}"     # AWS Access Key
    
    # Passwords
    "password.*=.*[\"'][^\"']{8,}[\"']"
    "PASSWORD.*=.*[\"'][^\"']{8,}[\"']"
    "passphrase.*=.*[\"'][^\"']{8,}[\"']"
)

# Function to scan a repository
scan_repo() {
    local repo_path=$1
    local repo_name=$(basename "$repo_path")
    
    echo -e "\n${YELLOW}Scanning: $repo_name${NC}"
    echo "------------------------"
    
    local found_issues=false
    
    # Skip if not a git repository
    if [ ! -d "$repo_path/.git" ]; then
        echo -e "${RED}⚠️  Not a git repository${NC}"
        return
    fi
    
    cd "$repo_path" || return
    
    # Check each pattern
    for pattern in "${PATTERNS[@]}"; do
        # Search in current files
        results=$(grep -r -E "$pattern" --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude="*.env" . 2>/dev/null)
        
        if [ ! -z "$results" ]; then
            echo -e "${RED}🚨 Found potential secrets matching pattern: $pattern${NC}"
            echo "$results" | head -5
            found_issues=true
        fi
        
        # Search in git history
        git_results=$(git grep -E "$pattern" $(git rev-list --all) 2>/dev/null | head -5)
        
        if [ ! -z "$git_results" ]; then
            echo -e "${RED}🚨 Found secrets in git history matching: $pattern${NC}"
            found_issues=true
        fi
    done
    
    # Check for .env files in git
    env_tracked=$(git ls-files | grep -E "\.env$|\.env\.")
    if [ ! -z "$env_tracked" ]; then
        echo -e "${RED}🚨 .env files tracked in git:${NC}"
        echo "$env_tracked"
        found_issues=true
    fi
    
    # Check .gitignore
    if [ ! -f ".gitignore" ]; then
        echo -e "${YELLOW}⚠️  No .gitignore file found${NC}"
        found_issues=true
    elif ! grep -q "\.env" .gitignore; then
        echo -e "${YELLOW}⚠️  .gitignore doesn't exclude .env files${NC}"
        found_issues=true
    fi
    
    if [ "$found_issues" = false ]; then
        echo -e "${GREEN}✅ No secrets found${NC}"
    else
        echo -e "${RED}❌ Security issues found - needs cleanup${NC}"
        echo "$repo_path" >> ../repos_to_clean.txt
    fi
}

# Main execution
rm -f repos_to_clean.txt
touch repos_to_clean.txt

# Scan all directories in current folder
for dir in */; do
    if [ -d "$dir" ]; then
        scan_repo "$dir"
    fi
done

echo -e "\n================================================"
echo -e "${YELLOW}📋 Summary:${NC}"
echo -e "Repositories that need cleaning:"
cat repos_to_clean.txt 2>/dev/null || echo "None found!"
```

Make it executable:
```bash
chmod +x scan_secrets.sh
```

## Step 3: Create Cleanup Script

Save this as `clean_repo.sh`:

```bash
#!/bin/bash

# Function to clean a repository
clean_repository() {
    local repo_path=$1
    local repo_name=$(basename "$repo_path")
    
    echo "🧹 Cleaning repository: $repo_name"
    cd "$repo_path" || exit
    
    # Backup current state
    echo "📦 Creating backup..."
    tar -czf "../${repo_name}_backup_$(date +%Y%m%d_%H%M%S).tar.gz" . \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='__pycache__'
    
    # Remove sensitive files from tracking
    echo "🔒 Removing sensitive files from git..."
    git rm --cached .env 2>/dev/null
    git rm --cached .env.* 2>/dev/null
    git rm --cached *_credentials.json 2>/dev/null
    git rm --cached *_api_keys.json 2>/dev/null
    
    # Update .gitignore
    echo "📝 Updating .gitignore..."
    if [ ! -f .gitignore ]; then
        touch .gitignore
    fi
    
    # Add security entries to .gitignore
    cat >> .gitignore << 'EOF'

# Security - Never commit these
.env
.env.*
!.env.example
*.pem
*.key
*.crt
*_credentials.json
*_api_keys.json
secrets.json
config.local.py
EOF
    
    # Create .env.example if it doesn't exist
    if [ -f .env ] && [ ! -f .env.example ]; then
        echo "📄 Creating .env.example..."
        sed 's/=.*/=/' .env > .env.example
    fi
    
    # Commit changes
    echo "💾 Committing security fixes..."
    git add .gitignore
    git add .env.example 2>/dev/null
    git commit -m "🔒 Security: Remove sensitive data and update .gitignore
    
    - Removed tracked .env files
    - Updated .gitignore to prevent future exposure
    - Added .env.example template
    - Security audit cleanup"
    
    echo "✅ Repository cleaned: $repo_name"
    echo "⚠️  Remember to:"
    echo "   1. Review the changes: git diff HEAD~1"
    echo "   2. Consider cleaning git history if secrets were exposed"
    echo "   3. Rotate any exposed API keys"
    echo ""
}

# Process repository passed as argument
if [ $# -eq 0 ]; then
    echo "Usage: ./clean_repo.sh <repository_path>"
    exit 1
fi

clean_repository "$1"
```

Make it executable:
```bash
chmod +x clean_repo.sh
```

## Step 4: Batch Process All Repositories

Save this as `secure_all_repos.sh`:

```bash
#!/bin/bash

echo "🔐 GitHub Repository Security Audit & Cleanup"
echo "============================================="

# Create workspace
WORKSPACE="github_security_audit_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# Get all repositories
echo "📥 Fetching repository list..."
gh repo list DansiDanutz --limit 100 --json name,visibility,url,sshUrl > repos.json

# Clone all repositories
echo "📦 Cloning repositories..."
cat repos.json | jq -r '.[].sshUrl' | while read repo_url; do
    git clone "$repo_url" 2>/dev/null
done

# Run security scan
echo "🔍 Running security scan..."
../scan_secrets.sh

# Show results
echo -e "\n📊 Scan Results:"
if [ -f repos_to_clean.txt ] && [ -s repos_to_clean.txt ]; then
    echo "Repositories needing cleanup:"
    cat repos_to_clean.txt
    
    echo -e "\n🤔 Do you want to clean these repositories? (y/n)"
    read -r response
    
    if [ "$response" = "y" ]; then
        while IFS= read -r repo; do
            ../clean_repo.sh "$repo"
        done < repos_to_clean.txt
        
        echo -e "\n✅ All repositories cleaned!"
        echo "📌 Next steps for each repository:"
        echo "   1. cd into each repository"
        echo "   2. Review changes: git log -1 -p"
        echo "   3. Push changes: git push"
        echo "   4. Consider using BFG Repo-Cleaner for history cleanup"
    fi
else
    echo "✅ No security issues found in any repository!"
fi
```

## Step 5: Clean Git History (For Repositories with Exposed Secrets)

For repositories with secrets in history, use BFG Repo-Cleaner:

```bash
# Install BFG
brew install bfg  # macOS

# Create a file with patterns to remove
cat > secrets.txt << 'EOF'
api_key*
*secret*
*token*
*password*
*.env
EOF

# Clean repository history
bfg --replace-text secrets.txt <repository>

# Force push cleaned history
cd <repository>
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

## Step 6: Set Up Pre-commit Hooks

Install pre-commit hooks to prevent future accidents:

```bash
# Install pre-commit
pip install pre-commit

# In each repository, create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: .*/tests/.*|.*/test/.*
EOF

# Install the hook
pre-commit install

# Create baseline
detect-secrets scan > .secrets.baseline
```

## Manual Checklist for Each Repository

After running the scripts, manually verify each repository:

- [ ] No API keys in source files
- [ ] No passwords in configuration
- [ ] .env files are not tracked
- [ ] .gitignore includes sensitive patterns
- [ ] .env.example exists as template
- [ ] README doesn't contain credentials
- [ ] Config files use environment variables
- [ ] No credentials in commit messages
- [ ] Pre-commit hooks installed
- [ ] API keys rotated if exposed

## Emergency: If Secrets Are Already Public

If secrets are already exposed on public GitHub:

1. **Immediately rotate all credentials**
2. **Delete the repository** if contains critical secrets
3. **Use BFG to clean history**
4. **Force push cleaned version**
5. **Contact GitHub Support** to purge cached views

## Preventive Measures

1. **Use GitHub Secrets** for Actions
2. **Enable Secret Scanning** in repository settings
3. **Use environment variables** always
4. **Review PRs carefully** before merging
5. **Set up branch protection** rules

---

**Remember**: Once a secret is exposed on GitHub, consider it compromised and rotate it immediately!