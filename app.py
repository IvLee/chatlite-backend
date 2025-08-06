import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_core import ask_gpt, handle_command, load_config, load_memory, save_config

app = Flask(__name__)
CORS(app)  # allow frontend (Angular) to call API from a different domain

# Ensure defaults exist on startup
config = load_config()
if not config.get("bot_role") or not config.get("theme"):
    from chatbot_core import default_role
    save_config(config.get("bot_role", default_role), config.get("theme", "Dark"))

@app.route("/chat", methods=["POST"])
def chat():
    """Receive a message and return the chatbot's reply."""
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "⚠️ Please enter a message."}), 400

    if message.startswith("/"):
        reply = handle_command(message)
    else:
        reply = ask_gpt(message)

    return jsonify({"reply": reply})

@app.route("/history", methods=["GET"])
def history():
    """Return chat history and current role/theme."""
    config = load_config()
    memory = load_memory()

    # Force Dark theme by default unless explicitly set to Light or Auto
    theme = config.get("theme", "Dark")
    if theme.lower() not in ["dark", "light", "auto"]:
        theme = "Dark"

    # Only send user/assistant messages for UI
    chat_history = [(m["role"], m["content"]) for m in memory if m["role"] in ["user", "assistant"]]

    return jsonify({
        "role": config["bot_role"],
        "theme": theme,
        "history": chat_history
    })


@app.route("/theme", methods=["POST"])
def set_theme():
    """Update the chatbot's theme."""
    data = request.get_json()
    new_theme = data.get("theme", "").capitalize()

    if new_theme not in ["Light", "Dark", "Auto"]:
        return jsonify({"error": "Invalid theme"}), 400

    # Load existing config
    config = load_config()

    # Save updated theme while keeping current bot role
    save_config(config["bot_role"], new_theme)

    # Return updated config so frontend can reflect immediately
    return jsonify({
        "message": f"Theme updated to {new_theme}",
        "theme": new_theme
    })

@app.route("/clear", methods=["POST"])
def clear():
    """Clear chat history both in memory and on disk."""
    from chatbot_core import save_memory
    save_memory([])  # Wipe stored messages
    return jsonify({"message": "Chat history cleared"}), 200

@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset chat history and AI role to default settings.
    """
    from chatbot_core import save_memory, save_config, default_role
    import chatbot_core
    chatbot_core.bot_role = default_role
    save_config(default_role, "Dark")  # Default theme now Dark
    save_memory([{"role": "system", "content": default_role}])
    return jsonify({
        "message": "🔄 Chat history and AI role have been reset to default.",
        "role": default_role
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
