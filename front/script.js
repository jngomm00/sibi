const chatContainer = document.getElementById("chat-container");
const input = document.querySelector(".prompt input");
const button = document.querySelector(".prompt button");

let typingElement = null;
let autoScroll = true;

// --- Scroll control ---
chatContainer.addEventListener("wheel", () => autoScroll = false);
chatContainer.addEventListener("touchstart", () => autoScroll = false);
chatContainer.addEventListener("scroll", () => {
    if (chatContainer.scrollTop + chatContainer.clientHeight < chatContainer.scrollHeight - 5)
        autoScroll = false;
    else
        autoScroll = true;
});

// --- UI helpers ---
function addSendedMessage(text) {
    let message = document.createElement("p");
    message.setAttribute("class", "message sended new");
    message.textContent = text;
    chatContainer.appendChild(message);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    setTimeout(() => message.classList.remove("new"), 300);
}

function addReceivedMessage(text) {
    disableSend();
    let message = document.createElement("p");
    message.setAttribute("class", "message received");
    chatContainer.appendChild(message);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    const words = text.split(" ");
    let i = 0;
    autoScroll = true;

    function typeWord() {
        if (i < words.length) {
            message.innerHTML += (i === 0 ? "" : " ") + words[i];
            i++;
            if (autoScroll)
                chatContainer.scrollTop = chatContainer.scrollHeight;
            requestAnimationFrame(typeWord);
        } else {
            enableSend();
        }
    }
    typeWord();
}

function showAnimation() {
    typingElement = document.createElement("p");
    typingElement.setAttribute("class", "message received typing");
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("span");
        dot.className = "typing-dot";
        typingElement.appendChild(dot);
    }
    chatContainer.appendChild(typingElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideAnimation() {
    if (typingElement) {
        typingElement.remove();
        typingElement = null;
    }
}

function disableSend() {
    button.disabled = true;
    button.style.opacity = 0.5;
}
function enableSend() {
    button.disabled = false;
    button.style.opacity = 1;
}

// --- Función principal de envío ---
async function send(txt) {
    if (button.disabled || !txt.trim()) return;

    addSendedMessage(txt);
    showAnimation();

    try {
        // 1. Enviar el texto al servidor
        const res = await fetch("/send", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: txt })
        });

        const data = await res.json();
        const link = data.link;
        // 2. Consultar periódicamente el resultado
        let result = null;

        while (true) {
            const r = await fetch(link);
            const resultData = await r.json();

            if (resultData.status === "not ready") {
                await new Promise(r => setTimeout(r, 2000)); // esperar 2 s
            } else if (resultData.status === "ready") {
                result = resultData.message;
                break;
            } else {
                result = "Error: " + (resultData.error || "unknown");
                break;
            }
        }

        hideAnimation();
        addReceivedMessage(result);

    } catch (err) {
        hideAnimation();
        addReceivedMessage("Error de conexión con el servidor.");
        console.error(err);
    }
}

// --- Eventos de interacción ---
button.addEventListener("click", () => {
    const text = input.value.trim();
    if (text) {
        send(text);
        input.value = "";
    }
});

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const text = input.value.trim();
        if (text) {
            send(text);
            input.value = "";
        }
    }
});
