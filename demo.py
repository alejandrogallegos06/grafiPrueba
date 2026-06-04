import time
import math
import numpy as np
import cv2
import os

# Constants
W, H = 800, 600
FPS = 30
DURATION = 60.0
TOTAL_FRAMES = int(DURATION * FPS)
OUTPUT_FILE = 'renders/demo.mp4'

# Ensure directories exist
os.makedirs('renders', exist_ok=True)

def clamp01(x): return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def smoothstep(a, b, x):
    x = clamp01((x - a) / (b - a))
    return x * x * (3 - 2 * x)

def poly_param(fx, fy, t0, t1, n, cx, cy, sx, sy):
    ts = np.linspace(t0, t1, n, dtype=np.float32)
    xs = fx(ts) * sx + cx
    ys = fy(ts) * sy + cy
    return np.round(np.stack([xs, ys], 1)).astype(np.int32).reshape((-1, 1, 2))

def hsv_to_bgr(h, s, v):
    hsv = np.uint8([[[h % 180, np.clip(s, 0, 255), np.clip(v, 0, 255)]]])
    return tuple(int(x) for x in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])

# --- FONDOS EN MOVIMIENTO (MÁS NOTORIOS Y VIBRANTES) ---

def background_waves(img, t):
    hsv = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    hue = (140 + 15 * np.sin(xx / 120.0 + t) + 10 * np.cos(yy / 100.0 - t * 0.7)) % 180
    hsv[:, :, 0] = hue.astype(np.uint8)
    hsv[:, :, 1] = 220  # Mayor saturación
    hsv[:, :, 2] = (100 + 55 * np.sin(yy / 150.0 + t * 0.8)).astype(np.uint8) # Mayor brillo
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def background_plasma(img, t):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx = W / 2 + W * 0.1 * math.sin(t * 0.4)
    cy = H / 2 + H * 0.1 * math.cos(t * 0.3)
    v1 = np.sin(xx / 50.0 + t)
    v2 = np.sin(yy / 40.0 + t * 1.2)
    v3 = np.sin((xx + yy + t) / 45.0)
    v4 = np.sin(np.sqrt((xx - cx)**2 + (yy - cy)**2) / 50.0 - t)
    plasma = (v1 + v2 + v3 + v4) * 0.25
    
    hsv = np.zeros((H, W, 3), np.uint8)
    hsv[:, :, 0] = ((plasma + 1.0) * 70 + t * 12) % 180
    hsv[:, :, 1] = 240  # Colores más intensos
    hsv[:, :, 2] = ((plasma + 1.0) * 60 + 80).astype(np.uint8) # Base de luz más alta
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def background_grid(img, t):
    img.fill(35) # Base gris más clara
    offset_x = int((t * 45) % 60)
    offset_y = int((t * 25) % 60)
    # Rejilla principal más brillante (azul neón)
    for x in range(offset_x, W, 60):
        cv2.line(img, (x, 0), (x, H), (140, 90, 50), 2)
    for y in range(offset_y, H, 60):
        cv2.line(img, (0, y), (W, y), (140, 90, 50), 2)

def background_tunnel(img, t):
    img.fill(15)
    cx, cy = W // 2, H // 2
    max_r = int(math.sqrt(cx**2 + cy**2))
    offset = int((t * 120) % 70) # Túnel más rápido
    for r in range(offset, max_r, 70):
        c_intensity = int(255 * (1.0 - r / max_r))
        # Colores más vibrantes en lugar de gris oscuro
        cv2.circle(img, (cx, cy), r, (c_intensity, c_intensity // 2, c_intensity // 4), 3, cv2.LINE_AA)

def background_stripes(img, t):
    hsv = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    val = np.sin((xx + yy) / 50.0 - t * 3.5)
    hsv[:, :, 0] = (110 + 20 * math.sin(t * 0.4)) % 180
    hsv[:, :, 1] = 230 # Alta saturación
    hsv[:, :, 2] = (80 + 50 * val).astype(np.uint8) # Mayor contraste
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def background_moving_scene2(img, t):
    hsv = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    hue = (160 + 20 * np.sin(xx / 90.0 + t * 1.5) + 20 * np.cos(yy / 80.0 - t * 1.2)) % 180
    hsv[:, :, 0] = hue.astype(np.uint8)
    hsv[:, :, 1] = 220
    hsv[:, :, 2] = (100 + 60 * np.sin((xx + yy) / 100.0 + t * 2.0)).astype(np.uint8) # Brillo incrementado
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# --- POST PROCESADO ---

def post_vignette(img, strength=0.6): # Viñeta reducida para que los fondos resalten más
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W*0.5) / (W*0.5)
    ny = (yy - H*0.5) / (H*0.5)
    r2 = nx*nx + ny*ny
    mask = np.clip(1.0 - strength * r2, 0.0, 1.0)
    return (img.astype(np.float32) * mask[..., None]).astype(np.uint8)

def post_scanlines(img, strength=0.22):
    out = img.astype(np.float32)
    y = np.arange(H, dtype=np.float32)
    m = 1.0 - strength * (0.5 + 0.5*np.sin(2*np.pi*y/3.0))
    out *= m[:, None, None]
    return np.clip(out, 0, 255).astype(np.uint8)

def post_posterize(img, q=32):
    q = max(1, int(q))
    return ((img // q) * q).astype(np.uint8)

def post_aberration(img, amount=4):
    b, g, r = cv2.split(img)
    rows, cols = img.shape[:2]
    M_r = np.float32([[1, 0, amount], [0, 1, 0]])
    M_b = np.float32([[1, 0, -amount], [0, 1, 0]])
    r = cv2.warpAffine(r, M_r, (cols, rows))
    b = cv2.warpAffine(b, M_b, (cols, rows))
    return cv2.merge([b, g, r])

# --- ESCENAS CON MÁS FIGURAS ---

def scene_credits(img, t):
    background_waves(img, t)
    rng = np.random.default_rng(1)
    
    # 1. Figuras secundarias: Anillos expansivos en el centro
    cx, cy = W//2, H//2
    for j in range(3):
        r_pulse = int(100 + 150 * math.sin(t * 1.5 - j * 1.2))
        if r_pulse > 0:
            c_ring = hsv_to_bgr(int(t*20 + j*30), 200, 200)
            cv2.circle(img, (cx, cy), r_pulse, c_ring, 2, cv2.LINE_AA)

    xs = rng.integers(0, W, 400)
    ys = rng.integers(0, H, 400)
    for i in range(len(xs)):
        v = int(180 + 75 * math.sin(t * 2.0 + i))
        cv2.circle(img, (xs[i], ys[i]), 1, (v, v, v), -1)
    
    alpha = smoothstep(0, 2, t) * (1.0 - smoothstep(8, 10, t))
    col = (int(255*alpha), int(255*alpha), int(255*alpha))
    cv2.putText(img, "Demo de Alejandro Gallegos", (100, 280), cv2.FONT_HERSHEY_TRIPLEX, 1.3, col, 2, cv2.LINE_AA)
    cv2.putText(img, "Exploracion Matematica", (240, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 1, cv2.LINE_AA)

def scene_lissajous(img, t):
    background_plasma(img, t)
    
    # 1. Figuras secundarias: Lunas orbitando
    orbit_x = int(W*0.5 + 320 * math.cos(t * 1.8))
    orbit_y = int(H*0.45 + 240 * math.sin(t * 2.5))
    cv2.circle(img, (orbit_x, orbit_y), 15, (255, 200, 100), -1, cv2.LINE_AA)
    cv2.circle(img, (orbit_x, orbit_y), 25, (150, 100, 255), 2, cv2.LINE_AA)

    # 2. Figura Principal: Lissajous
    a = 4 + 1.2 * math.sin(t*0.4)
    b = 3 + 0.8 * math.cos(t*0.5)
    delta = t * 0.5
    fx = lambda x: np.sin(a*x + delta)
    fy = lambda x: np.sin(b*x)
    for i in range(3):
        thickness = 6 - i*2
        alpha = 0.3 + i*0.3
        pts = poly_param(fx, fy, 0, 2*math.pi, 1000, W*0.5, H*0.45, 280, 200)
        col = hsv_to_bgr(int(100 + 40*np.sin(t*0.5)), 200, int(255 * alpha))
        cv2.polylines(img, [pts], False, col, thickness, cv2.LINE_AA)

def scene_rose_polar(img, t):
    background_moving_scene2(img, t)
    
    # 1. Figura secundaria: Hexágono perimetral rotando en reversa
    hex_pts = []
    for i in range(6):
        ang = -t * 1.2 + i * (math.pi / 3)
        hex_pts.append([W*0.5 + 340*math.cos(ang), H*0.45 + 340*math.sin(ang)])
    hex_pts = np.array(hex_pts, np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [hex_pts], True, (255, 150, 150), 3, cv2.LINE_AA)

    # 2. Figura Principal: Rosa Polar
    k = 3 + abs(math.sin(t*0.2) * 4)
    theta0 = t * 0.4
    fx = lambda th: np.cos(k*th) * np.cos(th + theta0)
    fy = lambda th: np.cos(k*th) * np.sin(th + theta0)
    pts = poly_param(fx, fy, 0, 2*math.pi, 1500, W*0.5, H*0.45, 250, 250)
    col = hsv_to_bgr(int(160 + 20*np.sin(t)), 255, 255)
    cv2.fillPoly(img, [pts], col)
    cv2.polylines(img, [pts], True, (255,255,255), 1, cv2.LINE_AA)

def scene_spirograph(img, t):
    background_tunnel(img, t)
    
    R, r, d = 10.0, 4.2, 6.0
    w = (R - r) / r
    fx = lambda x: (R-r)*np.cos(x) + d*np.cos(w*x + t)
    fy = lambda x: (R-r)*np.sin(x) - d*np.sin(w*x + t)
    
    # 1. Figura Principal: Espirógrafo
    pts = poly_param(fx, fy, 0, 20*math.pi, 2000, W*0.5, H*0.46, 22, 22)
    for i in range(len(pts)-1):
        c = hsv_to_bgr(int(t*20 + i*0.1), 200, 255)
        cv2.line(img, tuple(pts[i][0]), tuple(pts[i+1][0]), c, 2, cv2.LINE_AA)
        
    # 2. Figura Secundaria: Satélite viajando sobre la línea de la curva
    sat_t = t * 15  # Velocidad del recorrido
    sat_x = int(fx(sat_t) * 22 + W*0.5)
    sat_y = int(fy(sat_t) * 22 + H*0.46)
    cv2.circle(img, (sat_x, sat_y), 12, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(img, (sat_x, sat_y), 20, (0, 255, 255), 2, cv2.LINE_AA)

def scene_particles(img, t, rng):
    background_stripes(img, t)
    
    # 1. Figuras secundarias: Grandes esferas holográficas en el fondo
    orb_x1 = int(W*0.5 + 250*math.sin(t*0.8))
    orb_y1 = int(H*0.5 + 180*math.cos(t*0.5))
    orb_x2 = int(W*0.5 - 250*math.cos(t*0.6))
    orb_y2 = int(H*0.5 + 150*math.sin(t*0.7))
    cv2.circle(img, (orb_x1, orb_y1), 90, (180, 100, 255), 5, cv2.LINE_AA)
    cv2.circle(img, (orb_x2, orb_y2), 65, (100, 220, 255), 3, cv2.LINE_AA)

    # 2. Figura Principal: Partículas
    n = 1200
    xs = rng.random(n) * W
    ys = rng.random(n) * H
    xs = (xs + 110*np.sin(ys/55.0 + t*1.7) + 40*np.cos(t*0.7)) % W
    ys = (ys + 85*np.cos(xs/75.0 + t*1.2) + 30*np.sin(t*0.9)) % H
    v = (0.5 + 0.5*np.sin(t*1.9)).astype(float) if hasattr(t, "astype") else (0.5 + 0.5*math.sin(t*1.9))
    col = hsv_to_bgr(int(95 + 40*math.sin(t*0.8)), 210, int(210 + 40*v))
    
    img[np.clip(ys, 0, H-1).astype(np.int32), np.clip(xs, 0, W-1).astype(np.int32)] = col
    img[:] = cv2.GaussianBlur(img, (0,0), 1.1)

def scene_fire(img, t, state):
    heat = state["heat"]
    rng = state["rng"]
    heat[:] = (heat * 0.93).astype(np.float32)
    base_n = 1400
    xs = rng.integers(0, W, base_n)
    ys = rng.integers(int(H*0.82), H, base_n)
    heat[ys, xs] += rng.random(base_n) * (0.8 + 0.6*(0.5+0.5*math.sin(t*2.0)))
    heat[:] = cv2.GaussianBlur(heat, (0, 0), 2.2)
    heat[:-2, :] = heat[2:, :]
    heat[-2:, :] *= 0.0
    h = (20 - 20*np.clip(heat, 0, 1)).astype(np.uint8)
    s = (220 - 80*np.clip(heat, 0, 1)).astype(np.uint8)
    v = (60 + 195*np.clip(heat, 0, 1)).astype(np.uint8)
    hsv = np.dstack([h, s, v]).astype(np.uint8)
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    cx = W // 2
    cy = H // 3 + int(25 * math.sin(t * 2.5))  # Efecto levitación
    radius = 75 + int(12 * math.cos(t * 1.4))   # Pulsación
    
    # 1. Figuras secundarias: Triángulos místicos orbitando el prisma
    for i in range(3):
        ang_tri = t * 2.5 + i * (2 * math.pi / 3)
        rx = cx + int(160 * math.cos(ang_tri))
        ry = cy + int(50 * math.sin(ang_tri))
        tri_pts = np.array([[rx, ry-20], [rx-15, ry+15], [rx+15, ry+15]], np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [tri_pts], True, (150, 200, 255), 2, cv2.LINE_AA)

    # 2. Figura Principal: Prisma/Estrella
    sides = 6
    points = []
    angle_offset = t * 1.5
    for i in range(sides):
        angle = angle_offset + i * (2 * math.pi / sides)
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        points.append([x, y])
    pts = np.array(points, np.int32).reshape((-1, 1, 2))
    
    cv2.polylines(img, [pts], True, (255, 220, 140), 3, cv2.LINE_AA)
    for p in points:
        cv2.line(img, (cx, cy), tuple(p), (210, 140, 70), 1, cv2.LINE_AA)

    cv2.rectangle(img, (0, int(H*0.83)), (W, H), (10, 10, 10), -1)
    sparks = 160
    sx = rng.integers(0, W, sparks)
    sy = rng.integers(int(H*0.55), int(H*0.9), sparks)
    img[sy, sx] = (255, 255, 255)
    img[:] = cv2.GaussianBlur(img, (0,0), 0.6)

def render_scene(buf, scene_id, t, rng, fire_state):
    if scene_id == 0:
        scene_credits(buf, t)
    elif scene_id == 1:
        scene_lissajous(buf, t)
    elif scene_id == 2:
        scene_rose_polar(buf, t)
    elif scene_id == 3:
        scene_spirograph(buf, t)
    elif scene_id == 4:
        scene_particles(buf, t, rng)
    else:
        scene_fire(buf, t, fire_state)

def timeline(t, rng, bufA, bufB, fire_state):
    block = int(min(5, max(0, t // 10)))
    t_in = t - block*10
    render_scene(bufA, block, t, rng, fire_state)
    frame = bufA
    if block < 5 and t_in >= 8.8:
        render_scene(bufA, block, t, rng, fire_state)
        render_scene(bufB, block+1, t, rng, fire_state)
        a = smoothstep(8.8, 10.0, t_in)
        frame = cv2.addWeighted(bufA, 1-a, bufB, a, 0)
        flash = smoothstep(9.6, 10.0, t_in)
        if flash > 0:
            frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, 255), 0.12*flash, 0)
    fin = smoothstep(0.0, 1.5, t)
    fout = 1.0 - smoothstep(DURATION - 1.5, DURATION, t)
    f = fin * fout
    if f < 0.999:
        frame = (frame.astype(np.float32) * f).astype(np.uint8)
    return frame

def main():
    rng = np.random.default_rng(123)
    bufA = np.zeros((H, W, 3), np.uint8)
    bufB = np.zeros((H, W, 3), np.uint8)
    fire_state = {
        "heat": np.zeros((H, W), np.float32),
        "rng": np.random.default_rng(999),
    }

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (W, H))

    total_frames = int(DURATION * FPS)
    print(f"Generating {total_frames} frames...")
    
    scene_captures = {i: False for i in range(6)}

    for i in range(total_frames):
        t = i / FPS
        frame = timeline(t, rng, bufA, bufB, fire_state)
        frame = post_vignette(frame, 0.60) # Reducido para que los bordes destaquen más
        frame = post_scanlines(frame, 0.16)
        frame = post_posterize(frame, 24)
        frame = post_aberration(frame, 4)
        
        block = int(min(5, max(0, t // 10)))
        if not scene_captures[block] and (t % 10) > 2.0:
            cv2.imwrite(f"renders/scene_{block+1}.png", frame)
            scene_captures[block] = True

        video_out.write(frame)
        
        if i == 0:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            nx = (xx - W*0.5) / (W*0.5)
            ny = (yy - H*0.5) / (H*0.5)
            r2 = nx*nx + ny*ny
            mask_v = np.clip(1.0 - 0.60 * r2, 0.0, 1.0)
            cv2.imwrite('renders/mask_vignette.png', (mask_v * 255).astype(np.uint8))

        if block == 5 and not os.path.exists('renders/mask_fire_heat.png'):
            heat_norm = cv2.normalize(fire_state["heat"], None, 0, 255, cv2.NORM_MINMAX)
            cv2.imwrite('renders/mask_fire_heat.png', heat_norm.astype(np.uint8))
        
        try:
            cv2.imshow("Demo de Alejandro Gallegos", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        except:
            pass
            
        if i % 100 == 0:
            print(f"Progress: {i}/{total_frames}")

    video_out.release()
    cv2.destroyAllWindows()
    print(f"Demo saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()