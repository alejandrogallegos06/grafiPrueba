import math
import cv2
import numpy as np

# Cargar la imagen
img_qr = cv2.imread('qr_rotado.jpg')

alto, ancho = img_qr.shape[:2]
tx, ty = 300, 200
# ==========================================
# MÉTODO 1: MODO RAW (Trigonometría)
# ==========================================
# 1. Crea un lienzo vacío de 500x500
canvas_raw = np.zeros((alto, ancho, 3), dtype=np.uint8)
# 2. Usa las fórmulas de senos y cosenos para mapear los píxeles (¡Cuidado con los huecos negros si mapeas hacia adelante!)

cv2.imshow('preImagen - Metodo raw', canvas_raw)

cv2.waitKey(0)
cv2.destroyAllWindows()
# ==========================================
# MÉTODO 2: MODO OPENCV
# ==========================================
# 1. Obtén la matriz con cv2.getRotationMatrix2D
# 2. Aplica cv2.warpAffine