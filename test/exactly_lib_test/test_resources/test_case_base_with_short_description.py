import unittest


class TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType(unittest.TestCase):
    """
    Super class for test cases with a single test (implemented by runTest),
    and a short description from an configuration-like object that, together
    with the test case class, identifies the test case.
    """

    def __init__(self, object_whos_type_is_used_for_short_description):
        super().__init__()
        self.__object_whos_type_is_used_for_short_description = object_whos_type_is_used_for_short_description

    def shortDescription(self):
        return str(type(self)) + ' / ' + str(type(self.__object_whos_type_is_used_for_short_description))

    def runTest(self):
        raise NotImplementedError()
