#!/bin/bash
# Runs go vet for static analysis to find potential issues

cd ..
if go vet ./...; then
    echo "✓ Go vet passed"
    exit 0
else
    echo "✗ Go vet found issues"
    exit 1
fi