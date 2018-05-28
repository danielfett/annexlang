import yaml
from itertools import chain, count
import re

object_counter = 0


class cached_property(object):
    """
    Descriptor (non-data) for building an attribute on-demand on first use.
    """
    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)

        # Cache the value; hide ourselves.
        setattr(instance, self._attr_name, attr)

        return attr

    
class ProtocolObject(yaml.YAMLObject):
    def __new__(cls):
        global object_counter
        object_counter += 1

        obj = super().__new__(cls)
        obj.annexid = "{}-{}".format(cls.__name__, object_counter)

        return obj

    @staticmethod
    def get_pos(column, line):
        return f"pos-{column}-{line}"

    def __repr__(self):
        return f"""<{self.annexid}>"""

    
class ProtocolStep(ProtocolObject):
    node_name_counter = 0
    skip_number = 0
    _affecting_nodes = []
    
    def length(self):
        return 1

    def tikz_desc(self):
        return f"""% drawing node of type {self.__class__.__name__} in matrix line {self.line} with attributes: {self.__dict__!r}"""

    def tikz(self):
        return ""

    def tikz_arrows(self):
        return ""

    def tikz_markers(self):
        return ''

    def contour(self, text):
        if not text:
            return ''
        return r"\contour{white}{%s}" % text

    @cached_property
    def tikz_above(self):
        if not self.text_above and (not getattr(self, 'id_above', True) or not self.tex_id):
            return ""
        else:
            return r"""node [annex_arrow_text,above=2.6pt,anchor=base](%s){%s%s}""" % (
                self.create_affecting_node_name(parties=[]),
                self.tex_id if getattr(self, 'id_above', False) else '',
                self.contour(self.text_above)
            )

    @cached_property
    def tikz_below(self):
        if not self.text_below:
            return ""
        else:
            text = r"\contour{white}{%s}" % self.text_below
            return r"""node [annex_arrow_text,below=8pt,anchor=base](%s){%s}""" % (
                self.create_affecting_node_name(parties=[]),
                self.contour(self.text_below),
            )

    def create_affecting_node_name(self, parties=None):
        name = f"node{id(self)}n{self.node_name_counter}"
        self.node_name_counter += 1
        self._affecting_nodes = self._affecting_nodes + [name]

        if parties is None:
            parties = self.affected_parties
        for p in parties:
            p.add_affecting_node(name)
        return name

    def _init(self, protocol, counter, skip_number):
        self.protocol = protocol
        if not self.skip_number and not skip_number:
            self.counter = next(counter)
        

    @cached_property
    def tex_id(self):
        if not self.protocol.options['enumerate']:
            return ''
        if self.skip_number or not hasattr(self, 'counter'):
            return ''
        if hasattr(self, 'id'):
            t = self.id
        else:
            t = self.annexid
        return self.protocol.options['enumerate'] % (self.counter - 1, t)

    def set_line(self, line):
        self.line = line
        return 1

    def walk(self):
        yield self

    @property
    def affected_parties(self):
        yield self.party

    @property
    def affecting_nodes(self):
        return list(self._affecting_nodes)
        
    
class MultiStep(ProtocolStep):
    skip_number = True
    condense = False

    def draw(self):
        for d in self.steps:
            d.draw()

    def _init(self, protocol, counter, skip_number):
        if self.condense or skip_number:
            self.skip_number = False
            skip_numbers = True
        else:
            skip_numbers = False
        super()._init(protocol, counter, skip_number)
        for step in self.steps:
            step._init(protocol, counter, skip_numbers)

    def tikz_markers(self):
        if not self.condense:
            return ""

        if type(self.condense) is not str:
            self.condense = 'north west'

        fit_string = "fit=" + ''.join(f'({x})' for x in self.affecting_nodes)
        gid = f"group{id(self)}"
        out = fr"""\node[annex_condensed_box,{fit_string}]({gid}) {{}}; """
        out += fr"\node[] at ({gid}.{self.condense}) {{{self.tex_id}}};"
        return out
        
    def walk(self):
        yield self
        for step in self.steps:
            yield from step.walk()

    @property
    def affected_parties(self):
        for step in self.steps:
            yield from step.affected_parties

    @property
    def affecting_nodes(self):
        return chain(*(step.affecting_nodes for step in self.steps))
            

class Parallel(MultiStep):
    yaml_tag = '!Parallel'
    length_fun = max
    
    def set_line(self, line):
        length = 0
        for step in self.steps:
            length = max(step.set_line(line), length)
        self.line = line
        self.length = length
        return length
        

class Serial(MultiStep):
    yaml_tag = '!Serial'
    length_fun = sum
    
    def set_line(self, line):
        length = 0
        for step in self.steps:
            length += step.set_line(line + length)
        self.line = line
        self.length = length
        return length
    

class Protocol(Serial):
    yaml_tag = '!Protocol'
    extra_steps = []
    counter = 0

    def init(self, options):
        self.options = options
        # Set line numbers for each step
        self.set_line(1 if self.has_groups else 0)

        # Set column numbers for parties
        for p, column in zip(self.parties, range(len(self.parties))):
            p.column = column

        self._init(self, count(start=1, step=1), False)

        last_starts = {}
        for step in self.walk():
            if getattr(step, 'startsparty', False):
                if step.party in last_starts:
                    raise Exception("Started party that was already started: " + repr(step.party))
                last_starts[step.party] = step
            elif getattr(step, 'endsparty', False):
                if step.party not in last_starts:
                    raise Exception("Ended party that was not started: " + repr(step.party))
                last_starts[step.party].end = step
                del last_starts[step.party]
        if len(last_starts):
            raise Exception("Party was started but not ended: " + repr(last_starts))

    @property
    def has_groups(self):
        return hasattr(self, 'groups') and self.groups is not None
        

class Party(ProtocolObject):
    yaml_tag = '!Party'
    style = ''

    def add_affecting_node(self, node):
        if hasattr(self, '_affecting_nodes'):
            self._affecting_nodes.append(node)
        else:
            self._affecting_nodes = [node]

    @property
    def fit_string(self):
        if hasattr(self, '_affecting_nodes'):
            return self._affecting_nodes
        else:
            return ()


class Group(ProtocolObject):
    yaml_tag = '!Group'

    def tikz_desc(self):
        return f"""% drawing group {self.name}"""

    def tikz_groups(self, num_lines):
        columns_of_parties = {p.column:p for p in self.parties}
        first_column = min(columns_of_parties)
        first_party = columns_of_parties[first_column]
        last_column = max(columns_of_parties)
        last_party = columns_of_parties[last_column]
        fit_string = "fit=" + ''.join(f'({x})' for x in chain(
            [self.get_pos(first_column, 0)],
            first_party.fit_string,
            last_party.fit_string,
        ))
        gid = f"group{id(self)}"
        return fr"""\node[annex_group_box,{fit_string}]({gid}) {{}}; \node[anchor=base,above=of {gid}.north,above=-2.5ex,anchor=base] {{{self.name}}};"""


class Separator(ProtocolStep):
    skip_number = True

    def tikz_arrows(self):
        src = self.get_pos(self.protocol.parties[0].column, self.line)
        dest = self.get_pos(self.protocol.parties[-1].column, self.line)
        out = fr"""%% draw separator line
        \draw[annex_separator] ({src}) to  ({dest});"""
        out += super().tikz_arrows()
        return out

    @property
    def height(self):
        return "2ex", "center"

    @classmethod
    def constructor(cls, loader, node):
        return cls()


class Comment(ProtocolStep):
    yaml_tag = '!comment'
    id_above = False
    skip_number = True

    def tikz_arrows(self):
        src = self.get_pos(self.protocol.parties[0].column, self.line)
        dest = self.get_pos(self.protocol.parties[-1].column, self.line)
        self.text_below = self.label
        out = fr"""%% draw comment
        \draw[draw=none] ({src}) to {self.tikz_below} ({dest});"""
        out += super().tikz_arrows()
        return out
    
    @property
    def height(self):
        return "2ex", "center,yshift=-1ex"
    
    @property
    def affected_parties(self):
        yield from []

        
yaml.add_constructor('!separator', Separator.constructor)
pattern = re.compile(r'^-{3,}$')
yaml.add_implicit_resolver('!separator', pattern)
