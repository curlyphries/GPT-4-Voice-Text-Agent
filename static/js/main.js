// main.js

document.addEventListener('DOMContentLoaded', () => {
  const conversationElem = document.getElementById('conversation');
  const userInputElem = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');
  const voiceBtn = document.getElementById('voiceBtn');
  const outputModeElem = document.getElementById('outputMode');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const usageBtn = document.getElementById('usageBtn');
  const usageInfoElem = document.getElementById('usageInfo');

  // Helper to append lines to the conversation text area
  function appendConversation(line) {
    conversationElem.value += line + "\n";
    conversationElem.scrollTop = conversationElem.scrollHeight; // auto-scroll
  }

  // Send user input to the backend
  function sendMessage(text) {
    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: text })
    })
    .then(res => res.json())
    .then(data => {
      const assistantReply = data.response;
      appendConversation("Assistant: " + assistantReply);
      handleAssistantOutput(assistantReply);
    })
    .catch(err => {
      console.error(err);
      appendConversation("Error: " + err);
    });
  }

  // Handle text-to-speech depending on the selected output mode
  function handleAssistantOutput(reply) {
    const mode = outputModeElem.value;
    if (mode === 'voice' || mode === 'both') {
      speak(reply);
    }
  }

  // Use browser's speechSynthesis for TTS
  function speak(text) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      speechSynthesis.speak(utterance);
    } else {
      console.warn("This browser does not support speech synthesis.");
    }
  }

  // On click: send button
  sendBtn.addEventListener('click', () => {
    const userText = userInputElem.value.trim();
    if (userText) {
      appendConversation("You: " + userText);
      sendMessage(userText);
      userInputElem.value = "";
    }
  });

  // On click: voice button
  voiceBtn.addEventListener('click', () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Your browser does not support speech recognition.");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      appendConversation("You (voice): " + transcript);
      sendMessage(transcript);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
    };
  });

  // Toggle theme
  themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    document.body.classList.toggle('light-mode');
  });

  // Check usage
  usageBtn.addEventListener('click', () => {
    fetch('/usage')
      .then(res => res.json())
      .then(data => {
        // Show usage in a simple format
        const text = `
Total Prompt Tokens: ${data.total_prompt_tokens}
Total Completion Tokens: ${data.total_completion_tokens}
Estimated Total Cost (USD): $${data.total_cost}
        `;
        usageInfoElem.textContent = text;
      })
      .catch(err => {
        usageInfoElem.textContent = 'Error retrieving usage info.';
      });
  });
});
