import unittest


class TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType(unittest.TestCase):
    """
    Super class for test cases with a single test (implemented by runTest),
    and a short description from an configuration-like object that, together
    with the test case class, identifies the test case.
    """

    def __init__(self, object_who_s_type_is_used_for_short_description):
        super().__init__()
        self.__object_who_s_type_is_used_for_short_description = object_who_s_type_is_used_for_short_description

    def shortDescription(self):
        if isinstance(self.__object_who_s_type_is_used_for_short_description, str):
            object_str = self.__object_who_s_type_is_used_for_short_description
        else:
            object_str = str(type(self.__object_who_s_type_is_used_for_short_description))
        return str(type(self)) + '\n/ ' + object_str

    def runTest(self):
        raise NotImplementedError()
