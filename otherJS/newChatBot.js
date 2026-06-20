// Initialize current time in first message
document.addEventListener("DOMContentLoaded", function() {
    // Set the time for the first message
    const firstMessageTime = document.getElementById('first-message-time');
    if (firstMessageTime) {
        firstMessageTime.textContent = formatDate(new Date());
    }

    // Setup form submission
    setupChatForm();
});

// Global variables
const BOT_IMG = "../Images/illustration-new/home-bot-img.png";
const PERSON_IMG = "../Images/illustration/person.png"; // Add a person icon to your images folder
const BOT_NAME = "PsycheCare Assistant";
const PERSON_NAME = "You";

function setupChatForm() {
    const msgerForm = document.querySelector(".msger-inputarea");
    const msgerInput = document.querySelector(".msger-input");
    const msgerChat = document.querySelector(".msger-chat");

    if (msgerForm) {
        msgerForm.addEventListener("submit", event => {
            event.preventDefault();
            const msgText = msgerInput.value.trim();
            if (!msgText) return;

            // Add user message to chat
            appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
            msgerInput.value = "";

            // Show typing indicator
            showTypingIndicator();

            // Call the Flask API
            fetchBotResponse(msgText);
        });
    }
}

function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function appendMessage(name, img, side, text) {
    const msgerChat = document.querySelector(".msger-chat");

    const safeName = escapeHtml(name);
    const safeImg = escapeHtml(img);
    const safeText = escapeHtml(text);

    const msgHTML = `
    <div class="msg ${side}-msg">
        <div class="msg-img">
            <img src="${safeImg}" alt="${safeName}">
        </div>
        <div class="msg-bubble">
            <div class="msg-info">
                <div class="msg-info-name">${safeName}</div>
                <div class="msg-info-time">${formatDate(new Date())}</div>
            </div>
            <div class="msg-text">${safeText}</div>
        </div>
    </div>
    `;
    
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop = msgerChat.scrollHeight;
}

function showTypingIndicator() {
    const msgerChat = document.querySelector(".msger-chat");
    
    const typingHTML = `
    <div class="msg left-msg typing-indicator">
        <div class="msg-img">
            <img src="${BOT_IMG}" alt="${BOT_NAME}">
        </div>
        <div class="msg-bubble">
            <div class="typing">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    </div>
    `;
    
    msgerChat.insertAdjacentHTML("beforeend", typingHTML);
    msgerChat.scrollTop = msgerChat.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.querySelector(".typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function fetchBotResponse(userText) {
    try {
        // Call the Flask API endpoint
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userText })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add the bot's response to the chat
        appendMessage(BOT_NAME, BOT_IMG, "left", data.response);
        
    } catch (error) {
        console.error('Error fetching response from API:', error);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Show error message in chat
        appendMessage(BOT_NAME, BOT_IMG, "left", "Sorry, I'm having trouble connecting to my brain right now. Please try again later.");
    }
}

function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();
    return `${h.slice(-2)}:${m.slice(-2)}`;
}