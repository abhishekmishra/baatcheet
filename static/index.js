/**
 * Implements a user text entry which shows up in the chat window.
 */
class UserText {
  constructor(text) {
    this.text = text;
    this.parentDiv = document.getElementById("response");
    this.div = document.createElement("div");
    this.div.className = "user-text";
    this.div.innerHTML = text;
    this.parentDiv.appendChild(this.div);
  }
}

/**
 * Implements a bot text entry which shows up in the chat window.
 * The bot text can be appended to the div.
 * The bot text can also be thinking, in which case the thinking div is shown.
 * The bot text can also be final, in which case the final div is shown.
 */
class BotText {
  isThinking = false;
  currentLineDiv = null;
  constructor() {
    this.parentDiv = document.getElementById("response");
    this.div = document.createElement("div");
    this.div.className = "bot-text";
    this.parentDiv.appendChild(this.div);
    this.thinkingDiv = document.createElement("div");
    this.thinkingDiv.className = "bot-text-thinking";
    this.thinkingDiv.innerHTML = "Thinking...";
    this.div.appendChild(this.thinkingDiv);
    this.thinkingDiv.style.display = "none";

    this.finalOutputDiv = document.createElement("div");
    this.finalOutputDiv.className = "bot-text-final";
    this.div.appendChild(this.finalOutputDiv);
    this.finalOutputDiv.style.display = "none";

    this._createNewLine();
  }

  async _createNewLine() {
    // if the current line div is not null, then convert its contents
    // to markdown using marked, and replace with the markdown content.
    if (this.currentLineDiv) {
      this.currentLineDiv.innerHTML = marked.parse(this.currentLineDiv.innerHTML);
    }

    this.currentLineDiv = document.createElement("div");
    this.currentLineDiv.className = "bot-text-line";
    if (this.isThinking) {
      this.thinkingDiv.appendChild(this.currentLineDiv);
    } else {
      this.finalOutputDiv.appendChild(this.currentLineDiv);
    }
  }

  async _appendTextToCurrentLine(text) {
    this.currentLineDiv.innerHTML += text;
  }

  async appendText(text) {
    // if length of text is 0, then return
    if (text.length === 0) {
      return;
    }

    // if text contains a newline, then split the text by newline
    // append first part, then create a new line, then append the rest
    if (text.includes("\n")) {
      const lines = text.split("\n");
      await this._appendTextToCurrentLine(lines[0]);
      await this._createNewLine();
      await this.appendText(lines.slice(1).join("\n"));
      return;
    }

    // if text contains <think> then enable isThinking
    if (text.includes("<think>")) {
      this.isThinking = true;
      this.thinkingDiv.style.display = "block";
      this.finalOutputDiv.style.display = "none";
    } else if (text.includes("</think>")) {
      this.isThinking = false;
      this.thinkingDiv.style.display = "block";
      this.finalOutputDiv.style.display = "block";
    }

    // remove the think tags from the text now
    text = text.replace(/<think>/g, "").replace(/<\/think>/g, "");

    // append the text to the current line
    this._appendTextToCurrentLine(text);
  }
}

async function sendMessage() {
  const response = document.getElementById("response");
  response.innerHTML = "";

  const model = "deepseek-r1:1.5b"; // You can change this as needed
  const content = document.getElementById("input").value; // Get the value from the input div

  // Append the user's entry to the chat window
  new UserText(content);

  const botText = new BotText();

  const stream = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, content }),
  });

  const reader = stream.body.getReader();
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    // read the json response and get [message][content]
    // and append it to the response
    const text = new TextDecoder().decode(value);
    const json = JSON.parse(text);

    // Append the bot's entry to the chat window
    await botText.appendText(json.message.content);
    console.log(json.session_id, json.message.content);
  }
}

document.getElementById("send").addEventListener("click", sendMessage);

document.getElementById("input").addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});
