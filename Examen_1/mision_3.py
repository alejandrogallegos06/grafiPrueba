import cv2 as cv
import numpy as np

fondo_azul = np.zeros((500, 500, 3), dtype=np.uint8)
fondo_azul[:] = (50, 20, 20)

cv.circle(fondo_azul, (250, 250), 100, (0, 255, 255), 3)
cv.rectangle(fondo_azul, (200, 200), (300, 300), (0, 0, 255), -1)

# Dibujamos la línea
cv.line(fondo_azul, (0, 0), (500, 500) , (255, 255, 255), 2)
cv.line(fondo_azul, (500, 0), (0, 500) , (255, 255, 255), 2)

cv.imshow('Fondo Azul', fondo_azul)
cv.waitKey(0)
cv.destroyAllWindows()