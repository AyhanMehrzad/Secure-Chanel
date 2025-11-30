# Testing Guide

## Quick Start

### 1. Start the Server

**Option A: Using the start script**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Option B: Manual start**
```bash
source venv/bin/activate
python3 app.py
```

The server will start on `http://localhost:5000`

---

## Testing Methods

### 1. **Web Browser Testing**

#### Desktop Browser:
1. Open browser and go to: `http://localhost:5000`
2. Login with credentials:
   - Username: `sana` or `ayhan`
   - Password: `512683`
3. Test features:
   - Send messages
   - Use shortcut buttons (clear history, ping)
   - Test video call view
   - Test logout

#### Mobile Browser (On Same Network):
1. Find your computer's IP address:
   ```bash
   hostname -I
   # or
   ip addr show | grep "inet "
   ```
2. On your mobile device, open browser and go to:
   `http://YOUR_IP_ADDRESS:5000`
   Example: `http://192.168.1.100:5000`
3. Test mobile-specific features:
   - Touch interactions
   - Keyboard handling
   - Video/audio recording
   - Landscape/portrait orientation

#### Mobile Browser (Localhost via USB):
- **Android**: Use Chrome's port forwarding
- **iOS**: Use Safari's Web Inspector with your Mac

---

### 2. **API Endpoint Testing**

#### Using curl:
```bash
# Health check (no auth required)
curl http://localhost:5000/api/health

# Status (requires login - will return 401)
curl http://localhost:5000/api/status

# User info (requires login - will return 401)
curl http://localhost:5000/api/user
```

#### Using browser:
- Open: `http://localhost:5000/api/health`
- Should see JSON response with status information

#### Using Python requests:
```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Status (with session)
session = requests.Session()
session.post('http://localhost:5000/', data={
    'username': 'sana',
    'password': '512683'
})
response = session.get('http://localhost:5000/api/status')
print(response.json())
```

---

### 3. **Automated Test Suite**

Run the test suite:
```bash
# Option A: Using the test script
chmod +x run_tests.sh
./run_tests.sh

# Option B: Manual
source venv/bin/activate
pytest test_app.py -v

# Option C: With coverage
pytest test_app.py -v --cov=app
```

Test output will show:
- ✅ Passed tests
- ❌ Failed tests
- Test coverage information

---

### 4. **SocketIO Testing**

#### Browser Console:
1. Open browser DevTools (F12)
2. Go to Console tab
3. The SocketIO connection should be automatic
4. You can test manually:
```javascript
// Check if socket is connected
socket.connected

// Send a test message
socket.emit('chat_message', {msg: 'Test', type: 'text'});

// Test ping
socket.emit('ping');
```

#### Multiple Browser Windows:
1. Open two browser windows/tabs
2. Login with different users (sana and ayhan)
3. Send messages between them
4. Test real-time features

---

### 5. **Mobile Device Testing**

#### On Your Phone (Same WiFi):

1. **Find your computer's IP:**
   ```bash
   # Linux/Mac
   hostname -I
   # or
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. **Start server (make sure it's accessible):**
   ```bash
   # In app.py, it's already set to 0.0.0.0 which allows network access
   python3 app.py
   ```

3. **On your phone:**
   - Connect to same WiFi network
   - Open browser
   - Go to: `http://YOUR_IP:5000`
   - Example: `http://192.168.1.100:5000`

4. **Test mobile features:**
   - Touch interactions
   - Keyboard behavior
   - Video/audio recording
   - Orientation changes
   - Safe area handling (on iPhone X+)

#### Using Browser DevTools Mobile Emulation:
1. Open Chrome DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select device (iPhone, Android, etc.)
4. Test different screen sizes and orientations

---

### 6. **Testing Checklist**

#### Basic Functionality:
- [ ] Login page loads
- [ ] Login with valid credentials works
- [ ] Login with invalid credentials shows error
- [ ] Dashboard loads after login
- [ ] Logout works
- [ ] Session persists on page refresh

#### API Endpoints:
- [ ] `/api/health` returns 200
- [ ] `/api/status` requires auth (401 when not logged in)
- [ ] `/api/status` returns user info when logged in
- [ ] `/api/user` requires auth (401 when not logged in)
- [ ] `/api/user` returns user info when logged in

#### Real-time Features:
- [ ] SocketIO connection establishes
- [ ] Messages send and receive
- [ ] Ping functionality works
- [ ] Clear history works
- [ ] Multiple users can connect

#### Mobile Features:
- [ ] Touch targets are large enough (44px+)
- [ ] No zoom on input focus (iOS)
- [ ] Keyboard doesn't cover input
- [ ] Safe areas respected (iPhone notches)
- [ ] Landscape orientation works
- [ ] Video/audio recording works
- [ ] Pull-to-refresh prevented

---

## Troubleshooting

### Server won't start:
```bash
# Check if port 5000 is in use
lsof -i :5000
# or
netstat -an | grep 5000

# Kill process if needed
kill -9 <PID>
```

### Can't access from mobile:
1. Check firewall settings
2. Ensure server is on `0.0.0.0` (already set in app.py)
3. Verify both devices on same network
4. Check IP address is correct

### SocketIO not connecting:
1. Check browser console for errors
2. Verify SocketIO library loaded
3. Check network tab for WebSocket connection
4. Ensure no CORS issues

### Tests failing:
```bash
# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run with verbose output
pytest test_app.py -v -s
```

---

## Performance Testing

### Load Testing (Optional):
```bash
# Install locust
pip install locust

# Create locustfile.py (basic example)
# Then run:
locust -f locustfile.py --host=http://localhost:5000
```

---

## Security Testing

- Test IP blocking functionality
- Test session management
- Test authentication bypass attempts
- Test self-destruct feature (carefully!)

---

## Next Steps

After testing, you can:
1. Deploy to production (Heroku, DigitalOcean, etc.)
2. Add SSL/HTTPS
3. Set up proper database (replace in-memory storage)
4. Add more test cases
5. Set up CI/CD for automated testing

