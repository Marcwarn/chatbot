#!/bin/bash
# Vercel Deployment Script
# Kör detta för att deploya till Vercel

echo "🚀 Deployer chatbot till Vercel..."
echo ""

# Kolla om du är inloggad
if ! vercel whoami &> /dev/null; then
    echo "📝 Du behöver logga in först:"
    echo "   vercel login"
    echo ""
    exit 1
fi

# Deploya till preview först
echo "📦 Deployer till Preview..."
vercel --yes

echo ""
echo "✅ Preview deployment klar!"
echo ""
echo "🔍 Vill du deploya till Production?"
echo "   Kör: vercel --prod"
echo ""
