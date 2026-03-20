import cv2 as cv
import numpy as np
import math

casa = np.ones((400, 400, 3), dtype=np.uint8) * 255


angulo_grados = 30
angulo_rad = math.radians(angulo_grados)

x1 = 200
y1 = 400

x2 = int(x1 + 150 * math.cos(angulo_rad))
y2 = int(y1 - 150 * math.sin(angulo_rad))

# linea de la entrada
cv.line(casa, (x1, y1), (x2, y2), (30, 100, 0), 5)

# linea de la entrada techo
cv.line(casa, (200, 250), (x2, 200), (30, 100, 0), 5)

# linea del costado izquierdo
cv.line(casa, (x1, y1), (20,350), (30, 100, 0), 5)

# linea del costado izquierdo superior
cv.line(casa, (200, 250), (20,220), (30, 100, 0), 5)

# linea frontal vertical
cv.line(casa, (x1, y1), (200,250), (30, 100, 0), 5)

# linea frontal vertical esquina izquierda
cv.line(casa, (20, 350), (20,220), (30, 100, 0), 5)

# linea vertical esquina derecha
cv.line(casa, (x2, y2), (x2,200), (30, 100, 0), 5)

# linea del techo, costado izquierdo medio 
cv.line(casa, (170, 320), (10,280), (0, 155, 200), 10)

# linea del techo, Nivel superior frontal
cv.line(casa, (170, 320), (230,80), (0, 155, 200), 10)

# linea del techo, Nivel superior trasero
cv.line(casa, (10, 280), (50,80), (0, 155, 200), 10)

# linea del techo, Nivel superior 
cv.line(casa, (230, 80), (50,80), (0, 155, 200), 10)

# linea del techo, Nivel superior izquierda 
cv.line(casa, (230, 80), (350,230), (0, 155, 200), 10)

cv.imshow('casa',casa)

cv.waitKey(0)
cv.destroyAllWindows()