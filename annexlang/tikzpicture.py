class TikzPicture:

    options = {
        'colsep': '1.75ex',
        'rowsep': '4ex',
        'enumerate': '',
        'styles': [],
    }
    
    def __init__(self, annexfile):
        self.options.update(annexfile['options'])
        self.protocol = annexfile['protocol']
        self.protocol.init(self.options)

    def dump(self, f):
        self.dump_header(f)
        self.dump_matrix(f)
        self.dump_steps(f)
        self.dump_footer(f)

    def dump_header(self, f):
        style_string = ','.join(
            s.style.strip().strip(',') for s in self.options['styles']
        )
        f.write(r"""
        \begin{tikzpicture}[%s]
        \pgfdeclarelayer{arrows}
        \pgfdeclarelayer{groups}
        \pgfdeclarelayer{markers}
        \pgfsetlayers{groups,arrows,main,markers}
        """ % style_string)

    def dump_matrix(self, f):
        line_offset = 1 if self.protocol.has_groups else 0
        lines = self.count_lines()
        matrix_dummy_heights = [[] for i in range(lines + line_offset)]

        for step in self.protocol.walk():
            if hasattr(step, 'height'):
                matrix_dummy_heights[step.line].append(step.height)

        f.write(r"""
        %% MATRIX
        \matrix [column sep={%(colsep)s,between origins}, row sep=%(rowsep)s]
        {
        """ % self.options)

        # Draw the matrix (no real node contents yet)
        for line in range(len(matrix_dummy_heights)):
            for col in range(len(self.protocol.parties)):
                position = self.protocol.get_pos(col, line)
                f.write(r"""\node[annex_matrix_node,inner sep=0,outer sep=0](%s){};""" % (position,))
                
                extrawidths = []
                if hasattr(self.protocol.parties[col], 'extrawidth'):
                    extrawidths.append(self.protocol.parties[col].extrawidth + "/2")
                if col < (len(self.protocol.parties) - 1) and hasattr(self.protocol.parties[col+1], 'extrawidth'):
                    extrawidths.append(self.protocol.parties[col+1].extrawidth + "/2")
                if col < len(self.protocol.parties) - line_offset - 1:
                    f.write(r""" &""" )
                    if extrawidths:
                        f.write(f"[{'+'.join(extrawidths)}]")
                    
            if self.protocol.has_groups and line == 0:
                f.write(r"""\node[annex_group_title_placeholder,minimum height=2em]{};""")
            else:
                for height, anchor in matrix_dummy_heights[line]:
                    f.write(
                        fr"""\node[annex_matrix_dummy_height,minimum height={height},anchor={anchor}]{{}};""")
            f.write(r"""\\""")
            f.write("\n")

        f.write("};\n")

    def dump_steps(self, f):
        f.write("\n% MAIN LAYER\n\n")
        for step in self.protocol.walk():
            f.write(step.tikz_desc())
            f.write("\n");
            f.write(step.tikz())
            f.write("\n\n")
            
        f.write("\n% ARROWS LAYER\n\n")
        f.write(r"""\begin{pgfonlayer}{arrows}""")
        for step in self.protocol.walk():
            f.write(step.tikz_desc())
            f.write("\n");
            f.write(step.tikz_arrows())
            f.write("\n\n")
        f.write(r"""\end{pgfonlayer}""")

        if self.protocol.has_groups:
            f.write("\n% GROUPS LAYER\n\n")
            f.write(r"""\begin{pgfonlayer}{groups}""")
            for group in self.protocol.groups:
                f.write(group.tikz_desc())
                f.write("\n");
                f.write(group.tikz_groups(self.count_lines()))
                f.write("\n\n")
            f.write(r"""\end{pgfonlayer}""")

        f.write("\n% MARKERS LAYER\n\n")
        f.write(r"""\begin{pgfonlayer}{markers}""")
        for step in self.protocol.walk():
            f.write(step.tikz_desc())
            f.write("\n");
            f.write(step.tikz_markers())
            f.write("\n\n")
        f.write(r"""\end{pgfonlayer}""")

            
    def dump_footer(self, f):
        f.write(r"""
        \end{tikzpicture}
        """
        )

    def count_lines(self):
        return self.protocol.length
