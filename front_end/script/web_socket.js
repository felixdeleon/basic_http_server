let socket = new WebSocket('ws://' + window.location.host + '/socket');
socket.onmessage = renderMessages;

function sendMessage() {
    const name = document.getElementById("name")
    const color = document.getElementById("color")

    const _name = name.value;
    const _color = color.value;

    socket.send("Hello Server!")
// JSON.stringify({'Name': _name, 'Color': _color})
}

function renderMessages(message) {
    console.log(message.data);
}

