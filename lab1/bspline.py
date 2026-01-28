from utils import *

class Bspline:
    vertices = []
    scale = None

    def __init__(self, file):
        bspline_vertices, xyz = load_vertices(file)
        self.vertices = bspline_vertices
        scale = max(max(xyz[0]) - min(xyz[0]), max(xyz[1]) - min(xyz[1]), max(xyz[2]) - min(xyz[2]))
        self.scale = scale
