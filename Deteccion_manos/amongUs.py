import cv2
import mediapipe as mp
import math

def dibujar_among_us(frame, cx, cy, distancia):
    # Limitamos el tamaño del cuerpo (crece rápido con 'd_cuerpo')
    d_cuerpo = max(30, min(int(distancia), 300))
    
    color_cuerpo = (0, 0, 200)   # Rojo
    color_contorno = (0, 0, 0)   # Negro
    color_visor = (230, 216, 173) # Celeste
    color_brillo = (255, 255, 255) # Blanco
    grosor = 2
    
   
    # Cuerpo principal
    ejes_cuerpo = (int(d_cuerpo / 1.8), d_cuerpo)

    # Visor 
    anch_visor = int(30 + (distancia / 4)) 
    alt_visor = int(20 + (distancia / 6))  
    ejes_visor = (anch_visor, alt_visor)
    
    # Mochila
    anch_mochila = int(d_cuerpo / 4)
    alt_mochila = int(d_cuerpo * 1.2)
    x_mochila = cx - ejes_cuerpo[0] - anch_mochila + int(anch_mochila/2)
    y_mochila = cy - int(alt_mochila / 2)

    # Piernas
    anch_pierna = int(d_cuerpo / 3.5)
    alt_pierna = int(d_cuerpo / 2)
    y_piernas = cy + int(d_cuerpo * 0.7)
    x_pi = cx - int(d_cuerpo / 3)
    x_pd = cx + int(d_cuerpo / 3) - anch_pierna

    # Posicionamiento del Visor y Brillo
    cy_visor = cy - int(alt_visor / 1.5) 
    cx_visor = cx + int(anch_visor / 6)
    
    axes_brillo = (int(anch_visor / 3), int(alt_visor / 4))
    cx_brillo = cx_visor - axes_brillo[0]
    cy_brillo = cy_visor - axes_brillo[1]

  
    # Mochila
    cv2.rectangle(frame, (x_mochila, y_mochila), (x_mochila + anch_mochila, y_mochila + alt_mochila), color_cuerpo, -1)
    cv2.rectangle(frame, (x_mochila, y_mochila), (x_mochila + anch_mochila, y_mochila + alt_mochila), color_contorno, grosor)

    # Piernas
    cv2.rectangle(frame, (x_pi, y_piernas), (x_pi + anch_pierna, y_piernas + alt_pierna), color_cuerpo, -1)
    cv2.rectangle(frame, (x_pi, y_piernas), (x_pi + anch_pierna, y_piernas + alt_pierna), color_contorno, grosor)
    cv2.rectangle(frame, (x_pd, y_piernas), (x_pd + anch_pierna, y_piernas + alt_pierna), color_cuerpo, -1)
    cv2.rectangle(frame, (x_pd, y_piernas), (x_pd + anch_pierna, y_piernas + alt_pierna), color_contorno, grosor)

    # Cuerpo principal óvalo
    cv2.ellipse(frame, (cx, cy), ejes_cuerpo, 0, 0, 360, color_cuerpo, -1)
    cv2.ellipse(frame, (cx, cy), ejes_cuerpo, 0, 0, 360, color_contorno, grosor)

    # Visor glass
    cv2.ellipse(frame, (cx_visor, cy_visor), ejes_visor, 0, 0, 360, color_visor, -1)
    cv2.ellipse(frame, (cx_visor, cy_visor), ejes_visor, 0, 0, 360, color_contorno, grosor)
    
    # Brillo visor
    cv2.ellipse(frame, (cx_brillo, cy_brillo), axes_brillo, 0, 0, 360, color_brillo, -1)

    # --- UNICEJA 
    y_base_ceja = cy_visor - alt_visor + int(alt_visor/10) 
    ancho_ceja_mitad = int(anch_visor * 0.9) 
    
    intensidad_asombro = int(distancia / 8) 
    levantamiento_total = 5 + intensidad_asombro
    
    punto_izq = (cx - ancho_ceja_mitad, y_base_ceja)
    punto_der = (cx + ancho_ceja_mitad, y_base_ceja)
    punto_centro_alto = (cx, y_base_ceja - levantamiento_total) # Restamos para subir el punto
    
    cv2.line(frame, punto_izq, punto_centro_alto, color_contorno, grosor + 2)
    cv2.line(frame, punto_der, punto_centro_alto, color_contorno, grosor + 2)



BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Opciones del detector (Asegúrate de tener 'hand_landmarker.task' en tu carpeta)
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE, 
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

# Conexiones de la mano
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),       # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),  # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),# Anular
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Meñique
]


cap = cv2.VideoCapture(0)
distancia = 50 # Tamaño base inicial

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Espejo para controlar mejor
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape

        # Convertir imagen a RGB para MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Detectar manos
        results = landmarker.detect(mp_image)
        
        # Procesar los puntos si se detectan manos
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                keypoints = []
              
                for landmark in hand_landmarks:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    keypoints.append((cx, cy))
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                    
              
                for connection in HAND_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    cv2.line(frame, keypoints[start_idx], keypoints[end_idx], (0, 255, 0), 2)
                    
                
                if len(keypoints) >= 9: 
                    x1, y1 = keypoints[4] # Punta del pulgar
                    x2, y2 = keypoints[8] # Punta del índice
                    
                    
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.circle(frame, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
                    cv2.circle(frame, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
                    
                 
                    distancia = math.hypot(x2 - x1, y2 - y1)
                    
                  
                    cx_medio, cy_medio = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.putText(frame, f"{int(distancia)} px", (cx_medio, cy_medio), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        
        centro_x = int(w / 2)
        centro_y = int(h / 2)
        dibujar_among_us(frame, centro_x, centro_y, distancia)
      
        cv2.imshow("Among Us Sorprendido", frame)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()