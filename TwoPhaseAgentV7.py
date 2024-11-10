import copy
import random

import numpy as np
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus

# Constants
TWO_TOGETHER = 2
TWO_SPACE_TOGETHER = 2

# Pre-calculate priority scores as a single bitboard
PRIORITY_SCORES = 0
for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        priority = [-5, 1, -5][i//3] if i//3 < 3 else [-5, 1, -5][0]
        priority *= [-5, 1, -5][j//3] if j//3 < 3 else [-5, 1, -5][0]
        if priority != 0:
            PRIORITY_SCORES |= (priority << (i * 8 + j))

CENTERPRIORITY = 66229406269440
EDGEPRIORITY = 4340559386448706620
CORNERPRIORITY = 14106118457854575555

'''
This is a sample implementation of an agent that just plays a random valid move every turn.
I would not recommend using this lol, but you are welcome to use functions and the structure of this.
'''

class SuperAgent:
    def __init__(self, player=PLAYER1):
        self.player = player
        self.otherPlayer = PLAYER2 if player == PLAYER1 else PLAYER1
        self.linesReward = 1
    
    
    def get_bit_positions(self, bitmap):
        positions = []
        position = 0
        while bitmap:
            if bitmap & 1:
                positions.append(position)
            bitmap >>= 1
            position += 1
        return positions
    
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
        for _ in range(25):
            rand1 = random.randint(0, len(list)-1)
            rand2 = random.randint(0, len(list)-1)
            temp = list[rand1]
            list[rand1] = list[rand2]
            list[rand2] = temp
        return list
        
    def set_bit(self, bitmap, x, y):
        position = (7 - y) * 8 + (7 - x)
        bitmap |= (1 << position)
        return bitmap
    
    def unset_bit(self, bitmap, x, y):
        position = (7 - y) * 8 + (7 - x)  # Calculate bit position for (x, y)
        bitmap &= ~(1 << position)  # Use bitwise AND with negated bitmask to unset the bit
        return bitmap
    
    def bitmap_to_2d_array(self, bitmap, zero_value=0, one_value=1, size=8):
        board = []
        for y in range(size):
            row = []
            for x in range(size):
                bit_position = (7 - y) * 8 + (7 - x)
                if (bitmap & (1 << bit_position)) != 0:
                    row.append(one_value)
                else:
                    row.append(zero_value)
            
            board.append(row)
        
        return board


    # The torus function ensures the indices wrap around
    def torus(self, r, c):
        return (r + BOARD_SIZE) % BOARD_SIZE, (c + BOARD_SIZE) % BOARD_SIZE

    # Function to check if a position is set in a bitmap (bitboard)
    def is_position_set(self, bitmap, x, y):
        bit_position = (7 - y) * 8 + (7 - x)
        return (bitmap & (1 << bit_position)) != 0

    # Push mechanic that considers friendly and enemy pieces
    def push_neighbors(self, r0, c0, friend_bitmap, enemy_bitmap):
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        
        for dr, dc in dirs:
            # (r1, c1) is the 1-tile neighbor of (r0, c0) in direction (dr, dc)
            r1, c1 = self.torus(r0 + dr, c0 + dc)
            
            # Determine if the neighbor is a friendly or enemy piece
            if self.is_position_set(friend_bitmap, c1, r1):
                # (r2, c2) is the 2-tile neighbor in the same direction
                r2, c2 = self.torus(r1 + dr, c1 + dc)
                
                # If the 2-tile neighbor is empty (either a friend or enemy piece)
                if not self.is_position_set(friend_bitmap, c2, r2) and not self.is_position_set(enemy_bitmap, c2, r2):
                    # Move the piece from (r1, c1) to (r2, c2)
                    friend_bitmap |= (1 << ((7 - r2) * 8 + (7 - c2)))  # Set the bit at (r2, c2)
                    friend_bitmap &= ~(1 << ((7 - r1) * 8 + (7 - c1)))  # Clear the bit at (r1, c1)

            elif self.is_position_set(enemy_bitmap, c1, r1):
                # (r2, c2) is the 2-tile neighbor for enemy piece
                r2, c2 = self.torus(r1 + dr, c1 + dc)
                
                # If the 2-tile neighbor is empty
                if not self.is_position_set(friend_bitmap, c2, r2) and not self.is_position_set(enemy_bitmap, c2, r2):
                    # Move the enemy piece from (r1, c1) to (r2, c2)
                    enemy_bitmap |= (1 << ((7 - r2) * 8 + (7 - c2)))  # Set the bit at (r2, c2)
                    enemy_bitmap &= ~(1 << ((7 - r1) * 8 + (7 - c1)))  # Clear the bit at (r1, c1)
        return (friend_bitmap, enemy_bitmap)

    
    
    def get_best_move(self, game):
        # playerbitboard = [[True if i == 1 else False for i in r ] for r in game.board];
        playerbitboard = int("".join("".join("1" if i == 1 else "0" for i in r) for r in game.board), 2)
        enemybitboard = int("".join("".join("1" if i == -1 else "0" for i in r) for r in game.board), 2)
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces
        depth = 4 #if (current_pieces < NUM_PIECES) else 3
        best_score = -10000
        best_move = None
        alpha = -10000
        beta = 10000
        possible_moves = self.get_possible_moves(game)
        if current_pieces < NUM_PIECES:
            # return random.choice(possible_moves)
            for move in self.shuff(possible_moves):
                pbb, ebb = self.push_neighbors(move[0], move[1], playerbitboard, enemybitboard) 
                playerbb = self.set_bit(pbb, move[0], move[1])
                eval_score = self.minimaxPlacement(game,playerbb,ebb, depth-1, False, alpha, beta, current_pieces)
                
                if eval_score > best_score:
                    best_score = eval_score
                    best_move = move
                
                alpha = max(alpha, best_score)
        else:
            for move in possible_moves:
                
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
    
    
    def toXY(self, bitstring):
        return [(i // 8, i % 8)]

    def minimaxPlacement(self, game, playerbitboard, enemybitboard, depth, maximizingPlayer, alpha, beta, pieces):
        """Updated minimax for placement phase"""
        evalu = self.evaluate(playerbitboard, enemybitboard)
        if depth == 0 or (evalu > 10000) or (evalu < -10000):
            return evalu
            
        possible_moves = self.get_possible_moves(game)
        if pieces < NUM_PIECES:
            if maximizingPlayer:
                maxEval = -10000
                for move in possible_moves:
                    pbb,ebb = self.push_neighbors(move[0], move[1], playerbitboard, enemybitboard) 
                    playerbb = self.set_bit(pbb, move[0], move[1])
                    eval_score = self.minimaxPlacement(game, playerbb, ebb, depth-1, False, alpha, beta, pieces)
                    maxEval = max(maxEval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
                return maxEval
            else:
                minEval = 10000
                for move in possible_moves:
                    pbb,ebb = self.push_neighbors(move[0], move[1], playerbitboard, enemybitboard) 
                    playerbb = self.set_bit(pbb, move[0], move[1])
                    eval_score = self.minimaxPlacement(game, playerbb, ebb, depth-1, True, alpha, beta, pieces)
                    minEval = min(minEval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            return minEval
        else:
            if maximizingPlayer:
                maxEval = -10000
                for move in possible_moves:
                    pbb,ebb = self.push_neighbors(move[0], move[1], playerbitboard, enemybitboard) 
                    playerbb = self.set_bit(pbb, move[0], move[1])
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

    def minimaxMove(self, game, playerbitboard, enemybitboard, depth, maximizingPlayer, alpha, beta):
        """Updated minimax for movement phase"""
        evalu = self.evaluate(playerbitboard, enemybitboard)
        if depth == 0 or (evalu > 10000) or (evalu < -10000):
            return evalu
            
        possible_moves = self.get_possible_moves(game)
        
        if maximizingPlayer:
            maxEval = -10000
            for move in possible_moves:
                pbb,ebb = self.push_neighbors(move[0], move[1], playerbitboard, enemybitboard) 
                playerbb = self.set_bit(pbb, move[0], move[1])
                self.unset_bit(playerbb, move[0], move[1]) 
                self.set_bit(playerbb, move[2], move[3])
                eval_score = self.minimaxMove(game, playerbb, ebb, depth-1, False, alpha, beta)
                maxEval = max(maxEval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = 10000
            for move in possible_moves:
                pbb,ebb = self.push_neighbors(move[0], move[1], playerbitboard, enemybitboard) 
                playerbb = self.set_bit(pbb, move[0], move[1])
                self.unset_bit(playerbb, move[0], move[1]) 
                self.set_bit(playerbb, move[2], move[3])
                eval_score = self.minimaxMove(game, playerbb, ebb, depth-1, True, alpha, beta)
                minEval = min(minEval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return minEval
        
    def surrounding(self, bitmap):
    
        # Generate moves by shifting left, right, up, down, and diagonally
        return (
            ((bitmap << 1)) |  # Move left
            ((bitmap >> 1)) |  # Move right
            ((bitmap << 8)) |  # Move up
            ((bitmap >> 8)) |  # Move down
            ((bitmap << 9)) |  # Move up-left
            ((bitmap << 7) ) |  # Move up-right
            ((bitmap >> 7) ) |  # Move down-left
            ((bitmap >> 9))    # Move down-right
        )
    
    def doubleSurrounding(self, bitmap):
    
        # Generate moves by shifting left, right, up, down, and diagonally
        return (
            ((bitmap << 2)) |  # Move left
            ((bitmap << 2+8)) |  # Move leftM
            ((bitmap >> 8-2)) |  # Move leftMD
            ((bitmap >> 2)) |  # Move right
            ((bitmap << 8-2)) |  # Move leftM
            ((bitmap >> 2+8)) |  # Move leftMD
            ((bitmap << 16)) |  # Move up
            ((bitmap << 16+1)) |  # Move up
            ((bitmap << 16+2)) |  # Move up
            ((bitmap << 16-1)) |  # Move up
            ((bitmap << 16-2)) |  # Move up
            ((bitmap >> 16)) |  # Move down
            ((bitmap >> 16-2)) |  # Move down
            ((bitmap >> 16-1)) |  # Move down
            ((bitmap >> 16+1)) |  # Move down
            ((bitmap >> 16+2))  # Move down
        )
        
        
    def winmaps(self, bitmap):
        # Generate win maps by shifting left, right, up, down, and diagonally
        return (
            (((bitmap << 1)) |  # Move left
            ((bitmap >> 1))),  # Move right
            (((bitmap << 8)) |  # Move up ((bitmap 
            ((bitmap >> 8))),  # Move down
            ((bitmap << 9)) |  # Move up-left
            ((bitmap << 7) ),  # Move up-right
            ((bitmap >> 7) ) |  # Move down-left
            ((bitmap >> 9))    # Move down-right
        )
        
    def check_three_pawns_aligned(self, bitmask: int) -> bool:
        """
        Check if 3 pawns are lined up horizontally, vertically, or diagonally on a chess board.
        Only checks around existing pawns for better efficiency.
        
        Args:
            bitmask (int): 64-bit integer where 1s represent pawns on the board
            
        Returns:
            bool: True if 3 pawns are aligned, False otherwise
        """
        # Get positions of all pawns
        pawn_positions = []
        for i in range(64):
            if bitmask & (1 << i):
                pawn_positions.append((i // 8, i % 8))
                
        if len(pawn_positions) < 3:
            return False
            
        # For each pawn, check all 8 directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # NW, N, NE
            (0, -1),          (0, 1),     # W, E
            (1, -1),  (1, 0),  (1, 1)     # SW, S, SE
        ]
        
        for row, col in pawn_positions:
            for dx, dy in directions:
                count = 0
                # Check up to 2 spaces in each direction
                for i in range(3):
                    curr_row, curr_col = row + dx * i, col + dy * i
                    if 0 <= curr_row < 8 and 0 <= curr_col < 8:
                        if (curr_row, curr_col) in pawn_positions:
                            count += 1
                    else:
                        break
                if count >= 3:
                    return True
                    
        return False

    
    def evaluate(self, friendbb, enemybb):
        CENTERPRIORITY = 66229406269440
        EDGEPRIORITY = 4340559386448706620
        CORNERPRIORITY = 14106118457854575555
        score = 0
        
        # Calculate priority scores
        # score += sum(((friendbb >> i) & 1) * ((PRIORITY_SCORES >> i) & 1) for i in range(64))
        # score -= sum(((enemybb >> i) & 1) * ((PRIORITY_SCORES >> i) & 1) for i in range(64))
        # Check touching pairs for friend pieces
        surrBitmap = self.surrounding(friendbb)
        closeFriendlyMap = friendbb & surrBitmap
        score += closeFriendlyMap.bit_count() * TWO_TOGETHER
        # Check if enemy pieces are touching eachother
        surrBitmap = self.surrounding(enemybb)
        closeEnemyMap = enemybb & surrBitmap
        score -= closeEnemyMap.bit_count() * TWO_TOGETHER
        
        
        surrBitmap = self.doubleSurrounding(friendbb)
        closeFriendlyMap = friendbb & surrBitmap
        score += closeFriendlyMap.bit_count() * TWO_SPACE_TOGETHER
        # Check if enemy pieces are touching eachother
        surrBitmap = self.doubleSurrounding(enemybb)
        closeEnemyMap = enemybb & surrBitmap 
        score -= closeEnemyMap.bit_count() * TWO_SPACE_TOGETHER

        # Use Edge Masks to add some prioroty to base moves
        score += len(self.get_bit_positions(CENTERPRIORITY & friendbb)) * 1
        score += len(self.get_bit_positions(EDGEPRIORITY & friendbb)) * 0.3
        score += len(self.get_bit_positions(CORNERPRIORITY & friendbb)) * -1

        # Check for win condition
        if self.check_three_pawns_aligned(friendbb):
            score += 11000
        if self.check_three_pawns_aligned(enemybb):
            score -= 11000
        
            


        return score