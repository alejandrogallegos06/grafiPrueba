import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import cv2
import numpy as np

# --- CONFIGURACIÓN Y CONSTANTES ---
CAM_DISTANCE = 5.0
ANGLE_SPEED = 1.0
USE_LIGHTING = True

# Estado global
angle = 0.0
modo = 1  # 1: Obj Rota, 2: Cam Orbita (T+R), 3: gluLookAt

def save_screenshot(filename):
    width, height = 800, 600
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_BGR, GL_UNSIGNED_BYTE)
    image = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
    image = cv2.flip(image, 0)
    cv2.imwrite(f"Orbita_Dual/{filename}", image)
    print(f"Captura guardada: Orbita_Dual/{filename}")

def draw_scene():
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(2,0,0) # X
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,2,0) # Y
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,2) # Z
    glEnd()
    if USE_LIGHTING: glEnable(GL_LIGHTING)
    glColor3f(0.7, 0.7, 0.7)
    quad = gluNewQuadric()
    gluSphere(quad, 1.0, 32, 32)
    gluDeleteQuadric(quad)

def setup_lighting(fixed_to_cam=True):
    if not USE_LIGHTING:
        glDisable(GL_LIGHTING)
        return
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    if fixed_to_cam:
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    else:
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 5.0, 0.0, 1.0])

def render():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 800/600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if modo == 1:
        # Misión 1: Objeto Rota
        setup_lighting(fixed_to_cam=True)
        glTranslatef(0, 0, -CAM_DISTANCE)
        glRotatef(angle, 0, 1, 0)
    elif modo == 2:
        # Misión 1: Cámara Orbita (Inversa)
        glRotatef(-angle, 0, 1, 0)
        glTranslatef(0, 0, -CAM_DISTANCE)
        setup_lighting(fixed_to_cam=False)
    elif modo == 3:
        # Misión 2: gluLookAt
        rad = math.radians(angle)
        eyeX, eyeZ = 5 * math.cos(rad), 5 * math.sin(rad)
        gluLookAt(eyeX, 2.0, eyeZ, 0, 0, 0, 0, 1, 0)
        setup_lighting(fixed_to_cam=False)

    draw_scene()
    angle += ANGLE_SPEED

def key_callback(window, key, scancode, action, mods):
    global modo, USE_LIGHTING
    if action == glfw.PRESS:
        if key == glfw.KEY_1: modo = 1; print("Modo 1: Objeto Rota")
        elif key == glfw.KEY_2: modo = 2; print("Modo 2: Cámara Orbita")
        elif key == glfw.KEY_3: modo = 3; print("Modo 3: gluLookAt")
        elif key == glfw.KEY_L: USE_LIGHTING = not USE_LIGHTING
        elif key == glfw.KEY_S:
            names = {1:"m1_objeto_rota.png", 2:"m1_camara_orbita.png", 3:"m2_lookat_orbita.png"}
            save_screenshot(names.get(modo, "captura.png"))
        elif key in [glfw.KEY_ESCAPE, glfw.KEY_Q]: glfw.set_window_should_close(window, True)

def main():
    if not glfw.init(): return
    window = glfw.create_window(800, 600, "Orbita Dual Final", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)
    while not glfw.window_should_close(window):
        render()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()
