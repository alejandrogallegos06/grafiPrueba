import cv2
import numpy as np

# 1. Cargar la imagen de inteligencia (Asegúrate de la extensión .jpg o .png)
img = cv2.imread('m4_ruido.png')

if img is None:
    print("Error: No se encontró el archivo 'm4_ruido.png'. Verifica el nombre.")
else:
    # 2. Convertir al espacio de color HSV
    # Ideal para segmentar colores sin que afecte la iluminación
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. Definir los límites para el color Cyan (Celeste)
    # Hue: 80-100 es el rango del Cyan en OpenCV (escala 0-180)
    lower_cyan = np.array([80, 100, 100])
    upper_cyan = np.array([100, 255, 255])

    # 4. Crear la máscara binaria
    # Esto aísla los píxeles Cyan y los vuelve blancos, el resto negros
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)

    # 5. Limpieza Morfológica (Opcional pero recomendado para eliminar ruido residual)
    # Usamos un kernel de 3x3 para no borrar partes de las letras
    kernel = np.ones((3, 3), np.uint8)
    
    # MORPH_OPEN elimina puntitos blancos pequeños (ruido)
    # MORPH_CLOSE cierra pequeños huecos dentro de las letras
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    # 6. Aplicar la máscara sobre la imagen original (Para ver el color real)
    revelado_color = cv2.bitwise_and(img, img, mask=mask_clean)

    # --- VISUALIZACIÓN ---
    cv2.imshow("1. Imagen con Ruido", img)
    cv2.imshow("2. Mascara Binaria (Contrasena)", mask_clean)
    cv2.imshow("3. Resultado a Color", revelado_color)

    # Guardar el resultado final
    cv2.imwrite('password_descifrada.png', mask_clean)
    print("Misión cumplida. La contraseña ha sido guardada en 'password_descifrada.png'")

    cv2.waitKey(0)
    cv2.destroyAllWindows()