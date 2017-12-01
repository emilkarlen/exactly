from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.structure.core import TaggedItem


class ElementPopulator:
    def apply(self, parent: Element):
        pass


class ComplexElementPopulator(ElementPopulator):
    def __init__(self, populators):
        self.populators = populators

    def apply(self, parent: Element):
        for populator in self.populators:
            assert isinstance(populator, ElementPopulator)
            populator.apply(parent)


def set_class_attribute(output: dict, tagged_item: TaggedItem):
    if tagged_item.tags:
        class_value = ' '.join(sorted(tagged_item.tags))
        output['class'] = class_value


def set_class_attribute_on_element(output: Element, tagged_item: TaggedItem):
    if tagged_item.tags:
        class_value = ' '.join(sorted(tagged_item.tags))
        output.set('class', class_value)
