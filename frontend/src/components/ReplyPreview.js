import React from 'react';

const ReplyPreview = ({ replyTo, onClose }) => {
    if (!replyTo) return null;

    return (
        <div className="reply-preview-pill">
            <div className="reply-line-pill"></div>
            <div className="reply-preview-content">
                <div className="reply-preview-label">Replying to message</div>
                <div className="reply-preview-text">{replyTo.msg}</div>
            </div>
            <button className="reply-close-btn" onClick={onClose}>✕</button>
        </div>
    );
};

export default ReplyPreview;
