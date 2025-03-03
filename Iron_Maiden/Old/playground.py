def generate():
    playground = []
    for line in range(7):
        playground += ["0" * 7]

    return playground

def show(playground):
    for line in playground:
        print(line)
    print("")


def write(playground, x, y, symbol):
    playground = playground.copy()
    line = playground[y]
    playground[y] = line[:x] + symbol + line[x + 1:]

    return playground

def read(playground, x, y):
    line = playground[y]

    return line[x]