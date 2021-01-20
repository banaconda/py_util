import re
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