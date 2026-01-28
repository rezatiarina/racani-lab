def load_vertices(file):
    vertex_list = []
    xyz = []
    for i in range(3):
        xyz.append([])
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip().split()
            if line[0] == 'v':
                vertex_list.append([float(line[1]), float(line[2]), float(line[3])])
                for i in range(3):
                    xyz[i].append(float(line[i + 1]))
    return vertex_list, xyz


def load_polygons(file):
    polygon_list = []
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip().split()
            if line[0] == 'f':
                polygon_list.append([int(line[1]), int(line[2]), int(line[3])])
    return polygon_list