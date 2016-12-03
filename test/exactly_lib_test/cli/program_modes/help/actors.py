import unittest

from exactly_lib.cli.program_modes.help.actors import request_rendering as sut
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.help.actors.contents_structure import actors_help, ActorDocumentation
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib_test.help.actors.test_resources.documentation import ActorTestImpl
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


class TestActorHelpRequestRendererResolver(unittest.TestCase):
    def test_all_actors_list(self):
        # ARRANGE #
        actors = [
            ActorTestImpl('first'),
            ActorTestImpl('second'),
        ]
        resolver = sut.actor_help_request_renderer_resolver(actors_help(actors))
        # ACT #
        actual = resolver.renderer_for(_actor_help_request(EntityHelpItem.ALL_ENTITIES_LIST))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        # ACT #
        actual_rendition = actual.apply(_RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual_rendition)

    def test_individual_actor(self):
        # ARRANGE #
        first_actor = ActorTestImpl('first actor')
        actors = [
            first_actor,
        ]
        resolver = sut.actor_help_request_renderer_resolver(actors_help(actors))
        # ACT #
        actual = resolver.renderer_for(_actor_help_request(EntityHelpItem.INDIVIDUAL_ENTITY, first_actor))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        # ACT #
        actual_rendition = actual.apply(_RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual_rendition)


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestActorHelpRequestRendererResolver)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())

_RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())


def _actor_help_request(item: EntityHelpItem,
                        individual_actor: ActorDocumentation = None) -> EntityHelpRequest:
    return EntityHelpRequest(ACTOR_ENTITY_TYPE_NAME, item, individual_actor)
