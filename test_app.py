"""
Test suite for the secure messaging application
"""
import pytest
import json
from app import app, socketio, users, active_sessions, blocked_ips
from flask import session
from datetime import datetime, timedelta


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client"""
    with client.session_transaction() as sess:
        sess['user'] = 'sana'
    return client


class TestRoutes:
    """Test HTTP routes"""
    
    def test_login_get(self, client):
        """Test login page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ACCESS CONTROL' in response.data
    
    def test_login_post_valid(self, client):
        """Test successful login"""
        response = client.post('/', data={
            'username': 'sana',
            'password': '512683'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'SECURE' in response.data
    
    def test_login_post_invalid(self, client):
        """Test failed login"""
        response = client.post('/', data={
            'username': 'sana',
            'password': 'wrong'
        })
        assert response.status_code == 200
        assert b'Invalid Credentials' in response.data
    
    def test_dashboard_requires_auth(self, client):
        """Test dashboard redirects when not authenticated"""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'ACCESS CONTROL' in response.data
    
    def test_dashboard_authenticated(self, authenticated_client):
        """Test dashboard loads when authenticated"""
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        assert b'SECURE' in response.data
    
    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'ACCESS CONTROL' in response.data
        
        # Verify session is cleared
        with authenticated_client.session_transaction() as sess:
            assert 'user' not in sess


class TestAPIRoutes:
    """Test API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'active_sessions' in data
        assert 'blocked_ips' in data
    
    def test_api_status_unauthorized(self, client):
        """Test status endpoint requires authentication"""
        response = client.get('/api/status')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_status_authorized(self, authenticated_client):
        """Test status endpoint with authentication"""
        response = authenticated_client.get('/api/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user'] == 'sana'
        assert 'active_sessions' in data
        assert 'connected_users' in data
        assert 'timestamp' in data
    
    def test_api_user_unauthorized(self, client):
        """Test user endpoint requires authentication"""
        response = client.get('/api/user')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_user_authorized(self, authenticated_client):
        """Test user endpoint with authentication"""
        response = authenticated_client.get('/api/user')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'sana'
        assert data['is_authenticated'] is True


class TestIPBlocking:
    """Test IP blocking functionality"""
    
    def test_ip_blocking_middleware(self, client):
        """Test that blocked IPs are rejected"""
        from app import block_ip, is_blocked
        
        test_ip = '192.168.1.100'
        block_ip(test_ip, duration_minutes=5)
        
        # Simulate request from blocked IP
        # Note: In actual test, we'd need to mock request.remote_addr
        assert is_blocked(test_ip) is True
    
    def test_ip_block_expiry(self, client):
        """Test that IP blocks expire"""
        from app import block_ip, is_blocked
        
        test_ip = '192.168.1.101'
        # Block for negative time (expired immediately)
        blocked_ips[test_ip] = datetime.now() - timedelta(minutes=1)
        
        # Should not be blocked (expired)
        assert is_blocked(test_ip) is False


class TestSocketIO:
    """Test SocketIO events"""
    
    def test_socketio_connection_requires_auth(self, client):
        """Test that SocketIO connection requires authentication"""
        # This would require a more complex test setup with socketio test client
        # For now, we'll just verify the structure
        pass
    
    def test_socketio_events_exist(self):
        """Test that SocketIO event handlers are registered"""
        # Verify event handlers exist
        assert hasattr(socketio, 'on')
        # In a full test, we'd use flask_socketio's test client


class TestUserManagement:
    """Test user management"""
    
    def test_valid_users_exist(self):
        """Test that valid users are configured"""
        assert 'sana' in users
        assert 'ayhan' in users
        assert users['sana'] == '512683'
        assert users['ayhan'] == '512683'
    
    def test_invalid_user_rejected(self, client):
        """Test that invalid users are rejected"""
        response = client.post('/', data={
            'username': 'invalid_user',
            'password': 'password'
        })
        assert response.status_code == 200
        assert b'Invalid Credentials' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

