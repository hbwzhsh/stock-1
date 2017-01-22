from functools import reduce

def char2num(s):
    return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]

def str2int(s):
    print(map(char2num, s))
    return reduce(lambda x, y: x * 10 + y, map(char2num, s))




if __name__ == '__main__':
    print(str2int('157'))