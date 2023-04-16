let socket = new WebSocket("ws://localhost:8080");

socket.onopen = function(e) {
    alert("Соединение установлено");
    socket.send("testString");
};
  
socket.onmessage = function(event) {
    alert(`[message] Данные получены с сервера: ${event.data}`);
};

socket.onclose = function(event) {
    if (event.wasClean) {
        alert(`[close] Соединение закрыто чисто, код=${event.code} причина=${event.reason}`);
    } else {
        // например, сервер убил процесс или сеть недоступна
        // обычно в этом случае event.code 1006
        alert('[close] Соединение прервано');
    }
};

socket.onerror = function(error) {
    alert(`[error]`);
};


function alertMe(str){
    alert(str);
}