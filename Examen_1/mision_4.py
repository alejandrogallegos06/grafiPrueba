import cv2
import numpy as np


img = cv2.imread('m4_ruido.png')

if img is None:
    print("No charchea")
else:
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


    lower_cyan = np.array([80, 100, 100])
    upper_cyan = np.array([100, 255, 255])

    
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)

    kernel = np.ones((3, 3), np.uint8)
    
   
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    revelado_color = cv2.bitwise_and(img, img, mask=mask_clean)

    cv2.imshow("1. Imagen con Ruido", img)
    cv2.imshow("2. Mascara Binaria (Contrasena)", mask_clean)
    cv2.imshow("3. Resultado a Color", revelado_color)

    cv2.imwrite('password_descifrada.png', mask_clean)
    print("Misión cumplida. La contraseña ha sido guardada en 'password_descifrada.png'")

    cv2.waitKey(0)
    cv2.destroyAllWindows()