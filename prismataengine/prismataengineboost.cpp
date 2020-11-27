#include "prismataengineboost.h"

namespace Player {
void getMove(std::shared_ptr<Prismata::Player> p, const Prismata::GameState &g,
             Prismata::Move &m) {
  (*p).getMove(g, m);
}

}; // namespace Player

namespace GameState {
Prismata::GameState *fromJson(const std::string &json_str) {
  rapidjson::Document document;
  bool parsingFailed = document.Parse(json_str.c_str()).HasParseError();
  return new Prismata::GameState(document);
}
bool doActionInt(Prismata::GameState &g, uintptr_t a) {
  return g.doAction(*(reinterpret_cast<Prismata::Action*>(a)));
}
Prismata::CardVector &getPlayerCards(const Prismata::GameState &g,
                                     const Prismata::PlayerID player,
                                     Prismata::CardVector &c) {
  size_t n = g.numCards(player);
  c.reserve(n);
  c.resize(n);
  int i = 0;
  for (const auto &cardID : g.getCardIDs(player)) {
    c[i++] = g.getCardByID(cardID);
  }
  return c;
}
void generateLegalActions(const Prismata::GameState &g,
                          std::vector<Prismata::Action> &av,
                          boost::python::numpy::ndarray acv,
                          const boost::python::numpy::ndarray aa,
                          Prismata::Action &endPhase) {
  bool *acvp = reinterpret_cast<bool *>(acv.get_data()); //Extract vector of Booleans which are the abstract legal actions
  uintptr_t *aap = reinterpret_cast<uintptr_t *>(aa.get_data()); //Extract unsigned integer pointer width type for storing *Prismata::Action
  av.clear();
  g.generateLegalActions(av); //This is the output of the Prismata Gamestate engine code
  for (size_t i = 0; i < av.size(); i++) {
    int o = fromActionDispatch[av[i].getType()][Action::getCardType(av[i], g)]; //fromActionDispatch maps (card/buy type, action) to an offset o in O(1)
    acvp[o] = true;
    aap[o] = reinterpret_cast<uintptr_t>(&av[i]);//Stores pointer to a valid action that satisfies abstract action condition
  }
  if (g.isLegal(endPhase)) { //endPhase needs to be special cased because of frailties in the Prismata Engine code
    acvp[Action::Abstract::EndPhase] = true;
    aap[Action::Abstract::EndPhase] = reinterpret_cast<uintptr_t>(&endPhase);
  }
}
void cardCounting4(const Prismata::GameState &g, const Prismata::PlayerID player,
                  int offset, boost::python::numpy::ndarray &n) {
  uint16_t *state =
      reinterpret_cast<uint16_t *>(n.get_data() + sizeof(uint16_t) * offset);
  // maxDimension should be 9 for 4-card mode and 33 for 11-card mode
  for (int i = 0; i < 10; i++) {
      state[i] = 0;
  }
  for (const auto &cardID : g.getCardIDs(player)) {
    const Prismata::Card &c = g.getCardByID(cardID);
    // std::cout << Card::toJson(c) << " (" << Card::getBin(c) << ", " << Action::stateOffset[Card::getBin(c)] << ")" << std::endl;
    state[Action::stateOffset4[Card::getBin4(c)]] += 1;
  }
}
void cardCounting11(const Prismata::GameState &g, const Prismata::PlayerID player,
                  int offset, boost::python::numpy::ndarray &n) {
  uint16_t *state =
      reinterpret_cast<uint16_t *>(n.get_data() + sizeof(uint16_t) * offset);
  // maxDimension should be 9 for 4-card mode and 33 for 11-card mode
  for (int i = 0; i < 34; i++) {
      state[i] = 0;
  } //Clear everything
  for (const auto &cardID : g.getCardIDs(player)) { //Gets a vector of cardIDs for a player in a gamestate
    const Prismata::Card &c = g.getCardByID(cardID); //Convert to actual card object
    // std::cout << Card::toJson(c) << " (" << Card::getBin(c) << ", " << Action::stateOffset[Card::getBin(c)] << ")" << std::endl;
    state[Action::stateOffset11[Card::getBin11(c)]] += 1;
  }
}
void copyResources4(Prismata::GameState &g, const Prismata::PlayerID p,
                   int offset, boost::python::numpy::ndarray &n) {
//Converts integer/logical offset to a memory offset and then adds it to relative
  uint16_t *state =
      reinterpret_cast<uint16_t *>(n.get_data() + sizeof(uint16_t) * offset); 
  const Prismata::Resources &r = g.getResources(p);
  state[0] = r.amountOf(Prismata::Resources::Gold); //Starts at zero because of our pointer logic and avoids seperate additions
  state[1] = r.amountOf(Prismata::Resources::Energy);
  state[2] = r.amountOf(Prismata::Resources::Blue);
  state[3] = r.amountOf(Prismata::Resources::Attack);
}
void copyResources11(Prismata::GameState &g, const Prismata::PlayerID p,
                   int offset, boost::python::numpy::ndarray &n) {
  uint16_t *state =
      reinterpret_cast<uint16_t *>(n.get_data() + sizeof(uint16_t) * offset);
  const Prismata::Resources &r = g.getResources(p);
  state[0] = r.amountOf(Prismata::Resources::Gold);
  state[1] = r.amountOf(Prismata::Resources::Energy);
  state[2] = r.amountOf(Prismata::Resources::Blue);
  state[3] = r.amountOf(Prismata::Resources::Red);
  state[4] = r.amountOf(Prismata::Resources::Green);
  state[5] = r.amountOf(Prismata::Resources::Attack);
}
}; // namespace GameState

namespace Card { 
std::string toJson(const Prismata::Card &c) { return c.toJSONString(true); }
static inline unsigned int getBin4(const Prismata::Card &c) { //Construct bin index in our lookup table from the card
  return (c.getType().getID() << 2) | (c.isUnderConstruction() << 1) |
         (c.canBlock());
}//Shift ID bits 2 to the left, bitwise OR, underConstrion 1 to the left, bitwise OR, canBlock
static inline unsigned int getBin11(const Prismata::Card &c) {
  return (c.getType().getID() << 8) | (c.getConstructionTime() << 6) |
         (c.canBlock() << 5) | (c.currentHealth() << 2) | (c.getCurrentCharges());
}
/* static inline unsigned int getOffset(const Prismata::Card &c, int offset) {
  return Action::stateOffset[Card::getBin(c)] + offset;
} */
size_t getBuyableTypeId(const Prismata::CardBuyable &c) {
  return c.getType().getID();
}

size_t getTypeId(const Prismata::Card &c) { return c.getType().getID(); }
std::string buyableStringify(const Prismata::CardBuyable &c) {
  return c.getType().getName();
}
std::string stringify(const Prismata::Card &c) { return c.getType().getName(); }
} // namespace Card

namespace Action {
std::string stringifyp(Prismata::Action *a) {
  std::stringstream ss;
  ss << "(Player = " << (int)a->getPlayer()
     << ", Type = " << Action::typeStringify((int)a->getType())
     << ", ID = " << (int)a->getID() << ", Target = " << (int)a->getTargetID()
     << ")";
  return ss.str();
}
std::string stringify(const Prismata::Action &a) {
  std::stringstream ss;
  ss << "(Player = " << (int)a.getPlayer()
     << ", Type = " << Action::typeStringify((int)a.getType())
     << ", ID = " << (int)a.getID() << ", Target = " << (int)a.getTargetID()
     << ")";
  return ss.str();
}
static inline const char *typeStringify(int v) {
  switch (v) {
  case Prismata::ActionTypes::USE_ABILITY:
    return "USE_ABILITY";
  case Prismata::ActionTypes::BUY:
    return "BUY";
  case Prismata::ActionTypes::END_PHASE:
    return "END_PHASE";
  case Prismata::ActionTypes::ASSIGN_BLOCKER:
    return "ASSIGN_BLOCKER";
  case Prismata::ActionTypes::ASSIGN_BREACH:
    return "ASSIGN_BREACH";
  case Prismata::ActionTypes::ASSIGN_FRONTLINE:
    return "ASSIGN_FRONTLINE";
  case Prismata::ActionTypes::SNIPE:
    return "SNIPE";
  case Prismata::ActionTypes::CHILL:
    return "CHILL";
  case Prismata::ActionTypes::WIPEOUT:
    return "WIPEOUT";
  case Prismata::ActionTypes::UNDO_USE_ABILITY:
    return "UNDO_USE_ABILITY";
  case Prismata::ActionTypes::UNDO_CHILL:
    return "UNDO_CHILL";
  case Prismata::ActionTypes::UNDO_BREACH:
    return "UNDO_BREACH";
  case Prismata::ActionTypes::SELL:
    return "SELL";
  case Prismata::ActionTypes::NUM_TYPES:
    return "NUM_TYPES";
  default:
    return "NONE";
  }
}

boost::variant<Prismata::Card, Prismata::CardBuyable>
getCard(const Prismata::Action &a, const Prismata::GameState &g) {
  return a.getType() == Prismata::ActionTypes::BUY
             ? boost::variant<Prismata::Card, Prismata::CardBuyable>(
                   g.getCardBuyableByID(a.getID()))
             : boost::variant<Prismata::Card, Prismata::CardBuyable>(
                   g.getCardByID(a.getID()));
}

size_t getCardType(const Prismata::Action &a, const Prismata::GameState &g) {
  return a.getType() == Prismata::ActionTypes::BUY
             ? g.getCardBuyableByID(a.getID()).getType().getID() //Buyable types are different than card types for labelling Prismata::Actions
             : g.getCardByID(a.getID()).getType().getID();
}

std::string toJson(const Prismata::Action &a) {
  std::stringstream ss;
  ss << "{\"player\": " << (int)a.getPlayer() << ", \"type\": \""
     << Action::typeStringify((int)a.getType())
     << "\", \"id\": " << (int)a.getID()
     << ", \"target\": " << (int)a.getTargetID() << "}";
  return ss.str();
}

std::string vectorStringify(const std::vector<Prismata::Action> &v) {
  std::stringstream ss;
  ss << "[";
  for (size_t i = 0; i < v.size(); i++) {
    if (i != 0)
      ss << ", ";
    ss << Action::stringify(v[i]);
  }
  ss << "]";
  return ss.str();
}

std::string vectorToJson(const std::vector<Prismata::Action> &v) {
  std::stringstream ss;
  ss << "[";
  for (size_t i = 0; i < v.size(); i++) {
    if (i != 0)
      ss << ", ";
    ss << Action::toJson(v[i]);
  }
  ss << "]";

  return ss.str();
}

} // namespace Action

void playerFactoryInit(const std::string & s) {
    Prismata::AIParameters::Instance().parseJSONString(s);
}

const std::shared_ptr<Prismata::Player> playerFactory(const Prismata::PlayerID p, const std::string & playerName) {
    return Prismata::AIParameters::Instance().getPlayer(p, playerName);
}

BOOST_PYTHON_MODULE(_prismataengine) {
  boost::python::numpy::initialize();
  boost::python::def("init", &Prismata::InitFromCardLibrary);
  boost::python::def("jsonStrToGameState", &GameState::fromJson,
                     boost::python::return_value_policy<
                         boost::python::reference_existing_object>());
                         
  boost::python::def("getAIPlayer", &playerFactory,
                     boost::python::return_value_policy<
                         boost::python::return_by_value>());
  boost::python::def("initAI", &playerFactoryInit);

  boost::python::def("countCards4", &GameState::cardCounting4);
  boost::python::def("countCards11", &GameState::cardCounting11);
  boost::python::def("countResources4", &GameState::copyResources4);
  boost::python::def("countResources11", &GameState::copyResources11);
  boost::python::def("getMove", &Player::getMove, boost::python::args("p", "g", "m"));
  
  boost::python::enum_<Prismata::ActionID>("ActionType")
      .value("BUY", Prismata::ActionTypes::BUY)
      .value("END_PHASE", Prismata::ActionTypes::END_PHASE)
      .value("ASSIGN_BLOCKER", Prismata::ActionTypes::ASSIGN_BLOCKER)
      .value("ASSIGN_BREACH", Prismata::ActionTypes::ASSIGN_BREACH)
      .value("ASSIGN_FRONTLINE", Prismata::ActionTypes::ASSIGN_FRONTLINE)
      .value("SNIPE", Prismata::ActionTypes::SNIPE)
      .value("CHILL", Prismata::ActionTypes::CHILL)
      .value("WIPEOUT", Prismata::ActionTypes::WIPEOUT)
      .value("UNDO_USE_ABILITY", Prismata::ActionTypes::UNDO_USE_ABILITY)
      .value("UNDO_CHILL", Prismata::ActionTypes::UNDO_CHILL)
      .value("UNDO_BREACH", Prismata::ActionTypes::UNDO_BREACH)
      .value("SELL", Prismata::ActionTypes::SELL)
      .value("NUM_TYPES", Prismata::ActionTypes::NUM_TYPES)
      .value("NONE", Prismata::ActionTypes::NONE);

  boost::python::enum_<int>("Phases")
      .value("Action", Prismata::Phases::Action)
      .value("Breach", Prismata::Phases::Breach)
      .value("Confirm", Prismata::Phases::Confirm)
      .value("Defense", Prismata::Phases::Defense)
      .value("Swoosh", Prismata::Phases::Swoosh);

  boost::python::enum_<Prismata::ResourceType>("ResourceTypes")
      .value("Gold", 0)    // Prismata::Resources::Gold)
      .value("Energy", 1)  // Prismata::Resources::Energy)
      .value("Blue", 2)    // Prismata::Resources::Blue)
      .value("Red", 3)    // Prismata::Resources::Red)
      .value("Green", 4)    // Prismata::Resources::Green)
      .value("Attack", 5); // Prismata::Resources::Attack)

  boost::python::enum_<int>("AliveStatus")
      .value("Alive", Prismata::AliveStatus::Alive)
      .value("Dead", Prismata::AliveStatus::Dead)
      .value("KilledThisTurn", Prismata::AliveStatus::KilledThisTurn);

  boost::python::enum_<Action::Abstract>("AbstractAction")
      .value("BuyEngineer", Action::Abstract::BuyEngineer)
      .value("BuyDrone", Action::Abstract::BuyDrone)
      .value("BuySteelsplitter", Action::Abstract::BuySteelsplitter)
      .value("BuyBlastforge", Action::Abstract::BuyBlastforge)  
      .value("BuyAnimus", Action::Abstract::BuyAnimus)
      .value("BuyConduit", Action::Abstract::BuyConduit)
      .value("BuyWall", Action::Abstract::BuyWall)
      .value("BuyRhino", Action::Abstract::BuyRhino)
      .value("BuyTarsier", Action::Abstract::BuyTarsier)
      .value("BuyForceField", Action::Abstract::BuyForceField)
      .value("BuyGaussCannon", Action::Abstract::BuyGaussCannon)
      .value("UseAbilityDrone", Action::Abstract::UseAbilityDrone)
      .value("UseAbilityRhino", Action::Abstract::UseAbilityRhino)
      .value("UseAbilitySteelsplitter",
             Action::Abstract::UseAbilitySteelsplitter)
      .value("AssignBlockerEngineer", Action::Abstract::AssignBlockerEngineer)
      .value("AssignBlockerDrone", Action::Abstract::AssignBlockerDrone)
      .value("AssignBlockerWall", Action::Abstract::AssignBlockerWall)
      .value("AssignBlockerRhino", Action::Abstract::AssignBlockerRhino)
      .value("AssignBlockerForceField", Action::Abstract::AssignBlockerForceField)
      .value("AssignBlockerSteelsplitter",
             Action::Abstract::AssignBlockerSteelsplitter)
      .value("AssignBreachEngineer", Action::Abstract::AssignBreachEngineer)
      .value("AssignBreachDrone", Action::Abstract::AssignBreachDrone)
      .value("AssignBreachSteelsplitter",
             Action::Abstract::AssignBreachSteelsplitter)
      .value("AssignBreachBlastforge", Action::Abstract::AssignBreachBlastforge)
      .value("AssignBreachAnimus", Action::Abstract::AssignBreachAnimus)
      .value("AssignBreachConduit", Action::Abstract::AssignBreachConduit)
      .value("AssignBreachWall", Action::Abstract::AssignBreachWall)
      .value("AssignBreachRhino", Action::Abstract::AssignBreachRhino)
      .value("AssignBreachTarsier", Action::Abstract::AssignBreachTarsier)
      .value("AssignBreachForceField", Action::Abstract::AssignBreachForceField)
      .value("AssignBreachGaussCannon", Action::Abstract::AssignBreachGaussCannon)
      .value("EndPhase", Action::Abstract::EndPhase);

  boost::python::enum_<Prismata::PlayerID>("Players")
      .value("One", Prismata::Players::Player_One)
      .value("Two", Prismata::Players::Player_Two);

  boost::python::class_<Prismata::CardBuyable>("CardBuyable")
      .add_property("name", &Card::buyableStringify)
      .add_property("type", &Card::getBuyableTypeId)
      .def("__eq__", &Prismata::Card::operator==)
      .def("__lt__", &Prismata::Card::operator<)
      .def("__str__", &Card::buyableStringify);

  boost::python::class_<Prismata::Card>("Card")
      .add_property("bin4", &Card::getBin4)
      .add_property("bin11", &Card::getBin11)
      .add_property("canBlock", &Prismata::Card::canBlock)
      .add_property("charge", &Prismata::Card::getCurrentCharges)
      .add_property("constructionTime", &Prismata::Card::getConstructionTime)
      .add_property("delay", &Prismata::Card::getCurrentDelay)
      .add_property("disruptDamage", &Prismata::Card::currentChill)
      .add_property("health", &Prismata::Card::currentHealth)
      .add_property("name", &Card::stringify)
      .add_property("owner", &Prismata::Card::getPlayer)
      .add_property("status", &Prismata::Card::getStatus)
      .add_property("type", &Card::getTypeId)
      .add_property("underConstruction", &Prismata::Card::isUnderConstruction)
      .def(boost::python::init<Prismata::CardType, Prismata::PlayerID, int,
                               Prismata::TurnType, Prismata::TurnType>())
      .def(boost::python::init<std::string>())
      .def("__eq__", &Prismata::Card::operator==)
      .def("__lt__", &Prismata::Card::operator<)
      // .def("offset", &Card::getOffset)
      .def("__str__", &Card::toJson);

  boost::python::class_<Prismata::Action>("PrismataAction")
      .add_property("cardid", &Prismata::Action::getID)
      .add_property("player", &Prismata::Action::getPlayer)
      .add_property("target", &Prismata::Action::getTargetID)
      .add_property("type", &Prismata::Action::getType)
      .def(boost::python::init<Prismata::PlayerID, Prismata::ActionID,
                               Prismata::CardID>())
      .def(boost::python::init<Prismata::PlayerID, Prismata::ActionID,
                               Prismata::CardID, Prismata::CardID>())
      .def("card", &Action::getCard,
           boost::python::return_value_policy<boost::python::return_by_value>())
      .def("cardtype", &Action::getCardType)
      .def("describe", &Prismata::Action::toStringEnglish)
      .def("__eq__", &Prismata::Action::operator==)
      .def("json", &Action::toJson)
      .def("__ne__", &Prismata::Action::operator!=)
      .def("setSource", &Prismata::Action::setID)
      .def("shift", &Prismata::Action::getShift)
      .def("__str__", &Action::stringify);

  boost::python::class_<Prismata::Move>("Move")
      .def("append", &Prismata::Move::addAction)
      .def("clear", &Prismata::Move::clear)
      .def("__str__", &Prismata::Move::toString);

  boost::python::class_<Prismata::Resources>("Resources")
      .def("amountOf", &Prismata::Resources::amountOf,
           boost::python::return_value_policy<boost::python::return_by_value>())
      .def(boost::python::init<std::string>())
      .def("__eq__", &Prismata::Resources::operator==)
      .def("has", &Prismata::Resources::has)
      .def("__iadd__",
           static_cast<void (Prismata::Resources::*)(
               const Prismata::Resources &)>(&Prismata::Resources::add))
      .def("__ne__", &Prismata::Resources::operator!=)
      .def("__str__", &Prismata::Resources::getString);

  boost::python::class_<Prismata::CardVector>("CardVector")
      .def(boost::python::vector_indexing_suite<Prismata::CardVector>())
      .def("clear", &Prismata::CardVector::clear);

  boost::python::class_<std::vector<Prismata::Action>>("PrismataActions")
      .def(
          boost::python::vector_indexing_suite<std::vector<Prismata::Action>>())
      .def("clear", &std::vector<Prismata::Action>::clear)
      .def("json", &Action::vectorToJson)
      .def("__str__", &Action::vectorStringify);

  boost::python::class_<Prismata::GameState>("PrismataGameState")
      .add_property("activePhase", &Prismata::GameState::getActivePhase)
      .add_property("activePlayer", &Prismata::GameState::getActivePlayer)
      .add_property("inactivePlayer", &Prismata::GameState::getInactivePlayer)
      .add_property("winner", &Prismata::GameState::winner)
      .def("addCard",
           static_cast<void (Prismata::GameState::*)(const Prismata::Card &)>(
               &Prismata::GameState::addCard))
      .def("beginTurn", &Prismata::GameState::beginTurn)
      .def("doAction", &GameState::doActionInt)
      // .def("doAction", &Prismata::GameState::doAction)
      .def("doMove", &Prismata::GameState::doMove)
      .def("generateLegalActions", &Prismata::GameState::generateLegalActions)
      .def("generateLegalActionsVector", &GameState::generateLegalActions)
      .def("getCardBuyableById", &Prismata::GameState::getCardBuyableByID,
           boost::python::return_value_policy<
               boost::python::reference_existing_object>())
      .def("getCardById", &Prismata::GameState::getCardByID,
           boost::python::return_value_policy<
               boost::python::reference_existing_object>())
      .def("getLiveCards", &GameState::getPlayerCards,
           boost::python::return_value_policy<
               boost::python::reference_existing_object>())
      .def("getResources", &Prismata::GameState::getResources,
           boost::python::return_value_policy<
               boost::python::reference_existing_object>())
      .def("isGameOver", &Prismata::GameState::isGameOver)
      .def("isLegal", &Prismata::GameState::isLegal)
      .def("json", &Prismata::GameState::toJSONString)
      .def("numCardsBuyable", &Prismata::GameState::numCardsBuyable)
      .def("numCardsForPlayer", &Prismata::GameState::numCards)
      .def("setStartingState", &Prismata::GameState::setStartingState)
      .def("__str__", &Prismata::GameState::getStateString)
      .def("turnNumber", &Prismata::GameState::getTurnNumber);
  boost::python::class_<Prismata::Player, boost::noncopyable>("PrismataPlayer", boost::python::no_init);
  boost::python::register_ptr_to_python< std::shared_ptr<Prismata::Player> >();
  
}