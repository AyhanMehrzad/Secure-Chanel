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
                    created_at TEXT NOT NULL,
                    reply_to INTEGER,
                    FOREIGN KEY (reply_to) REFERENCES messages(id)
                )
            ''')
            
            # Migration: Add reply_to column if it doesn't exist
            cursor.execute("PRAGMA table_info(messages)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'reply_to' not in columns:
                cursor.execute('ALTER TABLE messages ADD COLUMN reply_to INTEGER')
                print("✅ Added reply_to column to messages table")
            
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
            try:
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
                # Switch to autocommit mode for VACUUM
                conn.isolation_level = None
                cursor.execute('VACUUM')
                
                final_size = self._get_db_size()
                print(f"✅ Cleanup complete. Database size: {final_size / 1024 / 1024:.2f}MB")
            except Exception as e:
                print(f"❌ Error in cleanup: {e}")
            finally:
                conn.close()
    
    def save_message(self, user: str, message: str, message_type: str = 'text', timestamp: Optional[float] = None, reply_to: Optional[int] = None) -> int:
        """Save a message and return its ID"""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (user, message, message_type, timestamp, created_at, reply_to)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user, message, message_type, timestamp, datetime.now().isoformat(), reply_to))
            
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
                SELECT id, user, message, message_type, timestamp, created_at, reply_to
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
                    'created_at': row['created_at'],
                    'reply_to': row['reply_to']
                })
            
            conn.close()
            return list(reversed(messages))  # Return in chronological order
    
    def get_messages_paginated(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get messages with pagination support"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user, message, message_type, timestamp, created_at, reply_to
                FROM messages
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row['id'],
                    'user': row['user'],
                    'msg': row['message'],
                    'type': row['message_type'],
                    'timestamp': row['timestamp'],
                    'created_at': row['created_at'],
                    'reply_to': row['reply_to']
                })
            
            conn.close()
            return list(reversed(messages))  # Return in chronological order
    
    def get_messages_before(self, before_timestamp: float, limit: int = 50) -> List[Dict]:
        """Get messages before a specific timestamp"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user, message, message_type, timestamp, created_at, reply_to
                FROM messages
                WHERE timestamp < ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (before_timestamp, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row['id'],
                    'user': row['user'],
                    'msg': row['message'],
                    'type': row['message_type'],
                    'timestamp': row['timestamp'],
                    'created_at': row['created_at'],
                    'reply_to': row['reply_to']
                })
            
            conn.close()
            return list(reversed(messages))  # Return in chronological order
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict]:
        """Get a specific message by ID (for reply context)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user, message, message_type, timestamp, created_at, reply_to
                FROM messages
                WHERE id = ?
            ''', (message_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row['id'],
                    'user': row['user'],
                    'msg': row['message'],
                    'type': row['message_type'],
                    'timestamp': row['timestamp'],
                    'created_at': row['created_at'],
                    'reply_to': row['reply_to']
                }
            return None
    
    def clear_all(self):
        """Clear all messages (for self-destruct)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM messages')
                conn.commit() # Commit the deletion first
                
                # VACUUM must be run outside of a transaction
                # Switch to autocommit mode for VACUUM
                conn.isolation_level = None
                cursor.execute('VACUUM')
                
                # Restore default isolation level (optional, but good practice if we reused conn)
                conn.isolation_level = '' 
                
                print("🗑️ All messages cleared")
            except Exception as e:
                print(f"❌ Error in clear_all: {e}")
                raise e
            finally:
                conn.close()
    
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

