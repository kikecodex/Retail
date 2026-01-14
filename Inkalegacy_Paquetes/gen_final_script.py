from PIL import Image
import base64
import io

IMAGE_PATH = 'C:/Users/Hp/.gemini/antigravity/brain/d53f92e6-c756-4a2d-9054-b7ab8bdce899/uploaded_image_1768344219641.jpg'
OUTPUT_JS = 'C:/Users/Hp/.gemini/antigravity/brain/d53f92e6-c756-4a2d-9054-b7ab8bdce899/agent_integration_fixed.js'

def get_base64(image_path):
    img = Image.open(image_path)
    img.thumbnail((150, 150)) # Avatar size check
    if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"

try:
    base64_img = get_base64(IMAGE_PATH)
except Exception as e:
    print(f"Error processing image: {e}")
    exit(1)

js_content = f"""/**
 * Agent Integration Script - Inka Legacy Tours
 * Handles the UI and logic for the Hybrid AI Assistant (Llamita)
 * FIXED VERSION - MANUAL UPLOAD
 */

const chatWindow = document.getElementById('chat-window');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-user-input');
const chatBubble = document.querySelector('.chat-bubble');
const chatNoti = document.querySelector('.chat-noti');

let isChatOpen = false;

// Toggle Chat Window
function toggleChat() {{
    isChatOpen = !isChatOpen;
    chatWindow.classList.toggle('active');
    chatBubble.classList.toggle('active');

    if (isChatOpen) {{
        chatNoti.style.display = 'none';
        chatInput.focus();
    }}
}}

const API_URL = "https://llamita-agent.onrender.com";

async function sendMessage() {{
    const text = chatInput.value.trim();
    if (text === '') return;

    addMessage(text, 'user');
    chatInput.value = '';

    const thinkingMessage = document.createElement('div');
    thinkingMessage.classList.add('message', 'bot', 'thinking');
    thinkingMessage.textContent = "...";
    chatMessages.appendChild(thinkingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {{
        const response = await fetch(`${{API_URL}}/api/chat`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ message: text, sender: 'web_user' }})
        }});

        const data = await response.json();
        chatMessages.removeChild(thinkingMessage);
        addMessage(data.response, 'bot');
    }} catch (error) {{
        console.error("Error calling API:", error);
        chatMessages.removeChild(thinkingMessage);
        addMessage("Lo siento, estoy teniendo problemas para conectarme. ¿Podrías intentar por WhatsApp?", 'bot');
    }}
}}

function sendQuickMessage(text) {{
    chatInput.value = text;
    sendMessage();
}}

function addMessage(text, sender) {{
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}}

function handleChatKey(event) {{
    if (event.key === 'Enter') {{
        sendMessage();
    }}
}}

setTimeout(() => {{
    if (!isChatOpen) {{
        chatNoti.style.display = 'block';
    }}
}}, 3000);

window.toggleChat = toggleChat;
window.sendMessage = sendMessage;
window.sendQuickMessage = sendQuickMessage;
window.handleChatKey = handleChatKey;

// -- CUSTOM AVATAR INJECTION (ROBUST & CLEAN) --
const CUSTOM_AVATAR_BS64 = "{base64_img}";

function applyCustomAvatar() {{
    const bubbleIcon = document.querySelector('.chat-bubble i');
    const bubbleContainer = document.querySelector('.chat-bubble');
    
    if (bubbleIcon && bubbleContainer && !bubbleIcon.classList.contains('avatar-replaced')) {{
        const img = document.createElement('img');
        img.src = CUSTOM_AVATAR_BS64;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.borderRadius = '50%';
        img.style.objectFit = 'cover';
        img.alt = 'Chat';
        bubbleIcon.replaceWith(img);
        if (img) img.classList.add('avatar-replaced');
    }}

    const headerAvatar = document.querySelector('.chat-avatar');
    if (headerAvatar && headerAvatar.src !== CUSTOM_AVATAR_BS64) {{
        headerAvatar.src = CUSTOM_AVATAR_BS64;
    }}
}}

applyCustomAvatar();
document.addEventListener('DOMContentLoaded', applyCustomAvatar);
const avatarInterval = setInterval(applyCustomAvatar, 500);
setTimeout(() => clearInterval(avatarInterval), 5000);
"""

with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Generated clean JS file at: {OUTPUT_JS}")
