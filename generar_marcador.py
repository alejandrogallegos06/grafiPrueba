import cv2
import numpy as np

def generate_marker():
    # Diccionario solicitado: 4x4 con 50 variantes
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    
    # Generar marcador ID 0
    # Tamaño de la imagen: 400x400 píxeles
    marker_id = 0
    marker_size = 400
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
    
    # Agregar un margen blanco
    margin = 50
    final_img = np.ones((marker_size + 2*margin, marker_size + 2*margin), dtype=np.uint8) * 255
    final_img[margin:margin+marker_size, margin:margin+marker_size] = marker_img
    
    # Guardar imagen
    cv2.imwrite("marcador_aruco_id0.png", final_img)
    print("Marcador ArUco ID 0 generado como 'marcador_aruco_id0.png'")

if __name__ == "__main__":
    generate_marker()
