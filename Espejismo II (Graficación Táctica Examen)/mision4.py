import cv2
import numpy as np

ruta_imagen = "m4_ruido.png"
img_ruido = cv2.imread(ruta_imagen)

if img_ruido is None:
    print(f"¡ALERTA TÁCTICA! No se encontró la imagen '{ruta_imagen}'. Operación abortada.")
else:
    print("Evidencia asegurada. Iniciando protocolo de reducción de ruido...")

  
    kernel_promedio = np.ones((3, 3), np.float32) / 9
    
   
    img_suavizada = cv2.filter2D(img_ruido, -1, kernel_promedio)
 
    cv2.imwrite("m4_suavizada.png", img_suavizada)
    print(">> Imagen suavizada exportada: 'm4_suavizada.png'")

 
    img_hsv = cv2.cvtColor(img_suavizada, cv2.COLOR_BGR2HSV)
    
    low_cyan = np.array([80, 100, 50])  
    high_cyan = np.array([100, 255, 255]) 
    
    mask_cyan = cv2.inRange(img_hsv, low_cyan, high_cyan)
    
    cv2.imwrite("m4_mask_cyan.png", mask_cyan)
    print(">> Máscara final exportada: 'm4_mask_cyan.png'. Revisa el archivo para la contraseña.")
    
    # Desplegar monitores
    cv2.imshow("1. Evidencia con Ruido", img_ruido)
    cv2.imshow("2. Suavizado Promedio 3x3", img_suavizada)
    cv2.imshow("3. Mascara Cyan (Contrasena Revelada)", mask_cyan)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()