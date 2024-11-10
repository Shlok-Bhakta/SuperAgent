from TwoPhaseAgentV7 import SuperAgent 
from TwoPhaseAgentV6 import SuperAgent as SuperAgent2
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus


def convert_board(board):
    board = board.replace(".", "0") 
    board = board.replace("W", "1") 
    board = board.replace("B", "-1")
    board = board.split("\n")[1:-1]
    finalboard = []
    for i in range(len(board)):
        finalboard.append(list(map(int, board[i].split(" "))))
    return finalboard

pastedBoard = """
W . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
"""



board = convert_board(pastedBoard)
playerbitboard = int("".join("".join("1" if i == 1 else "0" for i in r) for r in board), 2)
enemybitboard = int("".join("".join("1" if i == -1 else "0" for i in r) for r in board), 2)
print(playerbitboard)


game = Game()
game.current_player = PLAYER1
game.board = board
# bot = SuperAgent(PLAYER1)
bot = SuperAgent(PLAYER2)
bot2 = SuperAgent2(PLAYER2)
# moves = bot.get_possible_moves(game, playerbitboard, enemybitboard)
# print(moves)


# game.place_checker(3, 4)
print(f"NORMAL {bot2.evaluate(game)}") 
print(f"BB {bot.evaluate(playerbitboard, enemybitboard)}") 
print(game.display_board())