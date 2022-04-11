from . import requests, responses
from .converter import ConverterAttr2Attr as Converter

global_converter = Converter()
structure = global_converter.structure

__all__ = [
    "requests",
    "responses",
    "structure",
]
