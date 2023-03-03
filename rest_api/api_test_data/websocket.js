socket = new WebSocket("ws://" + "<ip>:<port>" + "/ws/<Token>/");
socket.onmessage = function(e) {
    alert(e.data);
};
if (socket.readyState == WebSocket.OPEN) socket.onopen();


// 当更新list subscribe时调用
socket.send('update_subscribe');