from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.command_line_syntax.elements import argument3 as arg
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


class DescribedArgument:
    def __init__(self,
                 argument: arg.Argument,
                 description: list,
                 see_also: list = ()):
        """
        :type description: [`ParagraphItem`]
        :type see_also: [`CrossReferenceTarget`]
        """
        self.argument = argument
        self.description = description
        self.see_also = list(see_also)


class ProgramDocumentationRenderer:
    def __init__(self, environment: RenderingEnvironment):
        self.environment = environment
        self.cmd_line_syntax_renderer = CommandLineSyntaxRenderer()
        self.arg_in_description_renderer = _ArgumentInArgumentDescriptionRenderer()

    def apply(self, command_line: arg.CommandLine,
              argument_descriptions: list) -> docs.SectionContents:
        options_sections = self._options_sections(argument_descriptions)
        return docs.SectionContents([docs.para(self.cmd_line_syntax_renderer.apply(command_line))],
                                    options_sections)

    def _options_sections(self, argument_descriptions: list) -> list:
        if not argument_descriptions:
            return []
        l = lists.HeaderContentList(map(self._arg_description_list_item, argument_descriptions),
                                    lists.Format(lists.ListType.VARIABLE_LIST,
                                                 custom_indent_spaces=0,
                                                 custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))

        return [docs.section(docs.text('OPTIONS'),
                             [l])]

    def _arg_description_list_item(self, argument: DescribedArgument) -> lists.HeaderContentListItem:
        header = docs.text(self.arg_in_description_renderer.visit(argument.argument))
        return lists.HeaderContentListItem(header, argument.description)


class CommandLineSyntaxRenderer:
    def __init__(self):
        self.arg_usage_renderer = _ArgumentUsageOnCommandLineRenderer()

    def apply(self, command_line: arg.CommandLine) -> docs.Text:
        components = [command_line.program_name] + list(map(self.arg_usage_renderer, command_line.argument_usages))
        return docs.text(' '.join(components))


class _ArgumentUsageOnCommandLineRenderer(arg.ArgumentUsageVisitor):
    CHOICE_SEPARATOR = '|'

    def __init__(self):
        self._arg_renderer = _ArgumentOnCommandLineRenderer()

    def visit_single(self, x: arg.Single) -> str:
        return self._multiplicity(self._arg_renderer.visit(x.argument),
                                  x.multiplicity)

    def visit_choice(self, x: arg.Choice) -> str:
        arg_str = self.CHOICE_SEPARATOR.join(map(self._arg_renderer, x.arguments))
        return self._multiplicity(arg_str, x.multiplicity)

    def _multiplicity(self, arg_str: str, multiplicity: arg.Multiplicity) -> str:
        return arg_str if multiplicity is arg.Multiplicity.MANDATORY else '[' + arg_str + ']'


class _ArgumentOnCommandLineRenderer(arg.ArgumentVisitor):
    def visit_constant(self, x: arg.Constant) -> str:
        return x.name

    def visit_named(self, x: arg.Named) -> str:
        return x.name

    def visit_option(self, x: arg.Option) -> str:
        ret_val = ''
        if x.long_name:
            ret_val = _long_option(x.long_name)
        else:
            ret_val = _short_option(x.short_name)
        if x.argument:
            return ret_val + ' ' + x.argument
        else:
            return ret_val


class _ArgumentInArgumentDescriptionRenderer(arg.ArgumentVisitor):
    LONG_OPTION_PREFIX = '--'
    SHORT_OPTION_PREFIX = '-'

    def visit_constant(self, x: arg.Constant) -> str:
        return x.name

    def visit_named(self, x: arg.Named) -> str:
        return x.name

    def visit_option(self, x: arg.Option) -> str:
        ret_val = []
        if x.long_name:
            ret_val.append(_long_option(x.long_name))
        if x.short_name:
            ret_val.append(_short_option(x.short_name))
        if x.argument:
            ret_val.append(x.argument)
        return ' '.join(ret_val) + ' (TODO)'


def _long_option(name: str) -> str:
    return '--' + name


def _short_option(name: str) -> str:
    return '-' + name
