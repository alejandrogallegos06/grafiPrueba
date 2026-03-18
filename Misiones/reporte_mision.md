
 ![Portada](../Portada.png)


# Objetivo de la práctica.

## Comprender las aplicaciones de las transformaciones geométricas como lo son rotación y escalado aplicadas en imágenes digitales mediante dos formas matemática manual desde cero (Modo Raw) y el uso de la libreria OpenCV. El propósito es analizar y comparar la eficiencia, la calidad y el manejo de herramientas computacionales.

# Capturas de pantalla de las máscaras generadas.
# Actividad 1
[Codigo mision 1](mision_1.py)
![Resultado_mision_1](Resultado_mision_1.png)

# Actividad 2
[mision_2](mision_2.py)
![Resultado_mision_2](Resultado_mision_2.png)

# Actividad 3
[mision_3](mision_3.py)
![Resultado_mision_3](Resultado_mision_3.png)

# Tabla comparativa de resultados.
| Característica | Modo Raw (Matemática Manual) | Modo OpenCV (Librería Optimizada) |
| :--- | :--- | :--- |
| **Tiempo de Ejecución** | Muy lento (Tarda varios segundos en procesar). | Casi instantáneo (Fracción de segundo). |
| **Calidad de Rotación** | Básica. Depende de cómo se maneje el redondeo de decimales. | Alta. Bordes definidos y sin huecos de información. |
| **Calidad de Escalado (Zoom)** | Pixelada / Cuadriculada (Efecto de "escalera"). | Suave y continua (Efecto difuminado en los bordes). |
| **Complejidad del Código** | Alta. Requiere ciclos anidados y trigonometría pura. | Baja. Requiere solo una o dos líneas de código preconstruido. |
| **Uso de Recursos** | Alto. Procesa píxel por píxel secuencialmente en Python. | Bajo. Usa aceleración por hardware y código C/C++ interno. |


Respuestas a las preguntas de análisis.
Conclusión final.
No se aceptarán archivos en PDF, Word o imágenes sueltas. La entrega debe consistir en un único archivo .md.
