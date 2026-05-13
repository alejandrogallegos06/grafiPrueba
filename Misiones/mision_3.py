import cv2
import numpy as np

# Cargar la imagen
img_microfilm = cv2.imread('microfilm.jpg')

if img_microfilm is None:
    print("no jalo.")
else:
    recorte = img_microfilm[900:1100, 900:1100]
    
    alto, ancho = recorte.shape[:2]
    factor = 5

    
    lienzo_raw = np.zeros((alto * factor, ancho * factor, 3), dtype=np.uint8)

    for y in range(alto * factor):
        for x in range(ancho * factor):
            y_orig = y // factor
            x_orig = x // factor
            lienzo_raw[y, x] = recorte[y_orig, x_orig]

    
    lienzo_opencv = cv2.resize(recorte, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)

    cv2.imshow("1. Evidencia (Recorte 200x200)", recorte)
    cv2.imshow("2. Aumento MODO RAW (Pixelado)", lienzo_raw)
    cv2.imshow("3. Aumento OPENCV (Suavizado Cubico)", lienzo_opencv)

    print("Misión completada. Compara las ventanas para tu reporte.")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()