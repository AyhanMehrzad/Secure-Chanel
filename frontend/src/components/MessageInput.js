import React, { useState, useRef, useEffect, useCallback } from 'react';

const MessageInput = ({ onSend, onSocketAction }) => {
    const [text, setText] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [recordingType, setRecordingType] = useState(null); // 'audio' | 'video'
    const [recordingTime, setRecordingTime] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [stream, setStream] = useState(null); // Keep track of stream for preview

    const textareaRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);
    const fileInputRef = useRef(null);
    const videoPreviewRef = useRef(null); // Self-view current video

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.style.scrollHeight + 'px';
        }
    }, [text]);

    // Keep track of stream in ref for cleanup
    const streamRef = useRef(null);

    // Sync ref with state
    useEffect(() => {
        streamRef.current = stream;
    }, [stream]);

    // Clean up stream on unmount
    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // Watch for stream changes to attach to video element
    useEffect(() => {
        if (videoPreviewRef.current && stream) {
            videoPreviewRef.current.srcObject = stream;
        }
    }, [stream, isRecording]);

    const stopMediaStream = useCallback(() => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    }, [stream]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendText();
        }
    };

    const handleSendText = () => {
        if (text.trim()) {
            onSend({ msg: text, type: 'text' });
            setText('');
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
                // Keep focus to prevent keyboard from closing on mobile
                textareaRef.current.focus();
            }
        }
    };

    const startRecording = async (type) => {
        try {
            const constraints = type === 'video'
                ? { video: true, audio: true }
                : { audio: true };

            const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            setStream(mediaStream); // Set state to trigger preview

            const mediaRecorder = new MediaRecorder(mediaStream);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: type === 'video' ? 'video/webm' : 'audio/webm' });
                uploadFile(blob, type);
                stopMediaStream();
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingType(type);
            setRecordingTime(0);

            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);

        } catch (err) {
            console.error("Error accessing media devices:", err);
            alert("Could not access camera/microphone. Please check permissions.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            setRecordingType(null);
            clearInterval(timerRef.current);
        }
    };

    const cancelRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.onstop = null; // Prevent upload
            mediaRecorderRef.current.stop();
            stopMediaStream();
            setIsRecording(false);
            setRecordingType(null);
            clearInterval(timerRef.current);
        }
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            let type = 'file';
            if (file.type.startsWith('image/')) type = 'image';
            else if (file.type.startsWith('video/')) type = 'video';
            else if (file.type.startsWith('audio/')) type = 'audio';

            uploadFile(file, type);
        }
    };

    const uploadFile = async (fileBlob, type) => {
        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', fileBlob, type === 'audio' ? 'recording.webm' : (type === 'video' ? 'recording.webm' : fileBlob.name));

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.url) {
                onSend({ msg: data.url, type: type });
            } else {
                alert("Upload failed");
            }
        } catch (err) {
            console.error("Upload error:", err);
            alert("Upload error");
        } finally {
            setIsUploading(false);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    };

    const handleEmojiClick = (emoji) => {
        setText(prev => prev + emoji);
    };

    // --- RENDER ---

    // Action Bar Handlers
    const handleAction = (action) => {
        if (onSocketAction) {
            onSocketAction(action);
        }
    };

    if (isRecording) {
        return (
            <div className="input-container recording-mode">
                {/* Self View for Video - Circular & Centered */}
                {recordingType === 'video' && (
                    <div className="video-preview-circle-container">
                        <video
                            ref={videoPreviewRef}
                            autoPlay
                            muted
                            playsInline
                            className="video-preview-feed-circle"
                        />
                    </div>
                )}

                <div className="recording-ui">
                    <div className="recording-indicator">
                        <div className="recording-dot"></div>
                        <span>{recordingType === 'audio' ? 'Recording Audio...' : 'Recording Video...'}</span>
                    </div>
                    <div className="recording-timer">{formatTime(recordingTime)}</div>
                    <div className="recording-actions">
                        <button className="btn-cancel" onClick={cancelRecording}>Cancel</button>
                        <button className="btn-stop" onClick={stopRecording}>Stop & Send</button>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="input-stack">
            {/* Action Bar Pill */}
            <div className="action-bar-pill">
                <button className="action-unit" onClick={() => handleAction('clear')} title="Clear History">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
                <button className="action-unit" onClick={() => handleAction('ping')} title="Ping User">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                </button>
                <button className="action-unit" onClick={() => handleEmojiClick('😊')} title="Emoji">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                </button>
                <button className="action-unit" onClick={() => handleAction('exit')} title="Exit App">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect><polyline points="17 2 12 7 7 2"></polyline></svg>
                </button>
            </div>

            {/* Input Pill */}
            <div className="input-pill-container">
                {/* Upload Overlay */}
                {isUploading && (
                    <div className="upload-overlay">
                        <div className="loading-spinner small"></div>
                        <span>Uploading...</span>
                    </div>
                )}

                <div className="input-pill-box">
                    {/* Attachment: Replaced Pin with simple Plus or Clip as requested (using Clip) */}
                    <button className="pin-btn" onClick={() => fileInputRef.current.click()}>
                        📎
                    </button>
                    <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileUpload} />

                    <textarea
                        ref={textareaRef}
                        className="input-textarea"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Message..."
                        rows={1}
                    />

                    <div className="input-actions-right">
                        {text.trim() ? (
                            <button className="send-btn-icon" onClick={handleSendText}>➤</button>
                        ) : (
                            <>
                                <button className="media-btn" onClick={() => startRecording('video')}>📹</button>
                                <button className="media-btn" onClick={() => startRecording('audio')}>🎤</button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MessageInput;
