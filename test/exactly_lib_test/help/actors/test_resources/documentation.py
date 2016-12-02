from exactly_lib.help.actors.contents_structure import ActorDocumentation


class ActorTestImpl(ActorDocumentation):
    def __init__(self, singular_name: str):
        super().__init__(singular_name)

    def single_line_description_str(self) -> str:
        return 'single line description str'

    def act_phase_contents(self) -> list:
        return []

    def act_phase_contents_syntax(self) -> list:
        return []
