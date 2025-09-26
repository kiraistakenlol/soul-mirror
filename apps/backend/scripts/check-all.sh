#!/bin/bash
# Runs all checks: format, build, and vet

echo "Running all checks..."
echo ""

./check-format.sh || exit 1
echo ""

./build.sh || exit 1
echo ""

./vet.sh || exit 1
echo ""

echo "✅ All checks passed!"