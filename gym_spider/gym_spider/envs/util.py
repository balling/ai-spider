from .constants import RANKS


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

def getValidMoves(state):
    moves = []
    empty_column = False
    for column in state[1:]:
        empty_column = empty_column or not column
    if state[0] and not empty_column:
        moves.append(('deal',))
    for fromi in range(1, len(state)):
        for ncard in range(1, len(state[fromi])+1):
            current = state[fromi][-ncard]
            if ncard < len(state[fromi]):
                nxt = state[fromi][-ncard-1]
                if nxt and current[0] == nxt[0] and nxt[1] == current[1]+1:
                    continue
            for toi in range(1, len(state)):
                if fromi == toi:
                    continue
                if not state[toi]:
                    if ncard!=len(state[fromi]):
                        moves.append(('move', fromi-1, toi-1, ncard))
                elif state[toi][-1][1] == current[1]+1:
                    moves.append(('move', fromi-1, toi-1, ncard))
            break
    return moves
