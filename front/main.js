let socket = new WebSocket("ws://192.168.0.2:8080");
let colors = ['#b9001f', '#E0FF4F', '#F18F01', '#2DE1FC', '#629460', '#3A405A', '#5C7AFF', '#ffc3cb'];
let turnsCount = 0;


socket.onopen = function(e) {
    socket.send(JSON.stringify({
        'message_type': 'handshake',
        'connection_type': 'front',
        'data': {}
    }));
};
  
socket.onmessage = function(event) {
    console.log(event.data);
    let response = JSON.parse(event.data);
    appendLogs(response.message_type, response.data);


    if(response.message_type == 'ready_request'){
        setTimeout(()=>{
            socket.send(JSON.stringify({
                'message_type': 'ready_response',
                'connection_type': 'front',
                'data': {}
            }));
            deleteField();
        }, 3000);
        
    }
    if(response.message_type == 'init_field_request'){
        createSetField(response.data.field_size, response.data.field);
    }
    if(response.message_type == 'update_field_request'){
        turnsCount++;
        redrawField(response.data.field_size, response.data.field);

        socket.send(JSON.stringify({
        'message_type': 'update_field_response',
        'connection_type': 'front',
        'data': {}
        }));
    }
    if(response.message_type == 'turn_request'){
                
        socket.send(JSON.stringify({
        'message_type': 'turn_request',
        'connection_type': 'front',
        'data': {}
        }));
    }
    
    
    //{"message_type": "update_field_request", "connection_type": "gateway", "data": 
    //{"field_size": 3, "field": [[0, 0, 0], [0, 0, 0], [0, 0, 0]], "color": 0, "turn": 0}}

   // {"message_type": "init_field_request", "connection_type": "gateway", 
    //"data": {"field_size": 3, "field": [[0, 1, 2], [2, 2, 2], [2, 0, 0]], "max_color": 2, "players": 1}}
};

socket.onclose = function(event) {
    if (event.wasClean) {
        alert(`[close] Connection closed clearly, code=${event.code} reason=${event.reason}`);
    } else {
        // например, сервер убил процесс или сеть недоступна
        // обычно в этом случае event.code 1006
        alert('[close] Connection lost');
    }
};

socket.onerror = function(error) {
    alert(`[error]`);
};


function appendLogs(message_type, data){
    let logs = document.getElementById('logs_div');
    let elem = document.createElement(`p`);
       
    
    if(message_type == 'init_field_request'){
        elem.innerText = `Game starts! Field ${data.field_size}x${data.field_size}, ${data.max_color + 1} colors. Players: ${data.players}`;
    }
    if(message_type == 'update_field_request'){
        elem.innerText = `Turn №${turnsCount}, ${data.turn} players turn! Color ${data.color} has been choosen`;
    }
    if(message_type == 'client_win'){
        elem.innerText = `Player ${data.turn} won!`;
    }
    if(message_type == 'client_killed'){
        elem.innerText = `Player ${data.turn} is killed!`;
    }
    logs.appendChild(elem);
    elem.scrollIntoView()
}


function createRundomField(size, maxColors = 8){
    let grid = document.getElementById('main_grid');
    grid.style.width = (size*20)+'px';

    for(let i = 0; i < size; i++){
        for(let j = 0; j < size; j++){
            let elem = document.createElement(`div`);
            elem.id = 'box'+i+j;
            elem.classList.add('simple_box');
            elem.style.backgroundColor = colors[ Math.floor(Math.random() * maxColors)];
            grid.appendChild(elem);
        }
    }
    console.log(grid, size);
  

}

function deleteField(){
    let grid = document.getElementById('main_grid');
    grid.innerHTML = '';
}


function createSetField(size, field ){
    let grid = document.getElementById('main_grid');
    grid.style.width = (size*25)+'px';
    grid.style.height = (size*25)+'px';

    for(let i = 0; i < size; i++){
        for(let j = 0; j < size; j++){
            let elem = document.createElement(`div`);
            elem.id = 'box'+i+j;
            elem.classList.add('simple_box');

            elem.classList.add(`color${field[i][j]}`);
            //elem.style.backgroundColor = colors[field[i][j]];
            grid.appendChild(elem);
        }
    }

}

function redrawField(size, field){
    let grid = document.getElementById('main_grid');

    for(let i = 0; i < size; i++){
        for(let j = 0; j < size; j++){
            let elem = document.getElementById('box'+i+j);
            if(!elem.classList.contains(`color${field[i][j]}`)){
                deSelectAllColors(elem);
                elem.classList.add(`color${field[i][j]}`);
                elem.classList.toggle('is-flipped');
            }

        }
    }
}

function deSelectAllColors(elem){
    elem.classList.remove('color0');
    elem.classList.remove('color1');
    elem.classList.remove('color2');
    elem.classList.remove('color3');
    elem.classList.remove('color4');
    elem.classList.remove('color5');
    elem.classList.remove('color6');
    elem.classList.remove('color7');
}