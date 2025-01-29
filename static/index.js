async function sendMessage() {
  const response = document.getElementById("response");
  response.innerHTML = "";

  const model = "deepseek-r1:1.5b"; // You can change this as needed
  const content = document.getElementById("input").value; // Get the value from the input div

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
    const partial_content = json.message.content;
    // replace <think> with <i> and </think> with </i>
    const content = partial_content.replace(/<think>/g, "THINKING [").replace(/<\/think>/g, "] DONE THINKING");
    response.innerHTML += content;
    console.log(content);
  }
}

document.getElementById("send").addEventListener("click", sendMessage);

document.getElementById("input").addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});
