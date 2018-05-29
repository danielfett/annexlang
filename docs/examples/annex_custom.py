# This file can be used to define custom protocol objects.

from annexlang.language import Action

class MyCustomAction(Action):
    yaml_tag = '!my-custom-action'

    def tikz(self):
        self.label = "MY CUSTOM ACTION"
        pos = self.get_pos(self.party.column, self.line)
        text = self.tex_id + self.contour(self.label)
        out = fr"""\node[annex_action,name={self.node_name}{self.tikz_extra_style}] at ({pos}) {{{text}}};"""
        return out

    @property
    def height(self):
        return "3ex", "center"
