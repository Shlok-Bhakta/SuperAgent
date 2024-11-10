import random
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus

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
        
    def get_best_move(self, game):
        print(game.board)
        
        depth = 3
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        possible_moves = self.get_possible_moves(game)
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces
        if current_pieces < NUM_PIECES:
            for move in possible_moves:
                newgamestate = game
                newgamestate.place_checker(move[0], move[1])
                newgamestate.push_neighbors(move[0], move[1])
                eval_score = self.minimaxPlacement(newgamestate, depth-1, False, alpha, beta)
                
                if eval_score > best_score:
                    best_score = eval_score
                    best_move = move
                
                alpha = max(alpha, best_score)
                
                # Pruning at root is optional but can save some time
                if beta <= alpha:
                    break
        else:
            for move in possible_moves:
                newgamestate = game
                newgamestate.move_checker(move[0], move[1], move[2], move[3])
                newgamestate.push_neighbors(move[2], move[3])
                eval_score = self.minimaxPlacement(newgamestate, depth-1, False, alpha, beta)
                
                if eval_score > best_score:
                    best_score = eval_score
                    best_move = move
                
                alpha = max(alpha, best_score)
                
                # Pruning at root is optional but can save some time
                if beta <= alpha:
                    break
            
                
        print(f"The current ")
        return best_move

    def minimaxPlacement(self, game, depth, maximizingPlayer, alpha, beta):
        """Minimax with alpha-beta pruning implementation."""
        if (depth == 0) or (game.check_winner() != EMPTY):
            return self.evaluate(game)
            
        possible_moves = self.get_possible_moves(game)
        
        if maximizingPlayer:
            maxEval = float('-inf')
            for move in possible_moves:
                newgamestate = game
                newgamestate.place_checker(move[0], move[1])
                newgamestate.push_neighbors(move[0], move[1])
                eval_score = self.minimaxPlacement(newgamestate, depth-1, False, alpha, beta)
                maxEval = max(maxEval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return maxEval
        else:
            minEval = float('inf')
            for move in possible_moves:
                newgamestate = game
                newgamestate.place_checker(move[0], move[1])
                newgamestate.push_neighbors(move[0], move[1])
                eval_score = self.minimaxPlacement(newgamestate, depth-1, True, alpha, beta)
                minEval = min(minEval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return minEval

    
    
    def minimaxMove(self, game, depth, maximizingPlayer, alpha, beta):
        """Minimax with alpha-beta pruning implementation."""
        if (depth == 0) or (game.check_winner() != EMPTY):
            return self.evaluate(game)
            
        possible_moves = self.get_possible_moves(game)
        
        if maximizingPlayer:
            maxEval = float('-inf')
            for move in possible_moves:
                newgamestate = game
                newgamestate.move_checker(move[0], move[1], move[2], move[3])
                newgamestate.push_neighbors(move[2], move[3])
                eval_score = self.minimaxMove(newgamestate, depth-1, False, alpha, beta)
                maxEval = max(maxEval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return maxEval
        else:
            minEval = float('inf')
            for move in possible_moves:
                newgamestate = game
                newgamestate.move_checker(move[0], move[1], move[2], move[3])
                newgamestate.push_neighbors(move[2], move[3])
                eval_score = self.minimaxMove(newgamestate, depth-1, True, alpha, beta)
                minEval = min(minEval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return minEval

    def evaluate(self, game):
        """Evaluation function remains the same as it's already optimized for the game."""
        score = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if game.board[i][j] == self.player:
                    # check the grid around to see if pairs exist
                    check_vectors = [(-1, -1), (-1, 0), (-1, 1),
                                (0, -1), (0, 1),
                                (1, -1), (1, 0), (1, 1)]
                    for k in check_vectors:
                        first = (i + k[0]) % BOARD_SIZE
                        second = (j + k[1]) % BOARD_SIZE
                        if game.board[first][second] == self.player:
                            score += self.linesReward
        return score