import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
from PIL import Image
import sys


window = None
tex_pasto = None
tex_pared = None
tex_techo = None

cam_x = 0.0
cam_y = 4.0
cam_z = 10.0
fov = 60.0  

def load_texture(path):
    img = Image.open(path).convert("RGB")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.tobytes()

    tex_id = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glBindTexture(GL_TEXTURE_2D, tex_id)


    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Envoltura (tiling)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.width, img.height, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)

    
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


def init():
    global tex_pasto, tex_pared, tex_techo

    glClearColor(0.5, 0.8, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

    tex_pasto = load_texture("formas_glut/1601.m10.i311.n029.S.c10.164511620 Seamless green grass vector pattern.jpg")
    tex_pared = load_texture("formas_glut/brick-wall-1916752_1280.jpg")
    tex_techo = load_texture("formas_glut/6682133.jpg")

def procesar_teclado(window):
    """Escanea las teclas presionadas para mover la cámara y hacer zoom"""
    global cam_x, cam_y, cam_z, fov
    velocidad = 0.1
    vel_zoom = 1.0

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cam_z -= velocidad
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cam_z += velocidad
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        cam_x -= velocidad
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        cam_x += velocidad

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cam_y += velocidad
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cam_y -= velocidad

    if glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS:
        fov -= vel_zoom
        if fov < 10.0: fov = 10.0  
    if glfw.get_key(window, glfw.KEY_X) == glfw.PRESS:
        fov += vel_zoom
        if fov > 120.0: fov = 120.0 


def draw_ground():
    glBindTexture(GL_TEXTURE_2D, tex_pasto)

    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)

    scale = 5

    glTexCoord2f(0, 0);           glVertex3f(-10, 0, 10)
    glTexCoord2f(scale, 0);       glVertex3f( 10, 0, 10)
    glTexCoord2f(scale, scale);   glVertex3f( 10, 0,-10)
    glTexCoord2f(0, scale);       glVertex3f(-10, 0,-10)

    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)


def draw_cube():
    glBindTexture(GL_TEXTURE_2D, tex_pared)

    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)

    # Frente
    glTexCoord2f(0, 0); glVertex3f(-1, 0, 1)
    glTexCoord2f(1, 0); glVertex3f( 1, 0, 1)
    glTexCoord2f(1, 1); glVertex3f( 1, 1, 1)
    glTexCoord2f(0, 1); glVertex3f(-1, 1, 1)

    # Atrás
    glTexCoord2f(0, 0); glVertex3f(-1, 0,-1)
    glTexCoord2f(1, 0); glVertex3f( 1, 0,-1)
    glTexCoord2f(1, 1); glVertex3f( 1, 1,-1)
    glTexCoord2f(0, 1); glVertex3f(-1, 1,-1)

    # Izquierda
    glTexCoord2f(0, 0); glVertex3f(-1, 0,-1)
    glTexCoord2f(1, 0); glVertex3f(-1, 0, 1)
    glTexCoord2f(1, 1); glVertex3f(-1, 1, 1)
    glTexCoord2f(0, 1); glVertex3f(-1, 1,-1)

    # Derecha
    glTexCoord2f(0, 0); glVertex3f( 1, 0,-1)
    glTexCoord2f(1, 0); glVertex3f( 1, 0, 1)
    glTexCoord2f(1, 1); glVertex3f( 1, 1, 1)
    glTexCoord2f(0, 1); glVertex3f( 1, 1,-1)

    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)


def draw_details():
    """Dibuja puerta y ventanas desactivando texturas temporalmente"""
    glDisable(GL_TEXTURE_2D) # Apagar texturas para colores sólidos
    
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.15, 0.05)
    glVertex3f(0.2, 0, 1.01)
    glVertex3f(0.7, 0, 1.01)
    glVertex3f(0.7, 1.0, 1.01)
    glVertex3f(0.2, 1.0, 1.01)

    glColor3f(0.6, 0.8, 0.9)
    glVertex3f(-0.7, 0.4, 1.01)
    glVertex3f(-0.2, 0.4, 1.01)
    glVertex3f(-0.2, 0.9, 1.01)
    glVertex3f(-0.7, 0.9, 1.01)
    glEnd()
    
    glLineWidth(3)
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_LINES)
    glVertex3f(-0.45, 0.4, 1.02); glVertex3f(-0.45, 0.9, 1.02)
    glVertex3f(-0.7, 0.65, 1.02); glVertex3f(-0.2, 0.65, 1.02)
    glEnd()

    glEnable(GL_TEXTURE_2D)


def draw_roof():
    glBindTexture(GL_TEXTURE_2D, tex_techo)

    glBegin(GL_TRIANGLES)
    glColor3f(1, 1, 1)

    # Frente
    glTexCoord2f(0, 0);    glVertex3f(-1, 1, 1)
    glTexCoord2f(1, 0);    glVertex3f( 1, 1, 1)
    glTexCoord2f(0.5, 1);  glVertex3f( 0, 2, 0)

    # Atrás
    glTexCoord2f(0, 0);    glVertex3f( 1, 1,-1)
    glTexCoord2f(1, 0);    glVertex3f(-1, 1,-1)
    glTexCoord2f(0.5, 1);  glVertex3f( 0, 2, 0)

    # Izquierda
    glTexCoord2f(0, 0);    glVertex3f(-1, 1,-1)
    glTexCoord2f(1, 0);    glVertex3f(-1, 1, 1)
    glTexCoord2f(0.5, 1);  glVertex3f( 0, 2, 0)

    # Derecha
    glTexCoord2f(0, 0);    glVertex3f( 1, 1, 1)
    glTexCoord2f(1, 0);    glVertex3f( 1, 1,-1)
    glTexCoord2f(0.5, 1);  glVertex3f( 0, 2, 0)

    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)


def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, 800 / 600, 0.1, 100.0)
    

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(cam_x, cam_y, cam_z, 
              cam_x, 1, cam_z - 5, 
              0, 1, 0)

    draw_ground()
    draw_cube()
    draw_details() # Llamamos a la puerta y ventanas aquí
    draw_roof()

    glfw.swap_buffers(window)


def main():
    global window

    if not glfw.init():
        sys.exit()

    window = glfw.create_window(800, 600, "Casa Texturizada Completa", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)
    glViewport(0, 0, 800, 600)

    init()

    # Bucle Principal
    while not glfw.window_should_close(window):
        procesar_teclado(window) 
        draw_scene()
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()