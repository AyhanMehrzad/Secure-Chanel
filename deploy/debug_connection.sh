#!/bin/bash

echo "=== Connection Debugger ==="

# 1. Check Public IP
echo "1. Checking Server IP..."
SERVER_IP=$(curl -s ifconfig.me)
echo "   Detected Public IP: $SERVER_IP"

# 2. Check Gunicorn
echo "2. Checking Gunicorn..."
if pgrep -f "gunicorn" > /dev/null; then
    echo "   ✅ Gunicorn is running."
    
    # Try to connect to Gunicorn directly
    echo "   Testing local connection to Gunicorn (127.0.0.1:8000)..."
    if curl -s -I http://127.0.0.1:8000 > /dev/null; then
        echo "   ✅ Gunicorn is accepting connections."
    else
        echo "   ❌ Gunicorn is running but NOT responding to curl."
        echo "   Last 20 lines of Gunicorn logs:"
        journalctl -u messageapp -n 20 --no-pager
    fi
else
    echo "   ❌ Gunicorn is NOT running."
    echo "   Attempting to restart..."
    systemctl restart messageapp
fi

# 3. Check Nginx
echo "3. Checking Nginx..."
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running."
else
    echo "   ❌ Nginx is NOT running."
    systemctl status nginx --no-pager
fi

# 4. DNS Check (Basic)
echo "4. DNS Check for securechanel.xyz..."
if host securechanel.xyz > /dev/null; then
    echo "   ✅ Domain resolves."
    host securechanel.xyz
else
    echo "   ❌ Domain does NOT resolve. Please check your DNS settings at your registrar."
fi

echo "=== End Debug ==="
