import unittest

from exactly_lib.help.actors import render as sut
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib_test.help.actors.test_resources.documentation import ActorTestImpl
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualActor),
        unittest.makeSuite(TestAllActorsList),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestAllActorsList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = sut.all_actors_list_renderer([ActorTestImpl('actor 1'),
                                                 ActorTestImpl('actor 2')])
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualActor(unittest.TestCase):
    def test_render(self):
        # ARRANGE #
        actor = ActorTestImpl('name')
        renderer = sut.IndividualActorRenderer(actor)
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
