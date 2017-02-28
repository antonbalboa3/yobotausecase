from django.core.checks import messages

from . import models
from django.contrib.auth.models import User

# CONSTANTS defining number of ROWS and COLS
MAX_ROW = 6
MAX_COL = 7

# Starts a game setting a player1 and status 'WAITING'
def createGame(request):
    new_game = models.Game()
    new_game.player1 = request.user
    new_game.status = 'WAITING'
    new_game.save()

# Controls the user is in the game and returns an object with info
# data['players'] Contains both representations of players in the game (id,username)
# data['moves'] Contains the moves from the coin_set in a certain representation
def restoreBoard(request, game_instance):
    data={}
    board = createBoard(game_instance)
    if game_instance.player1 != request.user and game_instance.player2 != request.user:
        messages.error(request, 'You don\'t belong to this game')
    else:
        coin_set = game_instance.coin_set
        moves=[]

        for coin in coin_set.all():
            moves.append(modelToView(integerFromPlayer(coin.player,game_instance),coin.row,coin.column))
            coin_dict = coin.__dict__
            board[coin_dict['row']][coin_dict['column']] = coin_dict['player_id']
        data['moves'] = moves
    data['players'] = {'1':{'id':game_instance.player1.id, 'username':game_instance.player1.username},
                           '2': {'id': game_instance.player2.id, 'username': game_instance.player2.username}}
    return data, board

# Returns the "number" of user
def integerFromPlayer(player, game_instance):
    if player == game_instance.player1:
        return 1
    else:
        return 2

# Returns custom representation of a user so it can be serialized
def modelToView(player,row,column):
    return {'player':player,'row':row,'column':column}

# Initializes internal matrix
def createBoard(game_instance):
    board=[]
    for i in range(MAX_ROW):
        board.append([])
        for j in range(MAX_COL):
            board[i].append(0)
    return board


def insertCoin(player,column,board, game_instance):
    top_row = validateMove(column,board)
    board[top_row][column] = player.id
    game_instance.make_move(player,top_row, column)
    game_instance.save()
    return board

# Win test taken from internet. http://stackoverflow.com/questions/21641807/python-connect-4. This will work for default
# board (7x6). Logic would be different for a different size.
def testWin(board):
    for row in range(MAX_ROW):
        for col in range(3):
            if (board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3]) and (board[row][col] != 0):
                return board[row][col]

    for col in range(MAX_ROW):
        for row in range(3):
            if (board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col]) and (board[row][col] != 0):
                return board[row][col]

    for row in range(5, 2, -1):
        for col in range(3):
            if (board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3]) and (board[row][col] != 0):
                return board[row][col]

    for row in range(3):
        for col in range(4):
            if (board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3]) and (board[row][col] != 0):
                return board[row][col]

    return 0


def validateMove(column, board):
    if column < MAX_COL:
        for i in range(MAX_ROW):
            if board[i][column] == 0:
                return i
    return -1

def makeMove(player,column,board,game_instance):
    insertCoin(player,column,board,game_instance)
    return board

# Transform game_isntance to a dict in order to serialize it.
def transformLastMove(game_instance):
    if len(game_instance.coin_set.all()) > 0 :
        last_move = game_instance.last_move.__dict__
        last_move_dict = modelToView(last_move['player_id'], last_move['row'], last_move['column'])
        return last_move_dict
    return None

def userModelToDict(user, game_instance):
    player_dict = user
    player = {}
    player['id'] = player_dict.id
    player['username'] = player_dict.username
    player['color'] = integerFromPlayer(user, game_instance)
    return player
