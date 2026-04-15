import cv2
import numpy as np

def desencriptar_mensaje_raw(img):
    alto, ancho = img.shape
    

    img_x50 = np.zeros((alto, ancho), dtype=np.uint8)
    img_x50_mas20 = np.zeros((alto, ancho), dtype=np.uint8)
    
    
    for y in range(alto):
        for x in range(ancho):
       
            val_original = int(img[y, x])
            
            
            val_a = val_original * 50
            
            val_a = min(max(val_a, 0), 255)
            img_x50[y, x] = val_a
          
            val_b = val_a + 20
           
            val_b = min(max(val_b, 0), 255)
            img_x50_mas20[y, x] = val_b
            
    return img_x50, img_x50_mas20

def desencriptar_mensaje_vectorizado(img):

    img_calc = img.astype(np.float32)
    
    img_vec_a = np.clip(img_calc * 50, 0, 255).astype(np.uint8)
    
    img_vec_b = np.clip(img_vec_a.astype(np.float32) + 20, 0, 255).astype(np.uint8)
    
    
    return img_vec_a, img_vec_b



ruta_imagen = "m1_oscura.png"
img_original = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)

if img_original is None:
    print(f"¡ALERTA! Evidencia '{ruta_imagen}' no encontrada en el directorio actual.")
else:
    print("Evidencia asegurada. Procesando desencriptación en 2 fases...")
    
    print(">> Ejecutando Modo Raw...")
    raw_x50, raw_x50_mas20 = desencriptar_mensaje_raw(img_original)
    
    print(">> Ejecutando Modo Vectorizado...")
    vec_x50, vec_x50_mas20 = desencriptar_mensaje_vectorizado(img_original)
    
    cv2.imwrite("m1_recuperado_x50.png", vec_x50)
    cv2.imwrite("m1_recuperado_x50_mas20.png", vec_x50_mas20)
    print(">> Evidencias exportadas: 'm1_recuperado_x50.png' y 'm1_recuperado_x50_mas20.png'")
    
    cv2.imshow("1. Evidencia Original (Subexpuesta)", img_original)
    cv2.imshow("2. Fase A: x50 (Vectorizado)", vec_x50)
    cv2.imshow("3. Fase B: x50 + 20 (Vectorizado)", vec_x50_mas20)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()