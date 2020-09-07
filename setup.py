import setuptools
from distutils.core import setup, Extension
import os.path
import sys

with open("README.md", "r") as fh:
        long_description = fh.read()

if sys.platform == "win32" :
    include_dirs = ["C:/Boost/include/boost-1_32","."]
    libraries=["boost_python-mgw"]
    library_dirs=['C:/Boost/lib']
else :
    include_dirs = ["/usr/include/boost-1_32","."]
    libraries=["boost_python3"]
    library_dirs=['/usr/local/lib']

include_dirs.extend(["PrismataAI/source", "PrismataAI/source/engine"])

prismataengine = Extension('prismataengine',
sources = ['PrismataAI/source/engine/Action.cpp',
'PrismataAI/source/engine/CardBuyable.cpp',
'PrismataAI/source/engine/CardBuyableData.cpp',
'PrismataAI/source/engine/Card.cpp',
'PrismataAI/source/engine/CardData.cpp',
'PrismataAI/source/engine/CardType.cpp',
'PrismataAI/source/engine/CardTypeData.cpp',
'PrismataAI/source/engine/CardTypeInfo.cpp',
'PrismataAI/source/engine/CardTypes.cpp',
'PrismataAI/source/engine/Common.cpp',
'PrismataAI/source/engine/Condition.cpp',
'PrismataAI/source/engine/CreateDescription.cpp',
'PrismataAI/source/engine/DestroyDescription.cpp',
'PrismataAI/source/engine/FileUtils.cpp',
'PrismataAI/source/engine/Game.cpp',
'PrismataAI/source/engine/GameState.cpp',
'PrismataAI/source/engine/GenericValue.cpp',
'PrismataAI/source/engine/JSONTools.cpp',
'PrismataAI/source/engine/Move.cpp',
'PrismataAI/source/engine/Player.cpp',
'PrismataAI/source/engine/PrismataAssert.cpp',
'PrismataAI/source/engine/Prismata.cpp',
'prismataengine/prismataengineboost.cpp',
'PrismataAI/source/engine/Resources.cpp',
'PrismataAI/source/engine/SacDescription.cpp',
'PrismataAI/source/engine/Script.cpp',
'PrismataAI/source/engine/ScriptEffect.cpp',
'PrismataAI/source/engine/Timer.cpp',
],
        library_dirs=library_dirs,
        libraries=libraries,
        include_dirs=include_dirs,
        depends=[])

setuptools.setup (name = 'prismataengine',
       version = '2.0',
       description = 'This package provides access to the GameState object and supporting methods from Prismata',
       ext_modules = [prismataengine],
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
       )
