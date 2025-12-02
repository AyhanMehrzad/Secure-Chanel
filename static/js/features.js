// ========================================
// REPLY SYSTEM, PAGINATION, AND PERMISSIONS
// Additional features for the message app
// ========================================

// --- Additional DOM Elements ---
const replyPreviewBar = document.getElementById('reply-preview-bar');
const replyPreviewText = document.getElementById('reply-preview-text');
const replyPreviewClose = document.getElementById('reply-preview-close');
const permissionOverlay = document.getElementById('permission-overlay');
const btnGrantPermissions = document.getElementById('btn-grant-permissions');

// --- Additional State Variables ---
let replyingToMessage = null;
let isLoadingMessages = false;
let oldestMessageTimestamp = null;
let hasMoreMessages = true;
let permissionsGranted = false;

// --- Permission System ---
// Check if permissions were previously granted
if (localStorage.getItem('permissionsGranted') === 'true') {
    permissionsGranted = true;
    if (permissionOverlay) {
        permissionOverlay.classList.add('hidden');
    }
} else {
    // Show permission modal on page load
    if (permissionOverlay) {
        permissionOverlay.classList.remove('hidden');
    }
}

// Handle permission grant button
if (btnGrantPermissions) {
    btnGrantPermissions.addEventListener('click', async () => {
        console.log('🔑 Requesting all permissions...');

        let allGranted = true;

        // 1. Notifications
        if ('Notification' in window) {
            try {
                const permission = await Notification.requestPermission();
                console.log('🔔 Notification permission:', permission);
                if (permission === 'granted') {
                    showBrowserNotification('System', 'Notifications enabled!');
                } else {
                    allGranted = false;
                }
            } catch (err) {
                console.error('Error requesting notification permission:', err);
                allGranted = false;
            }
        }

        // 2. Camera & Microphone
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            console.log('📹🎤 Camera & Mic permission granted');
            // Stop immediately
            stream.getTracks().forEach(track => track.stop());
        } catch (err) {
            console.error('Error requesting media permissions:', err);
            allGranted = false;
        }

        // 3. Storage (IndexedDB is already initialized)
        console.log('💾 Storage (IndexedDB) available');

        if (allGranted) {
            // Store permission status
            localStorage.setItem('permissionsGranted', 'true');
            permissionsGranted = true;

            // Hide overlay
            if (permissionOverlay) {
                permissionOverlay.classList.add('hidden');
            }

            // Visual feedback
            const div = document.createElement('div');
            div.className = 'message other';
            div.innerText = '✅ ALL PERMISSIONS GRANTED';
            chatWindow.appendChild(div);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            setTimeout(() => {
                if (div.parentNode) div.remove();
            }, 3000);
        } else {
            alert('Some permissions were denied. Please allow all permissions for full functionality.');
        }
    });
}

// --- Reply System ---

// Handle reply preview close button
if (replyPreviewClose) {
    replyPreviewClose.addEventListener('click', () => {
        cancelReply();
    });
}

function setReplyTo(messageData) {
    replyingToMessage = messageData;

    if (replyPreviewBar && replyPreviewText) {
        // Show reply preview
        replyPreviewBar.classList.remove('hidden');

        // Set preview text
        let previewText = '';
        if (messageData.type === 'text') {
            previewText = messageData.msg;
        } else if (messageData.type === 'audio') {
            previewText = '🔊 Audio message';
        } else if (messageData.type === 'video') {
            previewText = '📹 Video message';
        }

        replyPreviewText.textContent = `${messageData.user}: ${previewText}`;

        // Focus input
        if (msgInput) {
            msgInput.focus();
        }
    }
}

function cancelReply() {
    replyingToMessage = null;
    if (replyPreviewBar) {
        replyPreviewBar.classList.add('hidden');
    }
}

// Add long-press/context menu to messages for reply
function addReplyHandlerToMessage(messageElement, messageData) {
    let pressTimer;

    // Touch events for mobile
    messageElement.addEventListener('touchstart', (e) => {
        pressTimer = setTimeout(() => {
            showMessageActions(messageElement, messageData);
        }, 500); // 500ms long press
    });

    messageElement.addEventListener('touchend', () => {
        clearTimeout(pressTimer);
    });

    messageElement.addEventListener('touchmove', () => {
        clearTimeout(pressTimer);
    });

    // Right-click for desktop
    messageElement.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showMessageActions(messageElement, messageData);
    });
}

function showMessageActions(messageElement, messageData) {
    // Remove any existing action menus
    document.querySelectorAll('.message-actions').forEach(el => el.remove());

    // Create action menu
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'message-actions';

    const replyBtn = document.createElement('button');
    replyBtn.className = 'message-action-btn';
    replyBtn.innerHTML = '↩️';
    replyBtn.title = 'Reply';
    replyBtn.addEventListener('click', () => {
        setReplyTo(messageData);
        actionsDiv.remove();
    });

    actionsDiv.appendChild(replyBtn);

    // Position relative to message
    messageElement.style.position = 'relative';
    messageElement.appendChild(actionsDiv);

    // Remove on click outside
    setTimeout(() => {
        document.addEventListener('click', function removeActions(e) {
            if (!actionsDiv.contains(e.target)) {
                actionsDiv.remove();
                document.removeEventListener('click', removeActions);
            }
        });
    }, 100);
}

// Update sendMessage to include reply_to
const originalSendMessage = window.sendMessage;
window.sendMessage = function () {
    const msg = msgInput.value.trim();
    if (msg) {
        const messageData = {
            msg: msg,
            type: 'text'
        };

        // Add reply_to if replying
        if (replyingToMessage) {
            messageData.reply_to = replyingToMessage.id;
        }

        // Send to server
        socket.emit('chat_message', messageData);

        // Show locally immediately (Optimistic UI)
        addMessage({
            user: myUsername,
            msg: msg,
            type: 'text',
            timestamp: Date.now() / 1000,
            reply_to: replyingToMessage ? replyingToMessage.id : null,
            reply_context: replyingToMessage
        }, false);

        msgInput.value = '';
        cancelReply();
    }
};

// Override the original addMessage to support reply context
const originalAddMessage = window.addMessage;
window.addMessage = function (data, showNotification = true) {
    if (!chatWindow) {
        console.error('Chat window not found');
        return;
    }

    const div = document.createElement('div');
    const isMe = data.user === myUsername;
    div.className = `message ${isMe ? 'me' : 'other'}`;

    // Store message data for reply functionality
    div.dataset.messageId = data.id;
    div.dataset.messageUser = data.user;
    div.dataset.messageType = data.type;

    // Add reply context if this is a reply
    if (data.reply_to && data.reply_context) {
        const replyContext = document.createElement('div');
        replyContext.className = 'message-reply-context';

        const replyAuthor = document.createElement('div');
        replyAuthor.className = 'reply-author';
        replyAuthor.textContent = data.reply_context.user;

        const replyText = document.createElement('div');
        replyText.className = 'reply-text';

        if (data.reply_context.type === 'text') {
            replyText.textContent = data.reply_context.msg;
        } else if (data.reply_context.type === 'audio') {
            replyText.textContent = '🔊 Audio message';
        } else if (data.reply_context.type === 'video') {
            replyText.textContent = '📹 Video message';
        }

        replyContext.appendChild(replyAuthor);
        replyContext.appendChild(replyText);

        // Click to scroll to original message
        replyContext.addEventListener('click', () => {
            const originalMsg = document.querySelector(`[data-message-id="${data.reply_to}"]`);
            if (originalMsg) {
                originalMsg.scrollIntoView({ behavior: 'smooth', block: 'center' });
                originalMsg.style.background = 'rgba(0, 255, 204, 0.2)';
                setTimeout(() => {
                    originalMsg.style.background = '';
                }, 1000);
            }
        });

        div.appendChild(replyContext);
    }

    // Add message content
    if (data.type === 'text') {
        const textSpan = document.createElement('span');
        textSpan.innerText = data.msg;
        div.appendChild(textSpan);
    } else {
        // Call original addMessage for media types
        originalAddMessage.call(this, data, showNotification);
        return;
    }

    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Track oldest message timestamp for pagination
    if (!oldestMessageTimestamp || data.timestamp < oldestMessageTimestamp) {
        oldestMessageTimestamp = data.timestamp;
    }

    // Add reply handler
    addReplyHandlerToMessage(div, data);
};

// --- Message Pagination / Infinite Scroll ---

// Detect scroll to top
if (chatWindow) {
    chatWindow.addEventListener('scroll', () => {
        if (chatWindow.scrollTop === 0 && !isLoadingMessages && hasMoreMessages) {
            loadOlderMessages();
        }
    });
}

async function loadOlderMessages() {
    if (isLoadingMessages || !hasMoreMessages) return;

    isLoadingMessages = true;

    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = '<div class="loading-spinner"></div><span>Loading messages...</span>';
    chatWindow.insertBefore(loadingDiv, chatWindow.firstChild);

    // Save current scroll position
    const scrollHeightBefore = chatWindow.scrollHeight;

    try {
        const response = await fetch(`/api/messages/before?before=${oldestMessageTimestamp}&limit=20`);
        const result = await response.json();

        if (result.messages && result.messages.length > 0) {
            // Add messages to top
            result.messages.forEach(msg => {
                const div = document.createElement('div');
                const isMe = msg.user === myUsername;
                div.className = `message ${isMe ? 'me' : 'other'}`;
                div.dataset.messageId = msg.id;
                div.dataset.messageUser = msg.user;
                div.dataset.messageType = msg.type;

                if (msg.type === 'text') {
                    div.innerText = msg.msg;
                } else if (msg.type === 'audio') {
                    // Add audio element
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = msg.msg;
                    div.appendChild(audio);
                } else if (msg.type === 'video') {
                    // Add video element
                    const video = document.createElement('video');
                    video.controls = true;
                    video.src = msg.msg;
                    video.className = 'video-message-rect';
                    div.appendChild(video);
                }

                // Insert after loading indicator
                chatWindow.insertBefore(div, loadingDiv.nextSibling);

                // Add reply handler
                addReplyHandlerToMessage(div, msg);

                // Update oldest timestamp
                if (msg.timestamp < oldestMessageTimestamp) {
                    oldestMessageTimestamp = msg.timestamp;
                }
            });

            // Restore scroll position
            chatWindow.scrollTop = chatWindow.scrollHeight - scrollHeightBefore;

            hasMoreMessages = result.has_more;
        } else {
            hasMoreMessages = false;
        }
    } catch (error) {
        console.error('Error loading older messages:', error);
    } finally {
        loadingDiv.remove();
        isLoadingMessages = false;
    }
}

console.log('✅ Reply system, pagination, and permissions loaded');
