import prismataengine
gamestate = prismataengine.GameState('''{
                 "whiteMana":"0HH",
                 "blackMana":"0HH",
                 "phase":"action",
                 "table":
                 [
                     {"cardName":"Drone", "color":0, "amount":6},
                     {"cardName":"Engineer", "color":0, "amount":2},
                     {"cardName":"Drone", "color":1, "amount":7},
                     {"cardName":"Engineer", "color":1, "amount":2}
                 ],
                 "cards":["Drone","Engineer","Blastforge","Animus", "Conduit", "Steelsplitter", "Wall", "Rhino", "Tarsier", "Forcefield", "Gauss Cannon"]
             }''')
print(gamestate.toVector())
gamestate = prismataengine.GameState('''{
                 "whiteMana":"0HH",
                 "blackMana":"0HH",
                 "phase":"action",
                 "table":
                 [
                     {"cardName":"Drone", "color":0, "amount":1},
                     {"cardName":"Drone", "color":0, "amount":2, "constructionTime":1},
                     {"cardName":"Drone", "color":0, "amount":3, "blocking":false},
                     {"cardName":"Engineer", "color":0, "amount":4},
                     {"cardName":"Blastforge", "color":0 , "amount":5},
                     {"cardName":"Animus", "color":0 , "amount":6},
                     {"cardName":"Conduit", "color":0 , "amount":7},
                     {"cardName":"Drone", "color":1, "amount":8},
                     {"cardName":"Engineer", "color":1, "amount":9}
                 ],
                 "cards":["Drone","Engineer","Blastforge","Animus", "Conduit", "Steelsplitter", "Wall", "Rhino", "Tarsier", "Forcefield", "Gauss Cannon"]
             }''')
print(gamestate.toVector())
print(gamestate.json())
