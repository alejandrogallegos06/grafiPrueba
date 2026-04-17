import cv2
import numpy as np


print("Iniciando Fase 1: Forjado de evidencia 'm5_tricolor.png'...")


base_noise = np.full((300, 700, 3), (40, 60, 40), dtype=np.uint8)


noise = np.random.normal(0, 15, base_noise.shape).astype(np.int16)
img_final = np.clip(base_noise.astype(np.int16) + noise, 0, 255).astype(np.uint8)


tinta_tramposa = (20, 200, 40) 

texto_clave = "TRICOLOR-KEY"
fuente = cv2.FONT_HERSHEY_SIMPLEX
escala = 2.0
grosor = 6

tamaño_texto, _ = cv2.getTextSize(texto_clave, fuente, escala, grosor)
x_texto = (700 - tamaño_texto[0]) // 2
y_texto = (300 + tamaño_texto[1]) // 2

cv2.putText(img_final, texto_clave, (x_texto, y_texto), fuente, escala, tinta_tramposa, grosor)


img_final = cv2.GaussianBlur(img_final, (3, 3), 0)

cv2.imwrite("m5_tricolor.png", img_final)
print(">> Fase 1 Completada. Evidencia 'm5_tricolor.png' generada con éxito.")


print("\nIniciando Fase 2: Protocolo de recuperación forense...")

img_evidencia = cv2.imread("m5_tricolor.png")

if img_evidencia is None:
    print("¡ALERTA TÁCTICA! No se pudo leer 'm5_tricolor.png'. Operación abortada.")
else:
    b, g, r = cv2.split(img_evidencia)
    
   
    print(">> Analizando canales por separado...")
    cv2.imwrite("test_canal_b.png", b) 
    cv2.imwrite("test_canal_g.png", g) 
    cv2.imwrite("test_canal_r.png", r) 
    
    print(">> Ejecutando aritmética de canales forense...")
    
  
    diff_gb = cv2.absdiff(g, b)
    
  
    norm_gb = cv2.normalize(diff_gb, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    
    
    _, thresh_mensaje = cv2.threshold(norm_gb, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    cv2.imwrite("m5_mensaje.png", thresh_mensaje)
    print(">> Fase 2 Completada. Clave recuperada y exportada como 'm5_mensaje.png'.")
    
    cv2.imshow("1. Evidencia Interceptada", img_evidencia)
    cv2.imshow("2. Solo Canal G (Ruidoso)", g)
    cv2.imshow("3. Aritmetica abs(G - B)", diff_gb)
    cv2.imshow("4. Resultado Final (Binarizado)", thresh_mensaje)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()