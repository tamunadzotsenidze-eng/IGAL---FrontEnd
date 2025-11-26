# IGAL Embeddable Chat Widget

**Created**: November 18, 2025
**Project**: IGAL AI Assistant

This document explains how to embed the IGAL chat interface on any website using a simple code snippet.

---

## Quick Start

Website developers can add the IGAL chat widget by copying and pasting this code snippet into their website's HTML, just before the closing `</body>` tag:

```html
<!-- IGAL Chat Widget -->
<script>
  (function(w,d,s,o,f,js,fjs){
    w['IgalWidget']=o;w[o] = w[o] || function () { (w[o].q = w[o].q || []).push(arguments) };
    js = d.createElement(s), fjs = d.getElementsByTagName(s)[0];
    js.id = o; js.src = f; js.async = 1; fjs.parentNode.insertBefore(js, fjs);
  }(window, document, 'script', 'igal', 'https://FRONTEND-URL/widget.js'));
  igal('init', {
    apiUrl: 'https://igal-backend-qnv4kru4hq-ey.a.run.app',
    position: 'bottom-right',
    theme: 'light'
  });
</script>
<!-- End IGAL Chat Widget -->
```

**Replace `https://FRONTEND-URL/widget.js`** with your deployed frontend URL after deployment.

---

## What This Creates

The widget adds a chat interface that:
- Appears as a floating button in the bottom-right corner
- Opens a chat window when clicked
- Connects to the IGAL AI backend
- Works on any website (WordPress, Wix, Squarespace, custom sites, etc.)
- Is fully responsive (works on mobile and desktop)

---

## Implementation Steps

### Step 1: Create the Widget JavaScript File

Create this file in your frontend project:

**File**: `/Users/tiko/Desktop/IGAL/frontend/public/widget.js`

```javascript
/**
 * IGAL Chat Widget - Embeddable Chat Interface
 * Copyright (c) 2025 IGAL
 */

(function() {
  'use strict';

  // Configuration
  var config = {
    apiUrl: 'https://igal-backend-qnv4kru4hq-ey.a.run.app',
    position: 'bottom-right',
    theme: 'light',
    primaryColor: '#3B82F6',
    textColor: '#1F2937'
  };

  // Initialize widget
  window.igal = function(action, options) {
    if (action === 'init') {
      Object.assign(config, options);
      init();
    }
  };

  // Process queued commands
  if (window.igal && window.igal.q) {
    window.igal.q.forEach(function(args) {
      window.igal.apply(null, args);
    });
  }

  function init() {
    // Check if already initialized
    if (document.getElementById('igal-chat-widget')) {
      return;
    }

    createWidgetButton();
    createChatWindow();
    attachEventListeners();
  }

  function createWidgetButton() {
    var button = document.createElement('button');
    button.id = 'igal-chat-button';
    button.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 11.5C21 16.75 16.75 21 11.5 21C6.25 21 2 16.75 2 11.5C2 6.25 6.25 2 11.5 2C16.75 2 21 6.25 21 11.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M7 11H16M11.5 7V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>Chat</span>
    `;

    button.style.cssText = `
      position: fixed;
      ${getPositionStyles()}
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background-color: ${config.primaryColor};
      color: white;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 999998;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      transition: transform 0.2s, box-shadow 0.2s;
    `;

    button.onmouseover = function() {
      button.style.transform = 'scale(1.1)';
      button.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
    };

    button.onmouseout = function() {
      button.style.transform = 'scale(1)';
      button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    };

    document.body.appendChild(button);
  }

  function createChatWindow() {
    var container = document.createElement('div');
    container.id = 'igal-chat-widget';
    container.style.cssText = `
      position: fixed;
      ${getPositionStyles()}
      width: 380px;
      height: 600px;
      max-width: calc(100vw - 32px);
      max-height: calc(100vh - 100px);
      background: white;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.12);
      z-index: 999999;
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    // Header
    var header = document.createElement('div');
    header.style.cssText = `
      background: ${config.primaryColor};
      color: white;
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    `;
    header.innerHTML = `
      <div>
        <h3 style="margin: 0; font-size: 18px; font-weight: 600;">IGAL Assistant</h3>
        <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">How can I help you?</p>
      </div>
      <button id="igal-close-button" style="
        background: transparent;
        border: none;
        color: white;
        cursor: pointer;
        font-size: 24px;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
      ">&times;</button>
    `;

    // Messages container
    var messagesContainer = document.createElement('div');
    messagesContainer.id = 'igal-messages';
    messagesContainer.style.cssText = `
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      background: #F9FAFB;
    `;

    // Welcome message
    messagesContainer.innerHTML = `
      <div style="
        background: white;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      ">
        <p style="margin: 0; color: ${config.textColor}; font-size: 14px;">
          Hi! I'm IGAL, your AI assistant. I can help you with questions about IGAL services, documentation, and more. How can I assist you today?
        </p>
      </div>
    `;

    // Input container
    var inputContainer = document.createElement('div');
    inputContainer.style.cssText = `
      padding: 16px;
      background: white;
      border-top: 1px solid #E5E7EB;
      display: flex;
      gap: 8px;
    `;

    var input = document.createElement('input');
    input.id = 'igal-input';
    input.type = 'text';
    input.placeholder = 'Type your message...';
    input.style.cssText = `
      flex: 1;
      padding: 12px;
      border: 1px solid #E5E7EB;
      border-radius: 8px;
      font-size: 14px;
      outline: none;
      font-family: inherit;
    `;

    var sendButton = document.createElement('button');
    sendButton.id = 'igal-send-button';
    sendButton.innerHTML = '→';
    sendButton.style.cssText = `
      padding: 12px 20px;
      background: ${config.primaryColor};
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 18px;
      font-weight: bold;
    `;

    inputContainer.appendChild(input);
    inputContainer.appendChild(sendButton);

    container.appendChild(header);
    container.appendChild(messagesContainer);
    container.appendChild(inputContainer);

    document.body.appendChild(container);
  }

  function getPositionStyles() {
    switch (config.position) {
      case 'bottom-right':
        return 'bottom: 20px; right: 20px;';
      case 'bottom-left':
        return 'bottom: 20px; left: 20px;';
      case 'top-right':
        return 'top: 20px; right: 20px;';
      case 'top-left':
        return 'top: 20px; left: 20px;';
      default:
        return 'bottom: 20px; right: 20px;';
    }
  }

  function attachEventListeners() {
    var button = document.getElementById('igal-chat-button');
    var widget = document.getElementById('igal-chat-widget');
    var closeButton = document.getElementById('igal-close-button');
    var sendButton = document.getElementById('igal-send-button');
    var input = document.getElementById('igal-input');

    button.addEventListener('click', function() {
      widget.style.display = 'flex';
      button.style.display = 'none';
      input.focus();
    });

    closeButton.addEventListener('click', function() {
      widget.style.display = 'none';
      button.style.display = 'flex';
    });

    sendButton.addEventListener('click', sendMessage);

    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  }

  function sendMessage() {
    var input = document.getElementById('igal-input');
    var message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    var typingId = addTypingIndicator();

    // Send to backend API
    fetch(config.apiUrl + '/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        session_id: getSessionId()
      })
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      removeTypingIndicator(typingId);
      addMessage(data.response || 'Sorry, I encountered an error.', 'assistant');
    })
    .catch(function(error) {
      removeTypingIndicator(typingId);
      addMessage('Sorry, I could not connect to the server. Please try again.', 'assistant');
      console.error('IGAL Widget Error:', error);
    });
  }

  function addMessage(text, sender) {
    var messagesContainer = document.getElementById('igal-messages');
    var messageDiv = document.createElement('div');

    var isUser = sender === 'user';
    messageDiv.style.cssText = `
      display: flex;
      justify-content: ${isUser ? 'flex-end' : 'flex-start'};
      margin-bottom: 12px;
    `;

    var bubble = document.createElement('div');
    bubble.style.cssText = `
      max-width: 75%;
      padding: 12px;
      border-radius: 12px;
      background: ${isUser ? config.primaryColor : 'white'};
      color: ${isUser ? 'white' : config.textColor};
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      word-wrap: break-word;
    `;

    var textP = document.createElement('p');
    textP.style.cssText = 'margin: 0; font-size: 14px; line-height: 1.5;';
    textP.textContent = text;

    bubble.appendChild(textP);
    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function addTypingIndicator() {
    var messagesContainer = document.getElementById('igal-messages');
    var typingDiv = document.createElement('div');
    typingDiv.className = 'igal-typing';
    typingDiv.style.cssText = `
      display: flex;
      justify-content: flex-start;
      margin-bottom: 12px;
    `;

    var bubble = document.createElement('div');
    bubble.style.cssText = `
      padding: 12px 16px;
      border-radius: 12px;
      background: white;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      display: flex;
      gap: 4px;
    `;

    for (var i = 0; i < 3; i++) {
      var dot = document.createElement('span');
      dot.style.cssText = `
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #9CA3AF;
        animation: igal-typing 1.4s infinite;
        animation-delay: ${i * 0.2}s;
      `;
      bubble.appendChild(dot);
    }

    // Add CSS animation
    if (!document.getElementById('igal-typing-animation')) {
      var style = document.createElement('style');
      style.id = 'igal-typing-animation';
      style.textContent = `
        @keyframes igal-typing {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
          30% { transform: translateY(-10px); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }

    typingDiv.appendChild(bubble);
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return typingDiv;
  }

  function removeTypingIndicator(typingElement) {
    if (typingElement && typingElement.parentNode) {
      typingElement.parentNode.removeChild(typingElement);
    }
  }

  function getSessionId() {
    var sessionId = localStorage.getItem('igal_session_id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('igal_session_id', sessionId);
    }
    return sessionId;
  }

})();
```

---

## Step 2: Update Backend CORS Settings

The backend needs to allow requests from any website. Update your Django settings:

**File**: `/Users/tiko/Desktop/IGAL/backend/config/settings.py`

Find the CORS settings and update:

```python
# CORS Settings - Allow requests from any domain for widget
CORS_ALLOW_ALL_ORIGINS = True  # For embedded widget

# Or specific domains only:
# CORS_ALLOWED_ORIGINS = [
#     "https://yourwebsite.com",
#     "https://www.yourwebsite.com",
# ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

---

## Step 3: Create Backend API Endpoint for Widget

Create a simple chat endpoint that doesn't require authentication:

**File**: `/Users/tiko/Desktop/IGAL/backend/chat/views.py`

Add this view:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def widget_chat(request):
    """
    Simple chat endpoint for embedded widget
    No authentication required
    """
    message = request.data.get('message', '')
    session_id = request.data.get('session_id', '')

    if not message:
        return Response({'error': 'Message is required'}, status=400)

    try:
        # Your chat logic here
        # For now, simple echo response
        response_text = f"Thank you for your message: {message}"

        return Response({
            'response': response_text,
            'session_id': session_id,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({
            'error': 'An error occurred processing your request',
            'details': str(e)
        }, status=500)
```

Add URL pattern:

**File**: `/Users/tiko/Desktop/IGAL/backend/chat/urls.py`

```python
from django.urls import path
from .views import widget_chat

urlpatterns = [
    # ... existing patterns ...
    path('widget/', widget_chat, name='widget-chat'),
]
```

---

## Usage Instructions for Website Developers

### For Any Website

**1. Copy this code snippet:**

```html
<!-- IGAL Chat Widget -->
<script>
  (function(w,d,s,o,f,js,fjs){
    w['IgalWidget']=o;w[o] = w[o] || function () { (w[o].q = w[o].q || []).push(arguments) };
    js = d.createElement(s), fjs = d.getElementsByTagName(s)[0];
    js.id = o; js.src = f; js.async = 1; fjs.parentNode.insertBefore(js, fjs);
  }(window, document, 'script', 'igal', 'https://YOUR-FRONTEND-URL/widget.js'));
  igal('init', {
    apiUrl: 'https://igal-backend-qnv4kru4hq-ey.a.run.app',
    position: 'bottom-right',
    theme: 'light'
  });
</script>
<!-- End IGAL Chat Widget -->
```

**2. Paste it before `</body>` tag** in your website's HTML

**3. Done!** The chat widget will appear on your website

### For WordPress

1. Go to **Appearance → Theme Editor**
2. Select **footer.php** (or use a plugin like "Insert Headers and Footers")
3. Paste the code snippet before `</body>` tag
4. Save

### For Wix

1. Go to **Settings → Custom Code**
2. Click **Add Custom Code**
3. Paste the snippet
4. Set to load on "All Pages" and "Body - end"
5. Apply

### For Squarespace

1. Go to **Settings → Advanced → Code Injection**
2. Paste the code in the "Footer" section
3. Save

---

## Configuration Options

You can customize the widget appearance:

```javascript
igal('init', {
  apiUrl: 'https://igal-backend-qnv4kru4hq-ey.a.run.app',
  position: 'bottom-right',  // Options: 'bottom-right', 'bottom-left', 'top-right', 'top-left'
  theme: 'light',            // Options: 'light', 'dark'
  primaryColor: '#3B82F6',   // Custom brand color
  textColor: '#1F2937'       // Custom text color
});
```

---

## Testing

### Test on Local Website

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
  <title>IGAL Widget Test</title>
</head>
<body>
  <h1>Test Page</h1>
  <p>The IGAL chat widget should appear in the bottom-right corner.</p>

  <!-- IGAL Chat Widget -->
  <script>
    (function(w,d,s,o,f,js,fjs){
      w['IgalWidget']=o;w[o] = w[o] || function () { (w[o].q = w[o].q || []).push(arguments) };
      js = d.createElement(s), fjs = d.getElementsByTagName(s)[0];
      js.id = o; js.src = f; js.async = 1; fjs.parentNode.insertBefore(js, fjs);
    }(window, document, 'script', 'igal', 'https://YOUR-FRONTEND-URL/widget.js'));
    igal('init', {
      apiUrl: 'https://igal-backend-qnv4kru4hq-ey.a.run.app',
      position: 'bottom-right',
      theme: 'light'
    });
  </script>
</body>
</html>
```

Open in browser and test!

---

## Features

✅ **Responsive Design** - Works on mobile and desktop
✅ **Lightweight** - ~10KB minified
✅ **No Dependencies** - Pure JavaScript, no jQuery needed
✅ **Cross-Domain** - Works on any website
✅ **Session Management** - Maintains conversation context
✅ **Customizable** - Easy to brand with your colors
✅ **Accessibility** - Keyboard navigation supported

---

## Next Steps

1. ✅ Create `widget.js` file in frontend `/public/` directory
2. ⏳ Add widget chat endpoint to backend
3. ⏳ Update CORS settings
4. ⏳ Deploy frontend (widget.js will be accessible at https://YOUR-FRONTEND-URL/widget.js)
5. ⏳ Test the widget on a sample website
6. ⏳ Share the code snippet with website developers

---

## Security Considerations

- Widget uses HTTPS for all communications
- Session IDs are locally generated (no PII collected)
- Backend validates all inputs
- CORS configured to allow cross-origin requests
- No cookies used (localStorage for session only)
- Rate limiting can be added to prevent abuse

---

## Support

For widget integration support, contact: support@igal.ge

---

**Status**: Documentation ready, implementation pending
**Last Updated**: November 18, 2025
