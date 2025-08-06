import re
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

CONFIG_FILE = "config.json"
MEMORY_FILE = "memory.json"

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
default_role = os.getenv("BOT_ROLE", "You are a helpful AI assistant.")

if not api_key:
    raise ValueError("No OpenAI API key found. Please set it in the .env file.")

client = OpenAI(api_key=api_key)

# --- Config persistence for Role + Theme ---
def load_config():
    """Load bot role and theme from config.json or set defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "bot_role": data.get("bot_role", default_role),
                    "theme": data.get("theme", "Auto")
                }
        except (json.JSONDecodeError, IOError):
            pass
    return {"bot_role": default_role, "theme": "Auto"}

def save_config(bot_role, theme):
    """Save bot role and theme to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"bot_role": bot_role, "theme": theme}, f, indent=2)
    except IOError:
        print("⚠️ Could not save config file.")

# Load initial settings
config = load_config()
bot_role = config["bot_role"]
theme = config["theme"]

# --- Memory persistence ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return [{"role": "system", "content": bot_role}]

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def clear_memory():
    """Clear conversation history but keep the current role and theme."""
    global memory
    memory = [{"role": "system", "content": bot_role}]
    save_memory(memory)
    return "🧹 Memory cleared. Role and theme preserved."

memory = load_memory()

# --- Summarization ---
def summarize_memory(old_messages):
    text = "\n".join([f"{m['role']}: {m['content']}" for m in old_messages])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize this conversation history in under 80 words."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

# --- Role adjustment ---
def ai_fix_role(user_input, current_role):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You improve unclear chatbot role descriptions. "
                "If the input is a style/tone change, rephrase the current role to match. "
                "If the input is gibberish, guess a reasonable role."
            )},
            {"role": "user", "content": f"Current role: '{current_role}'\nUser request: '{user_input}'"}
        ]
    )
    return response.choices[0].message.content.strip()

def change_role(new_role):
    global bot_role, memory
    config = load_config()  # Get current theme so we don't overwrite it

    if not re.search(r"[a-zA-Z]{3,}", new_role) or len(new_role.split()) < 3:
        suggestion = ai_fix_role(new_role, bot_role)
        bot_role = suggestion
    else:
        bot_role = new_role.strip()

    save_config(bot_role, config["theme"])  # Save both role + theme
    clear_memory()
    return f"✅ Role updated to: {bot_role}"

# --- Centralized Command Handler ---
def handle_command(command_str):
    """Process commands like /forget and /role."""
    parts = command_str.strip().split(" ", 1)
    cmd = parts[0].lower()

    if cmd in ["/forget", "forget"]:
        return clear_memory()

    if cmd == "/role":
        if len(parts) < 2 or not parts[1].strip():
            return "⚠️ Please provide a role after /role"
        return change_role(parts[1].strip())
    
    if cmd == "/reset":
        global bot_role, memory
        from chatbot_core import save_memory, save_config, default_role
        bot_role = default_role
        save_config(bot_role, "Light")
        memory = [{"role": "system", "content": bot_role}]
        save_memory(memory)
        return "🔄 Chat history and AI role have been reset to default."

    return f"⚠️ Unknown command: {command_str}"

# --- Chat ---
def ask_gpt(user_message):
    global memory
    memory.append({"role": "user", "content": user_message})

    if len(memory) > 10:
        old = memory[:-10]
        summary = summarize_memory(old)
        memory = [{"role": "system", "content": f"{bot_role} | Context: {summary}"}] + memory[-10:]
    else:
        if memory[0]["role"] != "system":
            memory.insert(0, {"role": "system", "content": bot_role})

    save_memory(memory)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=memory
    )
    reply = response.choices[0].message.content
    memory.append({"role": "assistant", "content": reply})
    save_memory(memory)
    return reply
