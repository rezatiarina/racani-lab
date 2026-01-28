from utils import *

class Object:
    vertices = []
    polygons = []

    def __init__(self, file):
        vertices, xyz = load_vertices(file)
        scale = max(max(xyz[0]) - min(xyz[0]), max(xyz[1]) - min(xyz[1]), max(xyz[2]) - min(xyz[2]))
        trans = []
        for i in xyz:
            trans.append((max(i) + min(i)) / 2)
        for v in vertices:
            for i in range(3):
                v[i] = (v[i] - trans[i]) / scale
        polygons = load_polygons(file)
        self.vertices = vertices
        self.polygons = polygons
