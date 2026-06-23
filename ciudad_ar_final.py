#!/usr/bin/env python3
"""
Proyecto Final: Realidad Aumentada - Ciudad 3D sobre Marcador ArUco
Integración de:
- Detección de marcadores ArUco (OpenCV)
- Visualización 3D (PyOpenGL + GLFW)
- Modelo de Ciudad 3D (Primitivas OpenGL)

Instrucciones:
1. Imprima el marcador 'marcador_aruco_id0.png'.
2. Ejecute el programa: python ciudad_ar_final.py
3. Apunte la cámara al marcador para ver la maqueta de la ciudad.

Controles:
- ESC / Q: Salir del programa.
- '+' / '=': Aumentar escala de la ciudad.
- '-': Reducir escala de la ciudad.
- 'R': Reiniciar escala original.
"""

import sys
import os
import math
import time
from pathlib import Path

import cv2
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# ---------------------------------------------------------------------------
# Configuración Global
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0
MARKER_LENGTH_M = 0.10  # Tamaño real del marcador en metros (10 cm)
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 0  # ID del marcador que buscamos
BASE_MODEL_SCALE = 0.008  # Escala base para que la ciudad quepa en el marcador
Z_NEAR, Z_FAR = 0.01, 100.0
WINDOW_TITLE = "Ciudad AR: ArUco + OpenGL"

# Variables dinámicas
model_scale = BASE_MODEL_SCALE
fountain_angle = 0.0
water_bob = 0.0
wing_angle = 0.0

# ---------------------------------------------------------------------------
# Funciones de Soporte de ArUco y OpenGL
# ---------------------------------------------------------------------------

def make_aruco_detector():
    """Configura el detector de ArUco según la versión de OpenCV."""
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    params = cv2.aruco.DetectorParameters()
    if hasattr(cv2.aruco, "ArucoDetector"):
        return cv2.aruco.ArucoDetector(dictionary, params), dictionary
    return None, dictionary

def detect_marker(gray, detector, dictionary):
    """Detecta el marcador específico en la imagen."""
    if detector is not None:
        corners, ids, _ = detector.detectMarkers(gray)
    else:
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
        
    if ids is None or len(ids) == 0:
        return None
        
    # Filtrar por el ID solicitado
    matches = np.where(ids.flatten() == MARKER_ID)[0]
    if len(matches) == 0:
        return None
        
    return corners[int(matches[0])]

def estimate_pose(corners, camera_matrix, dist_coeffs):
    """Calcula la rotación y traslación del marcador respecto a la cámara."""
    # Puntos del marcador en su propio sistema de coordenadas (centrado en 0,0,0)
    # Siguiendo el orden de ArUco: Top-Left, Top-Right, Bottom-Right, Bottom-Left
    s = MARKER_LENGTH_M / 2.0
    # X derecha, Y arriba -> Z hacia afuera (RHS)
    obj_pts = np.array([[-s, s, 0], [s, s, 0], [s, -s, 0], [-s, -s, 0]], dtype=np.float32)
    
    # Resolver PnP para obtener pose
    ok, rvec, tvec = cv2.solvePnP(obj_pts, corners, camera_matrix, dist_coeffs, 
                                 flags=cv2.SOLVEPNP_IPPE_SQUARE)
    return rvec, tvec

def get_projection_matrix(K, w, h, znear, zfar):
    """Convierte la matriz intrínseca de la cámara a una matriz de proyección OpenGL."""
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    P = np.zeros((4, 4), dtype=np.float32)
    P[0, 0] = 2.0 * fx / w
    P[1, 1] = 2.0 * fy / h
    P[0, 2] = (w - 2.0 * cx) / w
    P[1, 2] = (2.0 * cy - h) / h
    P[2, 2] = -(zfar + znear) / (zfar - znear)
    P[2, 3] = -1.0
    P[3, 2] = -2.0 * zfar * znear / (zfar - znear)
    return P

def get_modelview_matrix(rvec, tvec):
    """Convierte la pose detectada (rvec, tvec) a una matriz ModelView de OpenGL."""
    R, _ = cv2.Rodrigues(rvec)
    M = np.eye(4, dtype=np.float64)
    M[:3, :3] = R
    M[:3, 3] = tvec.flatten()
    
    # Ajuste de coordenadas: CV (Y abajo, Z adelante) -> GL (Y arriba, Z atrás)
    cv_to_gl = np.diag([1.0, -1.0, -1.0, 1.0])
    return (cv_to_gl @ M).T.astype(np.float32)

# ---------------------------------------------------------------------------
# Primitivas de Dibujo (Adaptadas de ciudad.py)
# ---------------------------------------------------------------------------

_quadric = None

def get_quadric():
    global _quadric
    if _quadric is None:
        _quadric = gluNewQuadric()
        gluQuadricDrawStyle(_quadric, GLU_FILL)
    return _quadric

def draw_cube(x, y, z, sx, sy, sz, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    glColor3f(*color)
    
    glBegin(GL_QUADS)
    # Cara frontal
    glNormal3f(0, 0, 1)
    glVertex3f(-0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
    # Cara trasera
    glNormal3f(0, 0, -1)
    glVertex3f(0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, -0.5)
    # Cara superior
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.5, 0.5); glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5); glVertex3f(-0.5, 0.5, -0.5)
    # Cara inferior
    glNormal3f(0, -1, 0)
    glVertex3f(-0.5, -0.5, -0.5); glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5); glVertex3f(-0.5, -0.5, 0.5)
    # Cara derecha
    glNormal3f(1, 0, 0)
    glVertex3f(0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5); glVertex3f(0.5, 0.5, 0.5)
    # Cara izquierda
    glNormal3f(-1, 0, 0)
    glVertex3f(-0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, -0.5)
    glEnd()
    glPopMatrix()

def draw_pyramid(x, y, z, sx, sy, sz, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    glNormal3f(0, 0.7, 1); glVertex3f(0, 0.5, 0); glVertex3f(-0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, 0.5)
    glNormal3f(1, 0.7, 0); glVertex3f(0, 0.5, 0); glVertex3f(0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, -0.5)
    glNormal3f(0, 0.7, -1); glVertex3f(0, 0.5, 0); glVertex3f(0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5, -0.5)
    glNormal3f(-1, 0.7, 0); glVertex3f(0, 0.5, 0); glVertex3f(-0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5, 0.5)
    glEnd()
    glBegin(GL_QUADS)
    glNormal3f(0, -1, 0); glVertex3f(-0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5); glVertex3f(-0.5, -0.5, -0.5)
    glEnd()
    glPopMatrix()

def draw_sphere_obj(x, y, z, radius, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    gluSphere(get_quadric(), radius, 16, 16)
    glPopMatrix()

def draw_cylinder_obj(x, y, z, radius, height, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)
    glColor3f(*color)
    gluCylinder(get_quadric(), radius, radius, height, 16, 4)
    glPopMatrix()

def draw_cone_obj(x, y, z, radius, height, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)
    glColor3f(*color)
    gluCylinder(get_quadric(), radius, 0.0, height, 16, 4)
    glPopMatrix()

# ---------------------------------------------------------------------------
# Elementos de la Ciudad (Lógica completa de ciudad.py)
# ---------------------------------------------------------------------------

def draw_tree(x, z, scale=1.0):
    draw_cylinder_obj(x, 0.0, z, 0.16 * scale, 1.35 * scale, (0.34, 0.18, 0.07))
    draw_sphere_obj(x, 1.55 * scale, z, 0.65 * scale, (0.08, 0.48, 0.18))
    draw_sphere_obj(x - 0.35 * scale, 1.32 * scale, z + 0.10 * scale, 0.45 * scale, (0.07, 0.40, 0.15))
    draw_sphere_obj(x + 0.35 * scale, 1.32 * scale, z - 0.10 * scale, 0.45 * scale, (0.10, 0.55, 0.18))

def draw_lamp_post(x, z):
    draw_cylinder_obj(x, 0.0, z, 0.06, 2.1, (0.08, 0.08, 0.08))
    draw_sphere_obj(x, 2.18, z, 0.22, (1.0, 0.88, 0.45))
    draw_cone_obj(x, 2.35, z, 0.25, 0.32, (0.08, 0.08, 0.08))

def draw_bench(x, z, rotation=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    draw_cube(0, 0.45, 0, 1.6, 0.18, 0.35, (0.45, 0.23, 0.10))
    draw_cube(0, 0.85, -0.20, 1.6, 0.18, 0.18, (0.45, 0.23, 0.10))
    draw_cube(-0.65, 0.22, 0, 0.16, 0.45, 0.16, (0.12, 0.12, 0.12))
    draw_cube(0.65, 0.22, 0, 0.16, 0.45, 0.16, (0.12, 0.12, 0.12))
    glPopMatrix()

def draw_fountain():
    draw_cylinder_obj(0, 0.05, 0, 1.75, 0.35, (0.42, 0.42, 0.42))
    draw_cylinder_obj(0, 0.36, 0, 1.35, 0.18, (0.60, 0.60, 0.58))
    draw_cylinder_obj(0, 0.54, 0, 1.12, 0.08, (0.20, 0.62, 0.90))
    draw_cylinder_obj(0, 0.55, 0, 0.28, 1.10, (0.55, 0.55, 0.53))
    draw_cylinder_obj(0, 1.60, 0, 0.75, 0.15, (0.62, 0.62, 0.60))
    
    glPushMatrix()
    glTranslatef(0, 1.85 + water_bob, 0)
    glRotatef(fountain_angle, 0, 1, 0)
    draw_sphere_obj(0, 0, 0, 0.22, (0.28, 0.75, 1.0))
    for i in range(8):
        angle = math.radians(i * 45)
        draw_sphere_obj(math.cos(angle)*0.65, -0.25, math.sin(angle)*0.65, 0.12, (0.28, 0.75, 1.0))
    glPopMatrix()

def draw_house(x, z, wall, roof, rot=0, size=1.0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rot, 0, 1, 0)
    glScalef(size, size, size)
    draw_cube(0, 1.1, 0, 3.0, 2.2, 2.8, wall)
    draw_pyramid(0, 2.9, 0, 3.5, 1.5, 3.4, roof)
    draw_cube(0, 0.75, 1.43, 0.72, 1.35, 0.08, (0.28, 0.13, 0.05))
    draw_cube(-0.90, 1.35, 1.45, 0.55, 0.55, 0.08, (0.55, 0.82, 0.96))
    draw_cube(0.90, 1.35, 1.45, 0.55, 0.55, 0.08, (0.55, 0.82, 0.96))
    glPopMatrix()

def draw_store(x, z, wall_color, rotation=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    draw_cube(0, 1.0, 0, 3.7, 2.0, 3.0, wall_color)
    draw_cube(0, 2.25, 0, 4.0, 0.45, 3.2, (0.78, 0.20, 0.16))
    draw_cube(0, 1.95, 1.65, 3.9, 0.20, 0.45, (0.95, 0.82, 0.30))
    draw_cube(-1.0, 1.95, 1.68, 0.45, 0.24, 0.50, (0.95, 0.35, 0.25))
    draw_cube(0.0, 1.95, 1.68, 0.45, 0.24, 0.50, (0.95, 0.35, 0.25))
    draw_cube(1.0, 1.95, 1.68, 0.45, 0.24, 0.50, (0.95, 0.35, 0.25))
    draw_cube(0, 0.75, 1.53, 0.75, 1.30, 0.08, (0.30, 0.15, 0.06))
    glPopMatrix()

def draw_church():
    draw_cube(0, 0.15, -29.0, 8.8, 0.30, 7.0, (0.46, 0.46, 0.44))
    draw_cube(0, 2.0, -29.0, 7.0, 4.0, 5.5, (0.84, 0.78, 0.65))
    draw_pyramid(0, 4.7, -29.0, 7.8, 2.1, 6.3, (0.46, 0.10, 0.08))
    draw_cube(0, 2.7, -25.8, 7.6, 5.4, 0.75, (0.88, 0.82, 0.69))
    draw_cube(0, 5.1, -25.4, 2.4, 5.0, 2.3, (0.80, 0.74, 0.62))
    draw_pyramid(0, 8.15, -25.4, 3.1, 2.4, 3.1, (0.42, 0.08, 0.07))
    draw_cube(0, 9.75, -25.4, 0.16, 1.10, 0.16, (0.12, 0.10, 0.08))
    draw_cube(0, 9.90, -25.4, 0.75, 0.16, 0.16, (0.12, 0.10, 0.08))

def draw_roads():
    c, line = (0.3, 0.3, 0.3), (0.86, 0.82, 0.64)
    draw_cube(0, 0.01, -17.75, 6.0, 0.06, 15.5, c)
    draw_cube(0, 0.01, 15.0, 6.0, 0.06, 20.0, c)
    draw_cube(0, 0.02, -12.25, 50.0, 0.06, 4.5, c)
    draw_cube(0, 0.02, 6.5, 50.0, 0.06, 5.3, c)
    for z in range(-24, -13, 4): draw_cube(0, 0.07, z, 0.25, 0.04, 1.5, line)

def draw_plaza():
    draw_cube(0, 0.06, -2.5, 15.0, 0.12, 15.0, (0.56, 0.56, 0.54))
    glPushMatrix()
    glTranslatef(0, 0, -2.5)
    draw_fountain()
    glPopMatrix()
    draw_bench(-4.8, -2.5, 90); draw_bench(4.8, -2.5, -90)

def draw_gaviota(x, y, z, rot=0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rot, 0, 1, 0)
    draw_cube(0, 0, 0, 0.4, 0.12, 0.12, (0.9, 0.9, 0.9)) # Cuerpo
    glPushMatrix()
    glTranslatef(-0.15, 0, 0); glRotatef(wing_angle, 0, 0, 1); glTranslatef(-0.3, 0, 0)
    draw_cube(0, 0, 0, 0.6, 0.04, 0.18, (0.8, 0.8, 0.8))
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.15, 0, 0); glRotatef(-wing_angle, 0, 0, 1); glTranslatef(0.3, 0, 0)
    draw_cube(0, 0, 0, 0.6, 0.04, 0.18, (0.8, 0.8, 0.8))
    glPopMatrix()
    glPopMatrix()

def draw_persona(x, z, color_camisa, color_pantalon, rotation=0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    draw_cube(0, 0.3, 0, 0.25, 0.6, 0.2, color_pantalon)
    draw_cube(0, 0.85, 0, 0.35, 0.5, 0.22, color_camisa)
    draw_sphere_obj(0, 1.25, 0, 0.14, (0.92, 0.76, 0.62))
    glPopMatrix()

def draw_perrito(x, z, rotation=0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glRotatef(rotation, 0, 1, 0)
    draw_cube(0.0, 0.3, 0.0, 0.4, 0.2, 0.2, (0.55, 0.27, 0.07)) # Cuerpo
    draw_cube(0.22, 0.45, 0.0, 0.16, 0.16, 0.16, (0.55, 0.27, 0.07)) # Cabeza
    draw_cube(0.32, 0.41, 0.0, 0.08, 0.08, 0.1, (0.35, 0.16, 0.14)) # Hocico
    glPopMatrix()

def draw_nube(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    color = (0.95, 0.95, 0.95)
    draw_cube(0.0, 0.0, 0.0, 3.0, 1.0, 1.8, color)
    draw_cube(-1.5, -0.2, 0.2, 1.2, 0.7, 1.2, color)
    draw_cube(1.4, -0.1, -0.2, 1.5, 0.8, 1.3, color)
    glPopMatrix()

def draw_coche_base(x, z, color_cuerpo, rotation=0, es_emergencia=False):
    glPushMatrix()
    glTranslatef(x, 0.01, z)
    glRotatef(rotation, 0, 1, 0)
    draw_cube(0.0, 0.4, 0.0, 1.8, 0.4, 0.9, color_cuerpo)
    y_cabina = 0.95 if es_emergencia else 0.8
    draw_cube(-0.1, y_cabina, 0.0, 1.0, 0.45, 0.82, (0.9, 0.9, 0.9) if es_emergencia else color_cuerpo)
    glPopMatrix()

def draw_all_elements():
    """Dibuja todos los elementos de la ciudad."""
    # Suelo base (un poco más pequeño para AR)
    draw_cube(0, -0.12, -5, 60, 0.12, 60, (0.28, 0.62, 0.28))
    
    draw_roads()
    draw_plaza()
    draw_church()
    
    # Casas
    cream, salmon, blue, green = (0.92, 0.76, 0.48), (0.92, 0.48, 0.36), (0.50, 0.70, 0.88), (0.55, 0.78, 0.52)
    purple, orange, white, yellow = (0.75, 0.55, 0.80), (0.92, 0.62, 0.34), (0.88, 0.84, 0.76), (0.95, 0.80, 0.38)
    r_red, r_brown = (0.58, 0.12, 0.08), (0.42, 0.20, 0.10)
    
    draw_house(-14.0, -8.5, cream, r_red, 270)
    draw_house(14.0, -8.5, salmon, r_red, 90)
    draw_house(-14.0, -3, blue, r_brown, 270)
    draw_house(14.0, -3, green, r_brown, 90)
    draw_house(-14.0, 2, purple, r_red, 270)
    draw_house(14.0, 2, orange, r_red, 90)
    
    # Tiendas
    draw_store(-6.5, 12.0, (0.92, 0.68, 0.40), 180)
    draw_store(6.5, 12.0, (0.62, 0.78, 0.88), 180)
    
    # Árboles y faroles
    tree_pos = [(-10, -8), (10, -8), (-10, 3), (10, 3), (-23, -11), (23, -11), (-23, 8), (23, 8)]
    for tx, tz in tree_pos: draw_tree(tx, tz)
    lamp_pos = [(-7.8, 4.2), (7.8, 4.2), (-7.8, -9.2), (7.8, -9.2), (-16.5, 4.0), (16.5, 4.0)]
    for lx, lz in lamp_pos: draw_lamp_post(lx, lz)
    
    # Personas
    draw_persona(-3.5, -2.5, (0.8, 0.2, 0.2), (0.1, 0.1, 0.5), 90)
    draw_persona(2.5, -4.0, (0.2, 0.7, 0.3), (0.1, 0.1, 0.5), -90)
    draw_persona(0.8, 1.5, (0.9, 0.7, 0.1), (0.1, 0.1, 0.5), 180)
    
    # Mascotas
    draw_perrito(-4.5, -2.5, 45)
    draw_perrito(4.5, 0.5, -30)
    
    # Vehículos
    draw_coche_base(1.5, 16.0, (0.8, 0.1, 0.1), 90)
    draw_coche_base(1.5, -18.0, (0.9, 0.9, 0.9), 90, True)
    
    # Aves
    draw_gaviota(0, 15, -10, 45)
    draw_gaviota(-10, 12, 5, -30)
    draw_gaviota(0, 15.5, -22.0, 90)
    
    # Nubes
    draw_nube(-15.0, 22.0, -25.0)
    draw_nube(10.0, 25.0, -30.0)
    draw_nube(0.0, 26.0, 0.0)

# ---------------------------------------------------------------------------
# Sistema de Fondo de Cámara
# ---------------------------------------------------------------------------

_tex_id = None

def update_camera_background(frame):
    """Carga el frame de la cámara como una textura de fondo."""
    global _tex_id
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = cv2.flip(rgb, 0)
    
    if _tex_id is None:
        _tex_id = glGenTextures(1)
        
    glBindTexture(GL_TEXTURE_2D, _tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb)

def draw_background(w, h):
    """Dibuja el quad de fondo con la imagen de la cámara."""
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, _tex_id)
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(w, 0)
    glTexCoord2f(1, 1); glVertex2f(w, h)
    glTexCoord2f(0, 1); glVertex2f(0, h)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

# ---------------------------------------------------------------------------
# Loop Principal
# ---------------------------------------------------------------------------

def main():
    global model_scale, fountain_angle, water_bob, wing_angle
    
    # Inicializar Cámara
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return
        
    # Leer un frame para obtener dimensiones
    ret, frame = cap.read()
    if not ret: return
    cam_h, cam_w = frame.shape[:2]
    
    # Configuración de ArUco
    detector, dictionary = make_aruco_detector()
    # Matriz intrínseca aproximada (basada en resolución)
    f = float(max(cam_w, cam_h))
    camera_matrix = np.array([[f, 0, cam_w/2], [0, f, cam_h/2], [0, 0, 1]], dtype=np.float64)
    dist_coeffs = np.zeros((5, 1))
    
    # Inicializar GLFW
    if not glfw.init(): return
    window = glfw.create_window(cam_w, cam_h, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
    # Callback de Teclado
    def key_callback(win, key, scancode, action, mods):
        global model_scale
        if action != glfw.PRESS and action != glfw.REPEAT: return
        if key in (glfw.KEY_ESCAPE, glfw.KEY_Q):
            glfw.set_window_should_close(win, True)
        elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD): # Tecla '+'
            model_scale *= 1.1
        elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT): # Tecla '-'
            model_scale /= 1.1
        elif key == glfw.KEY_R: # Reiniciar escala
            model_scale = BASE_MODEL_SCALE
            
    glfw.set_key_callback(window, key_callback)
    
    # Configuración inicial OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.57, 0.78, 0.95, 1.0) # Color del cielo
    glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 10.0, 10.0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.7, 1.0))
    
    last_time = time.time()
    
    while not glfw.window_should_close(window):
        ret, frame = cap.read()
        if not ret: break
        
        # Animaciones
        curr_time = time.time()
        dt = curr_time - last_time
        fountain_angle += 100 * dt
        water_bob = math.sin(fountain_angle * 0.1) * 0.05
        wing_angle = math.sin(fountain_angle * 0.5) * 25.0
        last_time = curr_time
        
        # Procesar Frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners = detect_marker(gray, detector, dictionary)
        
        # Renderizado
        glViewport(0, 0, cam_w, cam_h)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 1. Fondo de cámara
        update_camera_background(frame)
        draw_background(cam_w, cam_h)
        
        # 2. Ciudad en RA
        if corners is not None:
            rvec, tvec = estimate_pose(corners, camera_matrix, dist_coeffs)
            
            # Matriz de Proyección
            P = get_projection_matrix(camera_matrix, cam_w, cam_h, Z_NEAR, Z_FAR)
            glMatrixMode(GL_PROJECTION)
            glLoadMatrixf(P)
            
            # Matriz de Vista (Pose del marcador)
            MV = get_modelview_matrix(rvec, tvec)
            glMatrixMode(GL_MODELVIEW)
            glLoadMatrixf(MV)
            
            # Dibujar la ciudad sobre el marcador
            glPushMatrix()
            # Rotar para que la ciudad crezca hacia la cámara (Z+ es hacia afuera del marcador en CV, -Z en GL)
            glRotatef(90, 1, 0, 0)
            # Escalar la ciudad enorme a tamaño maqueta
            glScalef(model_scale, model_scale, model_scale)
            # Centrar la plaza (está en Z=-2.5 originalmente)
            glTranslatef(0, 0, 2.5)
            
            draw_all_elements()
            glPopMatrix()
            
        glfw.swap_buffers(window)
        glfw.poll_events()
        
    cap.release()
    glfw.terminate()

if __name__ == "__main__":
    main()
