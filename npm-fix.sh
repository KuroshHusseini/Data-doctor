#!/bin/bash

# Quick fix for npm vulnerabilities

echo "🔧 Fixing npm security vulnerabilities..."

cd frontend

echo "📦 Current vulnerabilities:"
npm audit

echo ""
echo "🛠️ Applying fixes..."
npm audit fix

echo ""
echo "🔒 Checking for remaining critical vulnerabilities..."
if npm audit | grep -q "critical"; then
    echo "⚠️  Critical vulnerabilities still present. Applying force fix..."
    echo "   (This may update packages to newer versions)"
    read -p "Continue with force fix? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm audit fix --force
    fi
else
    echo "✅ No critical vulnerabilities found!"
fi

echo ""
echo "📊 Final audit report:"
npm audit

cd ..
echo "✅ npm fix complete!"