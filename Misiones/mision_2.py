import cv2
import numpy as np
import math

# ==========================================
# MÉTODO 1: MODO RAW (Matemática Manual CORREGIDA)
# ==========================================
def enderezar_qr_manual(imagen_interceptada):
    alto, ancho = imagen_interceptada.shape[:2]
    cx, cy = ancho // 2, alto // 2 
    
    # Lienzo negro para el resultado
    imagen_destino = np.zeros_like(imagen_interceptada)
    
    # Ángulo exacto de rotación (-45 grados para sentido horario)
    angulo_rad = math.radians(45) 
    cos_theta = math.cos(angulo_rad)
    sin_theta = math.sin(angulo_rad)
    
    # Escaneo píxel por píxel aplicando trigonometría ajustada al eje Y invertido
    for y_dest in range(alto):
        for x_dest in range(ancho):
            # Trasladar al origen (centro de la imagen)
            x_c = x_dest - cx
            y_c = y_dest - cy
            
            # Calcular coordenada de origen (Mapeo inverso corregido)
            x_src = int(x_c * cos_theta + y_c * sin_theta) + cx
            y_src = int(-x_c * sin_theta + y_c * cos_theta) + cy
            
            # Si el píxel de origen existe en la imagen original, lo copiamos
            if 0 <= x_src < ancho and 0 <= y_src < alto:
                imagen_destino[y_dest, x_dest] = imagen_interceptada[y_src, x_src]
                
    return imagen_destino

# ==========================================
# MÉTODO 2: MODO OPENCV (Optimizado)
# ==========================================
def enderezar_qr_opencv(imagen_interceptada):
    alto, ancho = imagen_interceptada.shape[:2]
    centro = (ancho // 2, alto // 2)
    
    # Crear matriz de rotación (-45 grados en sentido horario)
    matriz_rotacion = cv2.getRotationMatrix2D(centro, -45, 1.0)
    
    # Aplicar la matriz afín a toda la imagen
    imagen_destino = cv2.warpAffine(imagen_interceptada, matriz_rotacion, (ancho, alto))
    
    return imagen_destino

# ==========================================
# EJECUCIÓN TÁCTICA DE LA MISIÓN
# ==========================================

# 1. Definir la ruta con el nombre EXACTO de tu archivo
ruta_imagen = "qr_rotado.jpg" 

# 2. Cargar la evidencia interceptada
evidencia_qr = cv2.imread(ruta_imagen)

# 3. Escudo de seguridad
if evidencia_qr is None:
    print(f"¡ALERTA TÁCTICA! No se pudo encontrar o leer la imagen: '{ruta_imagen}'")
    print("Asegúrate de que la imagen 'qr_rotado.jpg' esté exactamente en la misma carpeta que este script.")
else:
    print("Imagen interceptada con éxito. Ejecutando algoritmos de rotación...")
    
    # 4. Procesar la imagen con AMBOS métodos
    qr_raw = enderezar_qr_manual(evidencia_qr)
    qr_opencv = enderezar_qr_opencv(evidencia_qr)
    
    # 5. Desplegar los resultados en los monitores
    cv2.imshow("Evidencia Interceptada", evidencia_qr)
    cv2.imshow("Resultado RAW (Matematica)", qr_raw)
    cv2.imshow("Resultado OpenCV (Optimizado)", qr_opencv)
    
    print("¡Misión cumplida! Monitores en línea. Ambos resultados deben ser idénticos.")
    print("Escanea el código con tu dispositivo para acceder al servidor.")
    
    # 6. Mantener las ventanas abiertas hasta presionar una tecla
    cv2.waitKey(0)
    cv2.destroyAllWindows()