import cv2
import numpy as np

img = cv2.imread('m1_oscura.png', cv2.IMREAD_GRAYSCALE)

alto,ancho = img.shape

img_revelada = np.zeros((alto, ancho), dtype=np.uint8)

# --- MODO RAW ---
# Recorre con un for y multiplica por 50
 
       
for y in range(alto):
    for x in range(ancho):  
            pixel_valor = img[y,x]
            resultado_bruto = int(pixel_valor) + 50 

            valor_final = np.clip(resultado_bruto, 0, 255)
            img_revelada[y,x] = valor_final


cv2.imshow('original', img)
cv2.imshow('m1_revelada.png', img_revelada)
cv2.waitKey(0)
cv2.destroyAllWindows()



