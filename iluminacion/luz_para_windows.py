import sys
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

rotation = 0.0
light_mode = 0  # 0=Básica, 1=Múltiple, 2=Direccional, 3=Spotlight, 4=Colores

def draw_two_spheres():
    """Dibuja las esferas formando el ojo"""
    glPushMatrix()
    
    # Esclerótica (blanco)
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0.56, 0, 0)
    glutSolidSphere(0.6, 40, 40)
    glPopMatrix()
    
    # Iris (azul grisáceo)
    glColor3f(0.84, 0.85, 0.92)
    glPushMatrix()
    glTranslatef(0.49, 0, 0)
    glutSolidSphere(0.55, 35, 35)
    glPopMatrix()
    
    # Parte rosada del iris
    glColor3f(0.85, 0.67, 0.65)
    glPushMatrix()
    glTranslatef(0.7, 0, 0)
    glutSolidSphere(0.54, 35, 35)
    glPopMatrix()

    # Pupila (negro)
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.3, 0, 0)
    glutSolidSphere(0.4, 30, 30)
    glPopMatrix()
    
    glPopMatrix()

# --- CONFIGURACIONES DE ILUMINACIÓN ---

def setup_lighting_basic():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    glDisable(GL_LIGHT2)
    
    # LUZ PUNTUAL (Point Light): Al terminar en 1.0, OpenGL sabe que es una coordenada (x, y, z) exacta.
    # Funciona como un foco o bombilla que irradia luz en todas direcciones desde ese punto.
    light_position = [3.0, 2.0, 3.0, 1.0]
    
    # LUZ DIFUSA (Diffuse Light): Es la iluminación principal. Da el color que golpea directamente al objeto,
    # revelando su volumen y creando el lado iluminado frente al lado en sombra.
    light_diffuse = [1.0, 1.0, 1.0, 1.0] 
    
    # LUZ AMBIENTE (Ambient Light): Es una luz base que llena toda la escena.
    # No viene de ningún punto específico; ilumina todo por igual y evita que las sombras sean negras al 100%.
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position) 
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

def setup_lighting_multiple():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0); glEnable(GL_LIGHT1); glEnable(GL_LIGHT2)
    
    # Aquí tenemos un sistema de 3 LUCES PUNTUALES ubicadas en diferentes partes de la escena.
    
    # Luz 0: Luz principal (Key Light) - Blanca y fuerte.
    glLightfv(GL_LIGHT0, GL_POSITION, [3.0, 4.0, 3.0, 1.0])  # Termina en 1.0 (Luz Puntual)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])   # Luz Difusa (Blanca)
    
    # Luz 1: Luz de relleno (Fill Light) - Tono azulado suave desde la izquierda/atrás.
    glLightfv(GL_LIGHT1, GL_POSITION, [-2.0, 1.0, -3.0, 1.0]) # Termina en 1.0 (Luz Puntual)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.4, 0.6, 1.0])    # Luz Difusa (Azul/Grisácea)
    
    # Luz 2: Luz de rebote/cálida - Tono naranja desde abajo a la derecha.
    glLightfv(GL_LIGHT2, GL_POSITION, [4.0, 0.0, 1.0, 1.0])   # Termina en 1.0 (Luz Puntual)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.9, 0.6, 0.3, 1.0])    # Luz Difusa (Naranja)

def setup_lighting_directional():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glDisable(GL_LIGHT1); glDisable(GL_LIGHT2)
    
    # LUZ DIRECCIONAL (Directional Light): Al terminar en 0.0, OpenGL ignora la posición.
    # Trata el vector como una *dirección*. Finge estar a una distancia infinita (como el Sol).
    # Todos los rayos de luz llegan paralelos al objeto, iluminando toda la cara frontal por igual.
    light_direction = [1.0, -1.0, 1.0, 0.0] 
    glLightfv(GL_LIGHT0, GL_POSITION, light_direction)
    
    # Luz difusa con un tono ligeramente cálido (luz solar)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.95, 0.8, 1.0])

def setup_lighting_spotlight():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # LUZ TIPO REFLECTOR / LINTERNA (Spotlight)
    # 1. Primero se define como una Luz Puntual (w=1.0) para que tenga un punto de origen.
    light_position = [0.0, 4.0, 2.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    # 2. Se le asigna un vector hacia donde apunta la "linterna"
    spot_direction = [0.0, -1.0, -0.5] 
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spot_direction)
    
    # 3. Se recorta el área que ilumina. Solo emite luz en un CONO de 30 grados de apertura.
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 30.0) 
    
    # 4. Difuminado de los bordes del cono. Mayor número = centro más brillante y bordes más suaves.
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 20.0)

def setup_lighting_colored():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0); glEnable(GL_LIGHT1); glEnable(GL_LIGHT2)
    
    # LUCES PUNTUALES RGB: 3 bombillas posicionadas alrededor del objeto
    # emitiendo luz difusa de colores puros para ver cómo se mezclan en el material blanco.
    
    # Bombilla Izquierda (Rojo intenso)
    glLightfv(GL_LIGHT0, GL_POSITION, [-3.0, 1.0, 2.0, 1.0]) # Puntual
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.2, 0.2, 1.0])   # Difusa Roja
    
    # Bombilla Derecha (Verde intenso)
    glLightfv(GL_LIGHT1, GL_POSITION, [3.0, 1.0, 2.0, 1.0])  # Puntual
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.2, 1.0, 0.3, 1.0])   # Difusa Verde
    
    # Bombilla Superior (Azul intenso)
    glLightfv(GL_LIGHT2, GL_POSITION, [0.0, 3.0, 0.0, 1.0])  # Puntual
    glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.3, 0.3, 1.0, 1.0])   # Difusa Azul

def setup_lighting():
    glEnable(GL_DEPTH_TEST)
    
    # Permite que glColor3f interactúe con las luces (de lo contrario, los objetos pierden sus colores y se ven grises)
    glEnable(GL_COLOR_MATERIAL) 
    
    if light_mode == 0: setup_lighting_basic()
    elif light_mode == 1: setup_lighting_multiple()
    elif light_mode == 2: setup_lighting_directional()
    elif light_mode == 3: setup_lighting_spotlight()
    elif light_mode == 4: setup_lighting_colored()

def draw_light_indicators():
    """Dibuja pequeñas esferas de alambre donde están las luces"""
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)
    
    if light_mode == 0:
        glPushMatrix(); glTranslatef(3.0, 2.0, 3.0); glutWireSphere(0.1, 8, 8); glPopMatrix()
    elif light_mode == 1:
        glPushMatrix(); glTranslatef(3.0, 4.0, 3.0); glutWireSphere(0.1, 8, 8); glPopMatrix()
        glPushMatrix(); glTranslatef(-2.0, 1.0, -3.0); glutWireSphere(0.1, 8, 8); glPopMatrix()
    elif light_mode == 4:
        glColor3f(1, 0, 0); glPushMatrix(); glTranslatef(-3.0, 1.0, 2.0); glutWireSphere(0.1, 8, 8); glPopMatrix()
        glColor3f(0, 1, 0); glPushMatrix(); glTranslatef(3.0, 1.0, 2.0); glutWireSphere(0.1, 8, 8); glPopMatrix()
        glColor3f(0, 0, 1); glPushMatrix(); glTranslatef(0.0, 3.0, 0.0); glutWireSphere(0.1, 8, 8); glPopMatrix()
    
    glEnable(GL_LIGHTING)

def key_callback(window, key, scancode, action, mods):
    global light_mode
    if action == glfw.PRESS:
        if glfw.KEY_0 <= key <= glfw.KEY_4:
            light_mode = key - glfw.KEY_0
            print(f"Cambio a Modo de Luz: {light_mode}")
            setup_lighting()

def main():
    global rotation
    
    # 1. Inicializar GLFW primero
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Tipos de Iluminacion OpenGL", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    # 2. Inicializar GLUT después de crear la ventana
    glutInit(sys.argv)

    # Configuración inicial de OpenGL
    glClearColor(0.1, 0.1, 0.1, 1.0) # Fondo oscuro para ver mejor las luces
    setup_lighting()
    
    # LUZ ESPECULAR (Specular Light): Crea el "brillo" fuerte en superficies pulidas (como el reflejo en el ojo).
    # Este parámetro se asigna al material (GL_FRONT) para indicar cómo reacciona a los reflejos directos de las luces.
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 100.0) # Tamaño del brillo especular (100 = brillo pequeño y muy concentrado)

    print("Controles: Teclas 0, 1, 2, 3, 4 para cambiar modos de iluminacion.")

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800/600, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -5)
        
        rotation += 0.5
        glRotatef(rotation, 0, 1, 0)
        glRotatef(20, 1, 0, 0)
        
        draw_two_spheres()
        draw_light_indicators()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()