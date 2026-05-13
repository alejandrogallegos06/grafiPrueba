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
    # OpenCV: H en [0,179], S,V en [0,255]
    hsv = np.uint8([[[h % 180, np.clip(s, 0, 255), np.clip(v, 0, 255)]]])
    return tuple(int(x) for x in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])

def post_vignette(img, strength=0.7):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W*0.5) / (W*0.5)
    ny = (yy - H*0.5) / (H*0.5)
    r2 = nx*nx + ny*ny
    mask = np.clip(1.0 - strength * r2, 0.0, 1.0)
    out = (img.astype(np.float32) * mask[..., None]).astype(np.uint8)
    return out

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

def background_hsv_gradient(img, t, hue0=10, hue1=140):
    hsv = np.zeros((H, W, 3), np.uint8)
    ys = np.linspace(0, 1, H, dtype=np.float32)
    hue = (hue0 + (hue1 - hue0) * ys + 15*np.sin(t*0.5 + ys*3.0)).astype(np.float32)
    hsv[:, :, 0] = np.clip(hue, 0, 179).astype(np.uint8)[:, None]
    hsv[:, :, 1] = (160 + 80*np.sin(t*0.3)).astype(np.uint8)
    hsv[:, :, 2] = (30 + 100*(1 - ys) + 20*np.cos(t*0.6)).astype(np.uint8)[:, None]
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def scene_credits(img, t):
    background_hsv_gradient(img, t, hue0=130, hue1=160)
    rng = np.random.default_rng(1)
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
    background_hsv_gradient(img, t, hue0=0, hue1=25)
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
    background_hsv_gradient(img, t, hue0=40, hue1=90)
    k = 3 + abs(math.sin(t*0.2) * 4)
    theta0 = t * 0.4
    fx = lambda th: np.cos(k*th) * np.cos(th + theta0)
    fy = lambda th: np.cos(k*th) * np.sin(th + theta0)
    pts = poly_param(fx, fy, 0, 2*math.pi, 1500, W*0.5, H*0.45, 250, 250)
    col = hsv_to_bgr(int(160 + 20*np.sin(t)), 255, 255)
    cv2.fillPoly(img, [pts], col)
    cv2.polylines(img, [pts], True, (255,255,255), 1, cv2.LINE_AA)

def scene_spirograph(img, t):
    background_hsv_gradient(img, t, hue0=110, hue1=140)
    R, r, d = 10.0, 4.2, 6.0
    w = (R - r) / r
    fx = lambda x: (R-r)*np.cos(x) + d*np.cos(w*x + t)
    fy = lambda x: (R-r)*np.sin(x) - d*np.sin(w*x + t)
    pts = poly_param(fx, fy, 0, 20*math.pi, 2000, W*0.5, H*0.46, 22, 22)
    for i in range(len(pts)-1):
        c = hsv_to_bgr(int(t*20 + i*0.1), 200, 255)
        cv2.line(img, tuple(pts[i][0]), tuple(pts[i+1][0]), c, 2, cv2.LINE_AA)

def scene_particles(img, t, rng):
    background_hsv_gradient(img, t, hue0=150, hue1=100)
    n = 1200
    xs = rng.random(n) * W
    ys = rng.random(n) * H
    xs = (xs + 110*np.sin(ys/55.0 + t*1.7) + 40*np.cos(t*0.7)) % W
    ys = (ys + 85*np.cos(xs/75.0 + t*1.2) + 30*np.sin(t*0.9)) % H
    v = (0.5 + 0.5*np.sin(t*1.9)).astype(float) if hasattr(t, "astype") else (0.5 + 0.5*math.sin(t*1.9))
    col = hsv_to_bgr(int(95 + 40*math.sin(t*0.8)), 210, int(210 + 40*v))
    img[ys.astype(np.int32), xs.astype(np.int32)] = col
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
        frame = post_vignette(frame, 0.72)
        frame = post_scanlines(frame, 0.16)
        frame = post_posterize(frame, 24)
        frame = post_aberration(frame, 4) # Added creative filter
        
        block = int(min(5, max(0, t // 10)))
        if not scene_captures[block] and (t % 10) > 2.0:
            cv2.imwrite(f"renders/scene_{block+1}.png", frame)
            scene_captures[block] = True

        video_out.write(frame)
        
        # Save specific masks for the report
        if i == 0:
            # Generate and save vignette mask for documentation
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            nx = (xx - W*0.5) / (W*0.5)
            ny = (yy - H*0.5) / (H*0.5)
            r2 = nx*nx + ny*ny
            mask_v = np.clip(1.0 - 0.72 * r2, 0.0, 1.0)
            cv2.imwrite('renders/mask_vignette.png', (mask_v * 255).astype(np.uint8))

        if block == 5 and not os.path.exists('renders/mask_fire_heat.png'):
            # Save a snapshot of the fire heat map
            heat_norm = cv2.normalize(fire_state["heat"], None, 0, 255, cv2.NORM_MINMAX)
            cv2.imwrite('renders/mask_fire_heat.png', heat_norm.astype(np.uint8))
        
        # Show window (Optional)
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
