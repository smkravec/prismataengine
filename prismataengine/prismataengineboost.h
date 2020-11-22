#pragma once

#include "Action.h"
#include "Card.h"
#include "Common.h"
#include "Constants.h"
#include "GameState.h"
#include "Move.h"
#include "Player_Random.h"
#include "Prismata.h"
#include "Resources.h"
#include "rapidjson.h"
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/numpy/ndarray.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/variant.hpp>

namespace Player {
void getMove(Prismata::Player &p, const Prismata::GameState &g,
             Prismata::Move &m);
};
namespace GameState {
bool doActionInt(Prismata::GameState &g, uintptr_t a);
Prismata::CardVector &getPlayerCards(const Prismata::GameState &g,
                                     const Prismata::PlayerID player,
                                     Prismata::CardVector &c);
Prismata::GameState *fromJson(const std::string &json_str);
void cardCounting(const Prismata::GameState &g, const Prismata::PlayerID player,
                  int offset, boost::python::numpy::ndarray &n);
void copyResources(Prismata::GameState &g, const Prismata::PlayerID p,
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
static inline unsigned int getBin(const Prismata::Card &c);
static inline unsigned int getOffset(const Prismata::Card &c, int offset);
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

std::map<unsigned int, unsigned int> stateOffset = {
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
    {31, 9}, // Steelsplitter under construction
};
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
  EndPhase = 13
};

}; // namespace Action

std::map<Prismata::ActionID, std::map<int, int>> fromActionDispatch = {
    {Prismata::ActionTypes::END_PHASE,
     {
         {0, Action::Abstract::EndPhase},
         {2, Action::Abstract::EndPhase},
         {3, Action::Abstract::EndPhase},
         {4, Action::Abstract::EndPhase},
         {7, Action::Abstract::EndPhase},
     }},
    {Prismata::ActionTypes::USE_ABILITY,
     {
         {2, Action::Abstract::UseAbilityDrone},
         {7, Action::Abstract::UseAbilitySteelsplitter},
     }},
    {Prismata::ActionTypes::ASSIGN_BREACH,
     {{3, Action::Abstract::AssignBreachEngineer},
      {2, Action::Abstract::AssignBreachDrone},
      {7, Action::Abstract::AssignBreachSteelsplitter},
      {4, Action::Abstract::AssignBreachBlastforge}}},
    {Prismata::ActionTypes::ASSIGN_BLOCKER,
     {
         {3, Action::Abstract::AssignBlockerEngineer},
         {2, Action::Abstract::AssignBlockerDrone},
         {7, Action::Abstract::AssignBlockerSteelsplitter},
     }},
    {Prismata::ActionTypes::BUY,
     {{3, Action::Abstract::BuyEngineer},
      {2, Action::Abstract::BuyDrone},
      {7, Action::Abstract::BuySteelsplitter},
      {4, Action::Abstract::BuyBlastforge}}}};
