import cv2 as cv 

# Cargar el clasificador
rostro = cv.CascadeClassifier('D:\\semestre_5_ISC\\Graficacion\\TareasGraficacion\\Filtros_Efects\\haarcascade_frontalface_alt2.xml')
cap = cv.VideoCapture(0)

while True:
    ret, img = cap.read()
    if not ret: break
    
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    rostros = rostro.detectMultiScale(gris, 1.3, 5)
    
    for (x, y, w, h) in rostros:
            # Ojo izquierdo y derecho
        #fondo blanco
        cv.circle(img, (x + int(w*0.3), y + int(h*0.4)), 30, (255, 255, 255), -1) 
        cv.circle(img, (x + int(w*0.7), y + int(h*0.4)), 30, (255, 255, 255), -1)
         # Pupila
        cv.circle(img, (x + int(w*0.3), y + int(h*0.4)), 10, (0, 0, 155), -1)      
        cv.circle(img, (x + int(w*0.7), y + int(h*0.4)), 10, (0, 0, 155), -1)

        # 2. NARIZ 
        # Punto central del rostro: (x + w//2, y + h//2)
        cv.circle(img, (x + int(w*0.5), y + int(h*0.6)), 15, (0, 50, 100), -1)

        # 3. Agregar BIGOTE (Dos líneas gruesas o rectángulos)
        cv.line(img, (x + int(w*0.3), y + int(h*0.7)), (x + int(w*0.5), y + int(h*0.7)), (0, 0, 0), 10)
        cv.line(img, (x + int(w*0.5), y + int(h*0.7)), (x + int(w*0.7), y + int(h*0.7)), (0, 0, 0), 10)

        
       
        cv.ellipse(img, (x + int(w*0.5), y + int(h*0.8)), (40, 20), 0, 0, 150, (0, 0, 25), 5)

        # Recorte del rostro (Corregido el error de la 'q' extra)
        img2 = img[y:y+h, x:x+w]
        cv.imshow('Recorte Rostro', img2)

    cv.imshow('Filtro en tiempo real', img)
    
    if cv.waitKey(1) == ord('q'):
        break
    
cap.release()
cv.destroyAllWindows()