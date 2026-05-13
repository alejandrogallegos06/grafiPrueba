import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import cv2
import numpy as np

CAM_DISTANCE = 5.0
ORBIT_RADIUS = 3.0 
ANGLE_SPEED = 1.0
USE_LIGHTING = False

angle = 0.0
modo_orbita = 1  # 1: Objeto Rota, 2: Cámara Orbita, 3: Variante B

def save_screenshot(filename):
    """Captura el frame actual y lo guarda como PNG usando OpenCV"""
    print(f"Capturando: {filename}...")
    width, height = 800, 600
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_BGR, GL_UNSIGNED_BYTE)
    image = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
    image = cv2.flip(image, 0)
    cv2.imwrite(f"Orbita_Dual/{filename}", image)
    print(f"Guardado exitoso en Orbita_Dual/{filename}")

def draw_sphere(radius, slices, stacks):
    """Primitiva de esfera usando GLU"""
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_scene():
    """Dibuja el objeto de prueba (esfera + ejes cartesianos)"""
    # Ejes para referencia espacial
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0); glVertex3f(0, 0, 0); glVertex3f(2, 0, 0) # X Rojo
    glColor3f(0, 1, 0); glVertex3f(0, 0, 0); glVertex3f(0, 2, 0) # Y Verde
    glColor3f(0, 0, 1); glVertex3f(0, 0, 0); glVertex3f(0, 0, 2) # Z Azul
    glEnd()
    
    if USE_LIGHTING:
        glEnable(GL_LIGHTING)

    glColor3f(0.8, 0.8, 0.8)
    draw_sphere(1.0, 32, 32)

def setup_lighting():
    """Configuración de luces para Misión 3"""
    if not USE_LIGHTING:
        glDisable(GL_LIGHTING)
        return
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    light_pos = [1.0, 1.0, 1.0, 0.0] 
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])

def render_rotating_object(angle):
    """
    MODO 1: Espejo de la Matriz - El Objeto Rota
    Semántica: La cámara es fija, el objeto gira.
    Matemática: Translate(vista) -> Rotate(objeto)
    """
    glLoadIdentity()
    glTranslatef(0, 0, -CAM_DISTANCE)
    glRotatef(angle, 0, 1, 0)
    draw_scene()

def render_orbiting_camera(angle):
    """
    MODO 2: Espejo de la Matriz - La Cámara Orbita
    Semántica: El objeto es fijo en el origen, la cámara gira alrededor.
    Matemática: Rotate(-angle) -> Translate(vista)
    Nota: Se aplica la inversa de la transformación de cámara al mundo.
    """
    glLoadIdentity()
    glRotatef(-angle, 0, 1, 0)
    glTranslatef(0, 0, -CAM_DISTANCE)
    draw_scene()

def render_orbiting_camera_variant_b(angle):
    """
    MODO 3: Variante B
    Orden: Translate -> Rotate (Inverso al Modo 2)
    Efecto: El objeto describe un círculo manteniendo su orientación.
    """
    glLoadIdentity()
    glTranslatef(0, 0, -CAM_DISTANCE)
    glRotatef(-angle, 0, 1, 0)
    draw_scene()

def key_callback(window, key, scancode, action, mods):
    global modo_orbita, USE_LIGHTING
    if action == glfw.PRESS:
        if key == glfw.KEY_1:
            modo_orbita = 1
            print("Modo 1: Objeto Rotando Activo")
        elif key == glfw.KEY_2:
            modo_orbita = 2
            print("Modo 2: Cámara Orbitando Activa")
        elif key == glfw.KEY_3:
            modo_orbita = 3
            print("Modo 3: Variante B Activa")
        elif key == glfw.KEY_L:
            USE_LIGHTING = not USE_LIGHTING
            print(f"Iluminación: {'ON' if USE_LIGHTING else 'OFF'}")
        elif key == glfw.KEY_S:
            names = {1: "m1_objeto_rota.png", 2: "m1_camara_orbita.png", 3: "m1_variante_b.png"}
            save_screenshot(names.get(modo_orbita, "captura.png"))
        elif key in [glfw.KEY_ESCAPE, glfw.KEY_Q]:
            glfw.set_window_should_close(window, True)

def main():
    global angle
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Proyecto: Orbita Dual (GLFW)", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.07, 0.07, 0.07, 1.0)

    print("--- PROYECTO ORBITA DUAL ---")
    print("Controles:")
    print("1, 2, 3: Cambiar Modos de Visualización")
    print("L: Alternar Luces (Misión 3)")
    print("S: Tomar Captura de Pantalla")
    print("ESC/Q: Cerrar")

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configuración de Proyección
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800/600, 0.1, 100.0)
        
        # Configuración de Modelo y Vista
        glMatrixMode(GL_MODELVIEW)
        
        setup_lighting()
        
        if modo_orbita == 1:
            render_rotating_object(angle)
        elif modo_orbita == 2:
            render_orbiting_camera(angle)
        else:
            render_orbiting_camera_variant_b(angle)
            
        angle += ANGLE_SPEED
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
