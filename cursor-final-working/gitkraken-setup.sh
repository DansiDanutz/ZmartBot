#!/bin/bash

# GitKraken Setup Script
# This creates a global command for GitKraken

echo "🐙 Setting up GitKraken command-line access..."

# Create symbolic link for command-line access
if [ ! -f /usr/local/bin/gitkraken ]; then
    echo "Creating gitkraken command..."
    sudo ln -s /Applications/GitKraken.app/Contents/MacOS/GitKraken /usr/local/bin/gitkraken
    echo "✅ GitKraken command created"
else
    echo "✅ GitKraken command already exists"
fi

# Add alias to shell profile
SHELL_PROFILE=""
if [ -f ~/.zshrc ]; then
    SHELL_PROFILE=~/.zshrc
elif [ -f ~/.bash_profile ]; then
    SHELL_PROFILE=~/.bash_profile
else
    SHELL_PROFILE=~/.profile
fi

# Add GitKraken alias if not already present
if ! grep -q "alias gk=" "$SHELL_PROFILE"; then
    echo "" >> "$SHELL_PROFILE"
    echo "# GitKraken aliases" >> "$SHELL_PROFILE"
    echo "alias gk='open -a GitKraken .'" >> "$SHELL_PROFILE"
    echo "alias gitkraken='open -a GitKraken'" >> "$SHELL_PROFILE"
    echo "✅ GitKraken aliases added to $SHELL_PROFILE"
else
    echo "✅ GitKraken aliases already exist"
fi

echo ""
echo "🎉 GitKraken Setup Complete!"
echo ""
echo "📝 Usage:"
echo "  gitkraken          - Open GitKraken"
echo "  gk                 - Open GitKraken in current directory"
echo "  gitkraken <path>   - Open GitKraken with specific repo"
echo ""
echo "🔄 Reload your shell or run:"
echo "  source $SHELL_PROFILE"
echo ""

# Test if GitKraken can be opened
echo "🧪 Testing GitKraken installation..."
if [ -d "/Applications/GitKraken.app" ]; then
    echo "✅ GitKraken is installed at: /Applications/GitKraken.app"
    echo "✅ Version: $(defaults read /Applications/GitKraken.app/Contents/Info.plist CFBundleShortVersionString 2>/dev/null || echo "Unknown")"
else
    echo "❌ GitKraken not found. Please install it first."
fi