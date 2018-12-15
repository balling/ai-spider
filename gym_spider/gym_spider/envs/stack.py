import random
from .card import Card
from .constants import RANKS, SUITS, DECKS
from .util import isSameSuitSequence, isRankSequence

class Stack():
    def __init__(self, game):
        self.id = len(game.allstacks)
        self.game = game
        game.allstacks.append(self)
        self.cards = []

    def addCard(self, card):
        self.cards.append(card)
        # check whether the sequence is complete here??
        return card

    def removeCard(self):
        assert len(self.cards) > 0
        card = self.cards[-1]
        del self.cards[-1]
        return card

    def move(self, ncards, to_stack):
        self.game.move(ncards, self, to_stack)

    def getCard(self):
        return self.cards[-1] if self.cards else None

    def __repr__(self):
        return 'Column[%d]' % self.id

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id


class Column(Stack):
    def removeCard(self):
        card = Stack.removeCard(self)
        if self.canFlipCard():
            self.game.flip(self)
        return card

    def hasCompleteSeq(self):
        if len(self.cards) < 13:
            return 0
        cards = self.cards[-13:]
        if isSameSuitSequence(cards):
            return 13
        return 0

    def dropPile(self):
        assert self.hasCompleteSeq()
        self.cards = self.cards[:-13]
        if self.canFlipCard():
            self.game.flip(self)

    def canFlipCard(self):
        return self.cards and not self.cards[-1].face_up

    def acceptsCards(self, cards):
        # cards must be an acceptable sequence
        if not isRankSequence(cards):
            return False
        # [topcard + cards] must be an acceptable sequence
        if (self.cards and not isRankSequence([self.cards[-1]] + cards)):
            return False
        return True

    def canMoveCards(self, ncards):
        return ncards <= len(self.cards) \
            and isSameSuitSequence(self.cards[-ncards:])

    def getPile(self):
        n = len(self.cards)
        # todo: optimize
        for i in range(n, 0, -1):
            if self.canMoveCards(i):
                return self.cards[-i:]
        return []


class Stock(Stack):
    def __init__(self, game, suits, rd):
        Stack.__init__(self, game)
        self.cards = self.createCards(suits)
        rd.shuffle(self.cards)

    def createCards(self, suits):
        return [Card(
            (deck*len(suits) + suit) * len(RANKS) + rank,
            suit, rank)
            for deck in range(DECKS)
            for suit in suits
            for rank in range(len(RANKS))]

    def canDealCards(self):
        return len(self.cards) > 0

    def dealRow(self, columns=None, flip=0):
        if not columns:
            columns = self.game.columns
        if not self.cards or not columns:
            return 0
        assert len(self.cards) >= len(columns)
        for c in columns:
            assert not self.getCard().face_up
            assert c is not self
            if (flip):
                self.game.flip(self)
            self.game.move(1, self, c)
        return len(columns)
