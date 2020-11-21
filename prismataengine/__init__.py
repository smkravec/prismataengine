import enum
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
    BuySteelSplitter = enum.auto()
    BuyBlastForge = enum.auto()
    UseAbilityDrone = enum.auto()
    UseAbilitySteelSplitter = enum.auto()
    AssignBlockerEngineer = enum.auto()
    AssignBlockerDrone = enum.auto()
    AssignBlockerSteelSplitter = enum.auto()
    AssignBreachEngineer = enum.auto()
    AssignBreachDrone = enum.auto()
    AssignBreachSteelSplitter = enum.auto()
    AssignBreachBlastForge = enum.auto()
    EndPhase = enum.auto()

    def fromAction(gamestate, action):
        action = ConcreteAction(gamestate, action)
        if action.type == ActionType.END_PHASE:
            return AbstractAction.EndPhase
        elif action.type == ActionType.USE_ABILITY:
            if action.card.name == "Drone":
                return AbstractAction.UseAbilityDrone
            elif action.card.name == "Treant":
                return AbstractAction.UseAbilitySteelSplitter
            else:
                return None
        elif action.type == ActionType.ASSIGN_BREACH:
            if action.card.name == "Engineer":
                return AbstractAction.AssignBreachEngineer
            elif action.card.name == "Drone":
                return AbstractAction.AssignBreachDrone
            elif action.card.name == "Treant":
                return AbstractAction.AssignBreachSteelSplitter
            elif action.card.name == "Brooder":
                return AbstractAction.AssignBreachBlastForge
            else:
                return None
        elif action.type == ActionType.ASSIGN_BLOCKER:
            if action.card.name == "Engineer":
                return AbstractAction.AssignBlockerEngineer
            elif action.card.name == "Drone":
                return AbstractAction.AssignBlockerDrone
            elif action.card.name == "Treant":
                return AbstractAction.AssignBlockerSteelSplitter
            else:
                return None
        elif action.type == ActionType.BUY:
            if action.card.name == "Engineer":
                return AbstractAction.BuyEngineer
            elif action.card.name == "Drone":
                return AbstractAction.BuyDrone
            elif action.card.name == "Treant":
                return AbstractAction.BuySteelSplitter
            elif action.card.name == "Brooder":
                return AbstractAction.BuyBlastForge
            else:
                return None
        else:
            print(action.type)
            print(action.card.name)
            return None
        
class ConcreteAction():
    def __init__(self, gamestate, action):
        self._action = action
        self.card = gamestate.getCardById(action.cardid)

    def __getattr__(self, key):
        if key == "card":
            return self.card
        else:
            return getattr(self._action, key)

class GameState():
    def __init__(self, string):
        self._state = jsonStrToGameState(string)
        self.endPhase = PrismataAction(self._state.activePlayer, ActionType.END_PHASE, 0);
        self._actions = PrismataActions()

    def getRawState(self):
        return self._state

    def getCardById(self, cardid):
        return self._state.getCardByID(cardid)

    def isLegal(self, action):
        return self._state.isLegal(self.coerceAction(action))

    def json(self):
        return self._state.json()

    def isGameOver(self):
        return self._state.isGameOver()

    def __str__(self):
        return self._state.__str__()

    def getAbstractActions(self):
        self._generateLegalActions()
        actions = set([AbstractAction.fromAction(self, action) for action in self._actions])
        if AbstractAction.EndPhase not in actions and self.isLegal(self.endPhase):
            actions.add(AbstractAction.EndPhase)
        return list(actions)

    def _generateLegalActions(self):
        self._actions.clear()
        self._state.generateLegalActions(self._actions)

    def getAction(self, abstractaction):
        self._generateLegalActions()
        return next(filter(lambda t: AbstractAction.fromAction(self, t) == abstractaction, self._actions), self.endPhase)

    def coerceAction(self, action):
        if type(action) == ConcreteAction:
            return action._action
        elif type(action) == PrismataAction:
            return action
        elif type(action) == AbstractAction:
            return self.getAction(action)
        else:
            raise ValueError(f"Unable to coerce type for {action} ({type(action)})")

    def doAction(self, action):
        self._state.doAction(self.coerceAction(action))

