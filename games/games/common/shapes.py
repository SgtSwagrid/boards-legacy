import math

class Shape:

    def __init__(self, width, height, hexagonal=False):
        self.width = width
        self.height = height
        self.hexagonal = hexagonal

    def row_spacing(self, y):
        return 0

    def row_height(self, y):
        return 1

    def row_offset(self, y):
        return sum(self.row_spacing(yy) + self.row_height(yy)
            for yy in range(y + 1, self.height)) + self.row_spacing(y)

    def row_centre(self, y):
        return self.row_offset(y) + self.row_height(y) / 2

    def row_indent(self, y):
        return 0

    def tile_spacing(self, x, y):
        return 0

    def tile_width(self, x, y):
        return 1

    def tile_offset(self, x, y):
        return sum(self.tile_spacing(xx, y) + self.tile_width(xx, y)
            for xx in range(0, x)) + self.tile_spacing(x, y) + self.row_indent(y)

    def tile_centre(self, x, y):
        return self.tile_offset(x, y) + self.tile_width(x, y) / 2

    def row_size(self, y):
        return self.width

    def pattern_offset(self, x, y):
        return 0

    def in_bounds(self, x, y):
        return 0 <= y < self.height and 0 <= x < self.row_size(y)

    def display_width(self):
        return max(sum(self.tile_spacing(x, y) + self.tile_width(x, y)
            for x in range(0, self.row_size(y)))
            for y in range(0, self.height))

    def display_height(self):
        return sum(self.row_spacing(y) + self.row_height(y)
            for y in range(0, self.height))

class Rectangle(Shape):
    pass

class Table(Rectangle):

    def __init__(self, width, height, cell_width, cell_height):
        super().__init__(2 * width + 1, 2 * height + 1)
        self.cell_width = cell_width
        self.cell_height = cell_height

    def row_height(self, y):
        return 1 if y % 2 == 0 else self.cell_height

    def tile_width(self, x, y):
        return 1 if x % 2 == 0 else self.cell_width

class Hexagonal(Shape):

    def __init__(self, width, height, slanted=False):
        super().__init__(width, height, hexagonal=True)
        self.slanted = slanted

    def tile_width(self, x, y):
        return math.sqrt(3)

    def row_spacing(self, y):
        return 0.5

    def row_indent(self, y):
        if not self.slanted: return math.sqrt(3) / 2 if y % 2 == 0 else 0
        else: return (self.height - y - 1) * math.sqrt(3) / 2

    def pattern_offset(self, x, y):
        return -(y // 2) if self.slanted else 0