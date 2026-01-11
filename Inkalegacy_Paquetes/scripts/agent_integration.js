/**
 * Agent Integration Script - Inka Legacy Tours
 * Handles the UI and logic for the Hybrid AI Assistant (Llamita)
 */

const chatWindow = document.getElementById('chat-window');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-user-input');
const chatBubble = document.querySelector('.chat-bubble');
const chatNoti = document.querySelector('.chat-noti');

let isChatOpen = false;

// Toggle Chat Window
function toggleChat() {
    isChatOpen = !isChatOpen;
    chatWindow.classList.toggle('active');
    chatBubble.classList.toggle('active');

    // Hide notification when opened
    if (isChatOpen) {
        chatNoti.style.display = 'none';
        chatInput.focus();
    }
}

// Configuración de la API (URL de Render del dashboard)
const API_URL = "https://llamita-agent.onrender.com";

// Send Message
async function sendMessage() {
    const text = chatInput.value.trim();
    if (text === '') return;

    // Add User Message
    addMessage(text, 'user');
    chatInput.value = '';

    // Show Thinking indicator
    const thinkingMessage = document.createElement('div');
    thinkingMessage.classList.add('message', 'bot', 'thinking');
    thinkingMessage.textContent = "...";
    chatMessages.appendChild(thinkingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, sender: 'web_user' })
        });

        const data = await response.json();
        chatMessages.removeChild(thinkingMessage);
        addMessage(data.response, 'bot');
    } catch (error) {
        console.error("Error calling API:", error);
        chatMessages.removeChild(thinkingMessage);
        addMessage("Lo siento, estoy teniendo problemas para conectarme. ¿Podrías intentar por WhatsApp?", 'bot');
    }
}

// Quick Message
function sendQuickMessage(text) {
    chatInput.value = text;
    sendMessage();
}

// Add Message to UI
function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle Enter Key
function handleChatKey(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Initial Animation
setTimeout(() => {
    if (!isChatOpen) {
        chatNoti.style.display = 'block';
    }
}, 3000);

// Global Exposure
window.toggleChat = toggleChat;
window.sendMessage = sendMessage;
window.sendQuickMessage = sendQuickMessage;
window.handleChatKey = handleChatKey;
