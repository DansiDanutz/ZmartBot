#!/bin/bash

# Automatic backup script for symbols database
DB_PATH="my_symbols_v2.db"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
cp $DB_PATH "$BACKUP_DIR/my_symbols_v2_backup_$TIMESTAMP.db"

# Keep only the last 5 backups
ls -t $BACKUP_DIR/my_symbols_v2_backup_*.db | tail -n +6 | xargs -r rm

echo "✅ Database backed up: $BACKUP_DIR/my_symbols_v2_backup_$TIMESTAMP.db"
