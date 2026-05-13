import cv2 as cv
import numpy as np
import math


casa = np.ones((500, 500, 3), dtype=np.uint8) * 255

angulo_grados = 30
angulo_rad = math.radians(angulo_grados)
profundidad = 120


dx = int(profundidad * math.cos(angulo_rad))
dy = int(profundidad * math.sin(angulo_rad))


A = (150, 350)  
B = (270, 350) 
C = (270, 230)  
D = (150, 230)  
Pico_F = (210, 150) 

E = (A[0] + dx, A[1] - dy)
F = (B[0] + dx, B[1] - dy)
G = (C[0] + dx, C[1] - dy)
H = (D[0] + dx, D[1] - dy)
Pico_T = (Pico_F[0] + dx, Pico_F[1] - dy) 


color_pared = (30, 100, 0)       
color_techo = (0, 155, 200)      
color_conexion = (100, 100, 100) 
grosor = 4



# Conexiones de profundidad
cv.line(casa, A, E, color_conexion, grosor)
cv.line(casa, B, F, color_conexion, grosor)
cv.line(casa, C, G, color_conexion, grosor)
cv.line(casa, D, H, color_conexion, grosor)

# Cara Trasera
cv.line(casa, E, F, color_pared, grosor)
cv.line(casa, F, G, color_pared, grosor)
cv.line(casa, G, H, color_pared, grosor)
cv.line(casa, H, E, color_pared, grosor)

# Techo Trasero y Línea central del techo 
cv.line(casa, H, Pico_T, color_techo, grosor)
cv.line(casa, G, Pico_T, color_techo, grosor)
cv.line(casa, Pico_F, Pico_T, color_techo, grosor)

# Cara Frontal 
cv.line(casa, A, B, color_pared, grosor)
cv.line(casa, B, C, color_pared, grosor)
cv.line(casa, C, D, color_pared, grosor)
cv.line(casa, D, A, color_pared, grosor)


cv.line(casa, D, Pico_F, color_techo, grosor)
cv.line(casa, C, Pico_F, color_techo, grosor)


cv.imshow('Casa 3D', casa)
cv.waitKey(0)
cv.destroyAllWindows()