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

class AbstractAction(enum.IntEnum):
    BuyEngineer = 0
    BuyDrone = 1
    BuySteelsplitter = 2
    BuyBlastforge = 3
    UseAbilityDrone = 4
    UseAbilitySteelsplitter = 5
    AssignBlockerEngineer = 6
    AssignBlockerDrone = 7
    AssignBlockerSteelsplitter = 8
    AssignBreachEngineer = 9
    AssignBreachDrone = 10
    AssignBreachSteelsplitter = 11
    AssignBreachBlastforge = 12
    EndPhase = 13

fromActionDispatch = {
        ActionType.END_PHASE: {
            0: AbstractAction.EndPhase,
            2: AbstractAction.EndPhase,
            3: AbstractAction.EndPhase,
            4: AbstractAction.EndPhase,
            7: AbstractAction.EndPhase,
            },
        ActionType.USE_ABILITY: {
            2: AbstractAction.UseAbilityDrone,
            7: AbstractAction.UseAbilitySteelsplitter,
            },
        ActionType.ASSIGN_BREACH: {
            3: AbstractAction.AssignBreachEngineer,
            2: AbstractAction.AssignBreachDrone,
            7: AbstractAction.AssignBreachSteelsplitter,
            4: AbstractAction.AssignBreachBlastforge
            },
        ActionType.ASSIGN_BLOCKER: {
            3: AbstractAction.AssignBlockerEngineer,
            2: AbstractAction.AssignBlockerDrone,
            7: AbstractAction.AssignBlockerSteelsplitter,
            },
        ActionType.BUY: {
            3: AbstractAction.BuyEngineer,
            2: AbstractAction.BuyDrone,
            7: AbstractAction.BuySteelsplitter,
            4: AbstractAction.BuyBlastforge
            }
        }
        
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
    def __init__(self, string, player1=None, player2=None):
        self._state = jsonStrToGameState(string)
        self._players = (player1, player2)
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = PrismataAction(self.activePlayer, ActionType.END_PHASE, 0);
        self._actions = PrismataActions()
        self._toVectorNeedsUpdate = True
        self._move = Move()
        self._cards = CardVector()
        self._abactions = [None] * 14
        self._ie = numpy.zeros(30, dtype=numpy.uint16)
        self._acvec = numpy.zeros(14, dtype=numpy.bool)
        self._state.generateLegalActions(self._actions)
        for action in self._actions:
            offset = fromActionDispatch[action.type][action.cardtype(self._state)]
            self._abactions[int(offset)] = action
            self._acvec[int(offset)] = True
        if self.isLegal(self.endPhase):
            self._abactions[int(AbstractAction.EndPhase)] = self.endPhase
            self._acvec[int(AbstractAction.EndPhase)] = True
        self._abactions_list = [AbstractAction(i) for i in range(14) if self._acvec[i]]

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
                    print(f"{action}, ", end="")
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
        self._actions.clear()
        self._state.generateLegalActions(self._actions)
        self._acvec.fill(False)
        self._abactions.clear()
        for action in self._actions:
            offset = fromActionDispatch[action.type][action.cardtype(self._state)]
            self._abactions[int(offset)] = action
            self._acvec[int(offset)] = True
        if self.isLegal(self.endPhase):
            self._abactions[int(AbstractAction.EndPhase)] = self.endPhase
            self._acvec[int(AbstractAction.EndPhase)] = True
        self._abactions_list = [AbstractAction(i) for i in range(14) if self._acvec[i]]

    def doAction(self, action):
        self._state.doAction(self.coerceAction(action))
        self._toVectorNeedsUpdate = True
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = PrismataAction(self.activePlayer, ActionType.END_PHASE, 0);
        self._actions.clear()
        self._state.generateLegalActions(self._actions)
        self._acvec.fill(False)
        for i in range(14):
            self._abactions[i] = None
        for action in self._actions:
            offset = fromActionDispatch[action.type][action.cardtype(self._state)]
            self._abactions[int(offset)] = action
            self._acvec[int(offset)] = True
        if self.isLegal(self.endPhase):
            self._abactions[int(AbstractAction.EndPhase)] = self.endPhase
            self._acvec[int(AbstractAction.EndPhase)] = True
        self._abactions_list = [AbstractAction(i) for i in range(14) if self._acvec[i]]

    @lru_cache
    def getCardBuyableById(self, cardid):
        return self._state.getCardBuyableById(cardid)

    def getCardById(self, cardid):
        return self._state.getCardById(cardid)

    def getLiveCards(self, player):
        return self._state.getLiveCards(player, self._cards)

    def winner(self):
        return self._state.winner

    def annotate(self, state):
        return {
                "gameOver": bool(self.isGameOver()),
                "player": state[0] + 1,
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
    def toVector(self):
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

    def __iter__(self):
        return iter(self.toVector())

