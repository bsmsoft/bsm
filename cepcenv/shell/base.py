class Base(object):
    def comment(self, content):
        lines = content.split('\n')
        newlines = map(lambda x:'# '+x, lines)
        return '\n'.join(newlines)
