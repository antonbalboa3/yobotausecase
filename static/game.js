var board=[];
last_move = null;
var currentPlayer=1;
var players=null;


// Taken from internet
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
var csrftoken = getCookie('csrftoken');
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



$( document ).ready(function() {
    $('th').click(function (event) {

        insertCoin(currentPlayer, $(this).index());
    });
    console.log("I'm initializing");
    $.ajax({
        url: "/connect4/play/",
        type: "POST",
        data: {'action': 'INIT', 'gameId': $("#gameId").val()},
        dataType: "json",
        success: function (resp) {
            initBoard(resp['board']);
            console.log("I sent something and received it");


        }
    });
});


function initBoard(savedBoard){
    players = savedBoard['players'];
    for (i = 0; i < 6; i++) {
        board.push([]);
        for (j = 0; j < 7; j++) {
            board[i].push(0);
        }
    }
    if(savedBoard['last_player'] != null){
        console.log('id' + savedBoard['last_player']['id']);
        console.log('id' + savedBoard['last_player']['username']);
        if(savedBoard['last_player']['id'] === players['1']['id']){
            currentPlayer=1;
        }else{
            currentPlayer=2;
        }
        console.log("LAST PAYER");
        console.log(currentPlayer);
    }

    moves = savedBoard['moves'];
    if(moves != null){
        for(index in moves) {
            if (moves[index]['row'] != -1) {
                markCell(moves[index]['player'], moves[index]['row'], moves[index]['column']);
                board[moves[index]['row']][moves[index]['column']] = moves[index]['player'];
            }
        }
    }
    if(savedBoard['last_move'] != null){
        last_move = savedBoard['last_move'];
        currentTurn(savedBoard['last_move']['player']['id']);
    }else{
        currentTurn(currentPlayer);
    }

}


function currentTurn(player){
    console.log("PLAYER IS");
    console.log(player);
    if(player == 1){
        $("#playerTurn").text(players['2']['username']);
        return players['2']
    }else{
        $("#playerTurn").text(players['1']['username']);
        return players['1']
    }

}



function insertCoin(player,column) {

    $.ajax({
        url: "/connect4/play/",
        type: "POST",
        data: {
            'action': 'MAKEMOVE',
            'gameId': $("#gameId").val(),
            'nextMove_player': currentPlayer,
            'nextMove_column': column
        },
        dataType: "json",
        success: function (resp) {
            last_move = resp['board']['last_move'];
            console.log("RESP GOES NEXT");

            console.log(resp);
            for (i = 0; i < 6; i++) {
                selectedRow = "row" + i;
                if (board[i][column] == 0) {
                    board[i][column] = player;
                    markCell(resp['board']['last_move']['player'], i, column);
                    break;
                }
            }
            currentTurn(last_move);

        }


    });
}
function markCell(player,row,column){
    selectedRow = ".row"+row;
    selectedPlayer = "player"+player;
    selectedItem = selectedRow + " td:nth-child(" + (column+1) + ")";
    $(selectedItem).addClass(selectedPlayer);

}

function handleLastMove(board){
  handle

}