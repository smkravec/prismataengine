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
            4: AbstractAction.AssignBreachSteelsplitter,
            7: AbstractAction.AssignBreachBlastforge
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
        self.card = gamestate.getCardById(action.cardid)

    def __getattr__(self, key):
        return getattr(self._action, key)

class GameState():
    def __init__(self, string):
        self._state = jsonStrToGameState(string)
        self.endPhase = PrismataAction(self._state.activePlayer, ActionType.END_PHASE, 0);
        self._actions = PrismataActions()
        self._cards = CardVector()
        self._state.generateLegalActions(self._actions)
        self._abactions = dict()
        for action in self._actions:
            self._abactions[AbstractAction.fromAction(self, action)] = action
        if self.isLegal(self.endPhase):
            self._abactions[AbstractAction.EndPhase] = self.endPhase
        self._abactions_list = list(self._abactions.keys())
        self._ie = numpy.zeros(31, dtype=numpy.uint)
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer

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
        self._state.doAction(self.coerceAction(action))
        self._actions.clear()
        self._state.generateLegalActions(self._actions)
        self._abactions.clear()
        for action in self._actions:
            self._abactions[AbstractAction.fromAction(self, action)] = action
        if self.isLegal(self.endPhase):
            self._abactions[AbstractAction.EndPhase] = self.endPhase
        self._abactions_list = list(self._abactions.keys())
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer

    def getCardById(self, cardid):
            return self._state.getCardByID(cardid)

    def getLiveCards(self, player):
        return self._state.getLiveCards(player, self._cards)

    def annotate(self, state):
        return {
                "gameOver": state[0],
                "player": state[1],
                "phase": state[2],
                "activePlayer": {
                    "resources": {
                        "gold": state[3],
                        "energy": state[4],
                        "blue": state[5],
                        "attack": state[6],
                        },
                    "cards": {
                        "engineer": (state[7], state[8]),
                        "brooder": (state[9], state[10]),
                        "drone": (state[11], state[12], state[13]),
                        "treant": (state[14], state[15], state[16]),
                        },
                    },
                "inactivePlayer": {
                    "resources": {
                        "gold": state[17],
                        "energy": state[18],
                        "blue": state[19],
                        "attack": state[20],
                        },
                    "cards": {
                        "engineer": (state[21], state[22]),
                        "brooder": (state[23], state[24]),
                        "drone": (state[25], state[26], state[27]),
                        "treant": (state[28], state[29], state[30]),
                        },
                    },
                }
    def toVector(self):
        self._ie[0] = self.isGameOver()
        self._ie[1] = self.activePlayer
        self._ie[2] = self._state.activePhase
        countResources(self._state, self.activePlayer, 3, self._ie)
        countCards(self.getLiveCards(self.activePlayer), 7, self._ie)
        countResources(self._state, self.inactivePlayer, 17, self._ie)
        countCards(self.getLiveCards(self.inactivePlayer), 21, self._ie)
        return self._ie

    def __iter__(self):
        return iter(self.toVector())

