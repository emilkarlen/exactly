import unittest

from exactly_lib.help.actors import render as sut
from exactly_lib.help.cross_reference_id import CustomCrossReferenceId
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import structures as docs
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

RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())


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
    def runTest(self):
        test_cases = [
            ('minimal',
             ActorTestImpl('name')
             ),
            ('with act_phase_contents',
             ActorTestImpl('name',
                           act_phase_contents=_section_contents())
             ),
            ('with act_phase_contents_syntax',
             ActorTestImpl('name',
                           act_phase_contents_syntax=_section_contents())
             ),
            ('see_also_specific',
             ActorTestImpl('name',
                           see_also_specific=[CustomCrossReferenceId('custom-cross-reference-target')])
             ),
            ('full',
             ActorTestImpl('name',
                           act_phase_contents=_section_contents(),
                           act_phase_contents_syntax=_section_contents(),
                           see_also_specific=[CustomCrossReferenceId('custom-cross-reference-target')])
             ),
        ]
        for test_case_name, documentation in test_cases:
            with self.subTest(test_case_name=test_case_name):
                # ARRANGE #
                renderer = sut.IndividualActorRenderer(documentation)
                # ACT #
                actual = renderer.apply(RENDERING_ENVIRONMENT)
                # ASSERT #
                struct_check.is_section_contents.apply(self, actual)


def _paragraphs() -> list:
    return [docs.para('paragraph text')]


def _sections():
    return [docs.section('header',
                         _paragraphs(),
                         [])]


def _section_contents():
    return docs.section_contents(_paragraphs(), _sections())
