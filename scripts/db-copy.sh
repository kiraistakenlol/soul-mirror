#!/bin/bash
# Copy database between local and cloud instances

set -e

SOURCE=$1
DEST=$2

if [ -z "$SOURCE" ] || [ -z "$DEST" ]; then
    echo "Usage: ./db-copy.sh <source> <dest>"
    echo "  source/dest: 'local' or 'cloud'"
    echo ""
    echo "Examples:"
    echo "  ./db-copy.sh local cloud   # Copy local → cloud"
    echo "  ./db-copy.sh cloud local   # Copy cloud → local"
    exit 1
fi

LOCAL_DB="postgresql://soulmirror:soulmirror@localhost:5433/soulmirror"
CLOUD_DB="postgresql://soulmirror:soulmirror@45.32.117.48:5432/soulmirror"

if [ "$SOURCE" = "local" ]; then
    SOURCE_DB=$LOCAL_DB
    SOURCE_NAME="local"
elif [ "$SOURCE" = "cloud" ]; then
    SOURCE_DB=$CLOUD_DB
    SOURCE_NAME="cloud"
else
    echo "Error: source must be 'local' or 'cloud'"
    exit 1
fi

if [ "$DEST" = "local" ]; then
    DEST_DB=$LOCAL_DB
    DEST_NAME="local"
elif [ "$DEST" = "cloud" ]; then
    DEST_DB=$CLOUD_DB
    DEST_NAME="cloud"
else
    echo "Error: dest must be 'local' or 'cloud'"
    exit 1
fi

echo "Copying $SOURCE_NAME → $DEST_NAME"
echo ""
echo "This will:"
echo "  1. Reset destination schema (baseline.sql)"
echo "  2. Copy all data from source"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 1
fi

echo "→ Resetting destination schema..."
psql $DEST_DB < apps/backend/baseline.sql

echo "→ Copying data..."
pg_dump $SOURCE_DB --data-only --column-inserts | psql $DEST_DB

echo "✓ Done"
