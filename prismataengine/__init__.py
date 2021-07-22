import enum
import numpy
from logger import logger
from os import environ
from functools import lru_cache
from _prismataengine import * #Imports all exported methods from boost
import _prismataengine as p
from importlib import resources

#Needs these files in environment path, init and initAI defined in prismataengineboost
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
else:
    with resources.path(__name__, 'AI_config.txt') as path:
        with open(path) as f:
            p.initAI(f.read())

#For creating annotation of state
def cslice(array, start, width):
    return array[start:start+width], start+width

class GameState():
    def __init__(self, game_state, cards=11, player1=None, player2=None, ai_json=None, one_hot=False):
        if cards not in (4, 11):
            raise Exception("cards parameter must be set to 4 or 11")
        self._state = p.jsonStrToGameState(game_state) if type(game_state)==str else game_state
        if type(self._state) is not p.PrismataGameState:
            raise Exception(f"Failed to load PrismataGameState from JSON (type(_state) = {type(self._state)})")
        if ai_json:
            p.initAI(p.ai_json)
        if type(player1) is str: #String values indicate pulling existing AI players from "PRISMATA_INIT_AI_JSON_PATH"
            player1 = p.getAIPlayer(p.Players.One, player1)
            if not player1:
                raise Exception("Player 1 not found in loaded AI JSON or AI JSON not loaded")
        if player1 and not hasattr(player1, "getMove") and not hasattr(player1, "getAction") and type(player1) is not p.PrismataPlayer:
            raise Exception("Player 1 must implement getMove(PrismataGameState, Move) or getAction(GameState) or be a PrismataPlayer pointer")
        if type(player2) is str:
            player2 = p.getAIPlayer(p.Players.Two, player2)
            if not player2:
                raise Exception("Player 2 not found in loaded AI JSON or AI JSON not loaded")
        if player2 and not hasattr(player2, "getMove") and not hasattr(player2, "getAction") and type(player2) is not p.PrismataPlayer:
            raise Exception(f"Player 2 must implement getMove(PrismataGameState, Move) or getAction(GameState) or be a PrismataPlayer pointer")
        self._players = (player1, player2)
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        self.endPhase = p.PrismataAction(self.activePlayer, p.ActionType.END_PHASE, 0)
        self._actions = p.PrismataActions() #std::vector of PrismataActions
        self._toVectorNeedsUpdate = True
        self._move = p.Move()
        self._cards = p.CardVector() #std::vector of Cards
        if cards==4 and not one_hot:
            self.abstract_actions_available_size = 14
            self.state_size = 30
            self._ie = numpy.zeros(self.state_size, dtype=numpy.uint16)
            self.toVector = self.toVector4
        elif cards==4 and one_hot:
            self.abstract_actions_available_size = 14
            self.state_size = 640+30
            self._ie = numpy.zeros(30, dtype=numpy.uint16)
            self._oh = numpy.zeros(self.state_size, dtype=numpy.uint16)
            self.toVector = self.toVectorOH4
        elif cards==11 and not one_hot:
            self.abstract_actions_available_size = 32
            self.state_size = 82
            self._ie = numpy.zeros(self.state_size, dtype=numpy.uint16)
            self.toVector = self.toVector11
        elif cards==11 and one_hot:
            self.abstract_actions_available_size = 32
            self.state_size = 1160+82
            self._ie = numpy.zeros(82, dtype=numpy.uint16)
            self._oh = numpy.zeros(self.state_size, dtype=numpy.uint16)
            self.toVector = self.toVectorOH11
        else:
            raise ValueError('Cards invalid. Implemented: 4 and 11')
        self._abactions = numpy.zeros(self.abstract_actions_available_size, dtype=numpy.uintp) #Array of pointers to Prismata::Actions
        self._acvec = numpy.zeros(self.abstract_actions_available_size, dtype=numpy.bool_) #Actual boolean vector encoding legal abstract actions
        self._state.generateLegalActionsVector(self._actions, self._acvec, self._abactions, self.endPhase)
        #Agents from upstream don't need abstract actions
        self.abstract_actions_list_disabled = player1 and player2 and type(player1) is p.PrismataPlayer and type(player2) is p.PrismataPlayer
        if not self.abstract_actions_list_disabled:
            self._abactions_list = [p.AbstractAction.values[i] for i in range(self.abstract_actions_available_size) if self._acvec[i]]
        self.annotate  = self.annotate4 if cards == 4 else self.annotate11
        if __debug__:
            logger.debug("Initialized GameState")

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

    #Accepts a variety of types and ways of referring to an abstract action
    def coerceAction(self, action):
        if type(action) == int:
            return p.unsafeIntToAction(self._abactions[action])
        elif type(action) == numpy.uint64:
            return p.unsafeIntToAction(self._abactions[int(action)])
        elif type(action) == p.AbstractAction:
            return p.unsafeIntToAction(self._abactions[int(action)])
        elif type(action) == p.PrismataAction:
            return action
        else:
            raise ValueError(f"Unable to coerce type for {action} ({type(action)})")

    def step(self):
        saveActivePlayer = self.activePlayer
        #PrismataPlayers do whole moves which are sequences of actions taken within a turn
        if self._players[self.activePlayer] and (type(self._players[self.activePlayer]) in [p.PrismataPlayer, p.PrismataPlayerPython] or hasattr(self._players[self.activePlayer], "getMove")):
            while saveActivePlayer == self.activePlayer and not self.isGameOver():
                self._move.clear()
                p.getMove(self._players[self.activePlayer], self._state, self._move)
                if __debug__:
                    logger.debug(f"Player {1+self.activePlayer} Move: {self._move}")
                self.doMove(self._move)
            return True
        elif self._players[self.activePlayer] and hasattr(self._players[self.activePlayer], "getAction"):
            #Other agents we assume have just an action method
            if __debug__:
                logger.debug(f"Player {1+self.activePlayer} Move: ", end="")
            while saveActivePlayer == self.activePlayer and not self.isGameOver():
                action = self._players[self.activePlayer].getAction(self)
                if __debug__:
                    logger.debug(f"{action}<{type(action).__name__}>, ", end="",flush=True)
                self.doAction(action)
            if __debug__:
                logger.debug("")
            return True
        else:
            if __debug__:
                logger.error("Couldn't do an action, dump debug info")
                logger.error(f"{type(self._players[self.activePlayer])}, {dir(self._players[self.activePlayer])}, {self._players[self.activePlayer]}")
            return False

    def doMove(self, move):
        self._state.doMove(move)
        self._toVectorNeedsUpdate = True
        #Reset active and inactive players
        self.inactivePlayer = self._state.inactivePlayer
        self.activePlayer = self._state.activePlayer
        #Create new endPhase action with new active player
        self.endPhase = p.PrismataAction(self.activePlayer, p.ActionType.END_PHASE, 0)
        self._acvec.fill(False) #Clear list of abstract actions
        self._abactions.fill(0) #Reset list of abstractAction offsets that map to prismataAction pointers
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
        return stateStruct

    def toVector4(self):
        if not self._toVectorNeedsUpdate:
            return self._ie
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        p.countResources4(self._state, self.activePlayer, 2, self._ie) #The number is an offset beginning
        p.countCards4(self._state, self.activePlayer, 5, self._ie)
        p.countResources4(self._state, self.inactivePlayer, 16, self._ie)
        p.countCards4(self._state, self.inactivePlayer, 19, self._ie)
        self._toVectorNeedsUpdate = False
        return self._ie

    def toVectorOH4(self):
        if not self._toVectorNeedsUpdate:
            return self._oh
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        p.countResources4(self._state, self.activePlayer, 2, self._ie)
        p.countCards4(self._state, self.activePlayer, 5, self._ie)
        p.countResources4(self._state, self.inactivePlayer, 16, self._ie)
        p.countCards4(self._state, self.inactivePlayer, 19, self._ie)
        p.oneHot4(self._ie, self._oh)
        self._toVectorNeedsUpdate = False
        return self._oh

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

    def toVectorOH11(self):
        if not self._toVectorNeedsUpdate:
            return self._oh
        self._ie[0] = self.activePlayer
        self._ie[1] = self._state.activePhase
        p.countResources11(self._state, self.activePlayer, 2, self._ie)
        p.countCards11(self._state, self.activePlayer, 9, self._ie)
        p.countResources11(self._state, self.inactivePlayer, 42, self._ie)
        p.countCards11(self._state, self.inactivePlayer, 49, self._ie)
        p.oneHot11(self._ie, self._oh)
        self._toVectorNeedsUpdate = False
        return self._oh

    def __iter__(self):
        return iter(self.toVector())
