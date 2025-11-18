#!/bin/bash
# Encoding validation script for NAS Docker deployment

set -e

echo "====================================="
echo "Encoding Validation Check"
echo "====================================="
echo ""

ERRORS=0

# Check 1: Python files must have UTF-8 declaration
echo "[1/5] Checking Python UTF-8 declarations..."
MISSING_UTF8=$(find backend -name "*.py" -type f -exec grep -L "coding: utf-8" {} \; 2>/dev/null || true)
if [ -n "$MISSING_UTF8" ]; then
    echo "ERROR: Python files missing UTF-8 declaration:"
    echo "$MISSING_UTF8"
    ERRORS=$((ERRORS+1))
else
    echo "✓ All Python files have UTF-8 declaration"
fi
echo ""

# Check 2: No UTF-16/UTF-32 files
echo "[2/5] Checking for incorrect UTF encodings..."
WRONG_ENCODING=$(find frontend/src backend -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.py" \) -exec file {} \; | grep -i "UTF-16\|UTF-32" || true)
if [ -n "$WRONG_ENCODING" ]; then
    echo "ERROR: Files with wrong encoding:"
    echo "$WRONG_ENCODING"
    ERRORS=$((ERRORS+1))
else
    echo "✓ No UTF-16/UTF-32 files found"
fi
echo ""

# Check 3: No BOM in files
echo "[3/5] Checking for BOM markers..."
BOM_FILES=$(find frontend/src backend -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.py" \) -exec file {} \; | grep -i "BOM" || true)
if [ -n "$BOM_FILES" ]; then
    echo "WARNING: Files with BOM (should be removed):"
    echo "$BOM_FILES"
fi
echo "✓ BOM check complete"
echo ""

# Check 4: No escaped operators in TypeScript files
echo "[4/5] Checking for escaped operators in TypeScript..."
ESCAPED_OPS=$(grep -r "\\\\[!=<>&|]" frontend/src --include="*.tsx" --include="*.ts" 2>/dev/null || true)
if [ -n "$ESCAPED_OPS" ]; then
    echo "ERROR: Found escaped operators:"
    echo "$ESCAPED_OPS"
    ERRORS=$((ERRORS+1))
else
    echo "✓ No escaped operators found"
fi
echo ""

# Check 5: Verify .editorconfig and .gitattributes exist
echo "[5/5] Checking encoding configuration files..."
if [ ! -f ".editorconfig" ]; then
    echo "ERROR: .editorconfig is missing"
    ERRORS=$((ERRORS+1))
else
    echo "✓ .editorconfig exists"
fi

if [ ! -f ".gitattributes" ]; then
    echo "ERROR: .gitattributes is missing"
    ERRORS=$((ERRORS+1))
else
    echo "✓ .gitattributes exists"
fi
echo ""

# Summary
echo "====================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All encoding checks PASSED"
    echo "====================================="
    exit 0
else
    echo "✗ Found $ERRORS error(s)"
    echo "====================================="
    exit 1
fi
