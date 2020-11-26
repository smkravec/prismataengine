import enum
import numpy
from os import environ
from functools import lru_cache
from _prismataengine import *
import _prismataengine as p
from importlib import resources
if "PRISMATA_INIT_CARD_PATH" in environ:
    if environ.get("PRISMATA_INIT_CARD_PATH", None):
        p.init(environ.get("PRISMATA_INIT_CARD_PATH", None))
else:
    with resources.path(__name__, 'cardLibrary.jso') as path:
        p.init(str(path))
if "PRISMATA_INIT_AI_JSON_PATH" in environ:
    if environ.get("PRISMATA_INIT_AI_JSON_PATH", None):
        with open(environ.get("PRISMATA_INIT_AI_JSON_PATH")) as f:
            p.initAI(f.read())

def cslice(array, start, width):
    return array[start:start+width], start+width

class GameState():
    def __init__(self, string, cards=11, player1=None, player2=None, ai_json=None):
        if cards not in set(4, 11):
            raise "cards parameter must be set to 4 or 11"
        self._state = p.jsonStrToGameState(string)
        if type(self._state) is not p.PrismataGameState:
            raise "Failed to load PrismataGameState from JSON"
        if ai_json:
            p.initAI(p.ai_json)
        if type(player1) is str:
            player1 = p.getAIPlayer(p.Players.One, player1)
            if not player1:
                raise "Player 1 not found in loaded AI JSON or AI JSON not loaded"
        if player1 and not hasattr(player1, "getMove") and not hasattr(player1, "getAction"):
            raise "Player 1 must implement getMove(PrismataGameState, Move) or getAction(GameState)"
        if type(player2) is str:
            player2 = p.getAIPlayer(p.Players.Two, player2)
            if not player2:
                raise "Player 2 not found in loaded AI JSON or AI JSON not loaded"
        if player2 and not hasattr(player2, "getMove") and not hasattr(player2, "getAction"):
            raise "Player 2 must implement getMove(PrismataGameState, Move) or getAction(GameState)"
        self._players = (player1, player2)
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = p.PrismataAction(self.activePlayer, p.ActionType.END_PHASE, 0)
        self._actions = p.PrismataActions()
        self._toVectorNeedsUpdate = True
        self._move = p.Move()
        self._cards = p.CardVector()
        self.abstract_actions_available_size = 14 if cards == 4 else 32
        self.state_size = 30 if cards == 4 else 82
        self._abactions = numpy.zeros(self.abstract_actions_available_size, dtype=numpy.uintp)
        self._ie = numpy.zeros(self.state_size, dtype=numpy.uint16)
        self._acvec = numpy.zeros(self.abstract_actions_available_size, dtype=numpy.bool)
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        self.abstract_actions_list_disabled = player1 and player2 and hasattr(player1, "getMove") and hasattr(player2, "getMove")
        if not self.abstract_actions_list_disabled:
            self._abactions_list = [p.AbstractAction.values[i] for i in range(self.abstract_actions_available_size) if self._acvec[i]]
        self.toVector = self.toVector4 if cards == 4 else self.toVector11
        self.annotate  = self.annotate4 if cards == 4 else self.annotate11
        if __debug__:
            print("Initialized GameState")
            
    '''
    Virtual method, see __init__
    def toVector(self):
        pass
    '''

    '''
    Virtual method, see __init__
    def annotate(self, state):
        pass
    '''

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
        elif type(action) == p.AbstractAction:
            return self._abactions[int(action)]
        elif type(action) == p.PrismataAction:
            return action
        else:
            raise ValueError(f"Unable to coerce type for {action} ({type(action)})")

    def step(self):
        saveActivePlayer = self.activePlayer
        if self._players[self.activePlayer] and type(self._players[self.activePlayer]) == p.PrismataPlayer:
            while saveActivePlayer == self.activePlayer and not self.isGameOver():
                self._move.clear()
                p.getMove(self._players[self.activePlayer], self._state, self._move)
                if __debug__:
                    print(f"Player {1+self.activePlayer} Move: {self._move}")
                self.doMove(self._move)
            return True
        elif self._players[self.activePlayer] and hasattr(self._players[self.activePlayer], "getAction"):
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
            print(type(self._players[self.activePlayer]), dir(self._players[self.activePlayer]), self._players[self.activePlayer])
            return False

    def doMove(self, move):
        self._state.doMove(move)
        self._toVectorNeedsUpdate = True
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = p.PrismataAction(self.activePlayer, p.ActionType.END_PHASE, 0)
        self._acvec.fill(False)
        self._abactions.fill(0)
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        if not self.abstract_actions_list_disabled:
            self._abactions_list = [p.AbstractAction.values[i] for i in range(self.abstract_actions_available_size) if self._acvec[i]]

    def doAction(self, action):
        actionPointer = self.coerceAction(action)
        assert(actionPointer)
        self._state.doAction(actionPointer)
        self._toVectorNeedsUpdate = True
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = p.PrismataAction(self.activePlayer, p.ActionType.END_PHASE, 0)
        self._acvec.fill(False)
        self._abactions.fill(0)
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        if not self.abstract_actions_list_disabled:
            self._abactions_list = [p.AbstractAction.values[i] for i in range(self.abstract_actions_available_size) if self._acvec[i]]

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
                "player": p.Players.values.get(state[0], state[0]),
                "phase": p.Phases.values.get(state[1], state[1]),
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
        stateStruct = {}
        stateStruct["player"] = p.Players.values.get(state[0])
        stateStruct["phase"] = p.Phases.values.get(state[1])
        i = 2
        player = "activePlayer"
        stateStruct[player] = {"resources": {}, "cards": {}}
        [stateStruct[player]["resources"]["Gold"], stateStruct[player]["resources"]["Energy"], stateStruct[player]["resources"]["Blue"], stateStruct[player]["resources"]["Red"], stateStruct[player]["resources"]["Green"], stateStruct[player]["resources"]["Attack"]], i = cslice(state, i, 6)
        stateStruct[player]["cards"]["Drone"], i = cslice(state, i, 3)
        stateStruct[player]["cards"]["Engineer"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Blastforge"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Animus"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Conduit"], i = cslice(state, i, 4)
        stateStruct[player]["cards"]["Steelsplitter"], i = cslice(state, i, 3)
        stateStruct[player]["cards"]["Wall"], i = cslice(state, i, 1)
        stateStruct[player]["cards"]["Rhino"], i = cslice(state, i, 6)
        stateStruct[player]["cards"]["Tarsier"], i = cslice(state, i, 3)
        stateStruct[player]["cards"]["Forcefield"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Gauss Cannon"], i = cslice(state, i, 6)
        player = "inactivePlayer"
        stateStruct[player] = {"resources": {}, "cards": {}}
        [stateStruct[player]["resources"]["Gold"], stateStruct[player]["resources"]["Energy"], stateStruct[player]["resources"]["Blue"], stateStruct[player]["resources"]["Red"], stateStruct[player]["resources"]["Green"], stateStruct[player]["resources"]["Attack"]], i = cslice(state, i, 6)
        stateStruct[player]["cards"]["Drone"], i = cslice(state, i, 3)
        stateStruct[player]["cards"]["Engineer"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Blastforge"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Animus"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Conduit"], i = cslice(state, i, 4)
        stateStruct[player]["cards"]["Steelsplitter"], i = cslice(state, i, 3)
        stateStruct[player]["cards"]["Wall"], i = cslice(state, i, 1)
        stateStruct[player]["cards"]["Rhino"], i = cslice(state, i, 6)
        stateStruct[player]["cards"]["Tarsier"], i = cslice(state, i, 3)
        stateStruct[player]["cards"]["Forcefield"], i = cslice(state, i, 2)
        stateStruct[player]["cards"]["Gauss Cannon"], i = cslice(state, i, 6)
        print(i)
        return stateStruct
 
    def toVector4(self):
        if not self._toVectorNeedsUpdate:
            return self._ie
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        p.countResources4(self._state, self.activePlayer, 2, self._ie)
        p.countCards4(self._state, self.activePlayer, 7, self._ie)
        p.countResources4(self._state, self.inactivePlayer, 16, self._ie)
        p.countCards4(self._state, self.inactivePlayer, 21, self._ie)
        self._toVectorNeedsUpdate = False
        return self._ie    
        
    def toVector11(self):
        if not self._toVectorNeedsUpdate:
            return self._ie
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        p.countResources11(self._state, self.activePlayer, 2, self._ie)
        p.countCards11(self._state, self.activePlayer, 9, self._ie)
        p.countResources11(self._state, self.inactivePlayer, 42, self._ie)
        p.countCards11(self._state, self.inactivePlayer, 49, self._ie)
        self._toVectorNeedsUpdate = False
        return self._ie

    def __iter__(self):
        return iter(self.toVector())

