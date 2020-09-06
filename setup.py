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

prismataengine = Extension('prismataengine', sources = ['Action.cpp', 'CardBuyable.cpp', 'CardBuyableData.cpp', 'Card.cpp', 'CardData.cpp', 'CardType.cpp', 'CardTypeData.cpp', 'CardTypeInfo.cpp', 'CardTypes.cpp', 'Common.cpp', 'Condition.cpp', 'CreateDescription.cpp', 'DestroyDescription.cpp', 'FileUtils.cpp', 'Game.cpp', 'GameState.cpp', 'GenericValue.cpp', 'JSONTools.cpp', 'Move.cpp', 'Player.cpp', 'PrismataAssert.cpp', 'Prismata.cpp', 'prismataengine/prismataengineboost.cpp', 'Resources.cpp', 'SacDescription.cpp', 'Script.cpp', 'ScriptEffect.cpp', 'Timer.cpp', ],
        library_dirs=library_dirs,
        libraries=libraries,
        include_dirs=include_dirs,
        depends=[])

setup (name = 'prismataengine',
       version = '2.0',
       description = 'This package provides access to the GameState object and supporting methods from Prismata',
       ext_modules = [prismataengine]
       author="Shauna Kravec",
       author_email="smkravec@celest.ai",
       long_description=long_description,
       long_description_content_type="text/markdown",
       url="https://github.com/smkravec/prismataengine",
       classifiers=[
           "Programming Language :: Python :: 3",
           "License :: Creative Commons Attribution-NonCommercial-ShareAlike 2.5 Canada License",
           "Operating System :: OS Independent",
           ],
       python_requires='>=3.6',
       )
