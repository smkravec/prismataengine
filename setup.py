from setuptools import setup, Extension
import os, os.path
import hashlib
import shutil
import sys

with open("README.md", "r") as fh:
        long_description = fh.read()

if sys.platform == "win32" : 
    include_dirs = ["C:/Boost/include/boost-1_32","."]
    libraries=["boost_python-mgw"]
    library_dirs=['C:/Boost/lib']
else :
    include_dirs = ["/usr/include/boost","."]
    libraries=["boost_python38", "boost_numpy38"]
    library_dirs=['/usr/local/lib']

extra_compile_args = ["-O3", "-g", "-std=c++17", "-flto"]
extra_link_args = ["-O3","-g",  "-flto", "-pthread", "-lsfml-graphics", "-lsfml-window", "-lsfml-system", "-lsfml-audio"]


include_dirs.extend(["PrismataAI/source", "PrismataAI/source/engine", "PrismataAI/source/gui", "PrismataAI/source/ai", "PrismataAI/source/rapidjson"])
#_prismataengine is the C++ extension this compiles to
md5_hash = hashlib.md5()
with open("PrismataAI/source/ai/AIParameters.h", "rb") as aip_file:
    content = aip_file.read()
    md5_hash.update(content)
if md5_hash.hexdigest() == 'd3e1f060f0d4109a9b2abaf03f93aafb':
    os.system('sh -c "cd PrismataAI; git apply ../AIParameters.patch"')
prismataengine = Extension('_prismataengine', sources = [
    'PrismataAI/source/engine/Action.cpp', 'PrismataAI/source/engine/CardBuyable.cpp', 'PrismataAI/source/engine/CardBuyableData.cpp', 'PrismataAI/source/engine/Card.cpp', 'PrismataAI/source/engine/CardData.cpp', 'PrismataAI/source/engine/CardType.cpp', 'PrismataAI/source/engine/CardTypeData.cpp', 'PrismataAI/source/engine/CardTypeInfo.cpp', 'PrismataAI/source/engine/CardTypes.cpp', 'PrismataAI/source/engine/Common.cpp', 'PrismataAI/source/engine/Condition.cpp', 'PrismataAI/source/engine/CreateDescription.cpp', 'PrismataAI/source/engine/DestroyDescription.cpp', 'PrismataAI/source/engine/FileUtils.cpp', 'PrismataAI/source/engine/Game.cpp', 'PrismataAI/source/engine/GameState.cpp', 'PrismataAI/source/engine/GenericValue.cpp', 'PrismataAI/source/engine/JSONTools.cpp', 'PrismataAI/source/engine/Move.cpp', 'PrismataAI/source/engine/Player.cpp', 'PrismataAI/source/engine/PrismataAssert.cpp', 'PrismataAI/source/engine/Prismata.cpp', 'prismataengine/prismataengineboost.cpp', 'PrismataAI/source/engine/Resources.cpp', 'PrismataAI/source/engine/SacDescription.cpp', 'PrismataAI/source/engine/Script.cpp', 'PrismataAI/source/engine/ScriptEffect.cpp', 'PrismataAI/source/engine/Timer.cpp',
    'PrismataAI/source/ai/AIParameters.cpp' , 'PrismataAI/source/ai/AITools.cpp', 'PrismataAI/source/ai/AllPlayers.cpp', 'PrismataAI/source/ai/AlphaBetaSearch.cpp', 'PrismataAI/source/ai/AttackDamageScenario.cpp', 'PrismataAI/source/ai/AvoidBreachBuyIterator.cpp', 'PrismataAI/source/ai/BlockIterator.cpp', 'PrismataAI/source/ai/BuildOrderIterator.cpp', 'PrismataAI/source/ai/BuildOrderSearch.cpp', 'PrismataAI/source/ai/BuildOrderSearchGoal.cpp', 'PrismataAI/source/ai/BuildOrderSearchParameters.cpp', 'PrismataAI/source/ai/BuyIterator.cpp', 'PrismataAI/source/ai/BuyLimits.cpp', 'PrismataAI/source/ai/CanonicalOrderComparator.cpp', 'PrismataAI/source/ai/CanonicalOrdering.cpp', 'PrismataAI/source/ai/CardFilter.cpp', 'PrismataAI/source/ai/CardFilterCondition.cpp', 'PrismataAI/source/ai/ChillIterator.cpp', 'PrismataAI/source/ai/ChillScenario.cpp', 'PrismataAI/source/ai/DefenseHistogramExperiment.cpp', 'PrismataAI/source/ai/Eval.cpp', 'PrismataAI/source/ai/Heuristics.cpp', 'PrismataAI/source/ai/IsomorphicCardSet.cpp', 'PrismataAI/source/ai/MoveIterator.cpp', 'PrismataAI/source/ai/MoveIterator_All.cpp', 'PrismataAI/source/ai/MoveIterator_AllAbility.cpp', 'PrismataAI/source/ai/MoveIterator_AllBreach.cpp', 'PrismataAI/source/ai/MoveIterator_AllBuy.cpp', 'PrismataAI/source/ai/MoveIterator_AllDefense.cpp', 'PrismataAI/source/ai/MoveIterator_PPPortfolio.cpp',
    'PrismataAI/source/ai/PartialPlayer.cpp', 'PrismataAI/source/ai/PartialPlayerSequence.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_ActivateAll.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_ActivateUtility.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_AttackDefault.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_AvoidAttackWaste.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_AvoidBreachSolver.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_AvoidEconomyWaste.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_ChillGreedyKnapsack.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_ChillSolver.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_Combination.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_Default.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_DontAttack.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_EconomyDefault.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_FrontlineGreedyKnapsack.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_Random.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_SnipeGreedyKnapsack.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionAbility_UntapAvoidBreach.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_AvoidBreach.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_Combination.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_Default.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_EngineerHeuristic.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_GreedyKnapsack.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_Iterator.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_Nothing.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_OpeningBook.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_Random.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_Sequence.cpp', 'PrismataAI/source/ai/PartialPlayer_ActionBuy_TechHeuristic.cpp', 'PrismataAI/source/ai/PartialPlayer_Breach_Default.cpp', 'PrismataAI/source/ai/PartialPlayer_Breach_GreedyKnapsack.cpp', 'PrismataAI/source/ai/PartialPlayer_Breach_Random.cpp', 'PrismataAI/source/ai/PartialPlayer_Defense_Default.cpp', 'PrismataAI/source/ai/PartialPlayer_Defense_GreedyKnapsack.cpp', 'PrismataAI/source/ai/PartialPlayer_Defense_Random.cpp', 'PrismataAI/source/ai/PartialPlayer_Defense_Solver.cpp',
    'PrismataAI/source/ai/Player_AlphaBeta.cpp', 'PrismataAI/source/ai/Player_Default.cpp', 'PrismataAI/source/ai/Player_GUI.cpp', 'PrismataAI/source/ai/Player_PPSequence.cpp', 'PrismataAI/source/ai/Player_Random.cpp', 'PrismataAI/source/ai/Player_RandomFromIterator.cpp', 'PrismataAI/source/ai/Player_StackAlphaBeta.cpp', 'PrismataAI/source/ai/Player_UCT.cpp', 'PrismataAI/source/ai/PuzzleSolver.cpp', 'PrismataAI/source/ai/StackAlphaBetaSearch.cpp', 'PrismataAI/source/ai/StateChillIterator.cpp', 'PrismataAI/source/ai/UCTNode.cpp', 'PrismataAI/source/ai/UCTSearch.cpp', 
    'PrismataAI/source/gui/Assets.cpp', 'PrismataAI/source/gui/GUICard.cpp', 'PrismataAI/source/gui/GUICardBuyable.cpp', 'PrismataAI/source/gui/GUIEngine.cpp', 'PrismataAI/source/gui/GUIState.cpp', 'PrismataAI/source/gui/GUIState_Menu.cpp', 'PrismataAI/source/gui/GUIState_Play.cpp', 'PrismataAI/source/gui/GUITools.cpp'],
        library_dirs=library_dirs,
        libraries=libraries,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        depends=[])
#If you haven't compiled this before, pulls cardlibrary.jso from submodule, needed for resource_import
if not os.path.isfile('prismataengine/cardLibrary.jso'): 
    shutil.copy('PrismataAI/bin/asset/config/cardLibrary.jso', 'prismataengine')

setup (name = 'prismataengine',
       version = '2.4.0',
       description = 'This package provides access to the GameState object and supporting methods from Prismata',
       ext_modules = [prismataengine],
       packages = ['prismataengine'],
       author="Shauna Kravec",
       author_email="smkravec@celest.ai",
       long_description=long_description,
       long_description_content_type="text/markdown",
       url="https://github.com/smkravec/prismataengine",
       classifiers=[
           "Programming Language :: Python :: 3",
           "Operating System :: OS Independent",
           ],
       python_requires='>=3.6',
       package_data={'prismataengine': ['cardLibrary.jso', 'AI_config.txt']},
       )
