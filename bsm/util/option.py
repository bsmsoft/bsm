def _parse_chunk(chunk):
    pos = chunk.find('=')
    if pos == -1:
        return {chunk.strip(): 'true'}
    key = chunk[:pos].strip()
    value = chunk[pos+1:].strip()
    return {key: value}

# Do NOT use this, because "," may be in value
def parse_line(line):
    chunks = line.split(',')
    result = {}
    for chunk in chunks:
        result.update(_parse_chunk(chunk))
    return result

def parse_lines(lines):
    result = {}
    for line in lines:
        result.update(parse_line(line))
    return result
