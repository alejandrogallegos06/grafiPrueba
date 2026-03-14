import cv2
import numpy as np
import math

alto, ancho = 500, 500
canvas = np.zeros((alto, ancho, 3), dtype=np.uint8)


t = 0.0
paso = 0.01
limite_t = 2 * math.pi  

print("Sintonizando frecuencia de antena...")


while t <= limite_t:
    
   
    x = int(250 + 150 * math.sin(3 * t))
    y = int(250 + 150 * math.sin(2 * t))
 
    cv2.circle(canvas, (x, y), 1, (0, 0, 150), -1)
  
    t += paso

cv2.imshow("Antena Identificada", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()