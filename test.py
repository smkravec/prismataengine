import json, prismataengine, random
import timeit

def runGame():
    gamestate = prismataengine.GameState('''{
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
    while not gamestate.isGameOver():
        actions = gamestate.getAbstractActions()
        action = random.choice(actions)
        gamestate.doAction(action)

print(timeit.timeit(runGame, setup='gc.enable()', number=1000))
