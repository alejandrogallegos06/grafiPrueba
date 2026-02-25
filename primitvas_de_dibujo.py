import numpy as np
import cv2 as cv

# Lienzo blanco
img = np.ones((400, 400, 3), dtype=np.uint8) * 255

# Cara (círculo grande)
cv.circle(img, (200, 200), 120, (0, 255, 255), -1)  # Amarillo relleno

# Ojos
cv.circle(img, (160, 170), 20, (0, 0, 0), -1)
cv.circle(img, (240, 170), 20, (0, 0, 0), -1)

# Boca (media elipse)
cv.ellipse(img, (200, 230), (60, 40), 0, 0, 180, (0, 0, 0), 4)

cv.imshow("Carita", img)
cv.waitKey(0)
cv.destroyAllWindows()