#pragma once

#include "Action.h"
#include "Card.h"
#include "Common.h"
#include "Constants.h"
#include "GameState.h"
#include "Move.h"
#include "AIParameters.h"
#include "Prismata.h"
#include "Resources.h"
#include "rapidjson.h"
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/numpy/ndarray.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/variant.hpp>

namespace Player {
void getMove(std::shared_ptr<Prismata::Player> p, const Prismata::GameState &g,
             Prismata::Move &m);
};
namespace GameState {
bool doActionInt(Prismata::GameState &g, uintptr_t a);
Prismata::CardVector &getPlayerCards(const Prismata::GameState &g,
                                     const Prismata::PlayerID player,
                                     Prismata::CardVector &c);
Prismata::GameState *fromJson(const std::string &json_str);
void cardCounting4(const Prismata::GameState &g, const Prismata::PlayerID player,
                  int offset, boost::python::numpy::ndarray &n);
void cardCounting11(const Prismata::GameState &g, const Prismata::PlayerID player,
                  int offset, boost::python::numpy::ndarray &n);
void copyResources4(Prismata::GameState &g, const Prismata::PlayerID p,
                   int offset, boost::python::numpy::ndarray &n);
void copyResources11(Prismata::GameState &g, const Prismata::PlayerID p,
                   int offset, boost::python::numpy::ndarray &n);
void generateLegalActions(const Prismata::GameState &g,
                          std::vector<Prismata::Action> &av,
                          boost::python::numpy::ndarray acv,
                          const boost::python::numpy::ndarray aa,
                          Prismata::Action &endPhase);
}; // namespace GameState
namespace Card {
size_t getBuyableTypeId(const Prismata::CardBuyable &c);
size_t getTypeId(const Prismata::Card &c);
static inline unsigned int getBin4(const Prismata::Card &c);
static inline unsigned int getBin11(const Prismata::Card &c);
// static inline unsigned int getOffset(const Prismata::Card &c, int offset);
std::string buyableStringify(const Prismata::CardBuyable &c);
std::string stringify(const Prismata::Card &c);
std::string toJson(const Prismata::Card &c);
}; // namespace Card
namespace Action {

boost::variant<Prismata::Card, Prismata::CardBuyable>
getCard(const Prismata::Action &a, const Prismata::GameState &g);
size_t getCardType(const Prismata::Action &a, const Prismata::GameState &g);
static inline const char *typeStringify(int v);
std::string stringify(const Prismata::Action &a);
std::string stringifyp(Prismata::Action *a);
std::string toJson(const Prismata::Action &a);
std::string vectorStringify(const std::vector<Prismata::Action> &v);
std::string vectorToJson(const std::vector<Prismata::Action> &v);
/* 
std::map<unsigned int, unsigned int> stateOffset4 = {
    {8, 1},  // Drone not under construction, can't block
    {9, 2},  // Drone not under construction, can block
    {10, 0}, // Drone under construction
    {11, 0}, // Drone under construction
    {12, 3}, // Engineer not under construction
    {13, 3}, // Engineer not under construction
    {14, 4}, // Engineer under construction
    {15, 4}, // Engineer under construction
    {16, 5}, // Blastforge not under construction
    {17, 5}, // Blastforge not under construction
    {18, 6}, // Blastforge under construction
    {19, 6}, // Blastforge under construction
    {28, 7}, // Steelsplitter not under construction, can't block
    {29, 8}, // Steelsplitter not under construction, can block
    {30, 9}, // Steelsplitter under construction
    {31, 9}  // Steelsplitter under construction
}; */
/* python to generate
l=[255]*3255
for t in range(2,13):
    for c in range(3):
        for b in range(2):
            for h in range(1,6):
                for charge in range(3):
                    if t == 2:
                        if c==0 and b==0:
                            o=0
                        elif c==0 and b==1:
                            o=1
                        else:
                            o=2
                    if t==3:
                        if c==0:
                            o=3
                        else:
                            o=4
                    if t==4:
                        if c==0:
                            o=5
                        else:
                            o=6
                    if t==5:
                        if c==0:
                            o=7
                        else:
                            o=8
                    if t==6:
                        if c==1:
                            o=9
                        elif c==0 and h==3:
                            o=10
                        elif c==0 and h==2:
                            o=11
                        else:
                            o=12
                    if t==7:
                        if c==0 and b==0:
                            o=13
                        elif c==0 and b==1:
                            o=14
                        else:
                            o=15
                    if t==8:
                        o=16
                    if t==9:
                        if b==1 and charge==2:
                            o=16
                        elif b==1 and charge==1:
                            o=17
                        elif b==1 and charge==0:
                            o=18
                        elif b==0 and charge==2:
                            o=19
                        elif b==0 and charge==1:
                            o=20
                        else:
                            o=21
                    if t==10:
                        if c==2:
                            o=22
                        elif c==1:
                            o=23
                        else:
                            o=24
                    if t==11:
                        if h==2:
                            o=25
                        else:
                            o=26
                    if t==12:
                        if c==1:
                            o=27
                        elif c==0 and h==5:
                            o=28
                        elif c==0 and h==4:
                            o=29
                        elif c==0 and h==3:
                            o=30
                        elif c==0 and h==2:
                            o=31
                        else:
                            o=32
                    # print('{'+str((t<<8)|(c<<6)|(b<<5)|(h<<2)|(charge))+', '+str(o)+'}')
                    l.append(o)
print(l)
  */
int stateOffset4 [32] = {255, 255, 255, 255, 255, 255, 255, 255, 0, 1, 2, 2, 4, 4, 5, 5, 6, 6, 7, 7, 255, 255, 255, 255, 255, 255, 255, 255, 8, 9, 10, 10};
int stateOffset11 [3255] = {255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 1, 1, 1, 255, 1, 1, 1, 255, 1, 1, 1, 255, 1, 1, 1, 255, 1, 1, 1, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 2, 2, 2, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 3, 3, 3, 255, 3, 3, 3, 255, 3, 3, 3, 255, 3, 3, 3, 255, 3, 3, 3, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 3, 3, 3, 255, 3, 3, 3, 255, 3, 3, 3, 255, 3, 3, 3, 255, 3, 3, 3, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 4, 4, 4, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 5, 5, 5, 255, 5, 5, 5, 255, 5, 5, 5, 255, 5, 5, 5, 255, 5, 5, 5, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 5, 5, 5, 255, 5, 5, 5, 255, 5, 5, 5, 255, 5, 5, 5, 255, 5, 5, 5, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 6, 6, 6, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 7, 7, 7, 255, 7, 7, 7, 255, 7, 7, 7, 255, 7, 7, 7, 255, 7, 7, 7, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 7, 7, 7, 255, 7, 7, 7, 255, 7, 7, 7, 255, 7, 7, 7, 255, 7, 7, 7, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 8, 8, 8, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 12, 12, 12, 255, 11, 11, 11, 255, 10, 10, 10, 255, 12, 12, 12, 255, 12, 12, 12, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 12, 12, 12, 255, 11, 11, 11, 255, 10, 10, 10, 255, 12, 12, 12, 255, 12, 12, 12, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 9, 9, 9, 255, 9, 9, 9, 255, 9, 9, 9, 255, 9, 9, 9, 255, 9, 9, 9, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 9, 9, 9, 255, 9, 9, 9, 255, 9, 9, 9, 255, 9, 9, 9, 255, 9, 9, 9, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 12, 12, 12, 255, 12, 12, 12, 255, 12, 12, 12, 255, 12, 12, 12, 255, 12, 12, 12, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 12, 12, 12, 255, 12, 12, 12, 255, 12, 12, 12, 255, 12, 12, 12, 255, 12, 12, 12, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 13, 13, 13, 255, 13, 13, 13, 255, 13, 13, 13, 255, 13, 13, 13, 255, 13, 13, 13, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 14, 14, 14, 255, 14, 14, 14, 255, 14, 14, 14, 255, 14, 14, 14, 255, 14, 14, 14, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 15, 15, 15, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 16, 16, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 21, 20, 19, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 18, 17, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 24, 24, 24, 255, 24, 24, 24, 255, 24, 24, 24, 255, 24, 24, 24, 255, 24, 24, 24, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 24, 24, 24, 255, 24, 24, 24, 255, 24, 24, 24, 255, 24, 24, 24, 255, 24, 24, 24, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 23, 23, 23, 255, 23, 23, 23, 255, 23, 23, 23, 255, 23, 23, 23, 255, 23, 23, 23, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 23, 23, 23, 255, 23, 23, 23, 255, 23, 23, 23, 255, 23, 23, 23, 255, 23, 23, 23, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 22, 22, 22, 255, 22, 22, 22, 255, 22, 22, 22, 255, 22, 22, 22, 255, 22, 22, 22, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 22, 22, 22, 255, 22, 22, 22, 255, 22, 22, 22, 255, 22, 22, 22, 255, 22, 22, 22, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 26, 26, 26, 255, 25, 25, 25, 255, 26, 26, 26, 255, 26, 26, 26, 255, 26, 26, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 26, 26, 26, 255, 25, 25, 25, 255, 26, 26, 26, 255, 26, 26, 26, 255, 26, 26, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 26, 26, 26, 255, 25, 25, 25, 255, 26, 26, 26, 255, 26, 26, 26, 255, 26, 26, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 26, 26, 26, 255, 25, 25, 25, 255, 26, 26, 26, 255, 26, 26, 26, 255, 26, 26, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 26, 26, 26, 255, 25, 25, 25, 255, 26, 26, 26, 255, 26, 26, 26, 255, 26, 26, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 26, 26, 26, 255, 25, 25, 25, 255, 26, 26, 26, 255, 26, 26, 26, 255, 26, 26, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 32, 32, 32, 255, 31, 31, 31, 255, 30, 30, 30, 255, 29, 29, 29, 255, 28, 28, 28, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 32, 32, 32, 255, 31, 31, 31, 255, 30, 30, 30, 255, 29, 29, 29, 255, 28, 28, 28, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 27, 27, 27, 255, 27, 27, 27, 255, 27, 27, 27, 255, 27, 27, 27, 255, 27, 27, 27, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 27, 27, 27, 255, 27, 27, 27, 255, 27, 27, 27, 255, 27, 27, 27, 255, 27, 27, 27, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 32, 32, 32, 255, 32, 32, 32, 255, 32, 32, 32, 255, 32, 32, 32, 255, 32, 32, 32, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 32, 32, 32, 255, 32, 32, 32, 255, 32, 32, 32, 255, 32, 32, 32, 255, 32, 32, 32};

enum Abstract {
  BuyEngineer = 0,
  BuyDrone = 1,
  BuySteelsplitter = 2,
  BuyBlastforge = 3,
  UseAbilityDrone = 4,
  UseAbilitySteelsplitter = 5,
  AssignBlockerEngineer = 6,
  AssignBlockerDrone = 7,
  AssignBlockerSteelsplitter = 8,
  AssignBreachEngineer = 9,
  AssignBreachDrone = 10,
  AssignBreachSteelsplitter = 11,
  AssignBreachBlastforge = 12,
  EndPhase = 13,
  BuyAnimus = 14,
  BuyConduit = 15,
  BuyWall = 16,
  BuyRhino = 17,
  BuyTarsier = 18,
  BuyForceField = 19,
  BuyGaussCannon = 20,
  UseAbilityRhino = 21,
  AssignBlockerWall = 22,
  AssignBlockerRhino = 23,
  AssignBlockerForceField = 24,
  AssignBreachAnimus = 25,
  AssignBreachConduit = 26,
  AssignBreachWall = 27,
  AssignBreachRhino = 28,
  AssignBreachTarsier = 29,
  AssignBreachForceField = 30,
  AssignBreachGaussCannon = 31,
};
}; // namespace Action

std::map<Prismata::ActionID, std::map<int, int>> fromActionDispatch = {
    {Prismata::ActionTypes::END_PHASE,
     {
         {0, Action::Abstract::EndPhase},
         {2, Action::Abstract::EndPhase},
         {3, Action::Abstract::EndPhase},
         {4, Action::Abstract::EndPhase},
         {5, Action::Abstract::EndPhase},
         {6, Action::Abstract::EndPhase},
         {7, Action::Abstract::EndPhase},
         {8, Action::Abstract::EndPhase},
         {9, Action::Abstract::EndPhase},
         {10, Action::Abstract::EndPhase},
         {11, Action::Abstract::EndPhase},        
         {12, Action::Abstract::EndPhase}
     }},
    {Prismata::ActionTypes::USE_ABILITY,
     {
         {2, Action::Abstract::UseAbilityDrone},
         {7, Action::Abstract::UseAbilitySteelsplitter},
         {9, Action::Abstract::UseAbilityRhino}
     }},
    {Prismata::ActionTypes::ASSIGN_BREACH,
     {{2, Action::Abstract::AssignBreachDrone},
      {3, Action::Abstract::AssignBreachEngineer},
      {4, Action::Abstract::AssignBreachBlastforge},
      {5, Action::Abstract::AssignBreachAnimus},
      {6, Action::Abstract::AssignBreachConduit},
      {7, Action::Abstract::AssignBreachSteelsplitter},
      {8, Action::Abstract::AssignBreachWall},
      {9, Action::Abstract::AssignBreachRhino},
      {10, Action::Abstract::AssignBreachTarsier},
      {11, Action::Abstract::AssignBreachForceField},
      {12, Action::Abstract::AssignBreachGaussCannon}
     }},
    {Prismata::ActionTypes::ASSIGN_BLOCKER,
     {
         {2, Action::Abstract::AssignBlockerDrone},
         {3, Action::Abstract::AssignBlockerEngineer},
         {7, Action::Abstract::AssignBlockerSteelsplitter},
         {8, Action::Abstract::AssignBlockerWall},
         {9, Action::Abstract::AssignBlockerRhino},
         {11, Action::Abstract::AssignBlockerForceField}
     }},
    {Prismata::ActionTypes::BUY,
     {
      {2, Action::Abstract::BuyDrone},
      {3, Action::Abstract::BuyEngineer},
      {4, Action::Abstract::BuyBlastforge},
      {5, Action::Abstract::BuyAnimus},
      {6, Action::Abstract::BuyConduit},
      {7, Action::Abstract::BuySteelsplitter},
      {8, Action::Abstract::BuyWall},
      {9, Action::Abstract::BuyRhino},
      {10, Action::Abstract::BuyTarsier},
      {11, Action::Abstract::BuyForceField},
      {12, Action::Abstract::BuyGaussCannon}}}};
