import cv2
import numpy as np

mitad1 = cv2.imread("m2_mitad1.png")
mitad2 = cv2.imread("m2_mitad2.png")

if mitad1 is None or mitad2 is None:
    print("¡ALERTA TÁCTICA! No se encontraron las imágenes m2_mitad1.png o m2_mitad2.png.")
else:
   
    lienzo = np.full((400, 400, 3), 255, dtype=np.uint8)

   
    h1, w1 = mitad1.shape[:2]
    h2, w2 = mitad2.shape[:2]

   
    dx = -50  
    dy = -30  
    
    
    M_traslacion = np.float32([[1, 0, dx], [0, 1, dy]])
    
    # Aplicar transformación. Usamos borderValue para que el fondo vacío quede blanco, no negro.
    mitad1_corregida = cv2.warpAffine(mitad1, M_traslacion, (w1, h1), borderValue=(255, 255, 255))

  
    centro_m2 = (w2 // 2, h2 // 2)
   
    M_rotacion = cv2.getRotationMatrix2D(centro_m2, 180, 1.0)
 
    mitad2_corregida = cv2.warpAffine(mitad2, M_rotacion, (w2, h2), borderValue=(255, 255, 255))

    
    lienzo[0:h1, 0:w1] = mitad1_corregida
    

    lienzo[h1:h1+h2, 0:w2] = mitad2_corregida


    cv2.imwrite("m2_qr_reconstruido.png", lienzo)
    print(">> Evidencia ensamblada y exportada: 'm2_qr_reconstruido.png'")

    # Mostrar en monitores
    cv2.imshow("Mitad 1 Corregida", mitad1_corregida)
    cv2.imshow("Mitad 2 Corregida", mitad2_corregida)
    cv2.imshow("QR Reconstruido", lienzo)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()