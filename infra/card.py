from .constants import SUITS, RANKS


class Card():
    def __init__(self, id, suit, rank):
        self.id = id
        self.suit = suit
        self.rank = rank
        self.face_up = False

    def __repr__(self):
        ret = "%s%3s" % (SUITS[self.suit], RANKS[self.rank])
        if self.face_up:
            ret = " %s " % ret
        else:
            ret = "-%s-" % ret
        return ret
