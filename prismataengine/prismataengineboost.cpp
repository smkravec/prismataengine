#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include "Action.h"
#include "Card.h"
#include "Common.h"
#include "GameState.h"
#include "Move.h"
#include "Prismata.h"
#include "Resources.h"

Prismata::GameState state;

inline const char* actiontype_tostring(int v) {
    switch (v)
    {
		case 0: return "USE_ABILITY";
		case 1: return "BUY";
		case 2: return "END_PHASE";
		case 3: return "ASSIGN_BLOCKER";
		case 4: return "ASSIGN_BREACH";
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

std::string action_stringify(const Prismata::Action & v)
{
	std::stringstream ss;
    ss << "(Player = " << (int)v.getPlayer() << ", Type = " << actiontype_tostring((int)v.getType()) << ", ID = " << (int)v.getID() << ", Target = " << (int)v.getTargetID() <<")";
	return ss.str();
}

std::string action_json(const Prismata::Action & v)
{
	std::stringstream ss;
    ss << "{\"player\": " << (int)v.getPlayer() << ", \"type\": \"" << actiontype_tostring((int)v.getType()) << "\", \"id\": " << (int)v.getID() << ", \"target\": " << (int)v.getTargetID() <<"}";
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

BOOST_PYTHON_MODULE(_prismataengine) {
	boost::python::def("init", &Prismata::InitFromCardLibrary);
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
	boost::python::enum_<int>("AliveStatus")
		.value("Alive", Prismata::AliveStatus::Alive)
		.value("Dead", Prismata::AliveStatus::Dead)
		.value("KilledThisTurn", Prismata::AliveStatus::KilledThisTurn)
		;
	boost::python::enum_<Prismata::PlayerID>("Players")
		.value("Player_One", Prismata::Players::Player_One)
		.value("Player_Two", Prismata::Players::Player_Two)
		;
	boost::python::class_<Prismata::Card>("Card")
		.def(boost::python::init<std::string>())
		.def(boost::python::init<Prismata::CardType, Prismata::PlayerID, int, Prismata::TurnType, Prismata::TurnType>())
		.def("__eq__", &Prismata::Card::operator==)
		.def("__lt__", &Prismata::Card::operator<)
		.def("__str__", &Prismata::Card::toJSONString)
		;
	boost::python::class_<Prismata::Action>("Action")
		.def(boost::python::init<Prismata::PlayerID, Prismata::ActionID, Prismata::CardID>())
		.def(boost::python::init<Prismata::PlayerID, Prismata::ActionID, Prismata::CardID, Prismata::CardID>())
		.def("describe", &Prismata::Action::toStringEnglish)
		.def("__eq__", &Prismata::Action::operator==)
		.def("__ne__", &Prismata::Action::operator!=)
		.def("player", &Prismata::Action::getPlayer)
		.def("setShift", &Prismata::Action::setShift)
		.def("setSource", &Prismata::Action::setID)
		.def("shift", &Prismata::Action::getShift)
		.def("source", &Prismata::Action::getID)
		.def("__str__", &action_stringify)
		.def("target", &Prismata::Action::getTargetID)
		.def("type", &Prismata::Action::getType)
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
		;
	boost::python::class_<std::vector<Prismata::Action>>("Actions")
		.def(boost::python::vector_indexing_suite<std::vector<Prismata::Action>>())
		.def("__str__", &actions_stringify)
        .def("json", &actions_json)
		.def("clear", &std::vector<Prismata::Action>::clear)
		;
	boost::python::class_<Prismata::GameState>("GameState")
		.def("activePlayer", &Prismata::GameState::getActivePlayer) 
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
		.def("__str__", &Prismata::GameState::getStateString) 
		.def("turnNumber", &Prismata::GameState::getTurnNumber) 
		;
}
