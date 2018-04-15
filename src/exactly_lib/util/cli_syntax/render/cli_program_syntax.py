from exactly_lib.definitions import doc_format
from exactly_lib.util.cli_syntax import short_and_long_option_syntax
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.textformat.structure import structures as docs


class CommandLineSyntaxRenderer:
    def __init__(self):
        self.arg_usage_renderer = ArgumentUsageOnCommandLineRenderer()

    def apply(self, command_line: arg.CommandLine) -> docs.Text:
        return doc_format.syntax_text(self.as_str(command_line))

    def as_str(self, command_line: arg.CommandLine) -> str:
        components = []
        if command_line.prefix:
            components.append(command_line.prefix)
        arguments_str = ' '.join((map(self.arg_usage_renderer, command_line.argument_usages)))
        components.append(arguments_str)
        if command_line.suffix:
            components.append(command_line.suffix)
        return ' '.join(components)


class ArgumentUsageOnCommandLineRenderer(arg.ArgumentUsageVisitor):
    CHOICE_SEPARATOR = '|'

    def __init__(self):
        self._arg_renderer = ArgumentOnCommandLineRenderer()

    def visit_single(self, x: arg.Single) -> str:
        arg_str = self._arg_renderer.visit(x.argument)
        if x.multiplicity is arg.Multiplicity.OPTIONAL:
            return self._optional(arg_str)
        elif x.multiplicity is arg.Multiplicity.MANDATORY:
            return arg_str
        elif x.multiplicity is arg.Multiplicity.ZERO_OR_MORE:
            return self._and_more(self._optional(arg_str))
        elif x.multiplicity is arg.Multiplicity.ONE_OR_MORE:
            return self._and_more(arg_str)
        else:
            raise ValueError('Invalid %s: %s' % (str(arg.Multiplicity), str(x.multiplicity)))

    def visit_choice(self, x: arg.Choice) -> str:
        arg_str = self.CHOICE_SEPARATOR.join(map(self._arg_renderer, x.arguments))
        if x.multiplicity is arg.Multiplicity.OPTIONAL:
            return self._optional(arg_str)
        elif x.multiplicity is arg.Multiplicity.MANDATORY:
            return self._mandatory_group(arg_str)
        elif x.multiplicity is arg.Multiplicity.ZERO_OR_MORE:
            return self._and_more(self._optional(arg_str))
        elif x.multiplicity is arg.Multiplicity.ONE_OR_MORE:
            return self._and_more(self._mandatory_group(arg_str))
        else:
            raise ValueError('Invalid %s: %s' % (str(arg.Multiplicity), str(x.multiplicity)))

    @staticmethod
    def _multiplicity(arg_str: str, multiplicity: arg.Multiplicity) -> str:
        return arg_str if multiplicity is arg.Multiplicity.MANDATORY else '[' + arg_str + ']'

    @staticmethod
    def _optional(arg_str) -> str:
        return '[' + arg_str + ']'

    @staticmethod
    def _mandatory_group(arg_str) -> str:
        return '(' + arg_str + ')'

    @staticmethod
    def _and_more(arg_str) -> str:
        return arg_str + '...'


class ArgumentOnCommandLineRenderer(arg.ArgumentVisitor):
    def visit_constant(self, x: arg.Constant) -> str:
        return x.name

    def visit_named(self, x: arg.Named) -> str:
        return x.name

    def visit_option(self, x: arg.Option) -> str:
        option_str = long_option_syntax(x.name.long)
        if x.argument:
            return option_str + ' ' + x.argument
        else:
            return option_str

    def visit_short_and_long_option(self, x: arg.ShortAndLongOption) -> str:
        if x.short_name:
            option_str = short_and_long_option_syntax.short_syntax(x.name.short)
        else:
            option_str = short_and_long_option_syntax.long_syntax(x.name.long)
        if x.argument:
            return option_str + ' ' + x.argument
        else:
            return option_str


class ArgumentInArgumentDescriptionRenderer(arg.ArgumentVisitor):
    def visit_constant(self, x: arg.Constant) -> str:
        return x.name

    def visit_named(self, x: arg.Named) -> str:
        return x.name

    def visit_option(self, x: arg.Option) -> str:
        ret_val = []
        ret_val.append(long_option_syntax(x.name.long))
        if x.argument:
            ret_val.append(' ')
            ret_val.append(x.argument)
        return ''.join(ret_val)

    def visit_short_and_long_option(self, x: arg.ShortAndLongOption) -> str:
        ret_val = []
        if x.short_name:
            ret_val.append(short_and_long_option_syntax.short_syntax(x.name.short))
        if x.long_name:
            if ret_val:
                ret_val.append(', ')
            ret_val.append(short_and_long_option_syntax.long_syntax(x.name.long))
        if x.argument:
            ret_val.append(' ')
            ret_val.append(x.argument)
        return ''.join(ret_val)


_ARGUMENT_IN_ARGUMENT_DESCRIPTION_RENDERER = ArgumentInArgumentDescriptionRenderer()


def render_argument(argument: arg.Argument) -> str:
    return _ARGUMENT_IN_ARGUMENT_DESCRIPTION_RENDERER.visit(argument)
