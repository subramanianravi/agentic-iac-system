#!/bin/bash

echo "🗄️ Agentic AI IaC Cache Management"
echo "=================================="

COMMAND=${1:-"info"}
CACHE_PREFIX="agentic-iac"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to get directory size safely
get_dir_size() {
    local dir="$1"
    if [ -d "$dir" ]; then
        du -sh "$dir" 2>/dev/null | cut -f1
    else
        echo "Not found"
    fi
}

# Function to count files in directory
count_files() {
    local dir="$1"
    if [ -d "$dir" ]; then
        find "$dir" -type f 2>/dev/null | wc -l | xargs echo
    else
        echo "0"
    fi
}

case $COMMAND in
    "clear")
        log_info "Clearing all local caches..."
        
        # Python caches
        log_info "Clearing Python caches..."
        rm -rf ~/.cache/pip
        rm -rf ~/.local/lib/python*/site-packages/agentic*
        rm -rf .pytest_cache
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
        find . -name "*.pyc" -delete 2>/dev/null
        find . -name "*.pyo" -delete 2>/dev/null
        
        # Node.js caches
        log_info "Clearing Node.js caches..."
        rm -rf ~/.npm
        rm -rf ~/.yarn/cache
        rm -rf ~/.pnpm-store
        rm -rf node_modules
        
        # Build artifacts
        log_info "Clearing build artifacts..."
        rm -rf build/
        rm -rf dist/
        rm -rf *.egg-info/
        
        # Demo artifacts
        log_info "Clearing demo artifacts..."
        rm -rf demo-apps/
        rm -rf demo-summary-*.json
        rm -rf deployment-analysis.json
        rm -rf provisioning-results.json
        rm -rf deployment-results-*.json
        rm -rf dr-validation-results.json
        
        # Test artifacts
        log_info "Clearing test artifacts..."
        rm -rf test-reports/
        rm -rf .coverage
        rm -rf htmlcov/
        rm -rf .tox/
        
        # Logs
        log_info "Clearing logs..."
        rm -rf logs/*
        rm -rf *.log
        
        # Temporary files
        log_info "Clearing temporary files..."
        rm -rf temp/
        rm -rf tmp/
        rm -rf .tmp/
        rm -rf artifacts/
        
        log_success "All local caches cleared successfully"
        ;;
        
    "info")
        log_info "Cache Information Report"
        echo ""
        
        echo "📊 Python Caches:"
        echo "  pip cache: $(get_dir_size ~/.cache/pip)"
        echo "  site-packages: $(get_dir_size ~/.local/lib/python*/site-packages)"
        echo "  pytest cache: $(get_dir_size .pytest_cache)"
        echo "  __pycache__ dirs: $(find . -name "__pycache__" -type d 2>/dev/null | wc -l)"
        echo ""
        
        echo "📦 Node.js Caches:"
        echo "  npm cache: $(get_dir_size ~/.npm)"
        echo "  yarn cache: $(get_dir_size ~/.yarn/cache)"
        echo "  pnpm store: $(get_dir_size ~/.pnpm-store)"
        echo "  node_modules: $(get_dir_size node_modules)"
        echo ""
        
        echo "🏗️ Build Artifacts:"
        echo "  build/: $(get_dir_size build)"
        echo "  dist/: $(get_dir_size dist)"
        echo "  *.egg-info: $(find . -name "*.egg-info" -type d 2>/dev/null | wc -l) directories"
        echo ""
        
        echo "🎯 Demo Artifacts:"
        echo "  demo-apps/: $(get_dir_size demo-apps)"
        echo "  demo summaries: $(count_files . | grep demo-summary 2>/dev/null || echo 0) files"
        echo "  analysis files: $(ls deployment-analysis*.json 2>/dev/null | wc -l) files"
        echo ""
        
        echo "🧪 Test Artifacts:"
        echo "  test-reports/: $(get_dir_size test-reports)"
        echo "  coverage data: $(get_dir_size htmlcov)"
        echo "  .coverage file: $([ -f .coverage ] && echo "Present" || echo "Not found")"
        echo ""
        
        echo "📝 Logs:"
        echo "  logs/: $(get_dir_size logs)"
        echo "  log files: $(find . -name "*.log" -type f 2>/dev/null | wc -l) files"
        echo ""
        
        echo "💾 Total Project Size:"
        echo "  Project root: $(get_dir_size .)"
        ;;
        
    "prepare")
        log_info "Preparing cache directories and environment..."
        
        # Create cache directories
        mkdir -p ~/.cache/pip
        mkdir -p ~/.local/lib/python3.11/site-packages
        mkdir -p ~/.npm
        mkdir -p logs
        mkdir -p temp
        mkdir -p results
        mkdir -p artifacts
        mkdir -p test-reports
        
        # Set proper permissions
        chmod 755 ~/.cache/pip 2>/dev/null
        chmod 755 logs temp results artifacts test-reports
        
        # Create configuration directories
        mkdir -p ~/.agentic-iac
        
        # Copy default configuration if available
        if [ -f "${PROJECT_ROOT}/config/agentic-config.yaml" ]; then
            cp "${PROJECT_ROOT}/config/agentic-config.yaml" ~/.agentic-iac/
            log_success "Configuration copied to ~/.agentic-iac/"
        fi
        
        # Make scripts executable
        find "${PROJECT_ROOT}/scripts" -name "*.sh" -exec chmod +x {} \; 2>/dev/null
        chmod +x "${PROJECT_ROOT}/agentic-iac" 2>/dev/null
        chmod +x "${PROJECT_ROOT}/demo-runner" 2>/dev/null
        
        log_success "Cache directories and environment prepared"
        ;;
        
    "optimize")
        log_info "Optimizing cache performance..."
        
        # Clean old Python cache files
        find ~/.cache/pip -name "*.whl" -mtime +30 -delete 2>/dev/null
        find ~/.cache/pip -type d -empty -delete 2>/dev/null
        
        # Clean old demo applications
        find demo-apps -name "*.git" -type d -exec rm -rf {} \; 2>/dev/null
        
        # Compress old logs
        find logs -name "*.log" -mtime +7 -exec gzip {} \; 2>/dev/null
        
        # Clean old test reports
        find test-reports -name "*.xml" -mtime +14 -delete 2>/dev/null
        find test-reports -name "*.json" -mtime +14 -delete 2>/dev/null
        
        log_success "Cache optimization completed"
        ;;
        
    "validate")
        log_info "Validating cache health..."
        
        ISSUES=0
        
        # Check Python cache
        if [ ! -d ~/.cache/pip ]; then
            log_warning "Python pip cache directory missing"
            ISSUES=$((ISSUES + 1))
        fi
        
        # Check permissions
        if [ ! -w ~/.cache/pip ]; then
            log_warning "Python cache directory not writable"
            ISSUES=$((ISSUES + 1))
        fi
        
        # Check disk space
        AVAILABLE_SPACE=$(df ~/.cache 2>/dev/null | tail -1 | awk '{print $4}')
        if [ "$AVAILABLE_SPACE" -lt 1000000 ]; then  # Less than 1GB
            log_warning "Low disk space in cache directory"
            ISSUES=$((ISSUES + 1))
        fi
        
        # Check project structure
        if [ ! -f "${PROJECT_ROOT}/requirements.txt" ]; then
            log_warning "requirements.txt not found"
            ISSUES=$((ISSUES + 1))
        fi
        
        if [ ! -d "${PROJECT_ROOT}/src" ]; then
            log_warning "src/ directory not found"
            ISSUES=$((ISSUES + 1))
        fi
        
        if [ $ISSUES -eq 0 ]; then
            log_success "Cache validation passed - no issues found"
        else
            log_warning "Cache validation completed with $ISSUES issues"
        fi
        
        return $ISSUES
        ;;
        
    "backup")
        log_info "Creating cache backup..."
        
        BACKUP_DIR="cache-backup-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup important cache data
        if [ -d ~/.cache/pip ]; then
            cp -r ~/.cache/pip "$BACKUP_DIR/pip-cache"
        fi
        
        if [ -d ~/.agentic-iac ]; then
            cp -r ~/.agentic-iac "$BACKUP_DIR/agentic-config"
        fi
        
        # Backup project artifacts
        if [ -f deployment-analysis.json ]; then
            cp deployment-analysis.json "$BACKUP_DIR/"
        fi
        
        if [ -d test-reports ]; then
            cp -r test-reports "$BACKUP_DIR/"
        fi
        
        # Create backup manifest
        cat > "$BACKUP_DIR/backup-manifest.txt" << EOF
Agentic AI IaC Cache Backup
Created: $(date)
Hostname: $(hostname)
User: $(whoami)
Project: $(pwd)

Contents:
$(find "$BACKUP_DIR" -type f | sort)
EOF
        
        log_success "Cache backup created in $BACKUP_DIR"
        ;;
        
    "restore")
        BACKUP_DIR="$2"
        if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
            log_error "Please specify a valid backup directory"
            log_info "Usage: $0 restore <backup-directory>"
            exit 1
        fi
        
        log_info "Restoring cache from $BACKUP_DIR..."
        
        # Restore pip cache
        if [ -d "$BACKUP_DIR/pip-cache" ]; then
            mkdir -p ~/.cache
            cp -r "$BACKUP_DIR/pip-cache" ~/.cache/pip
            log_success "Pip cache restored"
        fi
        
        # Restore configuration
        if [ -d "$BACKUP_DIR/agentic-config" ]; then
            cp -r "$BACKUP_DIR/agentic-config" ~/.agentic-iac
            log_success "Configuration restored"
        fi
        
        # Restore project artifacts
        if [ -f "$BACKUP_DIR/deployment-analysis.json" ]; then
            cp "$BACKUP_DIR/deployment-analysis.json" .
            log_success "Deployment analysis restored"
        fi
        
        if [ -d "$BACKUP_DIR/test-reports" ]; then
            cp -r "$BACKUP_DIR/test-reports" .
            log_success "Test reports restored"
        fi
        
        log_success "Cache restoration completed"
        ;;
        
    "stats")
        log_info "Generating cache statistics..."
        
        # Python stats
        PIP_COUNT=$(find ~/.cache/pip -name "*.whl" 2>/dev/null | wc -l)
        PIP_SIZE=$(get_dir_size ~/.cache/pip)
        
        # Demo stats
        DEMO_COUNT=$(find demo-apps -type d -mindepth 1 -maxdepth 1 2>/dev/null | wc -l)
        DEMO_SIZE=$(get_dir_size demo-apps)
        
        # Test stats
        TEST_FILES=$(find test-reports -name "*.xml" -o -name "*.json" 2>/dev/null | wc -l)
        TEST_SIZE=$(get_dir_size test-reports)
        
        # Log stats
        LOG_FILES=$(find logs -name "*.log" 2>/dev/null | wc -l)
        LOG_SIZE=$(get_dir_size logs)
        
        echo ""
        echo "📊 Cache Statistics Report"
        echo "=========================="
        echo ""
        echo "🐍 Python Cache:"
        echo "  Cached packages: $PIP_COUNT"
        echo "  Total size: $PIP_SIZE"
        echo ""
        echo "🎯 Demo Applications:"
        echo "  Cached demos: $DEMO_COUNT"
        echo "  Total size: $DEMO_SIZE"
        echo ""
        echo "🧪 Test Artifacts:"
        echo "  Test files: $TEST_FILES"
        echo "  Total size: $TEST_SIZE"
        echo ""
        echo "📝 Logs:"
        echo "  Log files: $LOG_FILES"
        echo "  Total size: $LOG_SIZE"
        echo ""
        
        # Cache efficiency calculation
        if [ "$PIP_COUNT" -gt 0 ]; then
            log_success "Cache appears to be active and beneficial"
        else
            log_warning "Cache appears to be empty - consider running a build"
        fi
        ;;
        
    "monitor")
        log_info "Starting cache monitoring (Press Ctrl+C to stop)..."
        
        MONITOR_INTERVAL=${2:-5}  # Default 5 seconds
        
        while true; do
            clear
            echo "🗄️ Agentic AI IaC Cache Monitor"
            echo "=============================="
            echo "Update interval: ${MONITOR_INTERVAL}s | $(date)"
            echo ""
            
            # Real-time cache sizes
            echo "📊 Real-time Cache Sizes:"
            echo "  Python pip: $(get_dir_size ~/.cache/pip)"
            echo "  Demo apps: $(get_dir_size demo-apps)"
            echo "  Test reports: $(get_dir_size test-reports)"
            echo "  Logs: $(get_dir_size logs)"
            echo ""
            
            # Recent activity
            echo "📈 Recent Activity:"
            echo "  Last pip install: $(find ~/.cache/pip -name "*.whl" -newer ~/.cache/pip 2>/dev/null | head -1 | xargs ls -lt 2>/dev/null | cut -d' ' -f6-8 || echo "None")"
            echo "  Last demo setup: $(find demo-apps -type f -newer demo-apps 2>/dev/null | head -1 | xargs ls -lt 2>/dev/null | cut -d' ' -f6-8 || echo "None")"
            echo "  Last test run: $(find test-reports -name "*.xml" -newer test-reports 2>/dev/null | head -1 | xargs ls -lt 2>/dev/null | cut -d' ' -f6-8 || echo "None")"
            echo ""
            
            sleep $MONITOR_INTERVAL
        done
        ;;
        
    *)
        echo "Agentic AI IaC Cache Management Tool"
        echo ""
        echo "Usage: $0 {command} [options]"
        echo ""
        echo "Commands:"
        echo "  info       - Show cache information and sizes"
        echo "  clear      - Clear all local caches and artifacts"
        echo "  prepare    - Create cache directories and setup environment"
        echo "  optimize   - Optimize cache performance and clean old files"
        echo "  validate   - Validate cache health and permissions"
        echo "  backup     - Create a backup of important cache data"
        echo "  restore    - Restore cache from backup directory"
        echo "  stats      - Generate detailed cache statistics"
        echo "  monitor    - Real-time cache monitoring (Ctrl+C to stop)"
        echo ""
        echo "Examples:"
        echo "  $0 info                    # Show current cache status"
        echo "  $0 clear                   # Clear all caches"
        echo "  $0 prepare                 # Setup environment"
        echo "  $0 backup                  # Create cache backup"
        echo "  $0 restore cache-backup-*  # Restore from backup"
        echo "  $0 monitor 10              # Monitor with 10s interval"
        echo ""
        echo "🔧 For GitHub Actions troubleshooting:"
        echo "  1. Run '$0 validate' to check for issues"
        echo "  2. Run '$0 clear && $0 prepare' to reset environment"
        echo "  3. Run '$0 stats' to verify cache effectiveness"
        ;;
esac
