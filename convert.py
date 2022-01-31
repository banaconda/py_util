import re

unit_map = {
    'K': 2 ** 10,
    'M': 2 ** 20,
    'G': 2 ** 30,
    'T': 2 ** 40,
    'P': 2 ** 50,
}
unit_set = ''.join(unit_map.keys())

def convert_human_byte_to_byte(human_byte):
    result = re.match(f'[1-9][0-9]*[{unit_set}]*', human_byte)
    if result == None or result.start() != 0:
        return None
    size = result.group()
    result = re.match('[1-9][0-9]*', size)
    quantity = int(result.group())
    if result.end() < len(size):
        unit = size[result.end():]
        return quantity * unit_map[unit]
    return quantity

def convert_byte_to_human_byte(byte):
    if byte < 1024:
        return str(byte)

    for unit, value in unit_map.items():
        quatity = byte // value
        if quatity < 1024:
            return str(quatity) + unit
    return None

def snake_to_pascal(string):
    capital = True
    result = ""
    for c in string:
        if c == '_':
            capital = True
            continue

        if capital == True:
            capital = False
            c = c.upper()

        result += c

    return result

def snake_to_camel(string):
    capital = False
    result = ""
    for c in string:
        if c == '_':
            capital = True
            continue

        if capital == True:
            capital = False
            c = c.upper()

        result += c

    return result

def camel_to_pascal(string):
    result = string[0].upper()
    for c in string[1:]:
        result += c
    return result

def pascal_to_camel(string):
    result = string[0].lower()
    for c in string[1:]:
        result += c
    return result

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')
def camel_to_snake(s):
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()