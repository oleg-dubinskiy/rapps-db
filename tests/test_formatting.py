'''
PROJECT:     ReactOS rapps-db validator
LICENSE:     MIT (https://spdx.org/licenses/MIT)
PURPOSE:     Validate validness of all rapps-db files
COPYRIGHT:   Copyright 2020 Mark Jansen (mark.jansen@reactos.org)
'''
import os

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))

ALL_KEYS = [
    b'Name',
    b'Version',
    b'License',
    b'Description',
    b'Size',
    b'Category',
    b'URLSite',
    b'URLDownload',
    b'SHA1',
    b'CDPath',
    b'SizeBytes',
    b'SizeInBytes',
    b'Icon',
    b'Screenshot1',
    b'LicenseInfo',
    b'Languages',
]


class RappsLine:
    def __init__(self, file, text):
        self._file = file
        self._text = text
        self.section = self.key = self.value = None
        parts = [part.strip() for part in text.split(b'=', 1)]
        first = parts[0]
        if first.startswith(b';') or (len(parts) == 1 and len(first) == 0):
            # comment or empty line
            pass
        elif len(parts) == 1:
            # Section header
            assert first.startswith(b'[') and first.endswith(b']'), self
            self.section = first[1:-1]
        else:
            # key = value
            assert len(parts) == 2, self
            self.key = parts[0]
            self.value = parts[1]

    def endswith(self, expr):
        return self._text.endswith(expr)

    def __repr__(self):
        return '{} -> {}'.format(self._file.filename, self._text)


class RappsFile:
    def __init__(self, fullname):
        self.path = fullname
        self.filename = os.path.basename(fullname)
        self._lines = None

    def lines(self):
        if not self._lines:
            with open(self.path, 'rb') as f:
                self._lines = [RappsLine(self, line) for line in f.readlines()]
            assert self._lines
        return self._lines


def walk_dir(basepath):
    for filename in os.listdir(basepath):
        if filename.endswith('.txt'):
            yield RappsFile(filename)


ALL_FILES = list(walk_dir(REPO_ROOT))


# Validate that all lines end with \r\n (including the last line!)
def test_lineendings():
    for file in ALL_FILES:
        for line in file.lines():
            assert line.endswith(b'\r\n'), line


# Validate that only known keys are used
def test_valid_keys():
    for file in ALL_FILES:
        for line in file.lines():
            if line.key:
                assert line.key in ALL_KEYS, line


if __name__ == '__main__':
    test_lineendings()
    test_valid_keys()
