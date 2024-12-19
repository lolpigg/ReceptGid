def a(str):
    m = str.split(' ')
    result = ''
    for s in m:
        result += chr(ord(s[0]) - 32) + s[1:]
        result += ' '
    return result[0:-1]


print(a('ass dsa'))