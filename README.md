
![image](https://github.com/user-attachments/assets/c391c69e-3f7e-47c0-97ad-7f8e82199bf8)

```markdown
# GPT-4 Voice & Text Agent

A **generic AI assistant** that integrates **GPT-4**, **Google Search**, and **voice interaction**.  
Supports **text and voice commands**, **conversation memory**, and **cost tracking** for API usage.

---

## 🚀 Features

- 🔹 **GPT-4-Powered Chat** – Handles text and voice input.  
- 🔹 **Google Search Integration** – Fetches relevant search results.  
- 🔹 **Conversation Memory** – Remembers recent messages using SQLite.  
- 🔹 **Voice Interaction** – Uses Web Speech API for speech-to-text & text-to-speech.  
- 🔹 **Dark/Light Mode** – Toggle UI themes.  
- 🔹 **Token & Cost Tracking** – Logs API usage and estimated cost.

---

## 📂 Project Structure

```plaintext
GPT-4-Voice-Text-Agent/
├── app.py                  # Flask backend
├── requirements.txt        # Dependencies
├── .env                    # API keys (ignored by Git)
├── database.db             # Auto-created conversation log
├── templates/
│   └── index.html          # Frontend UI
├── static/
│   ├── css/
│   │   └── styles.css      # UI styles
│   └── js/
│       └── main.js         # Frontend logic
└── README.md               # Project documentation
```

---

## ⚙️ Setup Instructions

1. **Clone this repo**  
   ```bash
   git clone https://github.com/curlyphries/GPT-4-Voice-Text-Agent.git
   cd GPT-4-Voice-Text-Agent
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a .env file (required for API keys)**  
   ```dotenv
   OPENAI_API_KEY=your-openai-api-key
   GOOGLE_API_KEY=your-google-api-key
   GOOGLE_CX=your-google-custom-search-engine-id
   ```

5. **Run the application**  
   ```bash
   python app.py
   ```

Open your browser at **http://127.0.0.1:5000**

---

## 📝 How It Works

### **Backend** (`app.py`)
1. **Uses Flask** to handle API requests.  
2. **Saves conversation history** in a local SQLite database (`database.db`).  
3. **Calls OpenAI GPT-4** and **Google Search API** for context and responses.  
4. **Logs token usage & cost** to track your OpenAI expenditures.

### **Frontend** (`index.html`, `main.js`, `styles.css`)
1. **Handles text & voice** input in the browser (Web Speech API).  
2. **Sends user queries** to the backend (`/chat` endpoint).  
3. **Displays responses** and can speak them aloud (text-to-speech).  
4. **Dark/Light theme toggle** for UI preferences.  
5. **Fetches usage stats** (tokens & cost) from the `/usage` endpoint.

---

## 🔧 Modifications & Contributions

- **Expand Memory**  
  - Increase the `limit` in your conversation retrieval function (e.g., `get_conversation_messages(limit=10)`).

- **Integrate More APIs**  
  - Create a new function in `app.py` and trigger it with an additional UI button in `index.html`.

- **Customize Voice Output**  
  - Modify `handleAssistantOutput(reply)` in `main.js` to change TTS parameters (language, pitch, rate, etc.).

- **Secure API Keys**  
  - Use a secrets manager or environment variable manager instead of `.env` in production.

---

## 📜 License

This project is under the **MIT License** – feel free to use and modify it! 🚀
