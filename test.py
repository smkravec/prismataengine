import json, prismataengine as p, random
import numpy
import timeit, time

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
         }''')
    print('----------------NEW GAME NEW LIFE-------------')
    lastPlayer = 0
    while not gamestate.isGameOver():
        # print([(card.type, card.name) for card in gamestate.getLiveCards(gamestate.activePlayer)])
        state = gamestate.toVector()
        if gamestate.activePlayer != lastPlayer:
            lastPlayer = gamestate.activePlayer
            print(gamestate.annotate(state))
            print(numpy.array_str(state, max_line_width=120))
            # print(gamestate.json())
            time.sleep(0.1)
        actions = gamestate.getAbstractActions()
        action = random.choice(actions)
        gamestate.doAction(action)
    # print(numpy.array_str(state, max_line_width=120))

n = 100
for n in range(n):
    runGame()
# time = timeit.timeit(runGame, setup='gc.enable()', number=n)
# print(f"n = {n}, wall time = {time} ({1/time*100} Hz)")
