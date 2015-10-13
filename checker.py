import re
import os
import shutil
import sys

__author__ = 'Alex H Wagner'


class Checker:

    def __init__(self, f_name, max_length=80, tab_spaces=4):
        self.filename = self.new_file = None
        self.set_file(f_name)
        self.line = None
        self.max_length = max_length
        self.tab_spaces = tab_spaces

    def set_file(self, f_name, mod_string='new'):
        self.filename = f_name
        (name, extension) = f_name.rsplit('.', maxsplit=1)
        self.new_file = '.'.join((name, mod_string, extension))

    def check_file(self, replace=False):
        paren_spaces = list()
        with open(self.filename, 'r') as f, open(self.new_file, 'w') as out:
            block = 0
            for i, line in enumerate(f, start=1):
                line = line.rstrip()
                if line.strip().startswith('#'):
                    out.write(line + "\n")
                    self.check_length(i, line)
                    continue
                try:
                    (line, comment) = line.split('#')
                except ValueError:
                    comment = ''
                up_count = line.count('{')
                down_count = line.count('}')
                block -= down_count
                line = re.sub(r'\t', ' ' * self.tab_spaces, line)
                if paren_spaces:
                    adjust = paren_spaces[-1]
                else:
                    adjust = self.tab_spaces * block
                m = re.match(' ' * adjust + r'\S', line)
                if m is None and len(line) > 0:
                    m = re.match(r'( )+', line)
                    if m:
                        counted_spaces = len(m.groups(1))
                    else:
                        counted_spaces = 0
                    err_str = '{0}: {1} spaces preceding line {2}. Expected {3}.'.format(
                        self.filename, counted_spaces, i, adjust)
                    line = ' ' * adjust + line.strip()
                    print(err_str)
                for j, char in enumerate(line, start=1):
                    if char == '(':
                        paren_spaces.append(j)
                    elif char == ')':
                        paren_spaces.pop()
                if comment:
                    line = '#'.join((line, comment))
                self.check_length(i, line)
                block += up_count
                out.write(line + "\n")
            if block != 0:
                raise ValueError("Wrong block count! Got {0}, expected 0.".format(block))
        if replace:
            os.remove(self.filename)
            shutil.copy(self.new_file, self.filename)
            os.remove(self.new_file)

    def check_length(self, i, line):
        if len(line) > self.max_length:
            err_str = '{0}: Line {1} ({2} characters) exceeds max length of {3}'.format(
                self.filename, i, len(line), self.max_length)
            print(err_str)


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        c = Checker(filename)
        c.check_file(replace=True)
