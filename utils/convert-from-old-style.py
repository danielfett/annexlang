#!/usr/bin/python3

import sys

if len(sys.argv) != 2:
    sys.exit("Usage: %s INPUTFILE" % sys.argv[0])

def get_content(line):
    return [x.strip() for x in line.split(':', 1)]

    
class Block():
    def __init__(self):
        self.type = None

    def add(self, key, value):
        key = key.lower()
        if key not in ['type', 'id'] and not self.type:
            self.type = key
        elif key == 'type' and value.startswith('http'):
            self.method = value.split('-')[-1]
        setattr(self, key, value)

    def addFor(self, what):
        if self.type != 'http-response':
            raise Exception("For keyword only allowed for http-response")
        setattr(self, 'from', getattr(what, 'to'))
        setattr(self, 'to', getattr(what, 'from'))
        setattr(self, 'for', what)

    def finish(self, previous):
        # set from and to automatically
        if self.type == 'http-response':
            if not hasattr(self, 'from') and not hasattr(self, 'to'):
                self.addFor(previous)
        if (self.type.startswith('http-') or self.type == 'postmessage') and (not hasattr(self, 'from') or not hasattr(self, 'to')):
            raise Exception("From or To omitted for Block of type %s" % self.type)
        if self.type.startswith('http') and self.method != 'response' and not hasattr(self, 'path'):
            raise Exception("HTTP request without path.")

    def getAboveBelow(self):
        above = None
        below = None
        if self.type.startswith('http'):
            if self.method == 'response':
                above = 'Response'
                below = texify(self.contents) if hasattr(self, 'contents') else ''
            elif self.method == 'roundtrip':
                above = 'GET ' + texify(self.path)
                below = ''
            else:
                above = '%s %s' % (self.method.upper(), texify(self.path))
                below = texify(self.contents) if hasattr(self, 'contents') else ''
        elif self.type == 'postmessage':
            above = texify(self.contents)
            below = texify(self.comment) if hasattr(self, 'comment') else ''
        elif self.type == 'open':
            above = '\\textbf{open}'
            below = texify(self.contents) if hasattr(self, 'contents') else ''
        elif self.type == 'create':
            above = '\\textbf{create}'
            below = texify(self.contents) if hasattr(self, 'contents') else ''

        above = "\\textbf{%s}" % above
        if above != None and hasattr(self, 'id'):
            above = "\protostep{%s} %s" % (self.id, above)
        return (above, below)
    
    def getLabel(self):
        above, below = self.getAboveBelow()
        if above != None or below != None:
            label = 'to node [above=2.6pt, anchor=base]{%(above)s} node [below=-8pt, text width=0.5\\linewidth, anchor=base]{\\begin{center} %(below)s\\end{center}}' % {'above': above, 'below': below}
        else:
            label = '--'
            
        return label

    def getDraw(self):
        draw = ''
        if self.type == 'postmessage':
            draw = ',color=red,dashed'
        elif self.type.startswith('http-xhr') \
                or (self.type == 'http-response' \
                        and hasattr(self, 'for') \
                        and getattr(self, 'for').type.startswith('http-xhr')):
            draw = ',color=blue,>=latex'
        elif self.type in ['open','create','close']:
            draw = ',snake=snake,segment amplitude=0.2ex'
        return draw

    def getContent(self, i, grid_started):
        out = ''
        if self.type == 'comment':
            out += '\\path (%s-%d) to node [above=-1ex,midway,text width=\\linewidth]{\\begin{center}\emph{\\scriptsize %s}\\end{center}} (%s-%d);\n' % (parties[0], i, texify(self.comment), parties[-1], i)
            return out
        elif self.type == 'event':
            out += '\\path (%s-%d) to node [above=-1ex,midway,text width=\\textwidth]{\\color{OliveGreen}\\begin{center}\\textbf{\\scriptsize %s}\\end{center}} (%s-%d);\n' % (parties[0], i, texify(self.event), parties[-1], i)
            return out
        elif self.type == 'action':
            text = ("\protostep{%s} " % self.id if hasattr(self, 'id') else '') + self.contents
            out += '\\node[draw,anchor=base,fill=white,rounded corners] at (%s-%d) {%s};' % (getattr(self, 'from'), i, text)
            return out
        elif self.type == 'close':
            # no need to draw anything here.
            return ''
        elif self.type == 'action':
            return ''
        elif self.type == 'separator':
            left = "(%s-%d.west)" % (parties[0], i)
            right = "(%s-%d.east)" % (parties[-1], i)
            out += "\\draw [dashed] %s -- %s;\n" % (left, right)
            if hasattr(self, 'comment'):
                out += '\\node[draw=none,anchor=northwest,below=2ex,right=1ex] at %s {%s};\n' % (left, texify(self.comment))
            return out


        draw = self.getDraw()

        arrow_from = "%s-%d" % (getattr(self, 'from'), i)
        arrow_to = "%s-%d" % (self.to, i)
        if self.type in ['open','create']:
            arrow_to = "%s-start-%d" % (self.to, grid_started.count(self.to))
            grid_started.append(self.to)

        label = self.getLabel()

        out += "\\draw[->%s] (%s) %s (%s); \n" % (draw, arrow_from, label, arrow_to)
        if self.type == 'http-roundtrip':
            out += "\\draw[->%s] ([yshift=-3pt]%s.west) to ([yshift=-3pt]%s.east); \n" % (draw, arrow_to, arrow_from)
        return out

    def getCalcBlockHeight(self, i, rowsep):
        above, below = self.getAboveBelow()
        var = self.getCalcBlockHeightVar(i)
        out = r'''\newlength''' + var + "\n"
        out += r'''\settototalheight%s{\parbox{0.4\linewidth}{%s}}''' % (var, below) + "\n"
        out += r'''\setlength%s{\dimexpr %s - %s/4}''' % (var, var, rowsep) + "\n"
        return out

    def getCalcBlockHeightVar(self, i):
        return r'''\blockExtraHeight%s%s''' % (replaceNumbers(str(i)), myuuid)

    
groups = {}
parties = []
blocks = []
blocks_by_id = {}
initial = []
options = []
aliases = {}

block = Block()
for line in open(sys.argv[1], 'r'):
    line = line.strip()

    if line.startswith(';'):
        continue

    if len(line) == 0:
        if block and block.type:
            block.finish(blocks[-1] if len(blocks) else None)
            blocks.append(block)
            if hasattr(block, 'id'):
                blocks_by_id[block.id] = block
            block = Block()
        continue

    if line.startswith('---'):
        block.add('Type', 'separator')
        continue

    key, value = get_content(line)
    if key == 'Groups':
        groups = dict([(x, []) for x in value.split(' ')])

    elif key.startswith('Parties-'):
        group = key.split('-')[1]
        if group not in groups.keys():
            raise Exception("Not a group: %s" % group)
        p = value.split(' ')
        groups[group] = p
        parties.extend(p)
        initial.extend(p)

    elif key == 'Initial':
        initial = value.split(' ')
        for p in initial:
            if p not in parties:
                parties.append(p)

    elif key == 'From' or key == 'To':
        if value not in parties:
            raise Exception("%s (%s) not a party." % (key, value))
        block.add(key, value)

    elif key == 'For':
        if not value in blocks_by_id:
            raise Exception("Unknown block id: %s" % value)
        block.addFor(blocks_by_id[value])

    elif key == 'Options':
        options += value.split(' ')

    elif key == 'Alias':
        aliases[value.split(' ')[0]] = ' '.join(value.split(' ')[1:])

    else:
        block.add(key, value)


print ("options:")
print ('  enumerate: "\\setcounter{protostep}{%d}\\protostep{%s} ')
print ('  styles:')
print ('    - !style-default {}')
print ('protocol:')
print ('  !Protocol')
print ('  parties:')

for p in parties:
    pname = p.lower()
    print (f'  - &{pname}')
    print ( '    !Party')
    print (f'    name: {p}')

print ('  steps:')
print ('# INITIALIZATION')
print ('  - !Parallel')
print ('    steps:')

for p in parties:
    pname = p.lower()
    print (f'  - &{pname}')
    print ( '    !Party')
    print (f'    name: {p}')

print ('# PROTOCOL')

for b in blocks:
    if b.type == 'http-post' or b.type == 'http-get':
        method = b.type[5:].upper()
        
        print (f'  - !http-request &{getattr(b, "id", id(b))}')
        print (f'    src: {getattr(b, "from").lower()}')
        print (f'    dest: {getattr(b, "to").lower()}')
        print (f'    method: {method}')
        if hasattr(b, 'path'):
            print (f'    path: {b.path}')
        if hasattr(b, 'contents'):
            print (f'    parameters: {b.contents}')
            
        
        
        
