import random

from .util import isRankSequence, isSameSuitSequence, isSequenceComplete, cardsFaceUp
from .stack import Stock, Column

class Game():
    def __init__(self, id):
        self.id = id
    
    def createGame(self, suits):
        ''' 
        suits:
        list(range(4)) for four suits
        (0,0,1,1) for two suits
        (0,0,0,0) for one suit
        '''
        self.allstacks = []
        self.stock = Stock(self, suits)
        self.columns = [Column(self) for _ in range(10)]
        self.completed = 0
        self.score = 500
        self.moves = 0
        self.states = set()

    def startGame(self):
        for _ in range(4):
            self.stock.dealRow(flip=0)
        self.stock.dealRow(columns=self.columns[:4], flip=0)
        self.stock.dealRow(flip=1)

    def move(self, ncards, from_stack, to_stack):
        assert from_stack and to_stack and from_stack is not to_stack
        assert 0 < ncards <= len(from_stack.cards)
        cards = from_stack.cards[-ncards:]
        if not from_stack is self.stock:
            assert to_stack.acceptsCards(cards)
            self.score -= 1
            self.moves += 1
        for _ in range(ncards):
            from_stack.removeCard()
        for c in cards:
            to_stack.addCard(c)
        if to_stack.hasCompleteSeq():
            to_stack.dropPile()
            return 100
        return -1

    def flip(self, stack):
        if not stack.cards:
            return
        card = stack.cards[-1]
        card.face_up = True

    def canDealCards(self):
        if not self.stock.canDealCards():
            return False
        # no row may be empty
        for c in self.columns:
            if not c.cards:
                return False
        return True
    
    def getValidMoves(self):
        moves = []
        state = self.getState()
        # todo: optimize
        for from_stack in self.columns:
            seen_empty = False
            for to_stack in self.columns:
                if from_stack is to_stack:
                    continue
                pile = from_stack.getPile()
                move = None
                if not to_stack.cards:
                    if seen_empty:
                        continue
                    if len(pile) < len(from_stack.cards):
                        move = (len(pile), 'move', len(pile), from_stack, to_stack)
                    elif len(pile) > 1 and self.stock.cards:
                        move = (len(pile)-1, 'move', len(pile)-1, from_stack, to_stack)
                    seen_empty = True
                elif pile and to_stack.acceptsCards(pile):
                    move = (len(pile), 'move', len(pile), from_stack, to_stack)
                if move and (state + move not in self.states):
                    moves.append(move)
        if self.stock.canDealCards():
            moves.append((-1, 'deal'))
        moves.sort(reverse=True)
        return moves
    
    def performMoves(self, move):
        state = self.getState()
        self.moves += 1
        if move[1] == 'move':
            _, _, ncards, from_stack, to_stack = move
            score = self.move(ncards, from_stack, to_stack)
            self.score += score
            if score > 0:
                self.completed += 1
            else:
                self.states.add(state + move)
        elif move[1] == 'deal':
            self.stock.dealRow(flip=1)
            self.score -= 1
    
    def getState(self):
        return tuple(tuple(stack.cards) for stack in self.allstacks)

    # According to this method, we can simply say the size of state space equals to 104 + 10 + 1
    # the action should be move or deal
    # (avoid too complex action space, we set every move we only move the valid move 0)

    def getStateForDQN(self):
        # the corresponding card, first the stock all should be zeros, the flipped card should also be zero
        # the agent should not know what happen in the covered cards
        state = [0] * len(self.stock.cards)
        for column in self.columns:
            for card in column.cards:
                if card.face_up == False:
                    state.append(0)
                else:
                    state.append(card.rank + 1)
        if len(state) != 104:
            state.extend([14] * (104 - len(state)))
        # calculate column number
        columnNum = [len(column.cards) for column in self.columns]
        state.extend(columnNum)
        # calculate the stock card numbers
        state.append(len(self.stock.cards))
        return state

    def performMovesForDQN(self, action):
        # only having two action, the first one should be move,
        # the second one should be deal
        moves = self.getValidMoves()
        if action == 1 and moves[0][1] != 'deal': # move
            action_temp = moves[0]
        else:
            action_temp = moves[-1]
        self.performMoves(action_temp)
        return action

    def won(self):
        return self.completed == 8

    def __repr__(self):
        ret = ''
        for i in range(max(len(c.cards) for c in self.columns)):
            ret += ' '.join((str(c.cards[i]) if len(c.cards) > i
                             else '      ' for c in self.columns))
            ret += '\n'
        ret += 'Game#%d Score: %d   Moves: %d   Completed: %d   Undealt: %d' % \
        (self.id, self.score, self.moves, self.completed, len(self.stock.cards)/10)
        return ret
