#!/bin/bash
# Checks if Go code is properly formatted without modifying files

if ! gofmt -l .. | grep -q .; then
    echo "✓ Code formatting OK"
    exit 0
else
    echo "✗ Formatting issues found in:"
    gofmt -l ..
    exit 1
fi