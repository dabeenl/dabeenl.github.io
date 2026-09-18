#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the illustrations in _includes/figures/*.svg.  Run:  python3 _tools/make_figures.py
Pure standard library; fixed random seeds, so output is reproducible."""
import math, random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_includes" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INK, NAVY, BLUE, SKY, TINT, LINE = "#1C1C21", "#12335E", "#1E4E8C", "#6FA3E8", "#E9EFF8", "#C9D2E3"
WHITE, MUTED = "#FFFFFF", "#5F6069"
TEAL, MINT, AMBER, SAND = "#0F8B8D", "#BFE6E0", "#E8A33D", "#FCEBC8"
CORAL, BLUSH, VIOLET, LILAC, GREEN = "#E4604E", "#FBD9D3", "#6B4FBB", "#E4DCF8", "#3C9A5F"
NIGHT, NIGHT2, NIGHTLINE = "#0C1D36", "#16305A", "#27477A"
FONT = "font-family=\"'Source Sans 3', Helvetica, Arial, sans-serif\""
SERIF = "font-family=\"Georgia, 'Times New Roman', serif\""
MONO = "font-family=\"'SF Mono', Menlo, Consolas, monospace\""


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[k] + (b[k] - a[k]) * t):02X}" for k in range(3))


def pts(seq):
    return " ".join(f"{n(x)},{n(y)}" for x, y in seq)


def write(name, w, h, label, body, defs=""):
    svg = (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">'
           f"<defs>{defs}</defs>{body}</svg>\n")
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def bg_light(pid, w, h, c1=TINT, c2=WHITE):
    d = (f'<linearGradient id="{pid}-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/>'
         f'<stop offset="1" stop-color="{c2}"/></linearGradient>')
    return d, f'<rect width="{w}" height="{h}" fill="url(#{pid}-bg)"/>'


def bg_paper(pid, w, h, step=20, c1="#F4F7FC", c2=WHITE):
    d, b = bg_light(pid, w, h, c1, c2)
    d += (f'<pattern id="{pid}-grid" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
          f'<path d="M{step} 0H0V{step}" fill="none" stroke="{LINE}" stroke-width="0.6" stroke-opacity="0.7"/></pattern>')
    return d, b + f'<rect width="{w}" height="{h}" fill="url(#{pid}-grid)"/>'


def bg_dark(pid, w, h, step=24, grid=True):
    d = (f'<linearGradient id="{pid}-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NIGHT2}"/>'
         f'<stop offset="1" stop-color="{NIGHT}"/></linearGradient>')
    b = f'<rect width="{w}" height="{h}" fill="url(#{pid}-bg)"/>'
    if grid:
        d += (f'<pattern id="{pid}-grid" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
              f'<path d="M{step} 0H0V{step}" fill="none" stroke="{NIGHTLINE}" stroke-width="0.7" stroke-opacity="0.75"/></pattern>')
        b += f'<rect width="{w}" height="{h}" fill="url(#{pid}-grid)"/>'
    return d, b


def arrow_marker(pid, color, key="ah"):
    return (f'<marker id="{pid}-{key}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{color}"/></marker>')


def glow(pid, color, key="glow"):
    return (f'<radialGradient id="{pid}-{key}"><stop offset="0" stop-color="{color}" stop-opacity="0.75"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')


# ---------------------------------------------------------------- shared pieces
def surface(pid, w, h, s, cx, cy, path_color=CORAL):
    """Shaded 3-D bowl with a zig-zagging descent path."""
    R = 1.6
    fz = lambda x, y: 0.35 * (x * x + 0.55 * y * y + 0.5 * x * y)
    zmax = fz(R * 0.72, R * 0.72)
    P = lambda x, y, z: (cx + (x - y) * 0.866 * s, cy + (x + y) * 0.40 * s - z * s * 0.55)
    NR, NT = 12, 56  # polar grid, so the rim is a smooth circle
    pol = lambda r, t: (r * math.cos(t), r * math.sin(t))
    cells = []
    for k in range(NR):
        for m in range(NT):
            r0, r1 = R * k / NR, R * (k + 1) / NR
            t0, t1 = 2 * math.pi * m / NT, 2 * math.pi * (m + 1) / NT
            corners = [pol(r0, t0), pol(r1, t0), pol(r1, t1), pol(r0, t1)]
            quad = [P(x, y, fz(x, y)) for x, y in corners]
            xc, yc = pol((r0 + r1) / 2, (t0 + t1) / 2)
            zc = fz(xc, yc)
            light = 0.10 * (math.cos((t0 + t1) / 2 - 2.4))
            shade = 0.10 + 0.78 * (zc / zmax) ** 0.75 + light
            cells.append((xc + yc, quad, mix("#E4EEFC", BLUE, shade)))
    cells.sort(key=lambda c: c[0])
    out = [f'<ellipse cx="{n(cx)}" cy="{n(cy + s * 0.5)}" rx="{n(s * 1.9)}" ry="{n(s * 0.42)}" fill="{NAVY}" fill-opacity="0.10"/>']
    for _, q, col in cells:
        out.append(f'<polygon points="{pts(q)}" fill="{col}" stroke="{WHITE}" stroke-width="0.4" stroke-opacity="0.7"/>')
    x, y, path = -1.22, 0.98, []
    for _ in range(11):
        path.append(P(x, y, fz(x, y) + 0.03))
        gx, gy = 0.35 * (2 * x + 0.5 * y), 0.35 * (1.1 * y + 0.5 * x)
        x, y = x - 1.75 * gx, y - 1.75 * gy
    out.append(f'<polyline points="{pts(path)}" fill="none" stroke="{WHITE}" stroke-width="{n(s * 0.085)}" stroke-linejoin="round" stroke-linecap="round" stroke-opacity="0.9"/>')
    out.append(f'<polyline points="{pts(path)}" fill="none" stroke="{path_color}" stroke-width="{n(s * 0.05)}" stroke-linejoin="round" stroke-linecap="round"/>')
    for k, (px, py) in enumerate(path):
        r = s * (0.07 if k in (0, len(path) - 1) else 0.045)
        out.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r)}" fill="{AMBER if k == len(path) - 1 else path_color}" stroke="{WHITE}" stroke-width="0.8"/>')
    return "".join(out)


def network(pid, x0, x1, y0, y1, layers, seed, r=6.0, palette=(BLUE, VIOLET, CORAL), dark=False):
    rnd = random.Random(seed)
    cols = [[(x0 + (x1 - x0) * li / (len(layers) - 1), y0 + (y1 - y0) * (k + 0.5) / m) for k in range(m)]
            for li, m in enumerate(layers)]
    out = []
    for a, b in zip(cols, cols[1:]):
        for p in a:
            for q in b:
                wgt = rnd.uniform(-1, 1)
                col = (SKY if dark else BLUE) if wgt > 0 else CORAL
                out.append(f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="{col}" '
                           f'stroke-width="{n(0.5 + 1.3 * abs(wgt) ** 2)}" stroke-opacity="{n(0.12 + 0.5 * abs(wgt) ** 2)}"/>')
    for li, col in enumerate(cols):
        t = li / (len(cols) - 1)
        c = mix(palette[0], palette[1], t * 2) if t < 0.5 else mix(palette[1], palette[2], t * 2 - 1)
        for (px, py) in col:
            act = rnd.random()
            out.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r)}" fill="{mix(WHITE, c, 0.25 + 0.75 * act)}" stroke="{c}" stroke-width="1.4"/>')
    return "".join(out)


def cluster(rnd, cx, cy, sx, sy, rot, m):
    out = []
    for _ in range(m):
        a, b = rnd.gauss(0, sx), rnd.gauss(0, sy)
        out.append((cx + a * math.cos(rot) - b * math.sin(rot), cy + a * math.sin(rot) + b * math.cos(rot)))
    return out


def hull(points):
    P = sorted(set(points))
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def inside(poly, p):
    x, y, c = p[0], p[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def tour(points):
    m = len(points); d = lambda a, b: math.dist(points[a], points[b])
    order, left = [0], set(range(1, m))
    while left:
        nxt = min(left, key=lambda k: d(order[-1], k)); order.append(nxt); left.remove(nxt)
    improved = True
    while improved:
        improved = False
        for i in range(1, m - 1):
            for j in range(i + 1, m):
                a, b, c, e = order[i - 1], order[i], order[j], order[(j + 1) % m]
                if d(a, b) + d(c, e) > d(a, c) + d(b, e) + 1e-9:
                    order[i:j + 1] = reversed(order[i:j + 1]); improved = True
    return order


# ---------------------------------------------------------------- teaching (240 x 160)
def t_ma1407():
    pid = "t-ma1407"; d, b = bg_light(pid, 240, 160, "#EFEAFB", WHITE)
    b += network(pid, 34, 206, 14, 146, [4, 6, 6, 3], 7, r=7)
    write("ma1407", 240, 160, "A neural network whose layers shade from blue to violet to coral, with signed weighted edges", b, d)


def t_mno():
    pid = "t-mno"; d, b = bg_light(pid, 240, 160)
    b += surface(pid, 240, 160, 54, 120, 92)
    write("mno", 240, 160, "A shaded three-dimensional bowl with a descent path zig-zagging to its minimum", b, d)


def t_ie331():
    pid = "t-ie331"; d, b = bg_paper(pid, 240, 160, 16, "#EAF6F4", WHITE)
    poly = [(40, 132), (40, 66), (88, 30), (164, 48), (196, 132)]
    cons_cols = [SKY, VIOLET, CORAL, GREEN]
    for k, ((x1, y1), (x2, y2)) in enumerate(zip(poly[1:], poly[2:] + poly[:1])):
        dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
        b += (f'<line x1="{n(x1 - ux * 60)}" y1="{n(y1 - uy * 60)}" x2="{n(x2 + ux * 60)}" y2="{n(y2 + uy * 60)}" '
              f'stroke="{cons_cols[k % 4]}" stroke-width="1.3" stroke-opacity="0.75"/>')
    b += f'<polygon points="{pts(poly)}" fill="{TEAL}" fill-opacity="0.2" stroke="{TEAL}" stroke-width="2.2" stroke-linejoin="round"/>'
    b += f'<polyline points="40,12 40,132 228,132" fill="none" stroke="{INK}" stroke-opacity="0.6" stroke-width="1.4"/>'
    for off in (-70, -35, 0):
        b += (f'<line x1="{n(164 - 80 + off * 0.5)}" y1="{n(48 - 48 - off * 0.857)}" x2="{n(164 + 60 + off * 0.5)}" y2="{n(48 + 36 - off * 0.857)}" '
              f'stroke="{AMBER}" stroke-width="{1.8 if off == 0 else 1.1}" stroke-dasharray="5 4" stroke-opacity="{1 if off == 0 else 0.7}"/>')
    d += arrow_marker(pid, AMBER)
    b += f'<line x1="104" y1="104" x2="128" y2="64" stroke="{AMBER}" stroke-width="2.6" marker-end="url(#{pid}-ah)"/>'
    b += f'<circle cx="164" cy="48" r="13" fill="{AMBER}" fill-opacity="0.3"/><circle cx="164" cy="48" r="6" fill="{AMBER}" stroke="{WHITE}" stroke-width="1.5"/>'
    for (x, y) in poly[:2] + poly[2:3] + poly[4:]:
        b += f'<circle cx="{x}" cy="{y}" r="3.4" fill="{WHITE}" stroke="{TEAL}" stroke-width="1.6"/>'
    write("ie331", 240, 160, "A linear program: constraint lines, the feasible polygon, objective level lines, and the optimal vertex", b, d)


def t_ie539():
    pid = "t-ie539"; d, b = bg_light(pid, 240, 160, "#F1ECFB", WHITE)
    X = lambda x: 120 + x * 62; Y = lambda y: 140 - y * 44
    d += f'<clipPath id="{pid}-clip"><rect x="6" y="6" width="228" height="148" rx="6"/></clipPath>'
    curve = [(X(-1.75 + 3.5 * k / 60), Y((-1.75 + 3.5 * k / 60) ** 2)) for k in range(61)]
    b += f'<g clip-path="url(#{pid}-clip)">'
    b += f'<polygon points="{pts(curve + [(X(1.75), -10), (X(-1.75), -10)])}" fill="{VIOLET}" fill-opacity="0.12"/>'
    for k in range(-7, 8):
        a = k * 0.22
        f_ = lambda x: 2 * a * (x - a) + a * a
        b += (f'<line x1="{n(X(-2))}" y1="{n(Y(f_(-2)))}" x2="{n(X(2))}" y2="{n(Y(f_(2)))}" stroke="{AMBER}" '
              f'stroke-width="1" stroke-opacity="{n(0.35 + 0.04 * (7 - abs(k)))}"/>')
    b += f'<polyline points="{pts(curve)}" fill="none" stroke="{VIOLET}" stroke-width="3.2" stroke-linecap="round"/>'
    a1, a2 = -1.25, 0.95
    b += f'<line x1="{n(X(a1))}" y1="{n(Y(a1 * a1))}" x2="{n(X(a2))}" y2="{n(Y(a2 * a2))}" stroke="{CORAL}" stroke-width="2" stroke-dasharray="5 3"/>'
    for a in (a1, a2):
        b += f'<circle cx="{n(X(a))}" cy="{n(Y(a * a))}" r="4.6" fill="{CORAL}" stroke="{WHITE}" stroke-width="1.4"/>'
    b += f'<circle cx="{n(X(0))}" cy="{n(Y(0))}" r="4.6" fill="{WHITE}" stroke="{VIOLET}" stroke-width="2"/></g>'
    write("ie539", 240, 160, "A convex function as the upper envelope of its tangent lines, with a chord lying above it", b, d)


def t_ie631():
    pid = "t-ie631"; d, b = bg_light(pid, 240, 160, "#FDF3E1", WHITE)
    G = lambda i, j: (24 + i * 19, 146 - j * 19)
    lp = [(0.5, 1.5), (3.5, -0.45), (7.75, 2.5), (6.6, 6.7), (2.4, 7.55), (-0.35, 4.4)]
    ip = [(i, j) for i in range(0, 9) for j in range(0, 8) if inside(lp, (i, j))]
    hl = hull(ip)
    b += f'<polygon points="{pts([G(*p) for p in lp])}" fill="{AMBER}" fill-opacity="0.22" stroke="{AMBER}" stroke-width="1.6" stroke-linejoin="round"/>'
    b += f'<polygon points="{pts([G(*p) for p in hl])}" fill="{BLUE}" fill-opacity="0.22" stroke="{NAVY}" stroke-width="2.2" stroke-linejoin="round"/>'
    e = max(zip(hl, hl[1:] + hl[:1]), key=lambda pq: pq[0][0] + pq[1][0] + 0.5 * (pq[0][1] + pq[1][1]) if pq[0][0] != pq[1][0] else -1)
    (ax, ay), (bx, by) = G(*e[0]), G(*e[1])
    ux, uy = (bx - ax), (by - ay); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    b += f'<line x1="{n(ax - ux * 46)}" y1="{n(ay - uy * 46)}" x2="{n(bx + ux * 40)}" y2="{n(by + uy * 40)}" stroke="{CORAL}" stroke-width="2.2" stroke-dasharray="6 3"/>'
    for i in range(0, 9):
        for j in range(0, 8):
            x, y = G(i, j); ins = (i, j) in ip
            b += f'<circle cx="{x}" cy="{y}" r="{3 if ins else 1.9}" fill="{NAVY if ins else MUTED}" fill-opacity="{1 if ins else 0.45}"/>'
    # branch-and-bound inset
    b += f'<rect x="178" y="8" width="56" height="62" rx="7" fill="{WHITE}" stroke="{LINE}"/>'
    tree = [((206, 18), (192, 36)), ((206, 18), (220, 36)), ((192, 36), (185, 56)), ((192, 36), (199, 56)), ((220, 36), (213, 56)), ((220, 36), (227, 56))]
    for (p, q) in tree:
        b += f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="{MUTED}" stroke-width="1.1"/>'
    for (x, y, c) in [(206, 18, NAVY), (192, 36, NAVY), (220, 36, NAVY), (185, 56, CORAL), (199, 56, GREEN), (213, 56, CORAL), (227, 56, MUTED)]:
        b += f'<circle cx="{x}" cy="{y}" r="4" fill="{c}"/>'
    write("ie631", 240, 160, "A polytope, the hull of its integer points, a cutting plane, and a small branch-and-bound tree", b, d)


def t_ds801():
    pid = "t-ds801"; rnd = random.Random(11); d, b = bg_light(pid, 240, 160, "#FDEDEA", "#EEF4FD")
    nx, ny = 0.94, 0.34  # unit normal of the separator through (120, 80)
    side = lambda p: (p[0] - 120) * nx + (p[1] - 80) * ny
    A = [p for p in cluster(rnd, 66, 88, 22, 30, 0.3, 60) if side(p) < -24 and 8 < p[0] and 8 < p[1] < 152][:26]
    B = [p for p in cluster(rnd, 176, 70, 22, 30, 0.3, 60) if side(p) > 24 and p[0] < 232 and 8 < p[1] < 152][:26]
    tx, ty = -ny, nx
    band = [(120 + nx * o + tx * t, 80 + ny * o + ty * t) for o, t in ((-22, -120), (22, -120), (22, 120), (-22, 120))]
    b += f'<polygon points="{pts(band)}" fill="{WHITE}" fill-opacity="0.85"/>'
    for o, col, wd, dash in ((-22, CORAL, 1.3, "5 4"), (22, BLUE, 1.3, "5 4"), (0, INK, 2.6, "")):
        b += (f'<line x1="{n(120 + nx * o - tx * 120)}" y1="{n(80 + ny * o - ty * 120)}" x2="{n(120 + nx * o + tx * 120)}" y2="{n(80 + ny * o + ty * 120)}" '
              f'stroke="{col}" stroke-width="{wd}" {"stroke-dasharray=" + chr(34) + dash + chr(34) if dash else ""}/>')
    sv = [((120 - 22 * nx + tx * -34, 80 - 22 * ny + ty * -34), CORAL), ((120 - 22 * nx + tx * 40, 80 - 22 * ny + ty * 40), CORAL), ((120 + 22 * nx + tx * 6, 80 + 22 * ny + ty * 6), BLUE)]
    for p in A: b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.6" fill="{CORAL}" fill-opacity="0.85"/>'
    for p in B: b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.6" fill="{BLUE}" fill-opacity="0.85"/>'
    for p, c in sv:
        b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="7.5" fill="none" stroke="{INK}" stroke-width="1.3"/><circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.8" fill="{c}"/>'
    write("ds801", 240, 160, "Two clouds of data separated by a maximum-margin line, with the support vectors circled", b, d)


def t_combopt():
    pid = "t-combopt"; rnd = random.Random(5); d, b = bg_light(pid, 240, 160, "#E6F5F2", WHITE)
    P = []
    while len(P) < 22:
        p = (rnd.uniform(18, 222), rnd.uniform(16, 144))
        if all(math.dist(p, q) > 26 for q in P): P.append(p)
    for i, p in enumerate(P):
        for j in sorted(range(len(P)), key=lambda k: math.dist(p, P[k]))[1:4]:
            b += f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(P[j][0])}" y2="{n(P[j][1])}" stroke="{TEAL}" stroke-opacity="0.28" stroke-width="1"/>'
    order = tour(P)
    b += f'<polygon points="{pts([P[k] for k in order])}" fill="{TEAL}" fill-opacity="0.07" stroke="{CORAL}" stroke-width="2.6" stroke-linejoin="round"/>'
    for k, p in enumerate(P):
        b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="4.6" fill="{AMBER if k == 0 else WHITE}" stroke="{NAVY}" stroke-width="1.8"/>'
    write("combopt", 240, 160, "A short tour through scattered points drawn over their nearest-neighbour graph", b, d)


# ---------------------------------------------------------------- projects (480 x 300)
def p_src():
    pid = "p-src"; d, b = bg_paper(pid, 480, 300, 20)
    O, b1, b2 = (140, 206), (60, -10), (24, -52)
    L = lambda i, j: (O[0] + i * b1[0] + j * b2[0], O[1] + i * b1[1] + j * b2[1])
    d += f'<clipPath id="{pid}-clip"><rect x="10" y="10" width="330" height="280" rx="10"/></clipPath>' + arrow_marker(pid, NAVY) + arrow_marker(pid, CORAL, "ahc")
    b += f'<g clip-path="url(#{pid}-clip)">'
    for k in range(-8, 12):
        p, q = L(-8, k), L(12, k); b += f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="{BLUE}" stroke-opacity="0.18"/>'
        p, q = L(k, -8), L(k, 12); b += f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="{BLUE}" stroke-opacity="0.18"/>'
    b += f'<polygon points="{pts([L(0, 0), L(1, 0), L(1, 1), L(0, 1)])}" fill="{AMBER}" fill-opacity="0.4" stroke="{AMBER}" stroke-width="1.4"/>'
    b += f'<circle cx="{O[0]}" cy="{O[1]}" r="{n(math.hypot(*b2))}" fill="{TEAL}" fill-opacity="0.08" stroke="{TEAL}" stroke-width="1.4" stroke-dasharray="5 4"/>'
    for i in range(-8, 12):
        for j in range(-8, 12):
            x, y = L(i, j)
            if 0 < x < 350 and 0 < y < 300: b += f'<circle cx="{n(x)}" cy="{n(y)}" r="3.1" fill="{BLUE}" fill-opacity="0.8"/>'
    for (i, j) in ((3, 1), (1, 2)):
        x, y = L(i, j); b += f'<line x1="{O[0]}" y1="{O[1]}" x2="{n(x)}" y2="{n(y)}" stroke="{CORAL}" stroke-width="2" stroke-dasharray="7 4" marker-end="url(#{pid}-ahc)"/>'
    for (i, j) in ((1, 0), (0, 1)):
        x, y = L(i, j); b += f'<line x1="{O[0]}" y1="{O[1]}" x2="{n(x)}" y2="{n(y)}" stroke="{NAVY}" stroke-width="3.4" marker-end="url(#{pid}-ah)"/>'
    b += f'<circle cx="{O[0]}" cy="{O[1]}" r="5.5" fill="{NAVY}" stroke="{WHITE}" stroke-width="1.5"/></g>'
    rnd = random.Random(3)
    for r_ in range(5):
        bits = "".join(rnd.choice("01") for _ in range(9))
        b += f'<text x="362" y="{36 + r_ * 17}" font-size="12.5" {MONO} fill="{BLUE}" fill-opacity="{n(0.25 + 0.13 * r_)}">{bits}</text>'
    b += (f'<path d="M392 176 v-22 a26 26 0 0 1 52 0 v22" fill="none" stroke="{NAVY}" stroke-width="9" stroke-linecap="round"/>'
          f'<rect x="374" y="174" width="88" height="78" rx="12" fill="{NAVY}"/><rect x="374" y="174" width="88" height="30" rx="12" fill="{BLUE}"/>'
          f'<circle cx="418" cy="206" r="10" fill="{AMBER}"/><path d="M413 210 h10 l3 24 h-16 z" fill="{AMBER}"/>')
    write("p-src", 480, 300, "A lattice with a reduced basis, a long basis, its fundamental cell and shortest-vector ball, beside a padlock fed by a bit stream", b, d)


def p_sota():
    pid = "p-sota"; rnd = random.Random(2); d, b = bg_dark(pid, 480, 300, grid=False)
    d += glow(pid, SKY)
    for _ in range(70):
        b += f'<circle cx="{n(rnd.uniform(0, 480))}" cy="{n(rnd.uniform(0, 300))}" r="{n(rnd.uniform(0.5, 1.5))}" fill="{WHITE}" fill-opacity="{n(rnd.uniform(0.2, 0.8))}"/>'
    for rx, ry in ((120, 52), (178, 88), (226, 124)):
        b += f'<ellipse cx="240" cy="150" rx="{rx}" ry="{ry}" fill="none" stroke="{SKY}" stroke-opacity="0.28" stroke-width="1" stroke-dasharray="2 5" transform="rotate(-12 240 150)"/>'
    agents = [("∑", 92, 74, AMBER), ("∫", 384, 70, MINT), ("π", 56, 196, CORAL), ("∀", 424, 204, "#B9A6F2"), ("∂", 170, 262, SKY), ("∞", 318, 264, "#F5C56B")]
    for s_, x, y, c in agents:
        mx, my = (x + 240) / 2 + (y - 150) * 0.18, (y + 150) / 2 - (x - 240) * 0.18
        b += f'<path d="M240 150 Q {n(mx)} {n(my)} {x} {y}" fill="none" stroke="{c}" stroke-width="1.8" stroke-opacity="0.85"/>'
        for t in (0.35, 0.62):
            px = (1 - t) ** 2 * 240 + 2 * (1 - t) * t * mx + t * t * x; py = (1 - t) ** 2 * 150 + 2 * (1 - t) * t * my + t * t * y
            b += f'<circle cx="{n(px)}" cy="{n(py)}" r="2.8" fill="{c}"/>'
    b += f'<circle cx="240" cy="150" r="78" fill="url(#{pid}-glow)"/><circle cx="240" cy="150" r="40" fill="{BLUE}" stroke="{SKY}" stroke-width="2.5"/>'
    b += f'<text x="240" y="160" text-anchor="middle" font-size="28" font-weight="700" {FONT} fill="{WHITE}">AI</text>'
    for s_, x, y, c in agents:
        b += (f'<circle cx="{x}" cy="{y}" r="26" fill="{NIGHT}" stroke="{c}" stroke-width="2.5"/>'
              f'<text x="{x}" y="{y + 9}" text-anchor="middle" font-size="27" {SERIF} fill="{c}">{s_}</text>')
    write("p-sota", 480, 300, "A glowing AI hub orchestrating colour-coded agents labelled with mathematical symbols against a night sky", b, d)


def p_ssm():
    pid = "p-ssm"; d, b = bg_light(pid, 480, 300, "#F2EDFC", WHITE)
    d += arrow_marker(pid, NAVY)
    lanes = [(22, NAVY, 1, 3.4), (84, VIOLET, 3, 2.8), (146, CORAL, 9, 2.2)]
    for y0, col, freq, wd in lanes:
        b += f'<rect x="20" y="{y0}" width="440" height="50" rx="12" fill="{WHITE}" stroke="{mix(WHITE, col, 0.45)}" stroke-width="1.4"/>'
        wave = [(30 + 420 * k / 240, y0 + 25 - 16 * math.sin(2 * math.pi * freq * k / 240 + 0.6) * (0.75 + 0.25 * math.sin(2 * math.pi * k / 240))) for k in range(241)]
        b += f'<polyline points="{pts(wave)}" fill="none" stroke="{col}" stroke-width="{wd}" stroke-linecap="round" stroke-linejoin="round"/>'
    for x in (130, 240, 350):
        b += f'<line x1="{x}" y1="146" x2="{x}" y2="137" stroke="{NAVY}" stroke-width="2" marker-end="url(#{pid}-ah)"/>'
    for x in (185, 295):
        b += f'<line x1="{x}" y1="84" x2="{x}" y2="75" stroke="{NAVY}" stroke-width="2" marker-end="url(#{pid}-ah)"/>'
    cols, rows, cw, ch = 44, 7, 10, 10
    for i in range(cols):
        for j in range(rows):
            v = 0.5 + 0.5 * math.sin(i * 0.33 + j * 0.9) * math.cos(i * 0.11 - j * 0.35)
            v *= math.exp(-((j - 3 - 2 * math.sin(i * 0.2)) ** 2) / 7)
            b += f'<rect x="{20 + i * cw}" y="{212 + j * ch}" width="{cw - 1}" height="{ch - 1}" rx="1.5" fill="{mix("#EEE8FB", VIOLET, v * 1.5) if v < 0.55 else mix(VIOLET, AMBER, (v - 0.55) * 2.6)}"/>'
    b += f'<line x1="20" y1="204" x2="460" y2="204" stroke="{LINE}" stroke-width="1"/>'
    write("p-ssm", 480, 300, "Slow, medium and fast waves stacked above a spectrogram, suggesting a hierarchical spectral sequence model", b, d)


def p_swarm():
    pid = "p-swarm"; rnd = random.Random(9); d, b = bg_dark(pid, 480, 300, grid=False)
    cx, cy = 196, 178
    d += (f'<clipPath id="{pid}-clip"><rect width="480" height="300"/></clipPath>'
          f'<linearGradient id="{pid}-sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MINT}" stop-opacity="0"/><stop offset="1" stop-color="{MINT}" stop-opacity="0.55"/></linearGradient>')
    b += f'<g clip-path="url(#{pid}-clip)">'
    for r_ in (50, 100, 150, 200, 250):
        b += f'<circle cx="{cx}" cy="{cy}" r="{r_}" fill="none" stroke="{MINT}" stroke-opacity="0.3" stroke-width="1"/>'
    for a in range(0, 180, 30):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        b += f'<line x1="{n(cx - 280 * ca)}" y1="{n(cy - 280 * sa)}" x2="{n(cx + 280 * ca)}" y2="{n(cy + 280 * sa)}" stroke="{MINT}" stroke-opacity="0.16"/>'
    a0, a1 = math.radians(-62), math.radians(-20)
    b += (f'<path d="M{cx} {cy} L{n(cx + 270 * math.cos(a0))} {n(cy + 270 * math.sin(a0))} A270 270 0 0 1 {n(cx + 270 * math.cos(a1))} {n(cy + 270 * math.sin(a1))} Z" fill="url(#{pid}-sweep)" fill-opacity="0.55"/>'
          f'<line x1="{cx}" y1="{cy}" x2="{n(cx + 270 * math.cos(a1))}" y2="{n(cy + 270 * math.sin(a1))}" stroke="{MINT}" stroke-width="1.8"/>')
    for _ in range(9):
        b += f'<circle cx="{n(rnd.uniform(20, 460))}" cy="{n(rnd.uniform(20, 280))}" r="2" fill="{MINT}" fill-opacity="0.5"/>'
    drones = [(330, 92), (296, 118), (364, 118), (262, 146), (398, 146), (330, 150), (296, 176)]
    links = [(0, 1), (0, 2), (1, 3), (2, 4), (1, 5), (2, 5), (3, 6), (5, 6), (1, 2)]
    for i, j in links:
        b += f'<line x1="{drones[i][0]}" y1="{drones[i][1]}" x2="{drones[j][0]}" y2="{drones[j][1]}" stroke="{SKY}" stroke-opacity="0.75" stroke-width="1.2" stroke-dasharray="3 4"/>'
    for (x, y) in drones:
        trail = [(x - 9 * k - 3 * math.sin(k * 0.9 + x), y + 8.5 * k) for k in range(8)]
        b += f'<polyline points="{pts(trail)}" fill="none" stroke="{AMBER}" stroke-opacity="0.45" stroke-width="1.6" stroke-linecap="round"/>'
    for k, (x, y) in enumerate(drones):
        b += (f'<circle cx="{x}" cy="{y}" r="15" fill="{SKY}" fill-opacity="0.12"/>'
              f'<path transform="translate({x} {y}) rotate(46)" d="M0 -12 L9 9 L0 4 L-9 9 Z" fill="{AMBER if k == 0 else WHITE}" stroke="{NIGHT}" stroke-width="1"/>')
    b += (f'<g fill="none" stroke="{CORAL}" stroke-width="2"><circle cx="432" cy="40" r="17"/><circle cx="432" cy="40" r="7"/><path d="M432 14 v12 M432 54 v12 M406 40 h12 M446 40 h12"/></g>'
          f'<path d="M346 78 L412 50" fill="none" stroke="{CORAL}" stroke-width="1.6" stroke-dasharray="6 4"/>'
          f'<circle cx="{cx}" cy="{cy}" r="7" fill="{MINT}"/><circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="{MINT}" stroke-width="1.5"/></g>')
    write("p-swarm", 480, 300, "A radar screen with a sweeping beam tracking a linked formation of vehicles heading for a marked target", b, d)


def p_blackbox():
    pid = "p-blackbox"; d, b = bg_light(pid, 480, 300, "#FFF5E3", WHITE)
    d += arrow_marker(pid, NAVY) + arrow_marker(pid, AMBER, "aha") + glow(pid, AMBER)
    cx, cy, s = 84, 118, 46
    top = [(cx, cy - s * 1.0), (cx + s * 0.87, cy - s * 0.5), (cx, cy), (cx - s * 0.87, cy - s * 0.5)]
    left = [(cx - s * 0.87, cy - s * 0.5), (cx, cy), (cx, cy + s), (cx - s * 0.87, cy + s * 0.5)]
    right = [(cx + s * 0.87, cy - s * 0.5), (cx, cy), (cx, cy + s), (cx + s * 0.87, cy + s * 0.5)]
    b += f'<circle cx="{cx}" cy="{cy}" r="84" fill="url(#{pid}-glow)" fill-opacity="0.55"/>'
    b += f'<polygon points="{pts(top)}" fill="#3A3A44"/><polygon points="{pts(left)}" fill="{INK}"/><polygon points="{pts(right)}" fill="#2A2A33"/>'
    b += f'<text x="{cx}" y="{cy + 40}" text-anchor="middle" font-size="34" font-weight="700" {FONT} fill="{AMBER}">?</text>'
    b += f'<text x="{cx}" y="196" text-anchor="middle" font-size="15" font-style="italic" {SERIF} fill="{INK}">f(x) unknown</text>'
    b += f'<line x1="140" y1="118" x2="170" y2="118" stroke="{NAVY}" stroke-width="3" marker-end="url(#{pid}-ah)"/>'
    b += network(pid, 190, 300, 56, 180, [3, 5, 5, 3], 4, r=6.5, palette=(BLUE, TEAL, VIOLET))
    b += f'<line x1="316" y1="118" x2="346" y2="118" stroke="{NAVY}" stroke-width="3" marker-end="url(#{pid}-ah)"/>'
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    for k, v in enumerate(bits):
        b += (f'<rect x="{360 + (k % 4) * 27}" y="{44 + (k // 4) * 27}" width="23" height="23" rx="5" fill="{NAVY if v else WHITE}" stroke="{NAVY}" stroke-width="1.5"/>'
              f'<text x="{371.5 + (k % 4) * 27}" y="{61 + (k // 4) * 27}" text-anchor="middle" font-size="14" font-weight="700" {MONO} fill="{WHITE if v else NAVY}">{v}</text>')
    G = [(372, 126), (412, 112), (452, 134), (440, 176), (396, 184), (364, 162)]
    for i in range(6):
        for j in range(i + 1, 6):
            if (i + j) % 2 or j - i == 1: b += f'<line x1="{G[i][0]}" y1="{G[i][1]}" x2="{G[j][0]}" y2="{G[j][1]}" stroke="{LINE}" stroke-width="1.4"/>'
    sel = [0, 2, 3, 6 - 1]
    b += f'<polygon points="{pts([G[k] for k in (0, 1, 3, 4)])}" fill="{TEAL}" fill-opacity="0.15" stroke="{TEAL}" stroke-width="2.6" stroke-linejoin="round"/>'
    for k, (x, y) in enumerate(G):
        b += f'<circle cx="{x}" cy="{y}" r="7" fill="{TEAL if k in (0, 1, 3, 4) else WHITE}" stroke="{TEAL}" stroke-width="2"/>'
    b += f'<path d="M412 204 C 412 286, 84 286, 84 214" fill="none" stroke="{AMBER}" stroke-width="3" stroke-dasharray="9 5" marker-end="url(#{pid}-aha)"/>'
    vals = [0.25, 0.4, 0.34, 0.55, 0.5, 0.72, 0.7, 0.9]
    for k, v in enumerate(vals):
        b += f'<rect x="{176 + k * 15}" y="{n(252 - v * 40)}" width="10" height="{n(v * 40)}" rx="2" fill="{mix(MINT, TEAL, v)}"/>'
    b += f'<text x="304" y="236" font-size="13" {FONT} fill="{MUTED}">evaluations</text>'
    write("p-blackbox", 480, 300, "An opaque cube feeding a neural model that proposes a bit vector and a graph solution, with an evaluation loop back to the cube", b, d)


def p_foundation():
    pid = "p-foundation"; d, b = bg_light(pid, 480, 300, "#EAF0FB", "#F6F1FD")
    cx, cy = 240, 86
    for x, y in ((74, 60), (406, 60), (74, 240), (406, 240)):
        b += f'<path d="M240 160 C {n((x + 240) / 2)} 160, {n((x + 240) / 2)} {y}, {x} {y}" fill="none" stroke="{VIOLET}" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="3 5"/>'
    for k in range(5):
        y0 = cy + 118 - k * 26; t = k / 4; top = mix(BLUE, VIOLET, t)
        slab = [(cx, y0 - 30), (cx + 78, y0), (cx, y0 + 30), (cx - 78, y0)]
        b += f'<polygon points="{pts([(cx - 78, y0), (cx, y0 + 30), (cx, y0 + 44), (cx - 78, y0 + 14)])}" fill="{mix(top, INK, 0.45)}"/>'
        b += f'<polygon points="{pts([(cx + 78, y0), (cx, y0 + 30), (cx, y0 + 44), (cx + 78, y0 + 14)])}" fill="{mix(top, INK, 0.25)}"/>'
        b += f'<polygon points="{pts(slab)}" fill="{mix(top, WHITE, 0.12)}" stroke="{WHITE}" stroke-opacity="0.7" stroke-width="1"/>'
        for m in range(-2, 3):
            b += f'<circle cx="{cx + m * 22}" cy="{n(y0 + m * 0)}" r="3.2" fill="{WHITE}" fill-opacity="{0.9 if (m + k) % 2 == 0 else 0.35}"/>'
    tiles = [(18, 14, CORAL, BLUSH), (350, 14, TEAL, MINT), (18, 194, AMBER, SAND), (350, 194, VIOLET, LILAC)]
    for x, y, c, soft in tiles:
        b += f'<rect x="{x}" y="{y}" width="112" height="92" rx="14" fill="{WHITE}" stroke="{c}" stroke-width="2"/><rect x="{x}" y="{y}" width="112" height="92" rx="14" fill="{soft}" fill-opacity="0.35"/>'
    rnd = random.Random(8); P = []
    while len(P) < 9:
        p = (rnd.uniform(32, 116), rnd.uniform(28, 92))
        if all(math.dist(p, q) > 17 for q in P): P.append(p)
    b += f'<polygon points="{pts([P[k] for k in tour(P)])}" fill="none" stroke="{CORAL}" stroke-width="2.4" stroke-linejoin="round"/>'
    for p in P: b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.6" fill="{WHITE}" stroke="{CORAL}" stroke-width="1.8"/>'
    bars = [(0, 0, 38), (0, 42, 30), (1, 10, 26), (1, 40, 46), (2, 0, 20), (2, 24, 34), (3, 16, 50)]
    for r_, x0, wd in bars:
        b += f'<rect x="{364 + x0}" y="{28 + r_ * 17}" width="{wd}" height="12" rx="3" fill="{mix(MINT, TEAL, 0.35 + 0.2 * ((r_ + x0) % 4))}"/>'
    b += f'<rect x="38" y="208" width="72" height="66" rx="3" fill="none" stroke="{INK}" stroke-opacity="0.7" stroke-width="2"/>'
    boxes = [(40, 244, 30, 28, AMBER), (71, 252, 37, 20, CORAL), (71, 228, 20, 23, TEAL), (92, 228, 16, 23, VIOLET), (40, 222, 30, 21, BLUE), (71, 212, 37, 15, "#F5C56B")]
    for x, y, w_, h_, c in boxes: b += f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" rx="2" fill="{c}" fill-opacity="0.9"/>'
    Lp = [(372, 212 + k * 19) for k in range(4)]; Rp = [(440, 212 + k * 19) for k in range(4)]
    for i in range(4):
        for j in range(4): b += f'<line x1="{Lp[i][0]}" y1="{Lp[i][1]}" x2="{Rp[j][0]}" y2="{Rp[j][1]}" stroke="{VIOLET}" stroke-opacity="0.18"/>'
    for i, j in ((0, 2), (1, 0), (2, 3), (3, 1)): b += f'<line x1="{Lp[i][0]}" y1="{Lp[i][1]}" x2="{Rp[j][0]}" y2="{Rp[j][1]}" stroke="{VIOLET}" stroke-width="2.6"/>'
    for p in Lp: b += f'<circle cx="{p[0]}" cy="{p[1]}" r="5" fill="{VIOLET}"/>'
    for p in Rp: b += f'<circle cx="{p[0]}" cy="{p[1]}" r="5" fill="{WHITE}" stroke="{VIOLET}" stroke-width="2"/>'
    write("p-foundation", 480, 300, "A stack of model layers connected to four tasks: a tour, a schedule, a packing, and a matching", b, d)


def p_ysf():
    pid = "p-ysf"; rnd = random.Random(21); d, b = bg_paper(pid, 480, 300, 24, "#E9F6F4", WHITE)
    d += arrow_marker(pid, NAVY)
    A = cluster(rnd, 190, 170, 44, 24, -0.5, 48); Bc = cluster(rnd, 300, 120, 30, 20, 0.4, 34)
    for (cx, cy, sx, sy, rot) in ((190, 170, 44, 24, -0.5), (300, 120, 30, 20, 0.4)):
        for k, op in ((2.4, 0.10), (1.7, 0.16), (1.0, 0.24)):
            b += f'<ellipse cx="{cx}" cy="{cy}" rx="{n(sx * k)}" ry="{n(sy * k)}" transform="rotate({n(math.degrees(rot))} {cx} {cy})" fill="{TEAL}" fill-opacity="{op}" stroke="{TEAL}" stroke-opacity="0.4" stroke-width="0.8"/>'
    safe = [(84, 196), (120, 96), (236, 52), (360, 66), (392, 150), (300, 232), (150, 252)]
    b += f'<polygon points="{pts(safe)}" fill="{BLUE}" fill-opacity="0.07" stroke="{NAVY}" stroke-width="2.8" stroke-linejoin="round"/>'
    for p in A + Bc:
        ok = inside(safe, p)
        b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.6" fill="{TEAL if ok else CORAL}" fill-opacity="{0.9 if ok else 1}" stroke="{WHITE}" stroke-width="0.8"/>'
    for p in ((432, 252), (52, 60), (446, 40)):
        b += f'<circle cx="{p[0]}" cy="{p[1]}" r="3.8" fill="{CORAL}" stroke="{WHITE}" stroke-width="0.8"/>'
    mx, my = 236, 150
    b += f'<circle cx="{mx}" cy="{my}" r="62" fill="none" stroke="{VIOLET}" stroke-width="2" stroke-dasharray="7 5"/><circle cx="{mx}" cy="{my}" r="6" fill="{VIOLET}" stroke="{WHITE}" stroke-width="1.5"/>'
    b += f'<line x1="{mx}" y1="{my}" x2="380" y2="147" stroke="{NAVY}" stroke-width="2.2" marker-end="url(#{pid}-ah)"/>'
    star = [(392 + (13 if k % 2 == 0 else 5.5) * math.sin(k * math.pi / 5), 150 - (13 if k % 2 == 0 else 5.5) * math.cos(k * math.pi / 5)) for k in range(10)]
    b += f'<circle cx="392" cy="150" r="22" fill="{AMBER}" fill-opacity="0.3"/><polygon points="{pts(star)}" fill="{AMBER}" stroke="{WHITE}" stroke-width="1.2"/>'
    write("p-ysf", 480, 300, "Data clouds with density contours, a safe region covering most points, an ambiguity ball around the centre, and the chosen decision on the boundary", b, d)


def p_jedec():
    pid = "p-jedec"; rnd = random.Random(13); d, b = bg_dark(pid, 480, 300, 20)
    d += (f'<linearGradient id="{pid}-gen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>' + arrow_marker(pid, WHITE))
    b += f'<rect x="14" y="92" width="84" height="116" rx="16" fill="url(#{pid}-gen)" stroke="#B9A6F2" stroke-width="1.5"/>'
    sp = lambda cx, cy, R: f'M{cx} {cy - R} Q{cx} {cy} {cx + R} {cy} Q{cx} {cy} {cx} {cy + R} Q{cx} {cy} {cx - R} {cy} Q{cx} {cy} {cx} {cy - R}Z'
    b += f'<path d="{sp(50, 138, 24)}" fill="{WHITE}"/><path d="{sp(76, 112, 9)}" fill="{AMBER}"/><path d="{sp(30, 170, 7)}" fill="{MINT}"/>'
    b += f'<text x="56" y="196" text-anchor="middle" font-size="12" font-weight="700" letter-spacing="1.5" {FONT} fill="{WHITE}" fill-opacity="0.9">GEN AI</text>'
    rows = [("CLK", SKY), ("CS_n", MINT), ("CA", AMBER), ("DQS", CORAL), ("DQ", "#B9A6F2")]
    x0, x1, step = 150, 366, 12
    for r_, (name, col) in enumerate(rows):
        y = 40 + r_ * 50; hi, lo = y, y + 24
        b += f'<text x="142" y="{y + 18}" text-anchor="end" font-size="12" {MONO} fill="{col}">{name}</text>'
        if name in ("CA", "DQ"):
            x = x0; segs = []
            while x < x1:
                wd = step * rnd.choice((2, 3, 4)); xe = min(x + wd, x1)
                segs.append(f'M{x} {y + 12} l5 -12 H{xe - 5} l5 12 l-5 12 H{x + 5} Z'); x = xe
            b += f'<path d="{" ".join(segs)}" fill="{col}" fill-opacity="0.16" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/>'
        else:
            level, x, path = 0, x0, f"M{x0} {lo}"
            while x < x1:
                wd = step if name in ("CLK", "DQS") else step * rnd.choice((1, 2, 3, 5))
                x = min(x + wd, x1); path += f" H{x}"
                if x < x1: level ^= 1; path += f" V{hi if level else lo}"
            b += f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>'
    b += f'<line x1="246" y1="24" x2="246" y2="284" stroke="{AMBER}" stroke-width="1.4" stroke-dasharray="4 4"/><path d="M240 18 h12 l-6 9z" fill="{AMBER}"/>'
    b += f'<line x1="102" y1="150" x2="112" y2="150" stroke="{WHITE}" stroke-width="2" marker-end="url(#{pid}-ah)"/><line x1="372" y1="150" x2="384" y2="150" stroke="{WHITE}" stroke-width="2" marker-end="url(#{pid}-ah)"/>'
    b += f'<rect x="392" y="56" width="70" height="188" rx="6" fill="#1F7A4D" stroke="#2FA56A" stroke-width="1.5"/>'
    for k in range(4):
        b += f'<rect x="404" y="{68 + k * 40}" width="46" height="30" rx="3" fill="{INK}"/><rect x="410" y="{74 + k * 40}" width="34" height="4" rx="1" fill="#55565F"/>'
    for k in range(14):
        b += f'<rect x="{396 + k * 4.6:.1f}" y="230" width="3" height="12" fill="{AMBER}"/>'
    write("p-jedec", 480, 300, "A generative model emitting clock, command, address and data waveforms on a logic-analyser screen that drive a memory module", b, d)


def p_iomargin():
    pid = "p-iomargin"; rnd = random.Random(17); d, b = bg_dark(pid, 480, 300, 20)
    d += arrow_marker(pid, AMBER)
    X0, X1, YH, YL = 24, 344, 66, 234; UI = (X1 - X0) / 2
    lvl = lambda v: YH if v else YL
    for _ in range(90):
        bits = [rnd.randint(0, 1) for _ in range(4)]; jit = rnd.gauss(0, 6); rise = rnd.uniform(0.16, 0.26) * UI
        amp = rnd.gauss(0, 5); path = []
        for k in range(81):
            x = X0 + (X1 - X0) * k / 80; y = lvl(bits[0])
            for e in range(3):
                xe = X0 + UI * (e + 0.0) + jit + (rnd.gauss(0, 0.5))
                if bits[e] != bits[e + 1]:
                    s_ = 1 / (1 + math.exp(-(x - xe) / (rise / 4)))
                    y += (lvl(bits[e + 1]) - lvl(bits[e])) * s_
            ov = 9 * math.exp(-((x - X0 - jit) % UI) / 26) * math.sin(((x - X0 - jit) % UI) / 9)
            path.append((x, y + amp + ov * (1 if rnd.random() < 0.5 else -1) * 0.5))
        b += f'<polyline points="{pts(path)}" fill="none" stroke="{SKY}" stroke-width="1.2" stroke-opacity="0.24" stroke-linejoin="round"/>'
    ex, ey, ew, eh = X0 + UI * 0.5 + 34, 104, UI - 68, 92
    b += f'<rect x="{n(ex)}" y="{ey}" width="{n(ew)}" height="{eh}" rx="6" fill="{AMBER}" fill-opacity="0.22" stroke="{AMBER}" stroke-width="2" stroke-dasharray="7 4"/>'
    b += (f'<line x1="{n(ex + 8)}" y1="150" x2="{n(ex + ew - 8)}" y2="150" stroke="{AMBER}" stroke-width="2" marker-start="url(#{pid}-ah)" marker-end="url(#{pid}-ah)"/>'
          f'<line x1="{n(ex + ew / 2)}" y1="{ey + 8}" x2="{n(ex + ew / 2)}" y2="{ey + eh - 8}" stroke="{AMBER}" stroke-width="2" marker-start="url(#{pid}-ah)" marker-end="url(#{pid}-ah)"/>')
    b += f'<rect x="368" y="22" width="98" height="256" rx="12" fill="{NIGHT}" stroke="{NIGHTLINE}" stroke-width="1.5"/>'
    b += f'<text x="417" y="46" text-anchor="middle" font-size="12" font-weight="700" letter-spacing="1.5" {FONT} fill="{MINT}">TMRS</text>'
    for k, v in enumerate([1, 0, 1, 1, 0, 1]):
        y = 60 + k * 35
        b += (f'<text x="380" y="{y + 16}" font-size="11" {MONO} fill="{WHITE}" fill-opacity="0.6">r{k}</text>'
              f'<rect x="404" y="{y}" width="50" height="22" rx="11" fill="{MINT if v else "#3A4E70"}"/><circle cx="{443 if v else 415}" cy="{y + 11}" r="8" fill="{WHITE}"/>')
    write("p-iomargin", 480, 300, "An oscilloscope eye diagram built from many signal traces with its margin window marked, next to a bank of register switches", b, d)


def p_tmrs():
    pid = "p-tmrs"; rnd = random.Random(29); d, b = bg_light(pid, 480, 300, "#EEF3FB", WHITE)
    cols, rows, cs = 14, 8, 18; gx, gy = 22, 22; best, bv = None, -1; vals = {}
    for i in range(cols):
        for j in range(rows):
            v = math.exp(-((i - 9.3) ** 2 / 18 + (j - 2.6) ** 2 / 7)) * 0.85 + 0.28 * math.exp(-((i - 2.5) ** 2 / 5 + (j - 5.5) ** 2 / 4)) + rnd.uniform(0, 0.13)
            vals[i, j] = v
            if v > bv: bv, best = v, (i, j)
    for (i, j), v in vals.items():
        c = mix("#F1F5FC", BLUE, (v / bv) ** 1.3) if v / bv < 0.8 else mix(BLUE, NAVY, (v / bv - 0.8) * 5)
        b += f'<rect x="{gx + i * cs}" y="{gy + j * cs}" width="{cs - 2}" height="{cs - 2}" rx="3" fill="{c}"/>'
    b += f'<rect x="{gx + best[0] * cs - 3}" y="{gy + best[1] * cs - 3}" width="{cs + 4}" height="{cs + 4}" rx="5" fill="none" stroke="{CORAL}" stroke-width="3"/>'
    b += f'<text x="{gx}" y="{gy + rows * cs + 14}" font-size="11.5" {FONT} fill="{MUTED}">register setting  ×  value</text>'
    hist, cur = [], 0.18
    for k in range(40):
        cur = max(cur, min(1.0, cur + (rnd.random() < 0.22) * rnd.uniform(0.04, 0.2))); hist.append(cur)
    px = lambda k: gx + k * (250 / 39); py = lambda v: 284 - v * 78
    step = [(px(0), py(hist[0]))]
    for k in range(1, 40): step += [(px(k), py(hist[k - 1])), (px(k), py(hist[k]))]
    b += f'<polygon points="{pts(step + [(px(39), 284), (px(0), 284)])}" fill="{TEAL}" fill-opacity="0.14"/><polyline points="{pts(step)}" fill="none" stroke="{TEAL}" stroke-width="2.6" stroke-linejoin="round"/>'
    for k in range(40):
        v = hist[k] - rnd.uniform(0.0, 0.5) * hist[k]
        b += f'<circle cx="{n(px(k))}" cy="{n(py(v))}" r="1.9" fill="{TEAL}" fill-opacity="0.45"/>'
    b += f'<line x1="{gx}" y1="284" x2="{gx + 252}" y2="284" stroke="{INK}" stroke-opacity="0.5"/><text x="{gx + 252}" y="198" text-anchor="end" font-size="11.5" {FONT} fill="{MUTED}">best margin so far</text>'
    root = (386, 30); lv = {0: [root]}
    for dpt in range(1, 5):
        m = 2 ** dpt; lv[dpt] = [(300 + (172 * (k + 0.5) / m), 30 + dpt * 58) for k in range(m)]
    good = [0, 1, 2, 5, 10]
    for dpt in range(1, 5):
        for k, p in enumerate(lv[dpt]):
            q = lv[dpt - 1][k // 2]; on = (k == good[dpt] and k // 2 == good[dpt - 1])
            pruned = not on and dpt >= 2 and (k // 2 != good[dpt - 1])
            b += f'<line x1="{n(q[0])}" y1="{n(q[1])}" x2="{n(p[0])}" y2="{n(p[1])}" stroke="{CORAL if on else LINE}" stroke-width="{3.4 if on else 1.4}" stroke-linecap="round"/>'
    for dpt in range(0, 5):
        for k, p in enumerate(lv[dpt]):
            on = k == good[dpt]; r_ = 8 - dpt * 1.1
            b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="{n(r_)}" fill="{CORAL if on else WHITE}" stroke="{CORAL if on else MUTED}" stroke-opacity="{1 if on else 0.55}" stroke-width="1.6"/>'
    p = lv[4][good[4]]
    b += f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="12" fill="{CORAL}" fill-opacity="0.22"/>'
    write("p-tmrs", 480, 300, "A heat map over register settings with the best cell marked, a best-so-far search curve, and a search tree with the winning branch highlighted", b, d)


# ---------------------------------------------------------------- home (400 x 260)
def h_opt():
    pid = "h-opt"; d, b = bg_light(pid, 400, 260)
    b += surface(pid, 400, 260, 88, 200, 150)
    write("h-opt", 400, 260, "A shaded three-dimensional bowl with a descent path zig-zagging to its minimum", b, d)


def h_learn():
    pid = "h-learn"; rnd = random.Random(31); d, b = bg_paper(pid, 400, 260, 26, "#EAF6F4", WHITE)
    X = lambda t: 44 + t * 330; Y = lambda v: 222 - v * 176
    up = [(X(k / 60), Y(min(1.05, 1.18 * math.sqrt(k / 60) * 0.92 + 0.0))) for k in range(61)]
    lo = [(X(k / 60), Y(0.62 * math.sqrt(k / 60))) for k in range(61)]
    b += f'<polygon points="{pts(up + lo[::-1])}" fill="{TEAL}" fill-opacity="0.13"/>'
    b += f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(0.98)}" y2="{Y(1.08)}" stroke="{CORAL}" stroke-width="2.2" stroke-dasharray="7 5"/>'
    for c in (SKY, VIOLET, AMBER, GREEN, BLUE, TEAL):
        v, path = 0.0, []
        scale = rnd.uniform(0.66, 1.02)
        for k in range(61):
            t = k / 60; target = scale * math.sqrt(t); v = max(v, target + rnd.gauss(0, 0.012)); path.append((X(t), Y(v)))
        b += f'<polyline points="{pts(path)}" fill="none" stroke="{c}" stroke-width="1.5" stroke-opacity="0.75" stroke-linejoin="round"/>'
    mean = [(X(k / 60), Y(0.84 * math.sqrt(k / 60))) for k in range(61)]
    b += f'<polyline points="{pts(mean)}" fill="none" stroke="{NAVY}" stroke-width="4" stroke-linecap="round"/>'
    b += f'<polyline points="{X(0)},20 {X(0)},{Y(0)} 384,{Y(0)}" fill="none" stroke="{INK}" stroke-opacity="0.6" stroke-width="1.8"/>'
    b += f'<text x="382" y="246" text-anchor="end" font-size="15" {FONT} fill="{MUTED}">rounds T</text><text x="54" y="32" font-size="15" {FONT} fill="{MUTED}">regret</text>'
    b += f'<text x="300" y="58" font-size="14" {FONT} fill="{CORAL}">linear</text><text x="318" y="108" font-size="14" font-weight="700" {SERIF} fill="{NAVY}">√T</text>'
    write("h-learn", 400, 260, "Regret curves of several runs staying inside a square-root band, far below the linear reference", b, d)


def h_ai():
    pid = "h-ai"; d, b = bg_dark(pid, 400, 260, grid=False)
    d += glow(pid, "#B9A6F2")
    b += f'<circle cx="352" cy="130" r="70" fill="url(#{pid}-glow)" fill-opacity="0.6"/>'
    b += network(pid, 48, 352, 20, 240, [4, 7, 7, 5, 2], 12, r=9, palette=(SKY, "#B9A6F2", CORAL), dark=True)
    write("h-ai", 400, 260, "A deep neural network with signed weighted edges glowing on a dark background", b, d)


def h_apps():
    pid = "h-apps"; d, b = bg_light(pid, 400, 260, "#F6F1FD", "#FFF5E3")
    tiles = [(22, 18, AMBER, SAND), (208, 18, TEAL, MINT), (22, 136, CORAL, BLUSH), (208, 136, VIOLET, LILAC)]
    for x, y, c, soft in tiles:
        b += f'<rect x="{x}" y="{y}" width="170" height="106" rx="18" fill="{WHITE}"/><rect x="{x}" y="{y}" width="170" height="106" rx="18" fill="{soft}" fill-opacity="0.55" stroke="{c}" stroke-width="2"/>'
    gx, gy = 107, 71
    teeth = "".join(f'<rect x="{gx - 7}" y="{gy - 40}" width="14" height="18" rx="3" fill="{AMBER}" transform="rotate({k * 45} {gx} {gy})"/>' for k in range(8))
    b += teeth + f'<circle cx="{gx}" cy="{gy}" r="28" fill="{AMBER}"/><circle cx="{gx}" cy="{gy}" r="11" fill="{WHITE}"/>'
    b += (f'<path d="M232 100 C 262 100, 250 52, 286 58 S 318 96, 346 70" fill="none" stroke="{TEAL}" stroke-width="4" stroke-dasharray="9 7" stroke-linecap="round"/>'
          f'<circle cx="232" cy="100" r="8" fill="{NAVY}"/><path d="M346 76 c-12 -17 -18 -24 -18 -33 a18 18 0 0 1 36 0 c0 9 -6 16 -18 33z" fill="{TEAL}"/><circle cx="346" cy="43" r="7" fill="{WHITE}"/>')
    b += f'<polyline points="38,192 72,192 84,172 96,222 110,152 124,208 134,192 176,192" fill="none" stroke="{CORAL}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>'
    for k in range(4):
        o = 264 + k * 19
        b += (f'<rect x="{o}" y="156" width="7" height="14" rx="2" fill="{VIOLET}"/><rect x="{o}" y="208" width="7" height="14" rx="2" fill="{VIOLET}"/>')
    for k in range(3):
        o = 172 + k * 17
        b += (f'<rect x="240" y="{o}" width="14" height="7" rx="2" fill="{VIOLET}"/><rect x="332" y="{o}" width="14" height="7" rx="2" fill="{VIOLET}"/>')
    b += f'<rect x="252" y="166" width="82" height="46" rx="8" fill="{VIOLET}"/><rect x="268" y="176" width="50" height="26" rx="4" fill="{LILAC}"/>'
    write("h-apps", 400, 260, "Four coloured tiles: a gear for production, a route for logistics, a heartbeat for healthcare, and a chip for semiconductors", b, d)


if __name__ == "__main__":
    for fn in (t_ma1407, t_mno, t_ie331, t_ie539, t_ie631, t_ds801, t_combopt,
               p_src, p_sota, p_ssm, p_swarm, p_blackbox, p_foundation, p_ysf, p_jedec, p_iomargin, p_tmrs,
               h_opt, h_learn, h_ai, h_apps):
        fn()
    print("wrote", len(list(OUT.glob("*.svg"))), "figures to", OUT)
