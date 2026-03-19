import cv2 as cv
import numpy as np
import math

casa = np.ones((400, 400, 3), dtype=np.uint8) * 255


angulo_grados = 30
angulo_rad = math.radians(angulo_grados)

x1 = 200
y1 = 400

x2 = int(x1 + 200 * math.cos(angulo_rad))
y2 = int(y1 - 200 * math.sin(angulo_rad))

# linea de la entrada
cv.line(casa, (x1, y1), (x2, y2), (0, 255, 0), 2)

# linea del costado izquierdo
cv.line(casa, (x1, y1), (20,350), (0, 255, 0), 2)


cv.imshow('casa',casa)

cv.waitKey(0)
cv.destroyAllWindows()