#  Reporte de Misión: Graficación Táctica
**Agente Especial:** Alejandro Antonio Gallegos Chavez

---
##  Evidencias de Misión
# Misión 1:
## Codigo 1.1: RAW
[Codigo Raw](mision_1.py)
![RAW](<screenshot/Captura de pantalla (115).png>)
## Codigo 1.2: Open Cv
[OpenCv](mision_1_2.py)
![OpenCv](<screenshot/Captura de pantalla (116).png>)
## Misión 2:
## Codigo 2:
[Misión2](mision_2_1.py)
![Misión2](<screenshot/Captura de pantalla (117).png>)
## Misión 3:
[Misión3](mision_3.py)
![Misión3](<screenshot/Captura de pantalla (118).png>)
## Misión 4:
[Misión4](mision_4.py)
![Misión3](<screenshot/Captura de pantalla (119).png>)
## Misión 5:
[Misión5](mision_5.py)
![Misión5](<screenshot/Captura de pantalla (120).png>)



---
##  Análisis del Analista (Reflexiones Finales)

1. **Sobre los Operadores Puntuales (Misión 1):** Matemáticamente, ¿qué pasaría si en lugar de multiplicar por 50, hubieras sumado 50 a cada píxel oscuro? ¿Se revelaría el texto igual de claro o la imagen perdería contraste?
> Con la suma, el texto se revelaría muy tenue, porque el fondo también se aclararía en la misma proporción. La multiplicación aumenta el contraste en cambio la suma solo aclara la oscuridad.

2. **Sobre el Espacio HSV (Misión 4):** ¿Por qué el modelo de color BGR es ineficiente para la Recuperación de Información cuando buscamos "todos los tonos de azul celeste", y por qué el modelo HSV resuelve este problema con una sola variable?
> en BGR Para encontrar un celeste, tendrías que definir rangos complejos para color. Si la iluminación cambia ligeramente, los tres valores cambian drásticamente, y tu filtro deja de funcionar. En HSV, el Celeste es simplemente un número en el canal Hue. No importa si el azul es oscuro, brillante o pastel;

3. **Sobre Ecuaciones Paramétricas (Misión 5):** ¿Por qué las ecuaciones paramétricas (usando el parámetro t) son mejores para dibujar formas cerradas y complejas en graficación por computadora que usar la clásica función $y=f(x)$?
> Una función clásica y=f(x) tiene una regla estricta: para cada valor de x solo puede existir un valor de y. Con el parámetro t (tiempo), la computadora sabe exactamente en qué orden dibujar los puntos. 