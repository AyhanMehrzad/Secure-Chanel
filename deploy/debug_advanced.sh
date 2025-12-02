#!/bin/bash

echo "=== Advanced Debugger ==="

# 1. Check Firewall (UFW)
echo "1. Checking Firewall..."
if command -v ufw > /dev/null; then
    ufw status verbose
else
    echo "   UFW not installed (iptables might be active)."
fi

# 2. Check Nginx Local Response
echo "2. Checking Nginx Local Response (Port 80)..."
if curl -s -I http://127.0.0.1 | grep "HTTP/"; then
    echo "   ✅ Nginx is responding locally."
else
    echo "   ❌ Nginx is NOT responding locally."
fi

# 3. Check Nginx Configuration Content
echo "3. Dumping Nginx Config..."
cat /etc/nginx/sites-enabled/messageapp

# 4. Check Error Logs again
echo "4. Recent Nginx Errors..."
tail -n 10 /var/log/nginx/error.log

echo "=== End Debug ==="
