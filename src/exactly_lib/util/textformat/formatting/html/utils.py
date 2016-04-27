from xml.etree.ElementTree import Element


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
