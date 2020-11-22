import json, prismataengine as p, random
from pprint import pprint
import numpy
import timeit, time

class PythonRandomPlayer(object):
    def getAction(self, gamestate):
        state = gamestate.toVector()
        actions = gamestate.getAbstractActions()
        # print(actions)
        # print([action.json() for action in gamestate._actions])
        # print([str(p.ConcreteAction(gamestate, action)) for action in gamestate._actions])
        action = random.choice(actions)
        return action

def runGame():
    gamestate = p.GameState('''{
             "whiteMana":"0HH",
             "blackMana":"0",
             "phase":"action",
             "table":
             [
                 {"cardName":"Drone", "color":0, "amount":6},
                 {"cardName":"Engineer", "color":0, "amount":2},
                 {"cardName":"Drone", "color":1, "amount":7},
                 {"cardName":"Engineer", "color":1, "amount":2}
             ],
             "cards":["Drone","Engineer","Blastforge","Steelsplitter"]
         }''')#, player1=PythonRandomPlayer(), player2=p.AIPlayerRandom(1))
    # print('----------------NEW GAME NEW LIFE-------------')
    lastPlayer = 0
    while not gamestate.isGameOver():
        # print([(card.type, card.name) for card in gamestate.getLiveCards(gamestate.activePlayer)])
        state = gamestate.toVector()
        print(gamestate.annotate(state))
        if gamestate.activePlayer != lastPlayer:
            lastPlayer = gamestate.activePlayer
            # pprint(gamestate.annotate(state))
            # print(numpy.array_str(state, max_line_width=120))
            # print(gamestate.json())
            # time.sleep(0.1)
        gamestate.step()
        actions = gamestate.getAbstractActions()
        # print(actions)
        # print([action.json() for action in gamestate._actions])
        # print([str(p.ConcreteAction(gamestate, action)) for action in gamestate._actions])
        action = random.choice(actions)
        gamestate.doAction(action)
    print(f"Winner: {gamestate.winner()}")
    state = gamestate.toVector()
    pprint(gamestate.annotate(state))
    print(numpy.array_str(state, max_line_width=120))

n = 1
# for n in range(n):
#     runGame()
time = timeit.timeit(runGame, setup='gc.enable()', number=n)
print(f"n = {n}, wall time = {time} ({1/time*n} Hz)")
