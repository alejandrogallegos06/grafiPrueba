import numpy as np
import cv2 as cv

# Matriz de enteros entre 0 y 255
# Cada número es un píxel

img2 = np.array([
    [255, 255, 255, 255, 255, 255, 255, 255],
    [255,   170,   0, 255, 255,   0,   0, 255],
    [255,   0,   170, 255, 255,   0,   0, 255],
    [255, 255, 255, 255, 255, 255, 255, 255],
    [255,   0,   0,   0,   0,   0,   0, 255],
    [255,   0,   0,   200,   200,   0,   0, 255],
    [255,   0,   0,   200,   200,   0,   0, 255],
    [255,   0,   0,   0,   0,   0,   0, 255]
], dtype=np.uint8)


# Escalar para que se vea grande (pixel art real)
img2_tamaño = cv.resize(
    img2,
    None,
    fx=40,
    fy=40,
    interpolation=cv.INTER_NEAREST
)

cv.imshow("Pixel Art", img2_tamaño)
cv.waitKey(0)
cv.destroyAllWindows()