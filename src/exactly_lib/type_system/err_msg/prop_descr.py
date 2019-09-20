from typing import List


class PropertyDescription:
    def __init__(self,
                 name: str,
                 object_description_lines: List[str]):
        self._name = name
        self._details_lines = object_description_lines

    @property
    def name(self) -> str:
        return self._name

    @property
    def object_description_lines(self) -> List[str]:
        return self._details_lines


class PropertyDescriptor:
    def description(self) -> PropertyDescription:
        raise NotImplementedError('abstract method')


class FilePropertyDescriptorConstructor:
    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        raise NotImplementedError('abstract method')
