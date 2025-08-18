def split_string(string, number, symbol):
    parts = string.split(symbol)
    if len(parts) > number:
        return parts[number]
    else:
        return None


def get_coord(command, number):  # input: command, number(x=1, y=2, z=3)
    try:
        coord = split_string(command, number+5, " ")
        coord = split_string(coord, 0, ".")
        coord = int(coord)
        return coord
    except (ValueError, AttributeError):
        print("Error: Invalid coordinate")


def get_dimension(command):
    dimension = split_string(command, 2, " ")
    dimension = split_string(dimension, 1, ":")
    return dimension


def convert_coord(coord, dimension):
    if dimension == "overworld":
        if coord < 0:
            coord = coord * -1
            coord = coord / 8
            coord = coord * -1
            coord = int(coord)
            return coord
        else:
            coord = coord / 8
            coord = int(coord)
            return coord
    elif dimension == "nether":
        if coord < 0:
            coord = coord * -1
            coord = coord * 8
            coord = coord * -1
            coord = int(coord)
            return coord
        else:
            coord = coord * 8
            coord = int(coord)
            return coord


def convert_y(coord, dimension):
    if dimension == "overworld":
        if coord < 0:
            coord = 5
            return coord
        else:
            return coord
    elif dimension == "nether":
        if coord < -59:
            coord = -59
            return coord
        else:
            return coord


def convert_coords(command):
    dimension = get_dimension(command)
    error = get_coord(command, 1)
    if error is None:
        return
    x = get_coord(command, 1)
    y = get_coord(command, 2)
    z = get_coord(command, 3)
    x = convert_coord(x, dimension)
    y = convert_y(y, dimension)
    z = convert_coord(z, dimension)
    print(f"New Coords: {x}, {y}, {z}")