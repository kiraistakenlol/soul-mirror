#!/bin/bash
# Builds the Go application to verify compilation

cd ..
if go build -o /dev/null .; then
    echo "✓ Build successful"
    exit 0
else
    echo "✗ Build failed"
    exit 1
fi