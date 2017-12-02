import unittest

from exactly_lib.cli.program_modes.help import entities_requests as sut
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entities.actors.entity_configuration import ACTOR_ENTITY_CONFIGURATION
from exactly_lib.help_texts.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment, \
    SectionContentsConstructor
from exactly_lib_test.help.entities.actors.test_resources.documentation import ActorTestImpl
from exactly_lib_test.util.textformat.construction.section_hierarchy.test_resources.misc import \
    CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


#
# Uses setup for actors - should use test data instead!
#
# Using actors setup means that bugs in actors will be reported here as bug in
# EntityHelpRequestRendererResolver!
#

def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestHelpRequestRendererResolver)


class TestHelpRequestRendererResolver(unittest.TestCase):
    def test_all_entities_list(self):
        # ARRANGE #
        actors = [
            ActorTestImpl('first'),
            ActorTestImpl('second'),
        ]
        resolver = help_request_renderer_resolver(actors)
        # ACT #
        actual = resolver.renderer_for(_actor_help_request(sut.EntityHelpItem.ALL_ENTITIES_LIST))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsConstructor)
        # ACT #
        actual_rendition = actual.apply(_CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual_rendition)

    def test_individual_entity(self):
        # ARRANGE #
        first_actor = ActorTestImpl('first actor')
        actors = [
            first_actor,
        ]
        resolver = help_request_renderer_resolver(actors)
        # ACT #
        actual = resolver.renderer_for(_actor_help_request(sut.EntityHelpItem.INDIVIDUAL_ENTITY, first_actor))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsConstructor)
        # ACT #
        actual_rendition = actual.apply(_CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual_rendition)


def help_request_renderer_resolver(entities: list) -> sut.EntityHelpRequestRendererResolver:
    return sut.EntityHelpRequestRendererResolver(
        ACTOR_ENTITY_CONFIGURATION.entity_doc_2_article_contents_renderer,
        ACTOR_ENTITY_CONFIGURATION.cli_list_constructor_getter,
        entities)


_CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())


def _actor_help_request(item: sut.EntityHelpItem,
                        individual_actor: ActorDocumentation = None) -> sut.EntityHelpRequest:
    return sut.EntityHelpRequest(ACTOR_ENTITY_TYPE_NAMES.identifier, item, individual_actor)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
