# prismataengine

This is a package that provides access to Dave Churchill's Prismata Engine from Python.

# Requirements

- Boost-Python
- SFML

# Install

From source:
```
git clone --recurse-submodules smkravec/prismataengine
cd prismataengine
gcc pip install .
```
If you encounter an error, you may need to change 
```
libraries=["boost_python3", "boost_numpy3"]
```
to 
```
libraries=["boost_python3#", "boost_numpy3#"]
```
where # is your relevant version.

The script ```test.py``` shows relevant use for initializing a game, look at state, and taking actions.

Not that vector embeddings exist only for Base set and a Steelsplitter only 4 card mode (WIP)
