import copy
import random

import numpy as np
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus

TWO_TOGETHER = 2
TWO_SPACE_TOGETHER = 2
PRIORITY_BOARD = [[-5, 1, -5], [1, 5, 1], [-5, 1, -5]]  
TOUCHING_VECTORS = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]
GAPPED_VECTORS = [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
                    (0, -2), (0, 2),
                    (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]
'''
This is a sample implementation of an agent that just plays a random valid move every turn.
I would not recommend using this lol, but you are welcome to use functions and the structure of this.
'''

class SuperAgent:
    def __init__(self, player=PLAYER1):
        self.player = player
        self.otherPlayer = PLAYER2 if player == PLAYER1 else PLAYER1
        self.linesReward = 1
    
    # given the game state, gets all of the possible moves
    def get_possible_moves(self, game):
        """Returns list of all possible moves in current state."""
        moves = []
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces
        
        if current_pieces < NUM_PIECES:
            # placement moves
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if game.board[r][c] == EMPTY:
                        moves.append((r, c))
        else:
            # movement moves
            for r0 in range(BOARD_SIZE):
                for c0 in range(BOARD_SIZE):
                    if game.board[r0][c0] == game.current_player:
                        for r1 in range(BOARD_SIZE):
                            for c1 in range(BOARD_SIZE):
                                if game.board[r1][c1] == EMPTY:
                                    moves.append((r0, c0, r1, c1))
        return moves


    def shuff(self, list):
        for _ in range(15):
            rand1 = random.randint(0, len(list)-1)
            rand2 = random.randint(0, len(list)-1)
            temp = list[rand1]
            list[rand1] = list[rand2]
            list[rand2] = temp
        return list
        
    def get_best_move(self, game):
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces
        depth = 3 if (current_pieces < NUM_PIECES) else 3
        best_score = -10000
        best_move = None
        alpha = -10000
        beta = 10000
        possible_moves = self.get_possible_moves(game)
        if current_pieces < NUM_PIECES:
            # return random.choice(possible_moves)
            for move in self.shuff(possible_moves):
                # Create a deep copy of the game state
                newgamestate = copy.deepcopy(game)
                newgamestate.place_checker(move[0], move[1])
                eval_score = self.minimaxPlacement(newgamestate, depth-1, False, alpha, beta, current_pieces)
                
                if eval_score > best_score:
                    best_score = eval_score
                    best_move = move
                
                alpha = max(alpha, best_score)
        else:
            for move in possible_moves:
                newgamestate = copy.deepcopy(game)
                newgamestate.move_checker(move[0], move[1], move[2], move[3])
                eval_score = self.minimaxMove(newgamestate, depth-1, False, alpha, beta)
                
                if eval_score > best_score:
                    best_score = eval_score
                    best_move = move
                
                alpha = max(alpha, best_score)
            newgamestate = copy.deepcopy(game)
            newgamestate.move_checker(best_move[0], best_move[1], best_move[2], best_move[3])
            eval_score = self.minimaxMove(newgamestate, depth-1, False, alpha, beta)
            # print(f"{newgamestate.display_board()} EVAL: {eval_score}")
        return best_move
    
    


    def minimaxPlacement(self, game, depth, maximizingPlayer, alpha, beta, pieces):
        """Updated minimax for placement phase"""
        evalu = self.evaluate(game)
        if depth == 0 or (evalu > 10000) or (evalu < -10000):
            return self.evaluate(game)
            
        possible_moves = self.get_possible_moves(game)
        if pieces < NUM_PIECES:
            if maximizingPlayer:
                maxEval = -10000
                for move in possible_moves:
                    newgamestate = copy.deepcopy(game)
                    newgamestate.place_checker(move[0], move[1])
                    eval_score = self.minimaxPlacement(newgamestate, depth-1, False, alpha, beta, pieces)
                    maxEval = max(maxEval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
                return maxEval
            else:
                minEval = 10000
                for move in possible_moves:
                    newgamestate = copy.deepcopy(game)
                    newgamestate.place_checker(move[0], move[1])
                    eval_score = self.minimaxPlacement(newgamestate, depth-1, True, alpha, beta, pieces)
                    minEval = min(minEval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            return minEval
        else:
            if maximizingPlayer:
                maxEval = -10000
                for move in possible_moves:
                    newgamestate = copy.deepcopy(game)
                    newgamestate.place_checker(move[0], move[1])
                    eval_score = self.minimaxMove(newgamestate, depth-1, False, alpha, beta)
                    maxEval = max(maxEval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
                return maxEval
            else:
                minEval = 10000
                for move in possible_moves:
                    newgamestate = copy.deepcopy(game)
                    newgamestate.place_checker(move[0], move[1])
                    eval_score = self.minimaxMove(newgamestate, depth-1, True, alpha, beta)
                    minEval = min(minEval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            return minEval

    def minimaxMove(self, game, depth, maximizingPlayer, alpha, beta):
        """Updated minimax for movement phase"""
        evalu = self.evaluate(game)
        if depth == 0 or (evalu > 10000) or (evalu < -10000):
            return eval
            
        possible_moves = self.get_possible_moves(game)
        
        if maximizingPlayer:
            maxEval = -10000
            for move in possible_moves:
                newgamestate = copy.deepcopy(game)
                newgamestate.move_checker(move[0], move[1], move[2], move[3])
                eval_score = self.minimaxMove(newgamestate, depth-1, False, alpha, beta)
                maxEval = max(maxEval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = 10000
            for move in possible_moves:
                newgamestate = copy.deepcopy(game)
                newgamestate.move_checker(move[0], move[1], move[2], move[3])
                eval_score = self.minimaxMove(newgamestate, depth-1, True, alpha, beta)
                minEval = min(minEval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return minEval
        
    def evaluate(self, game):
        # check if win
        score = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                # Evaling My Moves as the player
                if game.board[i][j] == self.player:
                    # check the grid around to see if pairs exist
                    for k in TOUCHING_VECTORS:
                        if game.board[(i + k[0]) % BOARD_SIZE][(j + k[1]) % BOARD_SIZE] == self.player:
                            score += TWO_TOGETHER
                            if(game.board[(i - k[0]) % BOARD_SIZE][(j - k[1]) % BOARD_SIZE] == self.player):
                                score += 10000
                            
                    # check the grid around to see if piece  Space Piece exists 
                    for k in GAPPED_VECTORS:
                        if game.board[(i + k[0]) % BOARD_SIZE][(j + k[1]) % BOARD_SIZE] == self.player:
                            score += TWO_SPACE_TOGETHER
                    # assign a score to the quadrant of the board, corners are worse
                    score += PRIORITY_BOARD[i // 3][j // 3]
                # Evaling Opponent Moves as the player
                elif game.board[i][j] == self.otherPlayer:
                    # check the grid around to see if pairs exist
                    for k in TOUCHING_VECTORS:
                        if game.board[(i + k[0]) % BOARD_SIZE][(j + k[1]) % BOARD_SIZE] == self.otherPlayer:
                            score -= TWO_TOGETHER
                            if(game.board[(i - k[0]) % BOARD_SIZE][(j - k[1]) % BOARD_SIZE] == self.otherPlayer):
                                score -= 10000
                            
                    # check the grid around to see if piece  Space Piece exists 
                    for k in GAPPED_VECTORS:
                        if game.board[(i + k[0]) % BOARD_SIZE][(j + k[1]) % BOARD_SIZE] == self.otherPlayer:
                            score -= TWO_SPACE_TOGETHER
                    
                    
        return score