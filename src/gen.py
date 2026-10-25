#!/usr/bin/env python3
"""Generate the 5.1.2 layout page (HTML fragment with inline SVG)."""
import math, sys

OUT = sys.argv[1]

def f(v):
    return f"{v:.1f}"

# ---------------------------------------------------------------- helpers
class Plan:
    """Plan view: x right (m), y forward (m), listener at (0,0)."""
    def __init__(self, S, ox, oy):
        self.S, self.ox, self.oy = S, ox, oy
        self.parts = []
    def px(self, x): return self.ox + x * self.S
    def py(self, y): return self.oy - y * self.S
    def add(self, s): self.parts.append(s)
    def text(self, x, y, s, cls="lab", anchor="middle", dy=0):
        self.add(f'<text class="{cls}" x="{f(self.px(x))}" y="{f(self.py(y)+dy)}" text-anchor="{anchor}">{s}</text>')
    def label2(self, x, y, a, b, anchor="middle", group=""):
        # two-line label: abbreviation + name, then detail
        X, Y = f(self.px(x)), self.py(y)
        self.add(f'<text class="lab" x="{X}" y="{f(Y)}" text-anchor="{anchor}">'
                 f'<tspan class="abbr {group}">{a[0]}</tspan> {a[1]}</text>')
        if b:
            self.add(f'<text class="sub" x="{X}" y="{f(Y+15)}" text-anchor="{anchor}">{b}</text>')
    def line(self, x1, y1, x2, y2, cls):
        self.add(f'<line class="{cls}" x1="{f(self.px(x1))}" y1="{f(self.py(y1))}" x2="{f(self.px(x2))}" y2="{f(self.py(y2))}"/>')
    def rect(self, x1, y1, x2, y2, cls):
        X1, X2 = sorted([self.px(x1), self.px(x2)])
        Y1, Y2 = sorted([self.py(y1), self.py(y2)])
        self.add(f'<rect class="{cls}" x="{f(X1)}" y="{f(Y1)}" width="{f(X2-X1)}" height="{f(Y2-Y1)}"/>')
    def circle(self, x, y, r, cls):
        self.add(f'<circle class="{cls}" cx="{f(self.px(x))}" cy="{f(self.py(y))}" r="{f(r*self.S)}"/>')
    def speaker(self, x, y, w, d, group, top=False):
        """Box whose front face points at the listener."""
        az = math.degrees(math.atan2(x, y))  # 0 = straight ahead, + = right
        W, D = w * self.S, d * self.S
        dash = " top" if top else ""
        self.add(
            f'<g transform="translate({f(self.px(x))} {f(self.py(y))}) rotate({az:.1f})">'
            f'<rect class="box {group}{dash}" x="{f(-W/2)}" y="{f(-D/2)}" width="{f(W)}" height="{f(D)}" rx="2"/>'
            f'<line class="face {group}" x1="{f(-W/2+2)}" y1="{f(D/2)}" x2="{f(W/2-2)}" y2="{f(D/2)}"/>'
            f'</g>')
    def aim(self, x, y, group, shorten=0.16):
        L = math.hypot(x, y)
        k = shorten / L
        self.line(x * (1 - 0.0), y, x * k, y * k, f"aim {group}") if False else None
        # from speaker toward listener, stopping short of head
        self.line(x, y, x * k, y * k, f"aim {group}")
    def head(self):
        r = 0.12 if self.S < 150 else 0.09
        self.circle(0, 0, r, "head")
        # nose (points forward)
        X, Y, R = self.px(0), self.py(0), r * self.S
        self.add(f'<path class="nose" d="M{f(X-R*0.38)} {f(Y-R*0.86)} L{f(X)} {f(Y-R*1.45)} L{f(X+R*0.38)} {f(Y-R*0.86)} Z"/>')
    def arc(self, r, a1, a2, cls):
        # angles in degrees, 0 = forward, + = right (clockwise on screen)
        def pt(a):
            return (self.px(r * math.sin(math.radians(a))), self.py(r * math.cos(math.radians(a))))
        (x1, y1), (x2, y2) = pt(a1), pt(a2)
        large = 1 if abs(a2 - a1) > 180 else 0
        sweep = 1 if a2 > a1 else 0
        R = r * self.S
        self.add(f'<path class="{cls}" d="M{f(x1)} {f(y1)} A{f(R)} {f(R)} 0 {large} {sweep} {f(x2)} {f(y2)}"/>')
    def dim_h(self, x1, x2, y, label, ext_from=None):
        Y = self.py(y)
        X1, X2 = self.px(x1), self.px(x2)
        if ext_from is not None:
            E = self.py(ext_from)
            self.add(f'<line class="ext" x1="{f(X1)}" y1="{f(E)}" x2="{f(X1)}" y2="{f(Y + (4 if Y < E else -4))}"/>')
            self.add(f'<line class="ext" x1="{f(X2)}" y1="{f(E)}" x2="{f(X2)}" y2="{f(Y + (4 if Y < E else -4))}"/>')
        self.add(f'<line class="dim" x1="{f(X1)}" y1="{f(Y)}" x2="{f(X2)}" y2="{f(Y)}"/>')
        for X in (X1, X2):
            self.add(f'<line class="tick" x1="{f(X-4)}" y1="{f(Y+4)}" x2="{f(X+4)}" y2="{f(Y-4)}"/>')
        self.add(f'<text class="dimtext" x="{f((X1+X2)/2)}" y="{f(Y-5)}" text-anchor="middle">{label}</text>')
    def dim_v(self, y1, y2, x, label, ext_from=None, side="left"):
        X = self.px(x)
        Y1, Y2 = self.py(y1), self.py(y2)
        if ext_from is not None:
            E = self.px(ext_from)
            for Yy in (Y1, Y2):
                self.add(f'<line class="ext" x1="{f(E)}" y1="{f(Yy)}" x2="{f(X + (4 if X > E else -4))}" y2="{f(Yy)}"/>')
        self.add(f'<line class="dim" x1="{f(X)}" y1="{f(Y1)}" x2="{f(X)}" y2="{f(Y2)}"/>')
        for Yy in (Y1, Y2):
            self.add(f'<line class="tick" x1="{f(X-4)}" y1="{f(Yy+4)}" x2="{f(X+4)}" y2="{f(Yy-4)}"/>')
        cx, cy = X + (-6 if side == "left" else 16), (Y1 + Y2) / 2
        self.add(f'<text class="dimtext" x="{f(cx)}" y="{f(cy)}" text-anchor="middle" '
                 f'transform="rotate(-90 {f(cx)} {f(cy)})">{label}</text>')
    def scalebar(self, x, y, meters, step):
        X0, Y = self.px(x), self.py(y)
        n = int(round(meters / step))
        for i in range(n):
            cls = "sb1" if i % 2 == 0 else "sb2"
            self.add(f'<rect class="{cls}" x="{f(X0 + i*step*self.S)}" y="{f(Y)}" width="{f(step*self.S)}" height="5"/>')
        for i in range(n + 1):
            v = i * step
            t = f"{v:g}"
            self.add(f'<text class="sbtext" x="{f(X0 + v*self.S)}" y="{f(Y+17)}" text-anchor="middle">{t}</text>')
        self.add(f'<text class="sbtext" x="{f(X0 + meters*self.S + 8)}" y="{f(Y+6)}" text-anchor="start">m</text>')
    def svg(self, w, h, title, cls="plan"):
        body = "\n".join(self.parts)
        return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}" '
                f'xmlns="http://www.w3.org/2000/svg">\n<title>{title}</title>\n{body}\n</svg>')


def pol(r, az):
    return (r * math.sin(math.radians(az)), r * math.cos(math.radians(az)))

checks = []

# ================================================================ FIG 1A studio
S = 90
ROOM_W, ROOM_L, CEIL = 5.0, 6.0, 2.8
DF = 2.73                      # listener -> front wall
yF, yR = DF, DF - ROOM_L       # wall y coords
r = 2.0
p = Plan(S, ox=150 + ROOM_W/2*S, oy=95 + DF*S)
W1, H1 = int(150 + ROOM_W*S + 175), int(95 + ROOM_L*S + 95)

# grid 0.5 m
gx = -2.5
while gx <= 2.5001:
    p.line(gx, yF, gx, yR, "grid"); gx += 0.5
gy = yR
k = 0
while gy <= yF + 1e-6:
    p.line(-2.5, gy, 2.5, gy, "grid"); gy += 0.5
# walls
p.rect(-2.5, yF, 2.5, yR, "wall")
p.text(-2.38, yF - 0.22, "前墙", "walltag", "start")
p.text(-2.38, yR + 0.12, "后墙", "walltag", "start")

# listening circle
p.circle(0, 0, r, "ring")

# positions
L = pol(r, -30); R = pol(r, 30); C = pol(r, 0)
Ls = pol(r, -110); Rs = pol(r, 110)
Ltm = (-1.0, 0.23); Rtm = (1.0, 0.23); TOPZ = 2.5; EAR = 1.2
SUB = (-1.90, 2.40)

# azimuth guide lines (floor speakers)
for (x, y) in (L, R, C, Ls, Rs):
    p.line(0, 0, x, y, "azi")
# angle arcs
p.arc(0.78, 0, 30, "anglearc")
p.text(*pol(0.92, 15), "30°", "angtext")
p.arc(0.55, -110, 0, "anglearc")
p.text(*pol(0.68, -100), "110°", "angtext")

# radius tag
rx, ry = pol(r, -150)
p.line(0, 0, rx, ry, "radius")
mx, my = pol(1.25, -150)
p.text(mx - 0.08, my, "r = 2.0 m", "dimtext", "end")

# speakers
p.speaker(*C, 0.46, 0.24, "g-c")
for pt in (L, R): p.speaker(*pt, 0.30, 0.28, "g-f")
for pt in (Ls, Rs): p.speaker(*pt, 0.30, 0.26, "g-s")
for pt in (Ltm, Rtm): p.speaker(*pt, 0.28, 0.28, "g-t", top=True)
p.rect(SUB[0]-0.2, SUB[1]+0.2, SUB[0]+0.2, SUB[1]-0.2, "box g-l")
for pt, g in ((L, "g-f"), (R, "g-f"), (C, "g-c"), (Ls, "g-s"), (Rs, "g-s"), (Ltm, "g-t"), (Rtm, "g-t")):
    p.aim(*pt, g, shorten=0.2)
p.head()

# labels
p.label2(L[0]-0.24, L[1]+0.02, ("L", "左前置"), "方位 −30°", "end", "g-f")
p.label2(R[0]+0.24, R[1]+0.02, ("R", "右前置"), "方位 +30°", "start", "g-f")
p.label2(0, C[1]+0.30, ("C", "中置"), None, "middle", "g-c")
p.text(0.30, C[1]+0.30, "0°", "sub", "start")
p.label2(Ls[0]+0.02, Ls[1]-0.33, ("Ls", "左环绕"), "方位 −110°", "middle", "g-s")
p.label2(Rs[0]-0.02, Rs[1]-0.33, ("Rs", "右环绕"), "方位 +110°", "middle", "g-s")
p.label2(Ltm[0], Ltm[1]+0.42, ("Ltm", "左顶中"), "吊顶 · 高 2.5 m", "middle", "g-t")
p.label2(Rtm[0], Rtm[1]+0.42, ("Rtm", "右顶中"), "吊顶 · 高 2.5 m", "middle", "g-t")
p.label2(SUB[0]+0.28, SUB[1]+0.02, ("LFE", "低音炮"), "地面 · 偏离中线", "start", "g-l")
p.text(0, -0.36, "听音位 MLP", "sub", "middle")

# dimensions
p.dim_h(-2.5, 2.5, yF + 0.42, "5.00 m", ext_from=yF)
p.dim_v(yF, yR, -2.5 - 0.55, "6.00 m", ext_from=-2.5)
p.dim_v(yF, 0, 2.5 + 0.45, "2.73 m", ext_from=2.5, side="right")
p.dim_v(0, yR, 2.5 + 0.45, "3.27 m", ext_from=2.5, side="right")
p.line(2.5, 0, 2.5 + 0.49, 0, "ext")
p.dim_h(Ls[0], Rs[0], -1.42, "3.76 m（环绕间距）", ext_from=Ls[1] - 0.15)

# room facts
p.text(0, yR + 0.95, "房间 6.0 × 5.0 m · 层高 2.8 m · 30 m²", "roomtag")
p.text(0, yR + 0.62, "参考面积 20–40 m²", "roomtag2")
p.scalebar(-2.5, yR - 0.42, 2, 0.5)
fig1a = p.svg(W1, H1, "图1A 录音棚 5.1.2 平面图")

checks.append(("1A L", L)); checks.append(("1A Ls", Ls))
checks.append(("1A Ltm lateral elev", math.degrees(math.atan2(TOPZ-EAR, abs(Ltm[0])))))
checks.append(("1A Ltm side angle", math.degrees(math.atan2(TOPZ-EAR, Ltm[1]))))
checks.append(("1A Ltm dist", math.sqrt(Ltm[0]**2 + Ltm[1]**2 + (TOPZ-EAR)**2)))
checks.append(("1A Ltm plan az", math.degrees(math.atan2(abs(Ltm[0]), Ltm[1]))))
checks.append(("1A Ls to side wall", 2.5 - abs(Ls[0])))
checks.append(("1A C to front wall", yF - C[1]))
checks.append(("1A MLP fraction of length", DF / ROOM_L))
checks.append(("1A volume", ROOM_W*ROOM_L*CEIL))

# ---------------- FIG 1A section (front view, looking at front wall)
S2 = 62
q = Plan(S2, ox=70 + 2.5*S2, oy=30 + CEIL*S2)   # here y = height z
W1s, H1s = int(70 + 5.0*S2 + 90), int(30 + CEIL*S2 + 46)
q.rect(-2.5, CEIL, 2.5, 0, "wall")
q.line(-2.5, EAR, 2.5, EAR, "earline")
q.text(0, EAR - 0.36, "耳高 1.2 m", "sub", "middle")
# floor-layer speakers (projected)
for x, g in ((-1.88, "g-s"), (-1.0, "g-f"), (1.0, "g-f"), (1.88, "g-s")):
    q.rect(x - 0.13, EAR + 0.15, x + 0.13, EAR - 0.15, f"box {g} faint")
# tops, tilted toward head
for sx in (-1.0, 1.0):
    ang = math.degrees(math.atan2(-sx, -(TOPZ - EAR)))  # rotate so face points to head
    X, Y = q.px(sx), q.py(TOPZ)
    w, d = 0.28 * S2, 0.24 * S2
    q.add(f'<g transform="translate({f(X)} {f(Y)}) rotate({-math.degrees(math.atan2(sx, (TOPZ-EAR))):.1f})">'
          f'<rect class="box g-t" x="{f(-w/2)}" y="{f(-d/2)}" width="{f(w)}" height="{f(d)}" rx="2"/>'
          f'<line class="face g-t" x1="{f(-w/2+2)}" y1="{f(d/2)}" x2="{f(w/2-2)}" y2="{f(d/2)}"/></g>')
    q.line(0, EAR, sx * 0.9, EAR + (TOPZ - EAR) * 0.9, "aim g-t")
# head
q.circle(0, EAR, 0.12, "head")
# elevation angle arc on right
el = math.degrees(math.atan2(TOPZ - EAR, 1.0))
Rarc = 0.55 * S2
X0, Y0 = q.px(0), q.py(EAR)
x2, y2 = X0 + Rarc * math.cos(math.radians(el)), Y0 - Rarc * math.sin(math.radians(el))
q.add(f'<path class="anglearc" d="M{f(X0+Rarc)} {f(Y0)} A{f(Rarc)} {f(Rarc)} 0 0 0 {f(x2)} {f(y2)}"/>')
q.add(f'<text class="angtext" x="{f(X0 + Rarc + 6)}" y="{f(Y0 - 12)}" text-anchor="start">{el:.0f}°</text>')
q.text(-1.0, TOPZ - 0.42, "Ltm", "abbr g-t")
q.text(1.0, TOPZ - 0.42, "Rtm", "abbr g-t")
q.dim_v(CEIL, 0, 2.5 + 0.42, "层高 2.80", ext_from=2.5, side="right")
q.dim_v(TOPZ, 0, -2.5 - 0.42, "顶箱 2.50", ext_from=-1.15)
q.text(0, -0.42, "A–A 剖面（从听音位看向前墙）", "sub", "middle")
fig1a_sec = q.svg(W1s, H1s, "图1A 剖面：天空声道高度与仰角", "section")

# ================================================================ FIG 1B desk
S = 200
r = 1.0
FW, FD = 2.4, 2.0             # footprint
WALL_Y = 1.30
DESK = (-0.8, 1.2, 0.8, 0.4)  # x1, y_back, x2, y_front
p = Plan(S, ox=110 + FW/2*S, oy=78 + WALL_Y*S)
W2, H2 = int(110 + FW*S + 120), int(78 + FD*S + 92)
yB = WALL_Y - FD
# grid 0.25? keep 0.5
gx = -1.0
while gx <= 1.0001:
    p.line(gx, WALL_Y, gx, yB, "grid"); gx += 0.5
gy = WALL_Y - 0.3
while gy >= yB - 1e-6:
    p.line(-1.2, gy, 1.2, gy, "grid"); gy -= 0.5
p.rect(-1.2, WALL_Y, 1.2, yB, "footprint")
p.line(-1.45, WALL_Y, 1.45, WALL_Y, "wallline")
p.text(-1.42, WALL_Y + 0.06, "墙", "walltag", "start")
# desk
p.rect(DESK[0], DESK[1], DESK[2], DESK[3], "desk")
p.text(0.62, DESK[3] + 0.06, "桌面", "walltag", "end")
# monitor
p.rect(-0.31, 1.13, 0.31, 1.10, "monitor")
p.text(0.36, 1.10, "显示器", "walltag", "start")
# chair
p.add(f'<rect class="chair" x="{f(p.px(-0.28))}" y="{f(p.py(0.12))}" width="{f(0.56*S)}" height="{f(0.56*S)}" rx="18"/>')
p.circle(0, 0, r, "ring")

L = pol(r, -30); R = pol(r, 30); C = pol(r, 0)
Ls = pol(r, -110); Rs = pol(r, 110)
Ltm = (-0.5, 0.12); Rtm = (0.5, 0.12); TOPZ_D = 1.9
SUB = (-1.0, 1.12)
for (x, y) in (L, R, C, Ls, Rs):
    p.line(0, 0, x, y, "azi")
p.arc(0.62, 0, 30, "anglearc")
p.text(*pol(0.72, 15), "30°", "angtext")
p.arc(0.45, -110, 0, "anglearc")
p.text(*pol(0.55, -100), "110°", "angtext")
rx, ry = pol(r, -150)
p.line(0, 0, rx, ry, "radius")
mx, my = pol(0.62, -150)
p.text(mx - 0.05, my - 0.02, "r = 1.0 m", "dimtext", "end")

p.speaker(*C, 0.32, 0.15, "g-c")
for pt in (L, R): p.speaker(*pt, 0.17, 0.21, "g-f")
for pt in (Ls, Rs): p.speaker(*pt, 0.17, 0.20, "g-s")
for pt in (Ltm, Rtm): p.speaker(*pt, 0.16, 0.18, "g-t", top=True)
p.rect(SUB[0]-0.14, SUB[1]+0.14, SUB[0]+0.14, SUB[1]-0.14, "box g-l")
for pt, g in ((L, "g-f"), (R, "g-f"), (C, "g-c"), (Ls, "g-s"), (Rs, "g-s"), (Ltm, "g-t"), (Rtm, "g-t")):
    p.aim(*pt, g, shorten=0.13)
p.head()

p.label2(L[0]-0.14, L[1]-0.18, ("L", "左前置"), "−30° · 桌面", "end", "g-f")
p.label2(R[0]+0.14, R[1]-0.18, ("R", "右前置"), "+30° · 桌面", "start", "g-f")
p.label2(0.06, C[1]-0.18, ("C", "中置"), "0°", "start", "g-c")
p.label2(Ls[0], Ls[1]+0.20, ("Ls", "左环绕"), "−110° · 落地架", "middle", "g-s")
p.label2(Rs[0], Rs[1]+0.20, ("Rs", "右环绕"), "+110° · 落地架", "middle", "g-s")
p.label2(Ltm[0]-0.13, Ltm[1]+0.02, ("Ltm", "左顶中"), "吊装 · 高 1.9 m", "end", "g-t")
p.label2(Rtm[0]+0.13, Rtm[1]+0.02, ("Rtm", "右顶中"), "吊装 · 高 1.9 m", "start", "g-t")
p.label2(SUB[0], SUB[1]-0.27, ("LFE", "低音炮"), "桌旁地面", "middle", "g-l")
p.text(0, -0.21, "听音位", "sub", "middle")

# dimensions
p.dim_h(-1.2, 1.2, WALL_Y + 0.22, "2.40 m（建议占地宽）", ext_from=WALL_Y)
p.dim_v(WALL_Y, yB, -1.2 - 0.26, "2.00 m（建议占地深）", ext_from=-1.2)
p.dim_h(DESK[0], DESK[2], 0.30, "桌宽 1.60 m")
p.dim_v(DESK[1], DESK[3], 1.2 + 0.24, "桌深 0.80", ext_from=0.8, side="right")
p.dim_v(DESK[3], 0, 1.2 + 0.24, "0.40", ext_from=0.8, side="right")
p.line(0.12, 0, 1.2 + 0.28, 0, "ext")
p.text(0.60, yB + 0.10, "占地约 2.4 × 2.0 m ≈ 4.8 m²", "roomtag")
p.scalebar(-1.2, yB - 0.20, 1, 0.25)
fig1b = p.svg(W2, H2, "图1B 桌面近场 5.1.2 平面图")

checks.append(("1B Ls", Ls))
checks.append(("1B Ltm lateral elev", math.degrees(math.atan2(TOPZ_D-EAR, abs(Ltm[0])))))
checks.append(("1B Ltm side angle", math.degrees(math.atan2(TOPZ_D-EAR, Ltm[1]))))
checks.append(("1B Ltm dist", math.sqrt(Ltm[0]**2 + Ltm[1]**2 + (TOPZ_D-EAR)**2)))
checks.append(("1B L to desk front edge", L[1] - DESK[3]))
checks.append(("1B footprint area", FW*FD))

# ---------------- FIG 1B section (front view)
S2 = 100
CEIL_D = 2.4
q = Plan(S2, ox=70 + 1.2*S2, oy=30 + CEIL_D*S2)
W2s, H2s = int(70 + 2.4*S2 + 100), int(30 + CEIL_D*S2 + 46)
q.line(-1.2, 0, 1.2, 0, "floor")
q.line(-1.2, CEIL_D, 1.2, CEIL_D, "ceil")
q.text(0, CEIL_D - 0.14, "最低层高 2.4 m", "walltag", "middle")
q.rect(-0.8, 0.75, 0.8, 0.72, "desk")
q.line(-0.74, 0.72, -0.74, 0, "deskleg"); q.line(0.74, 0.72, 0.74, 0, "deskleg")
q.line(-1.2, EAR, 1.2, EAR, "earline")
q.text(0, EAR - 0.22, "耳高 1.2 m", "sub", "middle")
for x, g in ((-0.5, "g-f"), (0.5, "g-f")):
    q.rect(x - 0.085, 1.27, x + 0.085, 0.95, f"box {g} faint")
    q.rect(x - 0.06, 0.95, x + 0.06, 0.75, "stand")
for x in (-0.94, 0.94):
    q.rect(x - 0.085, 1.30, x + 0.085, 1.10, "box g-s faint")
    q.line(x, 1.10, x, 0.02, "stand-l")
    q.line(x - 0.14, 0.01, x + 0.14, 0.01, "stand-l")
for sx in (-0.5, 0.5):
    X, Y = q.px(sx), q.py(TOPZ_D)
    w, d = 0.16 * S2, 0.15 * S2
    q.add(f'<g transform="translate({f(X)} {f(Y)}) rotate({-math.degrees(math.atan2(sx, (TOPZ_D-EAR))):.1f})">'
          f'<rect class="box g-t" x="{f(-w/2)}" y="{f(-d/2)}" width="{f(w)}" height="{f(d)}" rx="2"/>'
          f'<line class="face g-t" x1="{f(-w/2+2)}" y1="{f(d/2)}" x2="{f(w/2-2)}" y2="{f(d/2)}"/></g>')
    q.line(sx, TOPZ_D + 0.08, sx, CEIL_D, "stand-l")
    q.line(0, EAR, sx * 0.85, EAR + (TOPZ_D - EAR) * 0.85, "aim g-t")
q.circle(0, EAR, 0.09, "head")
el = math.degrees(math.atan2(TOPZ_D - EAR, 0.5))
Rarc = 0.30 * S2
X0, Y0 = q.px(0), q.py(EAR)
x2, y2 = X0 + Rarc * math.cos(math.radians(el)), Y0 - Rarc * math.sin(math.radians(el))
q.add(f'<path class="anglearc" d="M{f(X0+Rarc)} {f(Y0)} A{f(Rarc)} {f(Rarc)} 0 0 0 {f(x2)} {f(y2)}"/>')
q.add(f'<text class="angtext" x="{f(X0 + Rarc + 5)}" y="{f(Y0 - 9)}" text-anchor="start">{el:.0f}°</text>')
q.text(-0.5 - 0.16, TOPZ_D + 0.02, "Ltm", "abbr g-t", "end")
q.text(0.5 + 0.16, TOPZ_D + 0.02, "Rtm", "abbr g-t", "start")
q.dim_v(TOPZ_D, 0, -1.2 - 0.28, "顶箱 1.90", ext_from=-0.6)
q.dim_v(0.75, 0, 1.2 + 0.30, "桌高 0.75", ext_from=0.8, side="right")
q.text(0, -0.40, "剖面（从座位看向显示器）", "sub", "middle")
fig1b_sec = q.svg(W2s, H2s, "图1B 剖面：桌面近场高度", "section")

# ================================================================ FIG 2 coverage (polar)
R0 = 205
CX, CY = 400, 372
W3, H3 = 800, 760
parts = []
def P(r, az):
    return (CX + r * R0 * math.sin(math.radians(az)), CY - r * R0 * math.cos(math.radians(az)))
def sector(r1, r2, a1, a2, cls):
    (x1, y1), (x2, y2) = P(r2, a1), P(r2, a2)
    (x3, y3), (x4, y4) = P(r1, a2), P(r1, a1)
    large = 1 if (a2 - a1) > 180 else 0
    return (f'<path class="{cls}" d="M{f(x1)} {f(y1)} A{f(r2*R0)} {f(r2*R0)} 0 {large} 1 {f(x2)} {f(y2)} '
            f'L{f(x3)} {f(y3)} A{f(r1*R0)} {f(r1*R0)} 0 {large} 0 {f(x4)} {f(y4)} Z"/>')
def T(x, y, s, cls, anchor="middle"):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}">{s}</text>'

RIN, ROUT = 0.17, 0.86
parts.append(sector(RIN, ROUT, -15, 15, "zone g-c"))
parts.append(sector(RIN, ROUT, 15, 70, "zone g-f"))
parts.append(sector(RIN, ROUT, -70, -15, "zone g-f"))
parts.append(sector(RIN, ROUT, 70, 180, "zone g-s"))
parts.append(sector(RIN, ROUT, -180, -70, "zone g-s"))
# boundaries
for a in (-15, 15, -70, 70, 180):
    x1, y1 = P(RIN, a); x2, y2 = P(0.93, a)
    parts.append(f'<line class="bound" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')
# boundary labels
for a, s in ((-15, "−15°"), (15, "+15°"), (-70, "−70°"), (70, "+70°"), (180, "180°")):
    x, y = P(0.94, a)
    anchor = "middle"
    if 20 < a < 160: anchor = "start"
    if -160 < a < -20: anchor = "end"
    dy = 4 if abs(a) not in (15,) else -2
    if a == 180: dy = 14
    parts.append(T(x + (4 if anchor == "start" else -4 if anchor == "end" else 0), y + dy, s, "angtext", anchor))
# zone labels
def zl(r, az, a, b, g):
    x, y = P(r, az)
    parts.append(f'<text class="zlab" x="{f(x)}" y="{f(y-4)}" text-anchor="middle"><tspan class="abbr {g}">{a}</tspan></text>')
    parts.append(T(x, y + 13, b, "zsub"))
zl(0.52, 0, "C", "正前方", "g-c")
zl(0.56, -43, "L", "左前方", "g-f")
zl(0.56, 43, "R", "右前方", "g-f")
zl(0.55, -125, "Ls", "左侧 → 左后", "g-s")
zl(0.55, 125, "Rs", "右侧 → 右后", "g-s")
x, y = P(0.60, 180)
parts.append(T(x, y + 4, "正后方：Ls + Rs 拼出", "zsub"))
# speaker circle
parts.append(f'<circle class="ring" cx="{CX}" cy="{CY}" r="{R0}"/>')
# clarity band
def band(a1, a2, cls):
    parts.append(sector(1.16, 1.22, a1, a2, cls))
band(-30, 30, "clar c1")
band(30, 110, "clar c2"); band(-110, -30, "clar c2")
band(110, 250, "clar c3")
x, y = P(1.31, 0); parts.append(T(x, y + 2, "清晰 · 相邻音箱只隔 30°", "clartext"))
for sgn in (1, -1):
    x, y = P(1.30, 70 * sgn)
    anc = "start" if sgn > 0 else "end"
    parts.append(T(x, y - 4, "较虚", "clartext", anc))
    parts.append(T(x, y + 12, "间隔 80°", "zsub", anc))
x, y = P(1.30, 180); parts.append(T(x, y + 12, "弱 · Ls 与 Rs 之间隔 140°", "clartext"))
# speakers on circle
def spk(az, w, d, g, lab, labr=1.08):
    x, y = P(1.0, az)
    parts.append(f'<g transform="translate({f(x)} {f(y)}) rotate({az:.1f})">'
                 f'<rect class="box {g}" x="{f(-w/2)}" y="{f(-d/2)}" width="{w}" height="{d}" rx="2"/>'
                 f'<line class="face {g}" x1="{f(-w/2+2)}" y1="{f(d/2)}" x2="{f(w/2-2)}" y2="{f(d/2)}"/></g>')
    lx, ly = P(labr, az)
    return lx, ly
for az, g, lab in ((0, "g-c", "C 0°"), (-30, "g-f", "L −30°"), (30, "g-f", "R +30°"),
                   (-110, "g-s", "Ls −110°"), (110, "g-s", "Rs +110°")):
    lx, ly = spk(az, 34 if g == "g-c" else 24, 20, g, lab)
    # label placed inside the ring, just before the speaker
    ix, iy = P(0.91, az) if False else (lx, ly)
for az, s, anc, dx, dy in ((0, "C 0°", "start", 24, -12), (-30, "L −30°", "end", -16, -6), (30, "R +30°", "start", 16, -6),
                           (-110, "Ls −110°", "end", -16, 16), (110, "Rs +110°", "start", 16, 16)):
    x, y = P(1.0, az)
    parts.append(T(x + dx, y + dy, s, "spklab", anc))
# head + overhead hint
parts.append(f'<circle class="head" cx="{CX}" cy="{CY}" r="16"/>')
parts.append(f'<path class="nose" d="M{CX-6} {CY-14} L{CX} {CY-24} L{CX+6} {CY-14} Z"/>')
parts.append(T(CX, CY + 34, "↑ 头顶：Ltm / Rtm（见图 2B）", "zsub"))
# compass
parts.append(T(CX, 26, "前", "compass")); parts.append(T(CX, H3 - 10, "后", "compass"))
parts.append(T(20, CY + 6, "左", "compass", "start")); parts.append(T(W3 - 20, CY + 6, "右", "compass", "end"))
fig2 = (f'<svg class="plan" viewBox="0 0 {W3} {H3}" role="img" aria-label="图2A 水平方向分区" '
        f'xmlns="http://www.w3.org/2000/svg"><title>图2A 每组音箱负责的水平方向</title>\n' + "\n".join(parts) + "\n</svg>")

# ---------------- FIG 2B elevation (front view semicircle)
R1 = 190
CX2, CY2 = 300, 250
W4, H4 = 600, 318
parts = []
def Q(r, ang):  # ang: 0 = right horizon, 90 = zenith, 180 = left horizon
    return (CX2 + r * R1 * math.cos(math.radians(ang)), CY2 - r * R1 * math.sin(math.radians(ang)))
def sec2(r1, r2, a1, a2, cls):
    (x1, y1), (x2, y2) = Q(r2, a1), Q(r2, a2)
    (x3, y3), (x4, y4) = Q(r1, a2), Q(r1, a1)
    return (f'<path class="{cls}" d="M{f(x1)} {f(y1)} A{f(r2*R1)} {f(r2*R1)} 0 0 0 {f(x2)} {f(y2)} '
            f'L{f(x3)} {f(y3)} A{f(r1*R1)} {f(r1*R1)} 0 0 1 {f(x4)} {f(y4)} Z"/>')
parts.append(sec2(0.14, 0.86, 0, 30, "zone g-floor"))
parts.append(sec2(0.14, 0.86, 150, 180, "zone g-floor"))
parts.append(sec2(0.14, 0.86, 30, 90, "zone g-t"))
parts.append(sec2(0.14, 0.86, 90, 150, "zone g-t2"))
for a in (30, 90, 150):
    (x1, y1), (x2, y2) = Q(0.14, a), Q(0.93, a)
    parts.append(f'<line class="bound" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')
parts.append(f'<line class="earline" x1="{CX2 - R1 - 30}" y1="{CY2}" x2="{CX2 + R1 + 30}" y2="{CY2}"/>')
parts.append(f'<path class="ring" d="M{CX2 - R1} {CY2} A{R1} {R1} 0 0 1 {CX2 + R1} {CY2}"/>')
for a, s, anc in ((30, "≈30°", "start"), (150, "≈30°", "end")):
    x, y = Q(0.95, a)
    parts.append(T(x + (4 if anc == "start" else -4), y, s, "angtext", anc))
x, y = Q(0.95, 90); parts.append(T(x, y - 4, "90° 正上方", "angtext"))
# tops at elevation ~53° each side
for ang, g, s, anc, dx in ((180 - 53, "g-t", "Ltm 左顶中", "end", -14), (53, "g-t", "Rtm 右顶中", "start", 14)):
    x, y = Q(1.0, ang)
    rot = 90 - ang  # face toward center
    parts.append(f'<g transform="translate({f(x)} {f(y)}) rotate({rot:.1f})">'
                 f'<rect class="box {g}" x="-12" y="-10" width="24" height="20" rx="2"/>'
                 f'<line class="face {g}" x1="-10" y1="10" x2="10" y2="10"/></g>')
    parts.append(T(x + dx, y - 6, s, "spklab", anc))
for ang, s, anc, dx in ((180, "地面层 L / Ls", "start", 6), (0, "R / Rs 地面层", "end", -6)):
    x, y = Q(1.0, ang)
    parts.append(f'<rect class="box g-floor" x="{f(x-12)}" y="{f(y-10)}" width="24" height="20" rx="2"/>')
    parts.append(T(x + (18 if anc == "start" else -18), y + 26, s, "spklab", anc))
x, y = Q(0.55, 165); parts.append(T(x, y + 4, "地面层", "zsub"))
x, y = Q(0.55, 15); parts.append(T(x, y + 4, "地面层", "zsub"))
x, y = Q(0.52, 120); parts.append(T(x, y, "左上方", "zlab")); parts.append(T(x, y + 15, "Ltm 负责", "zsub"))
x, y = Q(0.52, 60); parts.append(T(x, y, "右上方", "zlab")); parts.append(T(x, y + 15, "Rtm 负责", "zsub"))
parts.append(f'<circle class="head" cx="{CX2}" cy="{CY2}" r="14"/>')
parts.append(T(CX2, CY2 + 34, "从正面看听音者（正视）", "zsub"))
fig2b = (f'<svg class="section" viewBox="0 0 {W4} {H4}" role="img" aria-label="图2B 上下方向分区" '
         f'xmlns="http://www.w3.org/2000/svg"><title>图2B 天空声道负责的仰角范围</title>\n' + "\n".join(parts) + "\n</svg>")

for k, v in checks:
    print(k, v if not isinstance(v, tuple) else tuple(round(t, 3) for t in v))

tpl = open(sys.argv[2], encoding="utf-8").read()
html = (tpl.replace("{{FIG1A}}", fig1a).replace("{{FIG1A_SEC}}", fig1a_sec)
           .replace("{{FIG1B}}", fig1b).replace("{{FIG1B_SEC}}", fig1b_sec)
           .replace("{{FIG2}}", fig2).replace("{{FIG2B}}", fig2b))
open(OUT, "w", encoding="utf-8").write(html)
print("written", OUT, len(html))
