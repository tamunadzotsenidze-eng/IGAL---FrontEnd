/**
 * IGAL Chat Widget - Enterprise-Grade Embeddable Chat Interface
 * Copyright (c) 2025 IGAL
 * Version: 2.0.0 - Enhanced Edition
 *
 * Features:
 * - Smooth animations and transitions
 * - Typing indicators
 * - Message timestamps
 * - Copy to clipboard
 * - Keyboard shortcuts
 * - Responsive design
 * - Performance optimized
 */

(function() {
  'use strict';

  // Configuration
  var config = {
    apiUrl: 'https://igal-backend-qnv4kru4hq-ey.a.run.app',
    position: 'bottom-right',
    theme: 'light',
    primaryColor: '#FDB022',
    secondaryColor: '#F59E0B',
    textColor: '#1F2937',
    showTimestamps: true,
    animationDuration: 300
  };

  // State
  var state = {
    isOpen: false,
    isTyping: false,
    messageCount: 0
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

    injectStyles();
    createWidgetButton();
    createChatWindow();
    attachEventListeners();
  }

  function injectStyles() {
    if (document.getElementById('igal-widget-styles')) return;

    var style = document.createElement('style');
    style.id = 'igal-widget-styles';
    style.textContent = `
      @keyframes igal-slide-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      @keyframes igal-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      @keyframes igal-typing-dot {
        0%, 60%, 100% {
          transform: translateY(0);
          opacity: 0.7;
        }
        30% {
          transform: translateY(-10px);
          opacity: 1;
        }
      }

      @keyframes igal-pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
      }

      @keyframes igal-shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
      }

      .igal-message-enter {
        animation: igal-slide-up 0.3s ease-out;
      }

      .igal-widget-open {
        animation: igal-fade-in 0.2s ease-out;
      }

      .igal-copy-btn {
        opacity: 0;
        transition: opacity 0.2s;
      }

      .igal-message-bubble:hover .igal-copy-btn {
        opacity: 1;
      }

      #igal-messages::-webkit-scrollbar {
        width: 6px;
      }

      #igal-messages::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
      }

      #igal-messages::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
      }

      #igal-messages::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
      }

      .igal-quick-reply {
        display: inline-block;
        padding: 8px 16px;
        margin: 4px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.2s;
      }

      .igal-quick-reply:hover {
        background: ${config.primaryColor};
        color: white;
        border-color: ${config.primaryColor};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
      }
    `;
    document.head.appendChild(style);
  }

  function createWidgetButton() {
    var button = document.createElement('button');
    button.id = 'igal-chat-button';
    button.setAttribute('aria-label', 'Open IGAL Chat');
    button.innerHTML = `
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;

    button.style.cssText = `
      position: fixed;
      ${getPositionStyles()}
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: linear-gradient(135deg, ${config.primaryColor} 0%, ${config.secondaryColor} 100%);
      color: white;
      border: none;
      cursor: pointer;
      box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
      z-index: 999998;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    `;

    button.onmouseover = function() {
      button.style.transform = 'scale(1.1) rotate(5deg)';
      button.style.boxShadow = '0 12px 32px rgba(102, 126, 234, 0.5)';
    };

    button.onmouseout = function() {
      button.style.transform = 'scale(1) rotate(0deg)';
      button.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.4)';
    };

    document.body.appendChild(button);
  }

  function createChatWindow() {
    var container = document.createElement('div');
    container.id = 'igal-chat-widget';
    container.setAttribute('role', 'dialog');
    container.setAttribute('aria-label', 'IGAL Chat Window');
    container.style.cssText = `
      position: fixed;
      ${getPositionStyles()}
      width: 400px;
      height: 650px;
      max-width: calc(100vw - 32px);
      max-height: calc(100vh - 100px);
      background: white;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.2);
      z-index: 999999;
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    `;

    // Header with gradient
    var header = document.createElement('div');
    header.style.cssText = `
      background: linear-gradient(135deg, ${config.primaryColor} 0%, ${config.secondaryColor} 100%);
      color: white;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    `;
    header.innerHTML = `
      <div style="flex: 1;">
        <h3 style="margin: 0; font-size: 20px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
          <span style="display: inline-block; width: 10px; height: 10px; background: #48bb78; border-radius: 50%; box-shadow: 0 0 8px #48bb78;"></span>
          IGAL ასისტენტი
        </h3>
        <p style="margin: 4px 0 0 18px; font-size: 13px; opacity: 0.95;">საგადასახადო და ფინანსური კანონები</p>
      </div>
      <button id="igal-close-button" aria-label="Close chat" style="
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        cursor: pointer;
        font-size: 24px;
        padding: 8px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        transition: all 0.2s;
      ">&times;</button>
    `;

    var closeBtn = header.querySelector('#igal-close-button');
    closeBtn.onmouseover = function() { this.style.background = 'rgba(255,255,255,0.3)'; };
    closeBtn.onmouseout = function() { this.style.background = 'rgba(255,255,255,0.2)'; };

    // Messages container
    var messagesContainer = document.createElement('div');
    messagesContainer.id = 'igal-messages';
    messagesContainer.style.cssText = `
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      background: linear-gradient(to bottom, #f9fafb 0%, #ffffff 100%);
    `;

    // Welcome message with quick replies
    var welcomeTime = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    messagesContainer.innerHTML = `
      <div class="igal-message-enter" style="
        background: white;
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid ${config.primaryColor};
      ">
        <p style="margin: 0; color: ${config.textColor}; font-size: 15px; line-height: 1.7;">
          👋 გამარჯობა! მე ვარ IGAL, თქვენი ასისტენტი საქართველოს საგადასახადო და ფინანსური კანონმდებლობაში. როგორ შემიძლია დაგეხმაროთ?
        </p>
        ${config.showTimestamps ? `<div style="margin-top: 8px; font-size: 11px; color: #9ca3af;">${welcomeTime}</div>` : ''}
      </div>
      <div style="margin: 16px 0;">
        <p style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">სწრაფი კითხვები:</p>
        <div id="igal-quick-replies">
          <button class="igal-quick-reply" data-message="რა არის ფიქსირებული გადასახადი?">💰 ფიქსირებული გადასახადი</button>
          <button class="igal-quick-reply" data-message="როგორ გამოვთვალო დღგ?">📊 დღგ გამოთვლა</button>
          <button class="igal-quick-reply" data-message="ბიზნესის რეგისტრაცია">📝 ბიზნესის რეგისტრაცია</button>
        </div>
      </div>
    `;

    // Input container
    var inputContainer = document.createElement('div');
    inputContainer.style.cssText = `
      padding: 16px 20px;
      background: white;
      border-top: 1px solid #e5e7eb;
      display: flex;
      gap: 12px;
      box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    `;

    var input = document.createElement('input');
    input.id = 'igal-input';
    input.type = 'text';
    input.placeholder = 'დასვით კითხვა...';
    input.setAttribute('aria-label', 'Message input');
    input.style.cssText = `
      flex: 1;
      padding: 14px 16px;
      border: 2px solid #e5e7eb;
      border-radius: 12px;
      font-size: 14px;
      outline: none;
      font-family: inherit;
      transition: border-color 0.2s;
    `;

    input.onfocus = function() {
      input.style.borderColor = config.primaryColor;
    };

    input.onblur = function() {
      input.style.borderColor = '#e5e7eb';
    };

    var sendButton = document.createElement('button');
    sendButton.id = 'igal-send-button';
    sendButton.setAttribute('aria-label', 'Send message');
    sendButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    sendButton.style.cssText = `
      padding: 14px 16px;
      background: linear-gradient(135deg, ${config.primaryColor} 0%, ${config.secondaryColor} 100%);
      color: white;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      font-size: 18px;
      font-weight: bold;
      transition: all 0.2s;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    `;

    sendButton.onmouseover = function() {
      sendButton.style.transform = 'translateY(-2px)';
      sendButton.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)';
    };

    sendButton.onmouseout = function() {
      sendButton.style.transform = 'translateY(0)';
      sendButton.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
    };

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

    button.addEventListener('click', openWidget);
    closeButton.addEventListener('click', closeWidget);
    sendButton.addEventListener('click', sendMessage);

    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Quick replies
    document.addEventListener('click', function(e) {
      if (e.target.classList.contains('igal-quick-reply')) {
        var message = e.target.getAttribute('data-message');
        input.value = message;
        sendMessage();
      }
    });

    // Keyboard shortcut: ESC to close
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && state.isOpen) {
        closeWidget();
      }
    });
  }

  function openWidget() {
    var button = document.getElementById('igal-chat-button');
    var widget = document.getElementById('igal-chat-widget');
    var input = document.getElementById('igal-input');

    widget.style.display = 'flex';
    widget.classList.add('igal-widget-open');
    button.style.display = 'none';
    state.isOpen = true;

    setTimeout(function() {
      input.focus();
    }, 100);
  }

  function closeWidget() {
    var button = document.getElementById('igal-chat-button');
    var widget = document.getElementById('igal-chat-widget');

    widget.style.display = 'none';
    button.style.display = 'flex';
    state.isOpen = false;
  }

  function sendMessage() {
    var input = document.getElementById('igal-input');
    var message = input.value.trim();

    if (!message || state.isTyping) return;

    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';
    state.messageCount++;

    // Show typing indicator
    state.isTyping = true;
    var typingElement = addTypingIndicator();

    // Send to backend API
    fetch(config.apiUrl + '/api/widget/', {
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
      if (!response.ok) {
        throw new Error('HTTP ' + response.status);
      }
      return response.json();
    })
    .then(function(data) {
      removeTypingIndicator(typingElement);
      state.isTyping = false;
      addMessage(data.response || 'Sorry, I encountered an error.', 'assistant');
    })
    .catch(function(error) {
      removeTypingIndicator(typingElement);
      state.isTyping = false;
      addMessage('⚠️ Sorry, I could not connect to the server. Please check your connection and try again.', 'assistant', true);
      console.error('IGAL Widget Error:', error);
    });
  }

  function addMessage(text, sender, isError) {
    var messagesContainer = document.getElementById('igal-messages');
    var messageDiv = document.createElement('div');
    var isUser = sender === 'user';
    var timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    messageDiv.className = 'igal-message-enter';
    messageDiv.style.cssText = `
      display: flex;
      justify-content: ${isUser ? 'flex-end' : 'flex-start'};
      margin-bottom: 16px;
    `;

    var bubble = document.createElement('div');
    bubble.className = 'igal-message-bubble';
    bubble.style.cssText = `
      max-width: 80%;
      padding: 14px 16px;
      border-radius: ${isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px'};
      background: ${isUser ? `linear-gradient(135deg, ${config.primaryColor} 0%, ${config.secondaryColor} 100%)` : (isError ? '#fee2e2' : 'white')};
      color: ${isUser ? 'white' : (isError ? '#dc2626' : config.textColor)};
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      word-wrap: break-word;
      position: relative;
    `;

    var textP = document.createElement('p');
    textP.style.cssText = 'margin: 0; font-size: 14px; line-height: 1.6; white-space: pre-wrap;';
    textP.textContent = text;

    bubble.appendChild(textP);

    if (config.showTimestamps) {
      var timeDiv = document.createElement('div');
      timeDiv.style.cssText = `margin-top: 6px; font-size: 11px; opacity: ${isUser ? '0.8' : '0.6'};`;
      timeDiv.textContent = timestamp;
      bubble.appendChild(timeDiv);
    }

    // Copy button for assistant messages
    if (!isUser && !isError) {
      var copyBtn = document.createElement('button');
      copyBtn.className = 'igal-copy-btn';
      copyBtn.innerHTML = '📋';
      copyBtn.title = 'Copy message';
      copyBtn.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0,0,0,0.05);
        border: none;
        border-radius: 6px;
        padding: 4px 8px;
        cursor: pointer;
        font-size: 12px;
      `;
      copyBtn.onclick = function() {
        copyToClipboard(text);
        copyBtn.innerHTML = '✓';
        setTimeout(function() { copyBtn.innerHTML = '📋'; }, 2000);
      };
      bubble.appendChild(copyBtn);
    }

    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);

    // Smooth scroll to bottom
    messagesContainer.scrollTo({
      top: messagesContainer.scrollHeight,
      behavior: 'smooth'
    });
  }

  function addTypingIndicator() {
    var messagesContainer = document.getElementById('igal-messages');
    var typingDiv = document.createElement('div');
    typingDiv.className = 'igal-typing igal-message-enter';
    typingDiv.style.cssText = `
      display: flex;
      justify-content: flex-start;
      margin-bottom: 16px;
    `;

    var bubble = document.createElement('div');
    bubble.style.cssText = `
      padding: 14px 20px;
      border-radius: 16px 16px 16px 4px;
      background: white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      display: flex;
      gap: 6px;
      align-items: center;
    `;

    for (var i = 0; i < 3; i++) {
      var dot = document.createElement('span');
      dot.style.cssText = `
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, ${config.primaryColor} 0%, ${config.secondaryColor} 100%);
        animation: igal-typing-dot 1.4s infinite;
        animation-delay: ${i * 0.2}s;
      `;
      bubble.appendChild(dot);
    }

    typingDiv.appendChild(bubble);
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTo({
      top: messagesContainer.scrollHeight,
      behavior: 'smooth'
    });

    return typingDiv;
  }

  function removeTypingIndicator(typingElement) {
    if (typingElement && typingElement.parentNode) {
      typingElement.style.opacity = '0';
      setTimeout(function() {
        if (typingElement.parentNode) {
          typingElement.parentNode.removeChild(typingElement);
        }
      }, 200);
    }
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      var textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
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
