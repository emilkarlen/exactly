import unittest

from shellcheck_lib.general.textformat.structure import core, lists, document as doc
from shellcheck_lib.general.textformat.structure.paragraph import Paragraph
from shellcheck_lib.general.textformat.structure.utils import ParagraphItemVisitor


def paragraph_item_list(put: unittest.TestCase,
                        x,
                        msg_prefix=''):
    check_list(ParagraphItemChecker,
               CheckerWithMsgPrefix(put, msg_prefix),
               x)


def section_contents(put: unittest.TestCase,
                     x,
                     msg_prefix=''):
    SectionContentsChecker(CheckerWithMsgPrefix(put, msg_prefix)).apply(x),


class Assertion:
    def apply(self, x):
        raise NotImplementedError()


class CheckerWithMsgPrefix:
    def __init__(self,
                 put: unittest.TestCase,
                 msg_prefix=''):
        self.put = put
        self.msg_prefix = msg_prefix

    def msg(self, s: str) -> str:
        return self.msg_prefix + s


def new_with_added_prefix(prefix_component: str, checker: CheckerWithMsgPrefix) -> CheckerWithMsgPrefix:
    return CheckerWithMsgPrefix(checker.put,
                                checker.msg_prefix + prefix_component)


def check_list(assertion_constructor_for_checker,
               checker: CheckerWithMsgPrefix,
               x):
    checker.put.assertIsInstance(x,
                                 list,
                                 checker.msg('Must be a list'))
    for (index, element) in enumerate(x):
        assertion = assertion_constructor_for_checker(new_with_added_prefix('[%d]: ' % index, checker))
        assertion.apply(element)


class TextChecker(Assertion):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, x):
        self.checker.put.assertIsInstance(x,
                                          core.Text,
                                          self.checker.msg('Must be Text instance'))
        assert isinstance(x, core.Text)
        self.checker.put.assertIsInstance(x.value,
                                          str,
                                          self.checker.msg('Value must be a str'))


class ParagraphItemChecker(Assertion):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, item):
        self.checker.put.assertIsInstance(item,
                                          core.ParagraphItem)
        concrete_checker = _ParagraphItemCheckerVisitor(self.checker)
        concrete_checker.visit(item)


class _ParagraphItemCheckerVisitor(ParagraphItemVisitor):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def visit_paragraph(self, paragraph: Paragraph):
        self.checker.put.assertIsInstance(paragraph.start_on_new_line_blocks,
                                          list,
                                          self.checker.msg('start_on_new_line_blocks must be a list'))
        for (pos, text) in enumerate(paragraph.start_on_new_line_blocks):
            TextChecker(new_with_added_prefix('Text[%d]: ' % pos, self.checker)).apply(text)

    def visit_header_value_list(self, header_value_list: lists.HeaderContentList):
        ListChecker(self.checker).apply(header_value_list)


class ListChecker(Assertion):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, x):
        self.checker.put.assertIsInstance(x,
                                          lists.HeaderContentList,
                                          self.checker.msg('Must be a %s' % lists.HeaderContentList))
        assert isinstance(x, lists.HeaderContentList)
        self.checker.put.assertIsInstance(x.list_type,
                                          lists.ListType,
                                          self.checker.msg('List type must be instance of %s' % lists.ListType))
        if x.custom_indent_spaces is not None:
            self.checker.put.assertIsInstance(x.custom_indent_spaces,
                                              int,
                                              self.checker.msg('custom_indent_spaces must be either None or an int'))
        check_list(ListItemChecker,
                   new_with_added_prefix('Items: ', self.checker),
                   x.items)


class ListItemChecker(Assertion):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, item):
        self.checker.put.assertIsInstance(item,
                                          lists.HeaderContentListItem,
                                          self.checker.msg('Must be a %s' % lists.HeaderContentListItem))
        assert isinstance(item, lists.HeaderContentListItem)
        TextChecker(new_with_added_prefix('Header: ', self.checker)).apply(item.header)
        check_list(ParagraphItemChecker,
                   new_with_added_prefix('Values: ', self.checker),
                   item.content_paragraph_items)


class SectionContentsChecker(Assertion):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, x):
        self.checker.put.assertIsInstance(x,
                                          doc.SectionContents,
                                          self.checker.msg('Must be SectionContents instance'))
        assert isinstance(x, doc.SectionContents)
        check_list(ParagraphItemChecker,
                   new_with_added_prefix('Initial paras: ', self.checker),
                   x.initial_paragraphs)
        check_list(SectionChecker,
                   new_with_added_prefix('sections: ', self.checker),
                   x.sections)


class SectionChecker(Assertion):
    def __init__(self,
                 checker: CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, x):
        self.checker.put.assertIsInstance(x,
                                          doc.Section,
                                          self.checker.msg('Must be Section instance'))
        assert isinstance(x, doc.Section)
        TextChecker(new_with_added_prefix('header: ', self.checker)).apply(x.header)
        SectionContentsChecker(new_with_added_prefix('contents: ', self.checker)).apply(x.contents)
