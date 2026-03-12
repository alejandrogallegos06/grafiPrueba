import cv2
import numpy as np

img = cv2.imread('m1_oscura.png', cv2.IMREAD_GRAYSCALE)

alto,ancho = img.shape

img_revelada = np.zeros((alto, ancho), dtype=np.uint8)

# --- MODO RAW ---
# Recorre con un for y multiplica por 50
 
       
for y in range(alto):
    for x in range(ancho):  
            pixel_original = img[y,x]
            nuevo_valor = int(pixel_original)*50
            img_revelada[y,x] = np.clip(nuevo_valor,0,255)
           

cv2.imshow('original', img)
cv2.imwrite('m1_revelada.png', img_revelada)
cv2.waitKey(0)
cv2.destroyAllWindows()



# --- MODO OPENCV ---
# Usa la magia de la vectorización