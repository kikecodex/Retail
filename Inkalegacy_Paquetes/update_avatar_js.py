from PIL import Image
import base64
import io
import os

# Paths
IMAGE_PATH = 'C:/Users/Hp/.gemini/antigravity/brain/d53f92e6-c756-4a2d-9054-b7ab8bdce899/uploaded_image_1768344219641.jpg'
JS_PATH = r'c:\Users\Hp\Desktop\Inkalegacy_Paquetes\scripts\agent_integration.js'

def optimize_image_to_base64(image_path):
    img = Image.open(image_path)
    # Resize to resonable icon size
    img.thumbnail((150, 150))
    
    # Convert to RGB if RGBA (jpeg doesn't support alpha)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
        
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

def update_js_file(js_path, base64_img):
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we already injected code
    marker = "// -- CUSTOM AVATAR INJECTION --"
    
    injection_code = f"""
{marker}
const CUSTOM_AVATAR_BS64 = "{base64_img}";

document.addEventListener('DOMContentLoaded', () => {{
    // Update Bubble Icon
    const bubbleIcon = document.querySelector('.chat-bubble i');
    const bubbleContainer = document.querySelector('.chat-bubble');
    if(bubbleIcon && bubbleContainer) {{
        const img = document.createElement('img');
        img.src = CUSTOM_AVATAR_BS64;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.borderRadius = '50%';
        img.style.objectFit = 'cover';
        img.alt = 'Chat';
        bubbleIcon.replaceWith(img);
    }}

    // Update Chat Header Avatar
    const headerAvatar = document.querySelector('.chat-avatar');
    if(headerAvatar) {{
        headerAvatar.src = CUSTOM_AVATAR_BS64;
    }}
    
    // Also update any other avatars if needed
    const botMessages = document.querySelectorAll('.message.bot');
    // If you want to add avatar to messages later
}});
"""

    if marker in content:
        # Remove old injection first (simple way: split and keep first part)
        content = content.split(marker)[0]
    
    new_content = content + injection_code
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("JS file updated successfully with new avatar.")

if __name__ == "__main__":
    try:
        b64 = optimize_image_to_base64(IMAGE_PATH)
        update_js_file(JS_PATH, b64)
    except Exception as e:
        print(f"Error: {e}")
