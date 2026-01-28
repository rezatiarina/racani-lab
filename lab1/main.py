import numpy as np
import pyglet
from pyglet.gl import *
import pyglet.gl as gl

from object import Object
from bspline import Bspline

window = pyglet.window.Window(1024, 768)

def bspline_approximation(bspline, t, i):
    T_3 = np.array([t ** 3, t ** 2, t, 1])
    B_i3 = 1 / 6 * np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]])
    R_i = np.array([bspline.vertices[i - 1], bspline.vertices[i], bspline.vertices[i + 1], bspline.vertices[i + 2]])
    return T_3 @ B_i3 @ R_i


def bspline_tangent(bspline, t, i):
    T_2 = np.array([t ** 2, t, 1])
    B_i3 = 0.5 * np.array([[-1, 3, -3, 1], [2, -4, 2, 0], [-1, 0, 1, 0]])
    R_i = np.array([bspline.vertices[i - 1], bspline.vertices[i], bspline.vertices[i + 1], bspline.vertices[i + 2]])
    return T_2 @ B_i3 @ R_i


def rotation(start, end):
    ax = np.cross(start, end)
    cos_theta = (start @ end) / (np.linalg.norm(start) * np.linalg.norm(end))
    theta = np.rad2deg(np.arccos(cos_theta))
    return ax, theta


def draw_curve(bspline):
    gl.glBegin(gl.GL_LINES)
    for i in range(len(bspline.vertices) - 2):
        for t in np.arange(0, 1, 0.05):
            p_i = bspline_approximation(bspline, t, i)
            dp_i = bspline_tangent(bspline, t, i) / bspline.scale
            p_i /= bspline.scale
            gl.glVertex3f(*p_i)
            p_i += dp_i
            gl.glVertex3f(*p_i)
    gl.glEnd()


def draw_object(object):
    gl.glBegin(gl.GL_TRIANGLES)
    for polygon in object.polygons:
        for vertex_id in polygon:
            gl.glVertex3f(*object.vertices[vertex_id - 1])
    gl.glEnd()


def update(x, dt):
    global t, i
    t += 0.1

    if t >= 1:
        t = 0
        i += 1

    if i >= (len(spline_object.vertices) - 2):
        i = 0


def set_parameters():
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glu.gluPerspective(50, 1, 0.1, 100)  # zoom, stretch, front, back
    gl.glu.gluLookAt(1, 1, 1, -1.5, -1.5, 0, 1, 1, 1)  # eye, center, up
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glLoadIdentity()


@window.event
def on_draw():
    set_parameters()

    bspline_vertex = bspline_approximation(spline_object, t, i)
    tangent = bspline_tangent(spline_object, t, i)
    axis, theta = rotation(np.array([0, 0, 1]), tangent)

    draw_curve(spline_object)

    bspline_vertex /= spline_object.scale
    gl.glTranslatef(*bspline_vertex)
    gl.glScalef(1 / 6, 1 / 6, 1 / 6)
    gl.glRotatef(theta, *axis)
    

    draw_object(o)


if __name__ == "__main__":
    t, i = 0, 0

    spline_object = Bspline('bspline.txt')
    o = Object('objects/bird.obj')

    pyglet.clock.schedule(update, 1)
    pyglet.app.run()
