import pathlib

from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments


class Actual:
    def __init__(self,
                 arguments: Arguments,
                 path: pathlib.Path,
                 ):
        self.path = path
        self.arguments = arguments
