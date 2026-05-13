# Reporte de Misión: Órbita Dual (Cámara vs Objeto)
**Agente Especial:** Alejandro Antonio Gallegos Chavez 24120333

---
## Evidencias

### Misión 1: El Espejo de la Matriz
En esta misión se demostró que mover el objeto y mover la cámara son operaciones matemáticamente inversas.

- **Objeto rota:** [Archivo: m1_objeto_rota.png]
- **Cámara orbita:** [Archivo: m1_camara_orbita.png]

### Misión 2: El Ojo Declarativo
Se implementó el uso de gluLookAt para definir la cámara de forma semántica (Ojo, Objetivo, Arriba).

- **LookAt órbita:** [Archivo: m2_lookat_orbita.png]

### Misión 3: La Brújula de Luces
Se analizó cómo la posición de la luz en el código afecta la percepción de las sombras.

- **Notas:** Al definir la luz antes de las transformaciones (Modo 1), esta se mueve con la cámara. Al definirla después (Modo 2), la luz permanece fija en el mundo.

---
## Bloque de Código Final (Extracto Principal)
El código completo se encuentra en orbita_dual_final.py.

```python
# Misión 1 & 2 Core Logic
if modo == 1:
    glTranslatef(0, 0, -CAM_DISTANCE)
    glRotatef(angle, 0, 1, 0) # Objeto rota
elif modo == 2:
    glRotatef(-angle, 0, 1, 0) # Mundo rota inverso
    glTranslatef(0, 0, -CAM_DISTANCE)
elif modo == 3:
    gluLookAt(eyeX, eyeY, eyeZ, 0,0,0, 0,1,0) # Cámara orbita
```

---
## Análisis del Analista (Reflexiones Finales)

1. **Orden de matrices:** ¿Por qué en OpenGL fijo el orden en que escribes glTranslatef / glRotatef cambia el resultado aunque uses los mismos números?
> **[Respuesta]:** Debido a que OpenGL utiliza la multiplicación de matrices por la derecha (post-multiplicación). Cada nueva transformación se aplica sobre el sistema de coordenadas local resultante de la anterior. Por ello, 'Rotar y luego Trasladar' no es lo mismo que 'Trasladar y luego Rotar'; en el primer caso, el eje de traslación ya ha sido rotado.

2. **Objeto vs cámara:** En la práctica, ¿cuándo prefieres rotar el modelo y cuándo orbitar la cámara?
> **[Respuesta]:** Prefiero rotar el modelo cuando el usuario necesita inspeccionar un objeto individual (como en un inventario o editor de personajes). Prefiero orbitar la cámara en escenas complejas o entornos (como en un juego de tercera persona) para mantener las referencias globales del mundo estables.

3. **gluLookAt vs translate+rotate:** ¿Qué ventaja tiene describir la cámara con ojo–objetivo–arriba para equipos de desarrollo?
> **[Respuesta]:** La principal ventaja es la legibilidad y semántica. Es mucho más intuitivo decir 'mira desde este punto a este edificio' que calcular manualmente los ángulos de Euler y las traslaciones necesarias. Facilita la colaboración entre diseñadores y programadores al usar términos espaciales claros.

4. **Luces:** Si la luz se define en el frame de la cámara sin reubicarla al mundo, ¿qué artefacto visual esperas al rotar solo el objeto?
> **[Respuesta]:** Se espera un efecto de 'linterna frontal'. La luz siempre iluminará la cara del objeto que el espectador está viendo, independientemente de cuánto gire el objeto. Las sombras no rotarán con el objeto, lo que puede romper la sensación de realismo si se busca una luz ambiental fija.
