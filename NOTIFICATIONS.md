# Browser Notification System Guide

## How It Works (No Account/APK Needed!)

This app uses the **Web Notifications API** - a built-in browser feature that works on:
- ✅ Desktop browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile browsers (Chrome Mobile, Safari iOS, Firefox Mobile)
- ✅ No app installation required
- ✅ No account needed
- ✅ Works directly in the browser

---

## How Notifications Work

### 1. **Permission Request**
When you first use the app, the browser will ask for notification permission:
- **Desktop**: Shows a popup asking "Allow notifications?"
- **Mobile**: Shows a system notification permission dialog

**User clicks "Allow"** → Notifications are enabled!

### 2. **When Notifications Appear**
Notifications are shown when:
- ✅ You receive a new message from another user
- ✅ Someone pings you
- ✅ The browser tab/window is **not focused** (you're on another tab/app)

### 3. **Notification Features**
- **Title**: Shows "🔔 New Message"
- **Body**: Shows sender name and message preview
- **Auto-close**: Closes after 5 seconds
- **Click to focus**: Clicking notification brings you back to the app
- **No duplicates**: Replaces previous notifications (tagged system)

---

## Browser Support

| Browser | Desktop | Mobile | Notes |
|---------|---------|--------|-------|
| Chrome | ✅ | ✅ | Full support |
| Firefox | ✅ | ✅ | Full support |
| Safari | ✅ | ✅ | iOS 16.4+ required |
| Edge | ✅ | ✅ | Full support |
| Opera | ✅ | ✅ | Full support |

---

## How to Enable Notifications

### First Time:
1. Open the app in your browser
2. Click anywhere on the page (triggers permission request)
3. Browser shows permission dialog
4. Click **"Allow"** or **"Allow notifications"**

### Check Status:
- **Granted**: Notifications will work automatically
- **Denied**: You need to enable in browser settings
- **Default**: Permission will be requested on next interaction

---

## Mobile-Specific Notes

### iOS Safari:
- Requires iOS 16.4 or later
- Must be added to home screen for best experience
- Notifications work even when Safari is closed (if added to home screen)

### Android Chrome:
- Works in regular browser
- Better experience if added to home screen
- Shows in system notification tray

---

## How to Re-enable Notifications (If Denied)

### Chrome/Edge:
1. Click the lock icon in address bar
2. Find "Notifications"
3. Change to "Allow"

### Firefox:
1. Click the lock icon in address bar
2. Click "More Information"
3. Go to "Permissions" tab
4. Change "Notifications" to "Allow"

### Safari (Mac):
1. Safari → Settings → Websites → Notifications
2. Find your site
3. Change to "Allow"

### Safari (iOS):
1. Settings → Safari → Notifications
2. Enable for your site

### Mobile Chrome:
1. Tap menu (3 dots)
2. Settings → Site Settings → Notifications
3. Find your site and enable

---

## Technical Details

### How It Works Without Account:
- Uses **browser's built-in Notification API**
- Permission is stored per domain (not per user)
- Works with any user logged into the app
- No server-side notification service needed

### How It Works Without APK:
- Pure web technology (HTML5/JavaScript)
- No native app installation required
- Works in any modern browser
- Can be "installed" as PWA (Progressive Web App) for better experience

### Connection Stability:
- **Auto-reconnection**: If connection drops, automatically reconnects
- **Message recovery**: On reconnection, loads recent messages
- **Connection status**: Visual indicator shows connection state
- **Multiple transport**: Tries WebSocket first, falls back to polling

---

## Testing Notifications

### Test on Desktop:
1. Open app in browser
2. Allow notifications
3. Open another tab or minimize browser
4. Send a message from another device/user
5. Notification should appear

### Test on Mobile:
1. Open app in mobile browser
2. Allow notifications
3. Switch to another app or lock screen
4. Send a message from another device
5. Notification should appear in notification tray

---

## Troubleshooting

### Notifications Not Showing:
1. **Check permission**: Make sure notifications are allowed
2. **Check browser support**: Use a modern browser
3. **Check tab focus**: Notifications only show when tab is hidden
4. **Check Do Not Disturb**: Disable DND mode on your device
5. **Check browser settings**: Some browsers block notifications by default

### Permission Denied:
- Follow the "Re-enable" steps above
- Some browsers require HTTPS for notifications (production only)

### Notifications Work But Don't Click:
- Make sure the app is still running
- Check if browser allows notification clicks
- Some browsers require user interaction first

---

## Privacy & Security

- ✅ Notifications are handled by your browser
- ✅ No third-party services involved
- ✅ No tracking or analytics
- ✅ Permission is stored locally in your browser
- ✅ You can revoke permission anytime

---

## Advanced: PWA Installation (Optional)

For even better notification experience on mobile:

1. **Add to Home Screen**:
   - iOS Safari: Share → Add to Home Screen
   - Android Chrome: Menu → Add to Home Screen

2. **Benefits**:
   - Notifications work even when browser is closed
   - App-like experience
   - Better performance
   - Offline capability (future feature)

---

## Summary

**No Account Needed**: Uses browser's built-in notification system
**No APK Needed**: Pure web technology, works in any browser
**Automatic**: Once enabled, works automatically
**Cross-Platform**: Works on desktop and mobile
**Privacy-Focused**: No third-party services, all handled by browser

The notification system is ready to use! Just allow permissions when prompted. 🎉

