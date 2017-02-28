var board=[];
last_move = null;
var currentPlayer={};
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

// AJAX request to initalize board (either started or not)
$( document ).ready(function() {

    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


    $('th').click(function (event) {
        insertCoin(currentPlayer['id'], $(this).index());
    });



    setTimeout(function(){
       window.location.reload(1);
    }, 100000);

    $.ajax({
        url: "/connect4/play/",
        type: "POST",
        data: {'action': 'INIT', 'gameId': $("#gameId").val()},
        dataType: "json",
        success: function (resp) {
            initBoard(resp['board']);
            currentPlayer = resp['player'];
            if(resp['board']['winner']['id']!=0){
                  $("#errorContainer").text("WINNER IS: " + resp['board']['winner']['username']);
            }

        }
    });
});

function initBoard(savedBoard){
    // Stores players in a variable
    players = savedBoard['players'];

    // Inits the board with 0's
    for (i = 0; i < 6; i++) {
        board.push([]);
        for (j = 0; j < 7; j++) {
            board[i].push(0);
        }
    }


        if(currentPlayer['id'] === players['1']['id']){
            currentPlayer['color']=1;
        }else{
            currentPlayer['color']=2;
        }


    moves = savedBoard['moves'];
    if(moves != null){
        for(index in moves) {
            if (moves[index]['row'] != -1) {
                // Change the color of the cells
                markCell(moves[index]['player'], moves[index]['row'], moves[index]['column']);
                board[moves[index]['row']][moves[index]['column']] = moves[index]['player'];
            }
        }
    }

    if(savedBoard['last_move'] != null){
        handleLastMove(savedBoard);
    }else{
        currentTurn(currentPlayer);
    }

}
function markCell(player,row,column){
    selectedRow = ".row"+row;
    selectedPlayer = "player"+player;
    selectedItem = selectedRow + " td:nth-child(" + (column+1) + ")";
    $(selectedItem).addClass(selectedPlayer);

}


function handleLastMove(board){
    last_move = board['last_move'];
    currentTurn(board['last_move']['player']);
    changeLastMove(last_move);

}

//Prints whose turn is and returns the value of the variable
function currentTurn(player){
    if(player == players['1']['id']){
        $("#playerTurn").text(players['2']['username']);
        return players['1']
    }else{
        $("#playerTurn").text(players['1']['username']);
        return players['2']
    }

}
function changeLastMove(last_move){
     $('#lastMove').text('Last move was made by: ' + currentTurn(last_move['player'])['username']+' R: '+last_move['row']+' C:' + last_move['column']);

}
// When clicking the "insert coin in column" button make AJAX request.
function insertCoin(player,column) {
    $.ajax({
        url: "/connect4/play/",
        type: "POST",
        data: {
            'action': 'MAKEMOVE',
            'gameId': $("#gameId").val(),
            'nextMove_player': currentPlayer['username'],
            'nextMove_column': column
        },
        dataType: "json",
        success: function (resp) {
            $("#errorContainer").text(resp['error']);
            if(resp['board'] != null){

            last_move = resp['board']['last_move'];

            for (i = 0; i < 6; i++) {
                selectedRow = "row" + i;
                if (board[i][column] == 0) {
                    board[i][column] = player;
                    markCell(currentPlayer['color'], i, column);
                    break;
                }
            }
            if(resp['board']['winner']['id']!=0){
                  $("#errorContainer").text("WINNER IS: " + resp['board']['winner']['username']);
            }
            changeLastMove(last_move);
        }
        }


    });
}
