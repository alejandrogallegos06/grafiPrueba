import cv2
import numpy as np

# Cargar la imagen proporcionada
img1 = cv2.imread('m2_mitad1.png')
img2 = cv2.imread('m2_mitad2.png')


canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255

canvas[0:200, 0:400] = img1



alto_mitad2, ancho_mitad2 = img2.shape[:2]
centro = (ancho_mitad2 // 2, alto_mitad2 // 2)


M_rot = cv2.getRotationMatrix2D(centro, 180, 1.0)
mitad2_rotada = cv2.warpAffine(img2, M_rot, (ancho_mitad2, alto_mitad2))


canvas[200:400, 0:400] = mitad2_rotada

cv2.imshow('400x400', canvas)
cv2.imwrite('resultado_mision2_examen1.png', canvas)



cv2.waitKey(0)
cv2.destroyAllWindows()