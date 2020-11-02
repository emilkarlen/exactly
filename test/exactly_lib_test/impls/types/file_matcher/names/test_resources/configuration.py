import unittest
from abc import ABC, abstractmethod

from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import NameVariant
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer


class Configuration(ABC):
    @property
    @abstractmethod
    def node_name(self) -> str:
        pass

    @abstractmethod
    def arguments(self, condition: NameVariant) -> ArgumentElementsRenderer:
        pass

    @abstractmethod
    def file_name_ending_with(self, s: str) -> str:
        pass


class TestCaseBase(unittest.TestCase, ABC):
    @property
    @abstractmethod
    def conf(self) -> Configuration:
        pass


class Case:
    def __init__(self,
                 name: str,
                 expected_result: bool,
                 model_tail: str,
                 pattern: str,
                 ):
        self.name = name
        self.expected_result = expected_result
        self.pattern = pattern
        self.model_tail = model_tail
