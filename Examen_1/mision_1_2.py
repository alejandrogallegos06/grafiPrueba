import cv2
import numpy as np

# --- MODO OPENCV ---
# Usa la magia de la vectorización

img = cv2.imread('m1_oscura.png', cv2.IMREAD_GRAYSCALE)

if img is not None:
    
    img_revelada_cv = np.clip(img.astype(np.uint16) * 50, 0, 255).astype(np.uint8)

    # Mostrar resultados
    cv2.imshow('Revelado con Vectorizacion (CV/NumPy)', img_revelada_cv)
    
    # Guardar el archivo final
    cv2.imwrite('m1_revelada_opencv.png', img_revelada_cv)
    
    print("Revelado con OpenCV y NumPy completado.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()