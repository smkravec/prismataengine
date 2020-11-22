import enum
import numpy
from os import environ
from _prismataengine import *
from importlib import resources
if "PRISMATA_INIT_CARD_PATH" in environ:
    if environ.getenv("PRISMATA_INIT_CARD_PATH", None):
        init(environ.getenv("PRISMATA_INIT_CARD_PATH", None))
else:
    with resources.path(__name__, 'cardLibrary.jso') as path:
        init(str(path))

class AbstractAction(enum.Enum):
    BuyEngineer = enum.auto()
    BuyDrone = enum.auto()
    BuySteelsplitter = enum.auto()
    BuyBlastforge = enum.auto()
    UseAbilityDrone = enum.auto()
    UseAbilitySteelsplitter = enum.auto()
    AssignBlockerEngineer = enum.auto()
    AssignBlockerDrone = enum.auto()
    AssignBlockerSteelsplitter = enum.auto()
    AssignBreachEngineer = enum.auto()
    AssignBreachDrone = enum.auto()
    AssignBreachSteelsplitter = enum.auto()
    AssignBreachBlastforge = enum.auto()
    EndPhase = enum.auto()

    def fromAction(gamestate, action):
        action = ConcreteAction(gamestate, action)
        try:
            return fromActionDispatch[action.type][action.card.type]
        except Exception as e:
            print(f"Exception: {e} ({type(e)})\nActionType: {action.type}, CardType: {action.card.type}, CardName: {action.card.name}")
            return None
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
        if self.type == ActionType.BUY:
            self.card = gamestate.getCardBuyableById(action.cardid)
        else:
            self.card = gamestate.getCardById(action.cardid)

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
        self._cards = CardVector()
        self._state.generateLegalActions(self._actions)
        self._abactions = dict()
        for action in self._actions:
            self._abactions[AbstractAction.fromAction(self, action)] = action
        if self.isLegal(self.endPhase):
            self._abactions[AbstractAction.EndPhase] = self.endPhase
        self._abactions_list = list(self._abactions.keys())
        self._ie = numpy.zeros(31, dtype=numpy.uint16)

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


    def getAction(self, abstractaction):
        return self._abactions[abstractaction]

    def coerceAction(self, action):
        if type(action) == AbstractAction:
            return self.getAction(action)
        elif type(action) == ConcreteAction:
            return action._action
        elif type(action) == PrismataAction:
            return action
        else:
            raise ValueError(f"Unable to coerce type for {action} ({type(action)})")

    def doAction(self, action):
        # print(action, end="/")
        action = self.coerceAction(action)
        # print(action.json(), end="/")
        # print(ConcreteAction(self,action).card)
        self._state.doAction(action)
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = PrismataAction(self.activePlayer, ActionType.END_PHASE, 0);
        self._actions.clear()
        self._state.generateLegalActions(self._actions)
        self._abactions.clear()
        for action in self._actions:
            self._abactions[AbstractAction.fromAction(self, action)] = action
        # if self.isLegal(self.endPhase):
        #     self._abactions[AbstractAction.EndPhase] = self.endPhase
        self._abactions_list = list(self._abactions.keys())

    def getCardBuyableById(self, cardid):
        return self._state.getCardBuyableById(cardid)

    def getCardById(self, cardid):
        return self._state.getCardById(cardid)

    def getLiveCards(self, player):
        return self._state.getLiveCards(player, self._cards)

    def winner(self):
        return f"Player {self._state.winner + 1}"

    def annotate(self, state):
        return {
                "gameOver": bool(state[0]),
                "player": state[1] + 1,
                "phase": Phases.values.get(state[2], state[2]),
                "activePlayer": {
                    "number": self.activePlayer + 1,
                    "resources": {
                        "Gold": state[3],
                        "Energy": state[4],
                        "Blue": state[5],
                        "Attack": state[6],
                        },
                    "cards": {
                        "Drone": (state[7], state[8], state[9]),
                        "Engineer": (state[10], state[11]),
                        "Blastforge": (state[12], state[13]),
                        "Steelsplitter": (state[14], state[15], state[16]),
                        },
                    },
                "inactivePlayer": {
                    "number": self.inactivePlayer + 1,
                    "resources": {
                        "Gold": state[17],
                        "Energy": state[18],
                        "Blue": state[19],
                        "Attack": state[20],
                        },
                    "cards": {
                        "Drone": (state[21], state[22], state[23]),
                        "Engineer": (state[24], state[25]),
                        "Blastforge": (state[26], state[27]),
                        "Steelsplitter": (state[28], state[29], state[30]),
                        },
                    },
                }
    def toVector(self):
        self._ie[0] = self.isGameOver()
        self._ie[1] = self.activePlayer
        self._ie[2] = self._state.activePhase
        countResources(self._state, self.activePlayer, 3, self._ie)
        (countCards(self.getLiveCards(self.activePlayer), 8, self._ie))
        countResources(self._state, self.inactivePlayer, 17, self._ie)
        (countCards(self.getLiveCards(self.inactivePlayer), 22, self._ie))
        return self._ie

    def __iter__(self):
        return iter(self.toVector())

