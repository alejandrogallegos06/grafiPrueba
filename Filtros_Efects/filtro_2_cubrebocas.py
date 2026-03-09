import cv2
import numpy as np
import os

# Configuración de archivos
dir_script = os.path.dirname(os.path.abspath(__file__))
PATH_CASCADE = os.path.join(dir_script, 'haarcascade_frontalface_alt2.xml')
PATH_MASK = os.path.join(dir_script, 'cubrebocas.png')

# Carga de recursos
face_cascade = cv2.CascadeClassifier(PATH_CASCADE)
mascara = cv2.imread(PATH_MASK, cv2.IMREAD_UNCHANGED)

# Validación silenciosa de la imagen
if mascara is None or mascara.shape[2] != 4:
    exit()

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = face_cascade.detectMultiScale(gris, 1.2, 5)

    for (x, y, w, h) in rostros:
        # Dimensiones de la máscara
        ancho_mask = int(w * 0.9)
        alto_mask = int(h * 0.8)
        
        mask_res = cv2.resize(mascara, (ancho_mask, alto_mask), interpolation=cv2.INTER_AREA)
        mask_rgb = mask_res[:, :, :3]
        mask_alpha = mask_res[:, :, 3]

        # Coordenadas
        x_offset = x + (w - ancho_mask) // 2
        y_offset = y + int(h * 0.4) 

        # Ajuste a bordes de pantalla (ROI)
        y1, y2 = max(0, y_offset), min(frame.shape[0], y_offset + alto_mask)
        x1, x2 = max(0, x_offset), min(frame.shape[1], x_offset + ancho_mask)

        # Recorte proporcional de máscara
        mask_part = mask_rgb[0:(y2-y1), 0:(x2-x1)]
        alpha_part = mask_alpha[0:(y2-y1), 0:(x2-x1)]
        alpha_inv = cv2.bitwise_not(alpha_part)

        # Aplicación del filtro (Bitwise operations)
        roi = frame[y1:y2, x1:x2]
        img_bg = cv2.bitwise_and(roi, roi, mask=alpha_inv)
        img_fg = cv2.bitwise_and(mask_part, mask_part, mask=alpha_part)
        
        frame[y1:y2, x1:x2] = cv2.add(img_bg, img_fg)

    cv2.imshow('Filtro Final', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()