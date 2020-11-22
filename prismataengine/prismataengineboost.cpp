#include <boost/python.hpp>
#include <boost/variant.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/numpy/ndarray.hpp>
#include "rapidjson.h"
#include "Action.h"
#include "Card.h"
#include "Common.h"
#include "Constants.h"
#include "GameState.h"
#include "Move.h"
#include "Prismata.h"
#include "Resources.h"

Prismata::GameState state;

inline const char* actiontype_tostring(int v) {
    switch (v)
    {
      case Prismata::ActionTypes::USE_ABILITY: return "USE_ABILITY";
      case Prismata::ActionTypes::BUY: return "BUY";
      case Prismata::ActionTypes::END_PHASE: return "END_PHASE";
      case Prismata::ActionTypes::ASSIGN_BLOCKER: return "ASSIGN_BLOCKER";
      case Prismata::ActionTypes::ASSIGN_BREACH: return "ASSIGN_BREACH";
		case 5: return "ASSIGN_FRONTLINE";
		case 6: return "SNIPE";
		case 7: return "CHILL";
		case 8: return "WIPEOUT";
		case 9: return "UNDO_USE_ABILITY";
		case 10: return "UNDO_CHILL";
		case 11: return "UNDO_BREACH";
		case 12: return "SELL";
		case 13: return "NUM_TYPES";
		default: return "NONE";
    }
}

Prismata::GameState * json_to_gamestate(const std::string & json_str)
{
  rapidjson::Document document;
  bool parsingFailed = document.Parse(json_str.c_str()).HasParseError();
  return new Prismata::GameState(document);
}

std::string card_json(const Prismata::Card & c)
{
  return c.toJSONString(true);
}

std::string action_stringify(const Prismata::Action & a)
{
	std::stringstream ss;
    ss << "(Player = " << (int)a.getPlayer() << ", Type = " << actiontype_tostring((int)a.getType()) << ", ID = " << (int)a.getID() << ", Target = " << (int)a.getTargetID() <<")";
	return ss.str();
}

boost::variant<Prismata::Card, Prismata::CardBuyable> action_card(const Prismata::Action & a, const Prismata::GameState & g)
{
  return a.getType() == Prismata::ActionTypes::BUY ? boost::variant<Prismata::Card, Prismata::CardBuyable>(g.getCardBuyableByID(a.getID())) : boost::variant<Prismata::Card, Prismata::CardBuyable>(g.getCardByID(a.getID()));
}

size_t action_card_type(const Prismata::Action & a, const Prismata::GameState & g)
{
  return a.getType() == Prismata::ActionTypes::BUY ? g.getCardBuyableByID(a.getID()).getType().getID() : g.getCardByID(a.getID()).getType().getID();
}
std::string action_json(const Prismata::Action & a)
{
	std::stringstream ss;
    ss << "{\"player\": " << (int)a.getPlayer() << ", \"type\": \"" << actiontype_tostring((int)a.getType()) << "\", \"id\": " << (int)a.getID() << ", \"target\": " << (int)a.getTargetID() <<"}";
	return ss.str();
}

std::string actions_stringify(const std::vector<Prismata::Action>& v)
{
	std::stringstream ss;
	ss << "[";
	for (size_t i = 0; i < v.size(); i++) {
		if (i != 0) ss << ", ";
		ss << action_stringify(v[i]);
	}
	ss << "]";

	return ss.str();
}

std::string actions_json(const std::vector<Prismata::Action>& v)
{
	std::stringstream ss;
	ss << "[";
	for (size_t i = 0; i < v.size(); i++) {
		if (i != 0) ss << ", ";
		ss << action_json(v[i]);
	}
	ss << "]";

	return ss.str();
}

std::map<unsigned int, unsigned int> offset_type = {
  {8,  1},
  {9,  2},
  {10, 0},
  {11, 0},
  {12, 3},
  {13, 3},
  {14, 4},
  {15, 4},
  {16, 5},
  {17, 5},
  {18, 6},
  {19, 6},
  {28, 7},
  {29, 8},
  {30, 9},
  {31, 9},
};
unsigned int card_bin(const Prismata::Card & c)
{
  return (c.getType().getID() << 2) | (c.isUnderConstruction() << 1) | (c.canBlock());
}
int card_offset(const Prismata::Card & c, int offset)
{
  return offset_type[((c.getType().getID() << 2) | (c.isUnderConstruction() << 1) | (c.canBlock())) + offset];
}
void copy_resources(Prismata::GameState & g, const Prismata::PlayerID p, int offset, boost::python::numpy::ndarray & n)
{
  uint16_t *state = reinterpret_cast<uint16_t *>(n.get_data() + sizeof(uint16_t) * offset);
  const Prismata::Resources & r = g.getResources(p);
  state[0] = r.amountOf(Prismata::Resources::Gold);
  state[1] = r.amountOf(Prismata::Resources::Energy);
  state[2] = r.amountOf(Prismata::Resources::Blue);
  state[3] = r.amountOf(Prismata::Resources::Attack);
}
size_t cardb_type_id(const Prismata::CardBuyable & c)
{
  return c.getType().getID();
}

size_t card_type_id(const Prismata::Card & c)
{
  return c.getType().getID();
}
std::string cardb_name_str(const Prismata::CardBuyable & c)
{
  return c.getType().getName();
}
std::string card_name_str(const Prismata::Card & c)
{
  return c.getType().getName();
}
void card_counting(const Prismata::GameState & g, const Prismata::PlayerID player, int offset, boost::python::numpy::ndarray & n)
{
  uint16_t *state = reinterpret_cast<uint16_t *>(n.get_data() + sizeof(uint16_t) * offset);
  state[0] = 0;
  state[1] = 0;
  state[2] = 0;
  state[3] = 0;
  state[4] = 0;
  state[5] = 0;
  state[6] = 0;
  state[7] = 0;
  state[8] = 0;
  std::stringstream ss;
  for (const auto & cardID : g.getCardIDs(player))
  {
    const Prismata::Card & c = g.getCardByID(cardID);
    state[offset_type[((c.getType().getID() << 2) | (c.isUnderConstruction() << 1) | (c.canBlock()))]] += 1;
  }
}
Prismata::CardVector & get_cards_player(const Prismata::GameState & g, const Prismata::PlayerID player, Prismata::CardVector & c)
{
  size_t n = g.numCards(player);
  c.reserve(n);
  c.resize(n);
  int i = 0;
  for (const auto & cardID : g.getCardIDs(player))
  {
    c[i++] = g.getCardByID(cardID);
  }
  return c;
}

BOOST_PYTHON_MODULE(_prismataengine) {
  boost::python::numpy::initialize();
	boost::python::def("init", &Prismata::InitFromCardLibrary);
	boost::python::def("jsonStrToGameState", &json_to_gamestate, boost::python::return_value_policy<boost::python::reference_existing_object>());
  boost::python::def("countCards", &card_counting);
  boost::python::def("countResources", &copy_resources);
	boost::python::enum_<Prismata::ActionID>("ActionType")
		.value("USE_ABILITY", Prismata::ActionTypes::USE_ABILITY)
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
		.value("NONE", Prismata::ActionTypes::NONE)
		;
	boost::python::enum_<int>("Phases")
    .value("Action", Prismata::Phases::Action)
    .value("Breach", Prismata::Phases::Breach)
    .value("Confirm", Prismata::Phases::Confirm)
    .value("Defense", Prismata::Phases::Defense)
    .value("Swoosh", Prismata::Phases::Swoosh)
    ;
	boost::python::enum_<Prismata::ResourceType>("ResourceTypes")
		.value("Gold", 0) // Prismata::Resources::Gold)
		.value("Energy", 1) // Prismata::Resources::Energy)
		.value("Blue", 2) // Prismata::Resources::Blue)
		.value("Attack", 5) // Prismata::Resources::Attack)
		;
	boost::python::enum_<int>("AliveStatus")
		.value("Alive", Prismata::AliveStatus::Alive)
		.value("Dead", Prismata::AliveStatus::Dead)
		.value("KilledThisTurn", Prismata::AliveStatus::KilledThisTurn)
		;
	boost::python::enum_<Prismata::PlayerID>("Players")
		.value("Player_One", Prismata::Players::Player_One)
		.value("Player_Two", Prismata::Players::Player_Two)
		;
	boost::python::class_<Prismata::CardBuyable>("CardBuyable")
    .add_property("name", &cardb_name_str)
    .def("__str__", &cardb_name_str)
    .add_property("type", &cardb_type_id)
		.def("__eq__", &Prismata::Card::operator==)
		.def("__lt__", &Prismata::Card::operator<)
    ;
	boost::python::class_<Prismata::Card>("Card")
		.def(boost::python::init<std::string>())
		.def(boost::python::init<Prismata::CardType, Prismata::PlayerID, int, Prismata::TurnType, Prismata::TurnType>())
    .add_property("owner", &Prismata::Card::getPlayer)
    .add_property("name", &card_name_str)
    .add_property("type", &card_type_id)
    .add_property("bin", &card_bin)
    .def("offset", &card_offset)
    .add_property("health", &Prismata::Card::currentHealth)
    .add_property("disruptDamage", &Prismata::Card::currentChill)
    .add_property("status", &Prismata::Card::getStatus)
    .add_property("constructionTime", &Prismata::Card::getConstructionTime)
    .add_property("charge", &Prismata::Card::getCurrentCharges)
    .add_property("delay", &Prismata::Card::getCurrentDelay)
    .add_property("canBlock", &Prismata::Card::canBlock)
    .add_property("underConstruction", &Prismata::Card::isUnderConstruction)
		.def("__eq__", &Prismata::Card::operator==)
		.def("__lt__", &Prismata::Card::operator<)
		.def("__str__", &card_json)
		;
	boost::python::class_<Prismata::Action>("PrismataAction")
		.def(boost::python::init<Prismata::PlayerID, Prismata::ActionID, Prismata::CardID>())
		.def(boost::python::init<Prismata::PlayerID, Prismata::ActionID, Prismata::CardID, Prismata::CardID>())
		.def("describe", &Prismata::Action::toStringEnglish)
		.def("__eq__", &Prismata::Action::operator==)
		.def("__ne__", &Prismata::Action::operator!=)
		.def("setSource", &Prismata::Action::setID)
		.def("shift", &Prismata::Action::getShift)
    .add_property("cardid", &Prismata::Action::getID)
    .def("cardtype", &action_card_type)
    .def("card", &action_card, boost::python::return_value_policy<boost::python::return_by_value>())
    .add_property("target", &Prismata::Action::getTargetID)
    .add_property("type", &Prismata::Action::getType)
    .add_property("player", &Prismata::Action::getPlayer)
		.def("__str__", &action_stringify)
		.def("json", &action_json)
		;
	boost::python::class_<Prismata::Move>("Move")
		.def("append", &Prismata::Move::addAction)
		.def("clear", &Prismata::Move::clear)
		.def("__str__", &Prismata::Move::toString)
		;
	boost::python::class_<Prismata::Resources>("Resources")
		.def(boost::python::init<std::string>())
		.def("__eq__", &Prismata::Resources::operator==)
		.def("__ne__", &Prismata::Resources::operator!=)
		.def("__str__", &Prismata::Resources::getString)
		.def("__iadd__", static_cast<void (Prismata::Resources::*)(const Prismata::Resources&)>(&Prismata::Resources::add))
    .def("amountOf", &Prismata::Resources::amountOf, boost::python::return_value_policy<boost::python::return_by_value>()) 
    .def("has", &Prismata::Resources::has)
    // .def("__dict__", &Prismata::Resources::amountOf, boost::python::return_value_policy<boost::python::return_by_value>()) 
		;
	boost::python::class_<Prismata::CardVector>("CardVector")
		.def(boost::python::vector_indexing_suite<Prismata::CardVector>())
		.def("clear", &Prismata::CardVector::clear)
		;
	boost::python::class_<std::vector<Prismata::Action>>("PrismataActions")
		.def(boost::python::vector_indexing_suite<std::vector<Prismata::Action>>())
		.def("__str__", &actions_stringify)
        .def("json", &actions_json)
		.def("clear", &std::vector<Prismata::Action>::clear)
		;
	boost::python::class_<Prismata::GameState>("PrismataGameState")
		.add_property("activePlayer", &Prismata::GameState::getActivePlayer) 
		.add_property("inactivePlayer", &Prismata::GameState::getInactivePlayer) 
		.add_property("winner", &Prismata::GameState::winner) 
		.add_property("activePhase", &Prismata::GameState::getActivePhase) 
		.def("addCard", static_cast<void (Prismata::GameState::*)(const Prismata::Card &)>(&Prismata::GameState::addCard))
		.def("beginTurn", &Prismata::GameState::beginTurn) 
		.def("doAction", &Prismata::GameState::doAction) 
		.def("doMove", &Prismata::GameState::doMove) 
		.def("generateLegalActions", &Prismata::GameState::generateLegalActions) 
		.def("getResources", &Prismata::GameState::getResources, boost::python::return_value_policy<boost::python::reference_existing_object>())
		.def("isGameOver", &Prismata::GameState::isGameOver) 
		.def("isLegal", &Prismata::GameState::isLegal) 
		.def("json", &Prismata::GameState::toJSONString)
		.def("numCardsBuyable", &Prismata::GameState::numCardsBuyable) 
		.def("numCardsForPlayer", &Prismata::GameState::numCards) 
		.def("setStartingState", &Prismata::GameState::setStartingState) 
		.def("getCardById", &Prismata::GameState::getCardByID, boost::python::return_value_policy<boost::python::reference_existing_object>()) 
		.def("getCardBuyableById", &Prismata::GameState::getCardBuyableByID, boost::python::return_value_policy<boost::python::reference_existing_object>()) 
		.def("__str__", &Prismata::GameState::getStateString) 
		.def("turnNumber", &Prismata::GameState::getTurnNumber) 
		.def("getLiveCards", &get_cards_player, boost::python::return_value_policy<boost::python::reference_existing_object>())
		;
}
