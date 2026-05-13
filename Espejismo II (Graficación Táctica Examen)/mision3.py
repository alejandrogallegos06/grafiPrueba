import cv2
import numpy as np
import math

img = np.zeros((600, 600, 3), dtype=np.uint8)
img[:] = (40, 20, 20)

centro = (300, 300)

cv2.circle(img, centro, 170, (0, 255, 255), 3)

cv2.circle(img, centro, 110, (0, 255, 255), 2)

cv2.rectangle(img, (250, 260), (350, 340), (0, 0, 255), -1)

cv2.line(img, (0, 0), (600, 600), (255, 255, 255), 2)
cv2.line(img, (600, 0), (0, 600), (255, 255, 255), 2)

distancia = 140
for angulo_grados in range(0, 360, 45):
    angulo_rad = math.radians(angulo_grados)
    
    cx = int(centro[0] + distancia * math.cos(angulo_rad))
    cy = int(centro[1] - distancia * math.sin(angulo_rad)) 
    
    cv2.circle(img, (cx, cy), 8, (0, 255, 0), -1)

texto = "SECTOR-9"
fuente = cv2.FONT_HERSHEY_SIMPLEX
escala = 1.2
grosor_txt = 2

tamaño_texto, _ = cv2.getTextSize(texto, fuente, escala, grosor_txt)
ancho_texto = tamaño_texto[0]
x_texto = (600 - ancho_texto) // 2

cv2.putText(img, texto, (x_texto, 560), fuente, escala, (255, 255, 255), grosor_txt)

cv2.imwrite("m3_sello_forjado_v2.png", img)
print(">> Evidencia falsificada exportada: 'm3_sello_forjado_v2.png'")

cv2.imshow("Sello Geometrico - SECTOR-9", img)
cv2.waitKey(0)
cv2.destroyAllWindows()