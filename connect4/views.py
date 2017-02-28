

#from django.shortcuts import render, redirect
import json

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
import django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response, render
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from .models import Game
from . import forms
from . import game
from . import models
from django.contrib import messages

from django.template import loader

# Create your views here.
@csrf_protect
def login(request):
    data={}
    data.update(csrf(request))
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        data['form']=form
        if form.is_valid():
            username = request.POST['usernameInput']
            password = request.POST['passwordInput']
            user = authenticate(username=username, password=password)
            if user is not None:
                django.contrib.auth.login(request, user)
                return HttpResponseRedirect('/connect4/games/')
            else:
                data['form'].add_error('usernameInput',ValidationError('User/Password not valid. Have you registered already?'))
    else:
        form = forms.LoginForm()
        data['form'] = form


    return render(request,'login.html',data)


def logout(request):
    django.contrib.auth.logout(request)
    return HttpResponseRedirect('/connect4/login/')

def signup(request):
    data = {}
    data.update(csrf(request))
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        data['form'] = form
        if form.is_valid():
            username = form.cleaned_data['usernameInput']
            password = form.cleaned_data['passwordInput1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            User.objects.create_user(username=username, password=password, first_name =first_name, last_name=last_name )
            user = authenticate(username=username, password=password)
            if user is not None:
                django.contrib.auth.login(request, user)
                return HttpResponseRedirect('/connect4/games/')
            else:
               data['form'].add_error(None,ValidationError('Something happened during registration'))
    else:
        form = forms.RegisterForm()
        data['form'] = form

    return render(request, 'signup.html', data)

@login_required
@csrf_protect
def games(request):
    if request.method == 'POST':
        if request.POST.get("_method", "") == 'PUT':
            # Creates the game (player2 still not assigned) and redirects to games list.
            game.createGame(request)
            return HttpResponseRedirect('/connect4/games/')
    else:
        avaliable_games = Game.objects.filter(player2=None).exclude(player1=request.user)
        current_not_finished_user_games = Game.objects.filter(
            (Q(player1=request.user)|Q(player2=request.user))).exclude(status='FINISHED')
        current_finished_user_games = Game.objects.filter(Q(player1=request.user)|Q(player2=request.user)).filter(status='FINISHED')
        data = {"avaliable_games":avaliable_games,
                "current_finished_user_games":current_finished_user_games,
                "current_not_finished_user_games":current_not_finished_user_games}

        data.update(csrf(request))
        return render(request, 'game.html', data)

@login_required
@csrf_protect
def play(request):
    if request.method == 'POST' and request.is_ajax():
        if request.POST.get('gameId') is not None:
            game_instance = models.Game.objects.filter(id=int(request.POST.get('gameId')))[0]
            last_move_dict = game.transformLastMove(game_instance)
            board, board_matrix = game.restoreBoard(request, game_instance)

            # Handle INIT of the board.
            if request.POST.get('action') is not None and request.POST.get('action') == 'INIT':
                board['last_move'] = last_move_dict
                player = game.userModelToDict(request.user, game_instance)

                # IF the winner is set, create representation of that winner.
                winner = game.testWin(board_matrix)
                winner_player = {}
                winner_player['id'] = winner
                if(winner!=0):
                    winner_player_dict = User.objects.filter(id=winner)[0].__dict__
                    winner_player['username'] = winner_player_dict['username']
                    winner_player['id'] = winner_player_dict['id']
                board['winner'] = winner_player
                return HttpResponse(json.dumps({'board': board, 'player':player,'error':''}), content_type="application/json")

            # Handle making a move event
            if request.POST.get('action') is not None and request.POST.get('action') == 'MAKEMOVE' and game_instance.status != 'FINISHED':
                # Retrieves from the client the id of the user that sent the move
                nextMove_player = request.POST.get('nextMove_player')
                nextMove_column= int(request.POST.get('nextMove_column'))


                # Player to comapre with is initially 2 (as if 2 started) and if any move was done, it is set to last move player
                player_to_compare = game_instance.player2
                if len(game_instance.coin_set.all()) > 0:
                    player_to_compare = game_instance.last_move.player

                # Checks that the user that sent the move is the one that has the turn and that the request has not been artificially changed
                if request.user.username != nextMove_player:
                    return HttpResponse(json.dumps({'error': 'Don\'t try to cheat'}), content_type="application/json")
                if nextMove_player == User.objects.filter(id=player_to_compare.id)[0].username:
                    return HttpResponse(json.dumps({'error': 'It\'s not your turn'}), content_type="application/json")
                #Finally makes a move
                game.makeMove(request.user,nextMove_column,board_matrix, game_instance)

                # Checks for a winner.
                winner = game.testWin(board_matrix)
                player = {}
                player['id'] = winner
                # Insert into helper function
                if winner != 0:
                    game_instance.status="FINISHED"
                    game_instance.save()
                    player_dict = User.objects.filter(id=winner)[0].__dict__
                    player['username'] = player_dict['username']

                last_move_dict = game.transformLastMove(game_instance)
                board['last_move'] = last_move_dict

                board['winner'] =player
                return HttpResponse(json.dumps({'board': board,'error':''}), content_type="application/json")
            else:
                messages.error(request, 'You must select a Game ID')


    elif request.method == 'POST':
        # Logic for joining a game
        form = forms.JoinGameForm(request.POST)
        if form.is_valid():
            game_id = form.cleaned_data['gameId']
            game_to_check = models.Game.objects.filter(id=game_id)[0]
            if game_to_check.player2 is None:
                if game_to_check.player1 != request.user:
                    game_to_check.join_up(request.user)
                else:
                    messages.error(request, 'You cannot play against yourself')
            else:
                if game_to_check.player1 != request.user and game_to_check.player2 != request.user:
                    messages.error(request, 'Game is already full, please select another')
                else:
                    return render(request,'play.html',{'gameId': game_id})
        else:
            messages.error(request, 'What you sent is not valid')
            return HttpResponseRedirect('/connect4/games/')
    return HttpResponseRedirect('/connect4/games/')