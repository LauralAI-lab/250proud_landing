(function() {
    // 1. Inject HTML for the chat widget
    const chatHTML = `
        <div class="lauralai-chat-widget">
            <div class="lauralai-chat-window" id="lauralaiChatWindow">
                <div class="lauralai-chat-header">
                    <div class="lauralai-header-title">
                        <span class="lauralai-online-dot"></span>
                        <span>LauralAI Support</span>
                    </div>
                    <button class="lauralai-close-btn" id="lauralaiCloseBtn">&times;</button>
                </div>
                <div class="lauralai-chat-messages" id="lauralaiChatMessages">
                    <div class="lauralai-message assistant">
                        Hi! I'm LauralAI, your expert marketing assistant for the 250PROUD platform. How can I help you leverage your custom coloring book today?
                    </div>
                    <div class="lauralai-typing-indicator" id="lauralaiTypingIndicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
                <div class="lauralai-chat-input-area">
                    <input type="text" class="lauralai-chat-input" id="lauralaiChatInput" placeholder="Ask a question..." autocomplete="off">
                    <button class="lauralai-chat-send" id="lauralaiSendBtn">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
            </div>
            
            <button class="lauralai-chat-button" id="lauralaiChatBtn" title="Chat with LauralAI">
                <span class="lauralai-btn-top">ASK</span>
                <span class="lauralai-btn-bottom">LauralAI</span>
            </button>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatHTML);

    // 2. Element References
    const chatBtn = document.getElementById('lauralaiChatBtn');
    const closeBtn = document.getElementById('lauralaiCloseBtn');
    const chatWindow = document.getElementById('lauralaiChatWindow');
    const chatInput = document.getElementById('lauralaiChatInput');
    const sendBtn = document.getElementById('lauralaiSendBtn');
    const messagesContainer = document.getElementById('lauralaiChatMessages');
    const typingIndicator = document.getElementById('lauralaiTypingIndicator');

    let messages = [];

    // 3. UI Logic
    const toggleChat = () => {
        chatWindow.classList.toggle('open');
        if (chatWindow.classList.contains('open')) {
            chatInput.focus();
        }
    };

    chatBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    const scrollToBottom = () => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const addMessageToUI = (content, role) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `lauralai-message ${role}`;
        
        // Convert URLs to clickable links if assistant
        if (role === 'assistant') {
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            content = content.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
        }
        
        msgDiv.innerHTML = content.replace(/\n/g, '<br>');
        
        messagesContainer.insertBefore(msgDiv, typingIndicator);
        scrollToBottom();
    };

    const setTyping = (isTyping) => {
        typingIndicator.style.display = isTyping ? 'block' : 'none';
        scrollToBottom();
    };

    // 4. API Call Logic
    const handleSend = async () => {
        const text = chatInput.value.trim();
        if (!text) return;

        // User message
        chatInput.value = '';
        addMessageToUI(text, 'user');
        messages.push({ role: 'user', content: text });

        setTyping(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages })
            });

            const data = await response.json();
            
            setTyping(false);

            if (data.reply) {
                addMessageToUI(data.reply, 'assistant');
                messages.push({ role: 'assistant', content: data.reply });
            } else {
                addMessageToUI("I'm sorry, I encountered an error. Please email info@250proud.net for support.", 'assistant');
            }
        } catch (err) {
            console.error('Chat Error:', err);
            setTyping(false);
            addMessageToUI("I'm sorry, I cannot connect to the server right now. Please email info@250proud.net for support.", 'assistant');
        }
    };

    sendBtn.addEventListener('click', handleSend);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
})();
