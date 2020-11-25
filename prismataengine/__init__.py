import enum
import numpy
from os import environ
from functools import lru_cache
from _prismataengine import *
from importlib import resources
if "PRISMATA_INIT_CARD_PATH" in environ:
    if environ.getenv("PRISMATA_INIT_CARD_PATH", None):
        init(environ.getenv("PRISMATA_INIT_CARD_PATH", None))
else:
    with resources.path(__name__, 'cardLibrary.jso') as path:
        init(str(path))

class ConcreteAction():
    def __init__(self, gamestate, action):
        self._action = action
        self.type = action.type
        self.card = action.card(gamestate)

    def __getattr__(self, key):
        return getattr(self._action, key)

    def __str__(self):
        return f"{self.card.name} ({self.card.type}): {ActionType.values[self._action.type]} ({self.type})"

class GameState():
    def __init__(self, string, cards=11, player1=None, player2=None):
        self._state = jsonStrToGameState(string)
        self._players = (player1, player2)
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = PrismataAction(self.activePlayer, ActionType.END_PHASE, 0);
        self._actions = PrismataActions()
        self._toVectorNeedsUpdate = True
        self._move = Move()
        self._cards = CardVector()
        self._abactions = numpy.zeros(14 if cards == 4 else 32, dtype=numpy.uintp)
        self._ie = numpy.zeros(30 if cards == 4 else 82, dtype=numpy.uint16)
        self._acvec = numpy.zeros(self._abactions.shape[0], dtype=numpy.bool)
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        self._abactions_list = [AbstractAction.values[i] for i in range(self._acvec.shape[0]) if self._acvec[i]]
        self.toVector = self.toVector4 if cards == 4 else self.toVector11
        if __debug__:
            print("Initialized GameState")
            
    '''
    Virtual method, see __init__
    '''
    def toVector(self):
        pass

    def getRawState(self):
        return self._state

    def isLegal(self, action):
        return self._state.isLegal(self.coerceAction(action))

    def json(self):
        return self._state.json()

    def isGameOver(self):
        return self._state.isGameOver()

    def __str__(self):
        return self._state.__str__()

    def getAbstractActions(self):
        return self._abactions_list

    def getAbstractActionsVector(self):
        return self._acvec

    def getAction(self, abstractaction):
        return self._abactions[abstractaction]

    def coerceAction(self, action):
        if type(action) == int:
            return self._abactions[action]
        elif type(action) == AbstractAction:
            return self._abactions[int(action)]
        elif type(action) == ConcreteAction:
            return action._action
        elif type(action) == PrismataAction:
            return action
        else:
            raise ValueError(f"Unable to coerce type for {action} ({type(action)})")

    def step(self):
        if self._players[self.activePlayer] and hasattr(self._players[self.activePlayer], "getMove"):
            self._players[self.activePlayer].getMove(self._state, self._move)
            if __debug__:
                print(f"Player {1+self.activePlayer} Move: {self._move}")
            self.doMove(self._move)
            return True
        elif self._players[self.activePlayer] and hasattr(self._players[self.activePlayer], "getAction"):
            saveActivePlayer = self.activePlayer
            if __debug__:
                print(f"Player {1+self.activePlayer} Move: ", end="")
            while saveActivePlayer == self.activePlayer and not self.isGameOver():
                action = self._players[self.activePlayer].getAction(self)
                if __debug__:
                    print(f"{action}<{type(action).__name__}>, ", end="")
                self.doAction(action)
            if __debug__:
                print("")
            return True
        else:
            return False

    def doMove(self, move):
        self._state.doMove(move)
        self._toVectorNeedsUpdate = True
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = PrismataAction(self.activePlayer, ActionType.END_PHASE, 0);
        self._acvec.fill(False)
        self._abactions.fill(0)
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        self._abactions_list = [AbstractAction.values[i] for i in range(self._acvec.shape[0]) if self._acvec[i]]

    def doAction(self, action):
        actionPointer = self.coerceAction(action)
        assert(actionPointer)
        self._state.doAction(actionPointer)
        self._toVectorNeedsUpdate = True
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = PrismataAction(self.activePlayer, ActionType.END_PHASE, 0);
        self._acvec.fill(False)
        self._abactions.fill(0)
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        self._abactions_list = [AbstractAction.values[i] for i in range(self._acvec.shape[0]) if self._acvec[i]]

    @lru_cache
    def getCardBuyableById(self, cardid):
        return self._state.getCardBuyableById(cardid)

    def getCardById(self, cardid):
        return self._state.getCardById(cardid)

    def getLiveCards(self, player):
        return self._state.getLiveCards(player, self._cards)

    def winner(self):
        return self._state.winner

    def annotate4(self, state):
        
        return {
                "gameOver": bool(self.isGameOver()),
                "player": Players.values.get(state[0], state[0]),
                "phase": Phases.values.get(state[1], state[1]),
                "activePlayer": {
                    "number": self.activePlayer + 1,
                    "resources": {
                        "Gold": state[2],
                        "Energy": state[3],
                        "Blue": state[4],
                        "Attack": state[5],
                        },
                    "cards": {
                        "Drone": (state[6], state[7], state[8]),
                        "Engineer": (state[9], state[10]),
                        "Blastforge": (state[11], state[12]),
                        "Steelsplitter": (state[13], state[14], state[15]),
                        },
                    },
                "inactivePlayer": {
                    "number": self.inactivePlayer + 1,
                    "resources": {
                        "Gold": state[16],
                        "Energy": state[17],
                        "Blue": state[18],
                        "Attack": state[19],
                        },
                    "cards": {
                        "Drone": (state[20], state[21], state[22]),
                        "Engineer": (state[23], state[24]),
                        "Blastforge": (state[25], state[26]),
                        "Steelsplitter": (state[27], state[28], state[29]),
                        },
                    },
                }
    
    def annotate11(self, state):
        
        return {
                "gameOver": bool(self.isGameOver()),
                "player": Players.values.get(state[0], state[0]),
                "phase": Phases.values.get(state[1], state[1]),
                "activePlayer": {
                    "number": self.activePlayer + 1,
                    "resources": {
                        "Gold": state[2],
                        "Energy": state[3],
                        "Blue": state[4],
                        "Attack": state[5],
                        },
                    "cards": {
                        "Drone": (state[6], state[7], state[8]),
                        "Engineer": (state[9], state[10]),
                        "Blastforge": (state[11], state[12]),
                        "Steelsplitter": (state[13], state[14], state[15]),
                        },
                    },
                "inactivePlayer": {
                    "number": self.inactivePlayer + 1,
                    "resources": {
                        "Gold": state[16],
                        "Energy": state[17],
                        "Blue": state[18],
                        "Attack": state[19],
                        },
                    "cards": {
                        "Drone": (state[20], state[21], state[22]),
                        "Engineer": (state[23], state[24]),
                        "Blastforge": (state[25], state[26]),
                        "Steelsplitter": (state[27], state[28], state[29]),
                        },
                    },
                }
    
    def toVector4(self):
        if not self._toVectorNeedsUpdate:
            return self._ie
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        countResources(self._state, self.activePlayer, 2, self._ie)
        countCards(self._state, self.activePlayer, 7, self._ie)
        countResources(self._state, self.inactivePlayer, 16, self._ie)
        countCards(self._state, self.inactivePlayer, 21, self._ie)
        self._toVectorNeedsUpdate = False
        return self._ie    
        
    def toVector11(self):
        if not self._toVectorNeedsUpdate:
            return self._ie
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        countResources(self._state, self.activePlayer, 2, self._ie)
        countCards(self._state, self.activePlayer, 9, self._ie)
        countResources(self._state, self.inactivePlayer, 42, self._ie)
        countCards(self._state, self.inactivePlayer, 49, self._ie)
        self._toVectorNeedsUpdate = False
        return self._ie

    def __iter__(self):
        return iter(self.toVector())

