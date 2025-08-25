#!/bin/bash

# 🧹 Scoring System Cleanup Script
# This script removes old scattered scoring components and organizes the system

echo "🧹 Starting Scoring System Cleanup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to backup file before deletion
backup_file() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        local backup_path="${file_path}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$file_path" "$backup_path"
        echo -e "${YELLOW}📦 Backed up: $file_path -> $backup_path${NC}"
    fi
}

# Function to safely remove file
safe_remove() {
    local file_path="$1"
    local reason="$2"
    
    if [ -f "$file_path" ]; then
        backup_file "$file_path"
        rm "$file_path"
        echo -e "${GREEN}✅ Removed: $file_path (Reason: $reason)${NC}"
    else
        echo -e "${YELLOW}⚠️ File not found: $file_path${NC}"
    fi
}

echo -e "${BLUE}📋 Cleaning up old scoring components...${NC}"

# Remove old scattered scoring files
echo -e "\n${YELLOW}🗑️ Removing old scoring files:${NC}"

# Old integrated scoring system (replaced by unified)
safe_remove "src/services/integrated_scoring_system.py" "Replaced by unified_scoring_system.py"

# Old scattered scoring routes
safe_remove "src/routes/scoring.py" "Replaced by unified_scoring.py"
safe_remove "src/routes/dynamic_scoring.py" "Functionality merged into unified_scoring.py"
safe_remove "src/routes/calibrated_scoring.py" "Functionality merged into unified_scoring.py"

# Old scoring agents (functionality consolidated)
safe_remove "src/agents/scoring/scoring_agent.py" "Functionality merged into unified_scoring_system.py"
safe_remove "src/agents/scoring/dynamic_scoring_agent.py" "Functionality merged into unified_scoring_system.py"
safe_remove "src/agents/scoring/win_rate_scoring_standard.py" "Functionality merged into unified_scoring_system.py"
safe_remove "src/agents/scoring/pattern_trigger_system.py" "Functionality merged into unified_scoring_system.py"
safe_remove "src/agents/scoring/ai_win_rate_predictor.py" "Functionality merged into unified_scoring_system.py"

# Remove old scoring service files
safe_remove "src/services/scoring_service.py" "Replaced by unified_scoring_system.py"

echo -e "\n${BLUE}📁 Organizing remaining scoring files...${NC}"

# Create backup of the cleanup
echo -e "${GREEN}📦 Creating cleanup backup...${NC}"
tar -czf "scoring_cleanup_backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
    src/services/integrated_scoring_system.py.backup.* \
    src/routes/scoring.py.backup.* \
    src/routes/dynamic_scoring.py.backup.* \
    src/routes/calibrated_scoring.py.backup.* \
    src/agents/scoring/scoring_agent.py.backup.* \
    src/agents/scoring/dynamic_scoring_agent.py.backup.* \
    src/agents/scoring/win_rate_scoring_standard.py.backup.* \
    src/agents/scoring/pattern_trigger_system.py.backup.* \
    src/agents/scoring/ai_win_rate_predictor.py.backup.* \
    src/services/scoring_service.py.backup.* 2>/dev/null || true

echo -e "\n${GREEN}✅ Scoring System Cleanup Complete!${NC}"
echo -e "\n${BLUE}📊 New Unified Scoring System:${NC}"
echo -e "  • ${GREEN}Main Service:${NC} src/services/unified_scoring_system.py"
echo -e "  • ${GREEN}API Routes:${NC} src/routes/unified_scoring.py"
echo -e "  • ${GREEN}Base Weights:${NC} KingFisher 30%, Cryptometer 50%, RiskMetric 20%"
echo -e "  • ${GREEN}Dynamic Weighting:${NC} Based on data quality and market conditions"
echo -e "  • ${GREEN}100-Point Scale:${NC} Unified scoring across all components"
echo -e "\n${BLUE}🔗 API Endpoints:${NC}"
echo -e "  • GET /api/scoring/health - System health"
echo -e "  • GET /api/scoring/score/{symbol} - Get comprehensive score"
echo -e "  • GET /api/scoring/scores/batch - Batch scoring"
echo -e "  • GET /api/scoring/history/{symbol} - Scoring history"
echo -e "  • POST /api/scoring/market-condition - Update market condition"
echo -e "  • POST /api/scoring/reliability - Update reliability scores"
echo -e "  • POST /api/scoring/manual - Manual score calculation"
echo -e "  • GET /api/scoring/statistics - System statistics"
echo -e "\n${YELLOW}💡 Next Steps:${NC}"
echo -e "  1. Test the new unified scoring system"
echo -e "  2. Update any frontend code to use new endpoints"
echo -e "  3. Monitor system performance and adjust weights as needed"
echo -e "  4. Remove backup files after confirming everything works"
