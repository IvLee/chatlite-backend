const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");

function appendMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add(role === "user" ? "user-msg" : "bot-msg");
    msgDiv.innerHTML = `<span>${text}</span>`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Enter to send, Shift+Enter for newline
messageInput.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    appendMessage("user", message);
    messageInput.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    })
    .then(res => res.json())
    .then(data => {
        appendMessage("bot", data.reply);
    })
    .catch(err => {
        appendMessage("bot", "⚠️ Error connecting to server.");
        console.error(err);
    });
}
