document.addEventListener("htmx:afterSwap", function (event) {
  if (event.target.id === "response") {
    const box = document.getElementById("chat-box");
    const input = document.querySelector("input[name='query']");
    const reply = JSON.parse(event.detail.xhr.responseText).reply;

    if (input && input.value) {
      const userMsg = document.createElement("div");
      userMsg.classList.add("message", "user");
      userMsg.innerText = input.value;
      box.appendChild(userMsg);
    }

    const botMsg = document.createElement("div");
    botMsg.classList.add("message", "bot");
    botMsg.innerText = reply;
    box.appendChild(botMsg);

    box.scrollTop = box.scrollHeight;
    input.value = "";
    document.getElementById("response").innerText = "";  // إخفاء رد HTMX
  }
});
