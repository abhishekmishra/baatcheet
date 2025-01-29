// when the user clicks the button with id "send"
// call the /api/chat endpoint and stream the response to the
// div with id "response"

document.getElementById("send").addEventListener("click", async () => {
  const response = document.getElementById("response");
  response.innerHTML = "";
  const stream = await fetch("/api/chat");
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

    // response.innerHTML += new TextDecoder().decode(value);
  }
});
