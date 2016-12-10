import unittest

from exactly_lib.cli.program_modes.help import argument_parsing as sut
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.cli.program_modes.help.error import HelpError
from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import *
from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class EntityTestSetup:
    def __init__(self,
                 documentation_class,
                 entity_type_name: str):
        self.entity_type_name = entity_type_name
        self.documentation_class = documentation_class

    def arguments_for_list(self) -> list:
        raise NotImplementedError()

    def arguments_for_single_entity(self, entity_name_pattern: str) -> list:
        raise NotImplementedError()

    def entity_with_name(self, entity_name: str):
        raise NotImplementedError()

    def application_help_for_list_of_entities(self, entities: list) -> ApplicationHelp:
        raise NotImplementedError()


class EntityTestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, setup: EntityTestSetup):
        super().__init__(setup)
        self.setup = setup


class TestActorList(EntityTestCaseBase):
    def runTest(self):
        arguments = self.setup.arguments_for_list()
        actual = sut.parse(self.setup.application_help_for_list_of_entities([]),
                           arguments)
        self.assertIsInstance(actual,
                              EntityHelpRequest,
                              'Expecting settings for {}s'.format(self.setup.entity_type_name))
        assert isinstance(actual, EntityHelpRequest, )
        self.assertEqual(actual.entity_type, self.setup.entity_type_name,
                         'Expecting settings for {}s'.format(self.setup.entity_type_name))
        self.assertIs(EntityHelpItem.ALL_ENTITIES_LIST,
                      actual.item,
                      'Item should denote help for ' + EntityHelpItem.ALL_ENTITIES_LIST.name)


class TestIndividualEntityWithSingleWordName(EntityTestCaseBase):
    def runTest(self):
        # ARRANGE #
        actors = [
            self.setup.entity_with_name('first'),
            self.setup.entity_with_name('second'),
        ]
        application_help = self.setup.application_help_for_list_of_entities(actors)
        # ACT #
        actual = sut.parse(application_help,
                           self.setup.arguments_for_single_entity('second'))
        # ASSERT #
        _assert_result_is_individual_entity(self, self.setup, actual, 'second')


class TestIndividualSearchForSubStringForSingleMatchingEntity(EntityTestCaseBase):
    def runTest(self):
        # ARRANGE #
        actors = [
            self.setup.entity_with_name('first'),
            self.setup.entity_with_name('second'),
        ]
        application_help = self.setup.application_help_for_list_of_entities(actors)
        # ACT #
        actual = sut.parse(application_help,
                           self.setup.arguments_for_single_entity('firs'))
        # ASSERT #
        _assert_result_is_individual_entity(self, self.setup, actual, 'first',
                                            check_is_include_entity_name_in_output=True)


class TestIndividualEntityWithMultipleWordsName(EntityTestCaseBase):
    def runTest(self):
        # ARRANGE #
        actors = [
            self.setup.entity_with_name('first'),
            self.setup.entity_with_name('a b c'),
            self.setup.entity_with_name('last'),
        ]
        application_help = self.setup.application_help_for_list_of_entities(actors)
        # ACT #
        actual = sut.parse(application_help,
                           self.setup.arguments_for_single_entity('a b c'))
        # ASSERT #
        _assert_result_is_individual_entity(self, self.setup, actual, 'a b c',
                                            check_is_include_entity_name_in_output=False)


class TestIndividualEntityWithMultipleWordsAndDifferentCaseName(EntityTestCaseBase):
    def runTest(self):
        # ARRANGE #
        actors = [
            self.setup.entity_with_name('first'),
            self.setup.entity_with_name('a b c'),
            self.setup.entity_with_name('last'),
        ]
        application_help = self.setup.application_help_for_list_of_entities(actors)
        # ACT #
        actual = sut.parse(application_help,
                           self.setup.arguments_for_single_entity('a B C'))
        # ASSERT #
        _assert_result_is_individual_entity(self, self.setup, actual, 'a b c',
                                            check_is_include_entity_name_in_output=False)


class TestSearchForNonExistingActorShouldRaiseHelpError(EntityTestCaseBase):
    def runTest(self):
        # ARRANGE #
        actors = [
            self.setup.entity_with_name('first'),
            self.setup.entity_with_name('second'),
        ]
        application_help = self.setup.application_help_for_list_of_entities(actors)
        # ACT & ASSERT #
        with self.assertRaises(HelpError):
            sut.parse(application_help,
                      self.setup.arguments_for_single_entity('non-existing actor'))


def _assert_result_is_individual_entity(self: unittest.TestCase,
                                        entity_setup: EntityTestSetup,
                                        actual: HelpRequest,
                                        actor_name: str,
                                        check_is_include_entity_name_in_output: bool = None):
    self.assertIsInstance(actual,
                          EntityHelpRequest,
                          'Expecting settings for {}s'.format(entity_setup.entity_type_name))
    assert isinstance(actual, EntityHelpRequest)
    self.assertEqual(actual.entity_type, entity_setup.entity_type_name,
                     'Expecting settings for {}s'.format(entity_setup.entity_type_name))
    self.assertIs(EntityHelpItem.INDIVIDUAL_ENTITY,
                  actual.item,
                  'Item should denote help for ' + EntityHelpItem.INDIVIDUAL_ENTITY.name)

    self.assertIsInstance(actual.individual_entity,
                          entity_setup.documentation_class,
                          'Individual {} is expected to an instance of {}'.format(entity_setup.entity_type_name,
                                                                                  str(ActorDocumentation)))
    if check_is_include_entity_name_in_output is not None:
        self.assertEquals(check_is_include_entity_name_in_output,
                          actual.do_include_name_in_output,
                          'do_include_name_in_output')
    self.assertEqual(actor_name,
                     actual.individual_entity.singular_name())


def suite_for(setup: EntityTestSetup) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(setup) for tcc in [
        TestActorList,
        TestIndividualEntityWithSingleWordName,
        TestIndividualSearchForSubStringForSingleMatchingEntity,
        TestIndividualEntityWithMultipleWordsName,
        TestIndividualEntityWithMultipleWordsAndDifferentCaseName,
        TestSearchForNonExistingActorShouldRaiseHelpError,
    ])
