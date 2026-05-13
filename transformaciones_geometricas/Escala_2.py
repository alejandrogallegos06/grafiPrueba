import cv2 as cv
import numpy as np

# Cargar la imagen en escala de grises
img = cv.imread('ImagenPrueba.jpg', 0)

# Obtener el tamaño de la imagen
x, y = img.shape

# Definir el factor de escala
scale_x, scale_y = 2, 2

# Crear una nueva imagen para almacenar el escalado manual
scaled_img_manual = np.zeros((int(x * scale_y), int(y * scale_x)), dtype=np.uint8)

# Escalado manual replicando píxeles en bloques 2x2
for i in range(x):
    for j in range(y):
        orig_val = img[i, j]
        # Copiar el píxel en un bloque de 2x2
        scaled_img_manual[i*scale_y:(i+1)*scale_y, j*scale_x:(j+1)*scale_x] = orig_val

# Escalado con OpenCV (interpolación)
scaled_img_cv = cv.resize(img, None, fx=2, fy=2, interpolation=cv.INTER_LINEAR)

# Mostrar resultados
cv.imshow('Imagen Original', img)
cv.imshow('Escalado Manual (bloques 2x2)', scaled_img_manual)
cv.imshow('Escalado con cv.resize (interpolacion)', scaled_img_cv)

cv.waitKey(0)
cv.destroyAllWindows()
