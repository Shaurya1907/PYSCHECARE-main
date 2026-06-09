// // Initialize current time in first message
// document.addEventListener("DOMContentLoaded", function() {
//     // Set the time for the first message
//     const firstMessageTime = document.getElementById('first-message-time');
//     if (firstMessageTime) {
//         firstMessageTime.textContent = formatDate(new Date());
//     }

//     // Setup form submission
//     setupChatForm();
// });

// // Global variables
// const BOT_IMG = "../Images/illustration-new/home-bot-img.png";
// const PERSON_IMG = "../Images/illustration/person.png"; // Add a person icon to your images folder
// const BOT_NAME = "PsycheCare Assistant";
// const PERSON_NAME = "You";

// // Mental health responses library - simplified version of the NLP model responses
// const mentalHealthResponses = {
//     "hello": ["Hello! How are you feeling today?", "Hi there! I'm here to chat. How are you doing?", "Hello! How can I assist you with your mental health today?"],
//     "how are you": ["I'm here to help you! How are you feeling today?", "I'm good, thanks for asking! How about you?", "I'm functioning well. More importantly, how are you doing?"],
//     "sad": ["I'm sorry to hear that you're feeling sad. Would you like to talk about what's making you feel this way?", "Feeling sad is a normal emotion. Would sharing what triggered this feeling help?", "I understand feeling sad can be difficult. Would you like some strategies that might help lift your mood?"],
//     "anxious": ["Anxiety can be challenging. Taking slow deep breaths might help in the moment. Would you like to talk about what's causing your anxiety?", "I'm sorry you're feeling anxious. Sometimes focusing on the present moment can help. What specific concerns are on your mind?", "Anxiety is something many people experience. Would you like to discuss some coping strategies?"],
//     "stressed": ["Stress can definitely be overwhelming. Would you like to talk about what's causing your stress?", "I understand feeling stressed. Would you like some relaxation techniques that might help?", "Stress is a common reaction to demanding situations. What specific situation is causing you stress right now?"],
//     "happy": ["I'm glad to hear you're feeling happy! What's contributed to your good mood?", "That's wonderful! Happiness is important for our wellbeing. What's making you feel this way?", "It's great that you're feeling happy! Would you like to talk about what positive things have been happening?"],
//     "tired": ["Feeling tired can affect our mental state. Have you been getting enough rest?", "Being tired is common when we're busy or stressed. Would you like some tips for better sleep?", "I understand feeling tired can be frustrating. Is there anything specific that might be disrupting your energy levels?"],
//     "depressed": ["I'm sorry you're feeling this way. Depression is difficult, but support is available. Have you considered speaking with a mental health professional?", "Depression can feel overwhelming, but you're not alone. Would you like information about professional support options?", "I understand those feelings can be very challenging. Is there someone trusted in your life you could reach out to for support?"],
//     "suicide": ["I'm really concerned about what you're sharing. Please know that you're not alone and help is available 24/7. Please call 1800-599-0019 (India), 988 (US/International), or +254 722 178 177 (Kenya) right away.", "This sounds really serious, and I want to make sure you get the support you need. Please reach out to emergency services or call a crisis helpline: 1800-599-0019 (India), 988 (International), or +254 722 178 177 (Kenya).", "I'm worried about your safety. Please call 988, 1800-599-0019, or go to your nearest emergency room right away. Visit our SOS page for more local emergency contacts. Your life matters."],
//     "help": ["I'm here to listen and offer support. What specific kind of help are you looking for today?", "I'd be happy to help. Could you tell me more about what you're going through?", "I'm glad you reached out for help. What would be most supportive for you right now?"],
//     "thank you": ["You're welcome! I'm glad I could be here for you.", "I'm happy I could help in some way. Take care of yourself!", "You're welcome! Remember that seeking support is a sign of strength."],
//     "bye": ["Take care! Remember, it's okay to come back anytime you want to talk.", "Goodbye for now. Be gentle with yourself!", "Bye! Remember that taking care of your mental health is important."]
// };

// // Default response when no keyword match is found
// const defaultResponses = [
//     "I'm here to listen. Could you tell me more about that?",
//     "That's interesting. How does that make you feel?",
//     "Thank you for sharing. Would you like to elaborate on that?",
//     "I'm here to support you. What else would you like to talk about?",
//     "I understand. Is there anything specific about that you'd like to discuss?"
// ];

// function setupChatForm() {
//     const msgerForm = document.querySelector(".msger-inputarea");
//     const msgerInput = document.querySelector(".msger-input");
//     const msgerChat = document.querySelector(".msger-chat");

//     if (msgerForm) {
//         msgerForm.addEventListener("submit", event => {
//             event.preventDefault();
//             const msgText = msgerInput.value.trim();
//             if (!msgText) return;

//             // Add user message to chat
//             appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
//             msgerInput.value = "";

//             // Get bot response
//             setTimeout(() => {
//                 getBotResponse(msgText);
//             }, 1000); // Slight delay for realism
//         });
//     }
// }

// function appendMessage(name, img, side, text) {
//     const msgerChat = document.querySelector(".msger-chat");
    
//     const msgHTML = `
//     <div class="msg ${side}-msg">
//         <div class="msg-img">
//             <img src="${img}" alt="${name}">
//         </div>
//         <div class="msg-bubble">
//             <div class="msg-info">
//                 <div class="msg-info-name">${name}</div>
//                 <div class="msg-info-time">${formatDate(new Date())}</div>
//             </div>
//             <div class="msg-text">${text}</div>
//         </div>
//     </div>
//     `;
    
//     msgerChat.insertAdjacentHTML("beforeend", msgHTML);
//     msgerChat.scrollTop = msgerChat.scrollHeight;
// }

// function getBotResponse(userText) {
//     // Convert to lowercase for easier matching
//     const text = userText.toLowerCase();
    
//     // Check for keyword matches
//     let response = null;
    
//     // Loop through our response dictionary
//     for (const [keyword, responses] of Object.entries(mentalHealthResponses)) {
//         if (text.includes(keyword)) {
//             // Select a random response for the matched keyword
//             response = responses[Math.floor(Math.random() * responses.length)];
//             break;
//         }
//     }
    
//     // If no match was found, use a default response
//     if (!response) {
//         response = defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
//     }
    
//     // Add the bot's response to the chat
//     appendMessage(BOT_NAME, BOT_IMG, "left", response);
// }

// function formatDate(date) {
//     const h = "0" + date.getHours();
//     const m = "0" + date.getMinutes();
//     return `${h.slice(-2)}:${m.slice(-2)}`;
// }



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

function appendMessage(name, img, side, text) {
    const msgerChat = document.querySelector(".msger-chat");
    
    const msgHTML = `
    <div class="msg ${side}-msg">
        <div class="msg-img">
            <img src="${img}" alt="${name}">
        </div>
        <div class="msg-bubble">
            <div class="msg-info">
                <div class="msg-info-name">${name}</div>
                <div class="msg-info-time">${formatDate(new Date())}</div>
            </div>
            <div class="msg-text">${text}</div>
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