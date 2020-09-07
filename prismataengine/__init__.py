from _prismataengine import *
from importlib import resources
with resources.path(__name__, 'cardLibrary.jso') as path:
    init(str(path))
