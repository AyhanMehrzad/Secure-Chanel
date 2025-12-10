import React, { useEffect, useRef, useState } from 'react';

const Message = ({ msg, user, setReplyTo }) => {
  const isMe = msg.user === user;

  const renderContent = () => {
    switch (msg.type) {
      case 'image':
        return <img src={msg.msg} alt="attachment" className="msg-image" />;
      case 'video':
        return <video src={msg.msg} controls className="msg-video" />;
      case 'audio':
        return <audio src={msg.msg} controls className="msg-audio" />;
      case 'file':
        // Extract filename from URL if possible, else generic
        const filename = msg.msg.split('/').pop().split('_').slice(2).join('_');
        return (
          <a href={msg.msg} target="_blank" rel="noopener noreferrer" className="msg-file">
            📄 {filename || 'Download File'}
          </a>
        );
      default:
        return <div className="msg-text">{msg.msg}</div>;
    }
  };

  return (
    <div className={`message ${isMe ? 'me' : 'other'} ${msg.type}`}>
      {/* Reply Context - Telegram Style */}
      {msg.reply_context && (
        <div className="message-reply-context" onClick={() => {
          // Optional: scroll to message if in view
        }}>
          <div className="reply-line"></div>
          <div className="reply-content">
            {/* Removed specific username, generic label or just text */}
            <div className="reply-author">Replying to message</div>
            <div className="reply-text">
              {msg.reply_context.type === 'text' ? msg.reply_context.msg : `[${msg.reply_context.type}]`}
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="msg-content-wrapper">
        {renderContent()}
      </div>

      {/* Time (Simulated or from timestamp) */}
      <div className="msg-time">
        {new Date(msg.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>

      {/* Reply Button */}
      <button
        className="reply-btn"
        onClick={() => setReplyTo(msg)}
        title="Reply"
      >
        ↩
      </button>
    </div>
  );
};

const ChatWindow = ({ messages, user, setReplyTo, onLoadMore }) => {
  const chatWindowRef = useRef(null);
  const scrollSentinelRef = useRef(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Check if we should auto-scroll before updates
  const handleScroll = () => {
    if (chatWindowRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatWindowRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShouldAutoScroll(isNearBottom);

      // Infinite Scroll: Load more when near top
      if (scrollTop < 50 && !isLoadingHistory && messages.length > 0) {
        setIsLoadingHistory(true);
        // Find oldest message timestamp
        const oldestMsg = messages[0];
        if (oldestMsg && onLoadMore) {
          onLoadMore(oldestMsg.timestamp).finally(() => {
            setIsLoadingHistory(false);
          });
        }
      }
    }
  };

  // Effect to handle auto-scrolling
  useEffect(() => {
    if (shouldAutoScroll && scrollSentinelRef.current) {
      scrollSentinelRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, shouldAutoScroll]);

  return (
    <div
      className="chat-window"
      ref={chatWindowRef}
      onScroll={handleScroll}
    >
      {isLoadingHistory && <div className="loading-history">Loading history...</div>}

      {messages.map((msg, index) => (
        <Message
          key={msg.id || `${msg.timestamp}-${index}`}
          msg={msg}
          user={user}
          setReplyTo={setReplyTo}
        />
      ))}
      <div ref={scrollSentinelRef} className="chat-spacer"></div>
    </div>
  );
};

export default ChatWindow;
