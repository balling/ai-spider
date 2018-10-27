from constants import RANKS


def cardsFaceUp(cards):
    if not cards:
        return False
    for c in cards:
        if not c.face_up:
            return False
    return True


def isSameSuitSequence(cards):
    if not cardsFaceUp(cards):
        return False
    c1 = cards[0]
    for c2 in cards[1:]:
        if c1.rank - 1 != c2.rank or c1.suit != c2.suit:
            return False
        c1 = c2
    return True


def isRankSequence(cards):
    if not cardsFaceUp(cards):
        return False
    c1 = cards[0]
    for c2 in cards[1:]:
        if c1.rank - 1 != c2.rank:
            return False
        c1 = c2
    return True


def isSequenceComplete(cards):
    if len(cards) != len(RANKS):
        return False
    return isSameSuitSequence(cards)
