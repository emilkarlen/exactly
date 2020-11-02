from abc import ABC, abstractmethod
from typing import List


class ArgumentsGenerator(ABC):
    @abstractmethod
    def generate(self,
                 program_arguments: List[str],
                 model_path: str,
                 ) -> List[str]:
        pass


class Last(ArgumentsGenerator):
    def generate(self,
                 program_arguments: List[str],
                 model_path: str,
                 ) -> List[str]:
        return program_arguments + [model_path]


class First(ArgumentsGenerator):
    def generate(self,
                 program_arguments: List[str],
                 model_path: str,
                 ) -> List[str]:
        return [model_path] + program_arguments


class Marker(ArgumentsGenerator):
    def __init__(self, marker: str):
        self._marker = marker

    def generate(self,
                 program_arguments: List[str],
                 model_path: str,
                 ) -> List[str]:
        return [
            (
                model_path
                if arg == self._marker
                else
                arg
            )
            for arg in program_arguments
        ]
