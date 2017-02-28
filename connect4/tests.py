from django.test import TestCase
from django.contrib.auth import authenticate
from . import game

from . import models
from django.contrib.auth.models import User

class ValidateCreateUser(TestCase):
    def test_creating_a_player(self):
        """creating a player"""
        player = User(username='yobota',first_name='Yobota', last_name='Yobota')
        self.assertEqual(player.username, 'yobota')
        self.assertEqual(player.first_name, 'Yobota')
        self.assertEqual(player.last_name, 'Yobota')

class ValidateCreateGame(TestCase):
    def setUp(self):
        User.objects.create(username='yobota', first_name='Yobota', last_name='Yobota')
    # Animal.objects.create(name="lion", sound="roar")
    def test_creating_a_game(self):
        """creating a player"""
        player1 = User.objects.filter(username='yobota')[0]
        game = models.Game(player1=player1)
        self.assertEqual(game.player1.username, 'yobota')

class ValidateAuthenticate(TestCase):

    def setUp(self):
        User.objects.create(username='yobota', password='yobota', first_name='Yobota', last_name='Yobota')
    def test_authenticate(self):

        user = authenticate(username='notUser', password='notUser')
        self.assertEquals(user, None)

class ValidateCreateboard(TestCase):

    class Request():
        def __init__(self,user):
            self.user = user

    def setUp(self):
        User.objects.create(username='yobota', password='yobota')
        User.objects.create(username='yobota2', password='yobota2')

    def test_create_board(self):
        player1 = User.objects.filter(username='yobota')[0]
        player2 = User.objects.filter(username='yobota2')[0]
        game_instance = models.Game.objects.create(player1=player1, player2 = player2)
        game_instance.make_move(player2, 0, 0)
        # Simulate the request.user
        request=self.Request(player1)
        board, board_matrix = game.restoreBoard(request, game_instance)
        self.assertEquals(board_matrix[0][0], player2.id)

class ValidateMovesAndWin(TestCase):
    class Request():
        def __init__(self, user):
            self.user = user

    def setUp(self):
        User.objects.create(username='yobota', password='yobota')
        User.objects.create(username='yobota2', password='yobota2')

    def test_create_board(self):
        player1 = User.objects.filter(username='yobota')[0]
        player2 = User.objects.filter(username='yobota2')[0]
        game_instance = models.Game.objects.create(player1=player1, player2=player2)

        game_instance.make_move(player1, 0, 0)
        game_instance.make_move(player2, 0, 1)
        game_instance.make_move(player1, 1, 0)
        game_instance.make_move(player2, 1, 1)
        game_instance.make_move(player1, 2, 0)
        game_instance.make_move(player2, 2, 1)

        request = self.Request(player1)
        board, board_matrix = game.restoreBoard(request, game_instance)
        winner = game.testWin(board_matrix)
        # No one won yet
        self.assertEquals(winner, 0)

        game_instance.make_move(player1, 3, 0)
        board, board_matrix = game.restoreBoard(request, game_instance)
        winner = game.testWin(board_matrix)
        # After last move, player1 won
        self.assertEquals(winner, player1.id)

