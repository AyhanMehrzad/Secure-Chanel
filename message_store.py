"""
Message Storage System with 500MB limit and auto-cleanup
Uses SQLite (file-based, no server needed)
"""
import sqlite3
import os
import threading
from datetime import datetime
from typing import Optional, List, Dict

# Maximum database size: 500MB
MAX_DB_SIZE_MB = 500
MAX_DB_SIZE_BYTES = MAX_DB_SIZE_MB * 1024 * 1024

class MessageStore:
    """Manages message storage with automatic cleanup"""
    
    def __init__(self, db_path: str = 'messages.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        self._check_and_cleanup()
    
    def _init_database(self):
        """Initialize the database schema"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    message TEXT NOT NULL,
                    message_type TEXT NOT NULL DEFAULT 'text',
                    timestamp REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Create index on timestamp for faster cleanup
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)
            ''')
            
            conn.commit()
            conn.close()
    
    def _get_db_size(self) -> int:
        """Get current database file size in bytes"""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
    
    def _check_and_cleanup(self):
        """Check database size and cleanup if needed"""
        current_size = self._get_db_size()
        
        if current_size > MAX_DB_SIZE_BYTES:
            print(f"⚠️ Database size ({current_size / 1024 / 1024:.2f}MB) exceeds limit. Cleaning up...")
            self._cleanup_oldest_messages()
    
    def _cleanup_oldest_messages(self):
        """Remove oldest messages until under size limit"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            # Delete oldest 10% of messages at a time
            while self._get_db_size() > MAX_DB_SIZE_BYTES * 0.9:  # Clean until 90% of limit
                cursor.execute('''
                    SELECT id FROM messages 
                    ORDER BY timestamp ASC 
                    LIMIT 100
                ''')
                ids_to_delete = [row[0] for row in cursor.fetchall()]
                
                if not ids_to_delete:
                    break
                
                placeholders = ','.join('?' * len(ids_to_delete))
                cursor.execute(f'DELETE FROM messages WHERE id IN ({placeholders})', ids_to_delete)
                conn.commit()
                
                print(f"🗑️ Deleted {len(ids_to_delete)} oldest messages")
            
            # Vacuum to reclaim space
            cursor.execute('VACUUM')
            conn.commit()
            conn.close()
            
            final_size = self._get_db_size()
            print(f"✅ Cleanup complete. Database size: {final_size / 1024 / 1024:.2f}MB")
    
    def save_message(self, user: str, message: str, message_type: str = 'text', timestamp: Optional[float] = None) -> int:
        """Save a message and return its ID"""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (user, message, message_type, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user, message, message_type, timestamp, datetime.now().isoformat()))
            
            message_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Check size after each save (async cleanup)
            if self._get_db_size() > MAX_DB_SIZE_BYTES:
                # Run cleanup in background thread to not block
                threading.Thread(target=self._cleanup_oldest_messages, daemon=True).start()
            
            return message_id
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """Get recent messages"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user, message, message_type, timestamp, created_at
                FROM messages
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row['id'],
                    'user': row['user'],
                    'msg': row['message'],
                    'type': row['message_type'],
                    'timestamp': row['timestamp'],
                    'created_at': row['created_at']
                })
            
            conn.close()
            return list(reversed(messages))  # Return in chronological order
    
    def clear_all(self):
        """Clear all messages (for self-destruct)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages')
            cursor.execute('VACUUM')
            conn.commit()
            conn.close()
            print("🗑️ All messages cleared")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            count = cursor.fetchone()[0]
            
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM messages')
            result = cursor.fetchone()
            oldest = result[0] if result[0] else None
            newest = result[1] if result[1] else None
            
            conn.close()
            
            size = self._get_db_size()
            
            return {
                'message_count': count,
                'size_bytes': size,
                'size_mb': size / 1024 / 1024,
                'max_size_mb': MAX_DB_SIZE_MB,
                'oldest_timestamp': oldest,
                'newest_timestamp': newest
            }

