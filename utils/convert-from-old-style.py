#!/usr/bin/python3

import sys
import json

if len(sys.argv) != 2:
    sys.exit("Usage: %s INPUTFILE" % sys.argv[0])

    
def get_content(line):
    return [x.strip() for x in line.split(':', 1)]


def warn(text):
    sys.stderr.write(text + "\n")


def esc(text):
    return json.dumps(text)

    
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


print("options:")
print(r'  enumerate: "\\setcounter{protostep}{%d}\\protostep{%s}"')
print('  styles:')
print('    - !style-default {}')
print('protocol:')
print('  !Protocol')
print('  parties:')

for p in parties:
    pname = p.lower()
    print(f'  - &{pname}')
    print( '    !Party')
    print(f'    name: {p}')

print('  steps:')
print('# INITIALIZATION')
print('  - !Parallel')
print('    steps:')

for p in parties:
    pname = p.lower()
    print(f'    - !start-party')
    print(f'      party: *{pname}')

print('# PROTOCOL')

for b in blocks:
    if b.type == 'http-post' or b.type == 'http-get':
        method = b.type[5:].upper()
        
        print(f'  - !http-request &{getattr(b, "id", id(b))}')
        if hasattr(b, 'id'):
            print(f'    id: {b.id}')
        print(f'    src: *{getattr(b, "from").lower()}')
        print(f'    dest: *{getattr(b, "to").lower()}')
        print(f'    method: {method}')
        if hasattr(b, 'path'):
            print(f'    url: {esc(b.path)}')
        if hasattr(b, 'contents'):
            params = b.contents.replace(r'\\', '\\\\')
            print(f'    parameters: {esc(params)}')
    elif b.type == 'http-response':
        print(f'  - !http-response')
        if hasattr(b, 'id'):
            print(f'    id: {b.id}')
        print(f'    src: *{getattr(b, "from").lower()}')
        print(f'    dest: *{getattr(b, "to").lower()}')
        if hasattr(b, 'contents'):
            params = b.contents.replace(r'\\', '\\\\')
            print(f'    parameters: {esc(params)}')
        
    elif b.type == 'separator':
        print('  - -----------------------------')
        if hasattr(b, 'comment'):
            print( '  - !comment')
            print(f'    label: {esc(b.comment)}')

    elif b.type == 'comment':
        print( '  - !comment')
        print(f'    label: {esc(b.comment)}')
    else:
        warn(f"Skipped block of unknown type: {b.type}")
        print(f'# skipped block of type {b.type}.')
        
print('# FINISH UP')
print('  - !Parallel')
print('    steps:')

for p in parties:
    pname = p.lower()
    print(f'    - !end-party')
    print(f'      party: *{pname}')
