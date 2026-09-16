#!/usr/bin/env python3
"""verify_enclosure.py — check the EXPORTED case and lid meshes, with numpy only.

WHY THIS EXISTS
    af4_enclosure_ocp.py checks its own parameters and its own OCP solids, so it can
    only ever agree with itself, and it needs cadquery-ocp, which no session shell can
    install (PyPI is 403-blocked from both). This script needs nothing but numpy. It reads
    the STL files that actually get printed and tests them against the parameters, the
    measured tall parts on the Olimex board and the vendor ESP32 mesh.

    It catches the failure that bit on 2026-09-16: script edited, exports never
    regenerated, old print in hand. A stale export fails check 1 or 2 immediately.

WHAT IT CHECKS
    1. case and lid bounding boxes against the parameters (catches stale exports)
    2. top of every standoff, read by a ray cast into the mesh
    3. no case material inside the hat's envelope or above the ESP32 up to the
       tallest measured part (point-in-mesh by ray parity)
    4. both jack holes are open along their axes through the +X wall
    5. hat board slab against the measured TALL_PARTS, and against the vendor mesh

USAGE (from hardware/enclosure/)
    python3 verify_enclosure.py
    python3 verify_enclosure.py --script OTHER.py   # parameters from another version
Runs in Kenny's Mac, the Mac-side session VM and the cloud container. Parameters are
read from the parameter section of af4_enclosure_ocp.py, never retyped here.
"""
import argparse, math, os, struct, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load_params(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("# =====") and "parameters" in l)
    j = next(k for k, l in enumerate(lines) if k > i and l.startswith("# =====") and "helpers" in l)
    g = {"math": math}
    exec("\n".join(lines[i:j]), g)
    # constants that live outside the parameter section
    g.setdefault("TAB_L", 12.0)
    g.setdefault("LIP_H", 2.0)
    g.setdefault("TALL_PARTS", [])
    return g


def load_stl(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        v = [list(map(float, l.split()[1:4])) for l in data.decode(errors="ignore").splitlines()
             if l.strip().startswith("vertex")]
        return np.array(v, dtype=np.float64).reshape(-1, 3, 3)
    n = struct.unpack("<I", data[80:84])[0]
    arr = np.frombuffer(data, dtype=np.uint8, count=n * 50, offset=84).reshape(n, 50)
    return arr[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)


def ray_hits_z(tris, pts):
    """For each point, the z of every triangle crossing the vertical line through it.
    Returns a list of arrays. Points are jittered off exact edges by the caller."""
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    xmin = tris[:, :, 0].min(1); xmax = tris[:, :, 0].max(1)
    ymin = tris[:, :, 1].min(1); ymax = tris[:, :, 1].max(1)
    out = []
    for p in pts:
        m = (xmin <= p[0]) & (p[0] <= xmax) & (ymin <= p[1]) & (p[1] <= ymax)
        if not m.any():
            out.append(np.empty(0)); continue
        A, B, C = a[m], b[m], c[m]
        v0 = C[:, :2] - A[:, :2]; v1 = B[:, :2] - A[:, :2]; v2 = p[:2] - A[:, :2]
        den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
        ok = np.abs(den) > 1e-12
        u = np.where(ok, (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / np.where(ok, den, 1), -1)
        w = np.where(ok, (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / np.where(ok, den, 1), -1)
        hit = ok & (u >= 0) & (w >= 0) & (u + w <= 1)
        z = A[hit, 2] + u[hit] * (C[hit, 2] - A[hit, 2]) + w[hit] * (B[hit, 2] - A[hit, 2])
        out.append(np.sort(z))
    return out


def inside(tris, pts):
    """Ray-parity point-in-mesh along +z."""
    hits = ray_hits_z(tris, pts)
    return np.array([(np.count_nonzero(h > p[2]) % 2) == 1 for h, p in zip(hits, pts)])


JIT = np.array([0.0137, 0.0071, 0.0])   # keep sample points off exact edges


def grid(x0, x1, y0, y1, z0, z1, step):
    xs = np.arange(x0, x1 + 1e-9, step); ys = np.arange(y0, y1 + 1e-9, step)
    zs = np.arange(z0, z1 + 1e-9, step)
    g = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    return g + JIT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=os.path.join(HERE, "af4_enclosure_ocp.py"))
    ap.add_argument("--case", default=os.path.join(HERE, "aF4-trigger-case.stl"))
    ap.add_argument("--lid", default=os.path.join(HERE, "aF4-trigger-lid.stl"))
    ap.add_argument("--esp", default=os.path.join(HERE, "..", "..", "reference", "vendor",
                                                  "ESP32-PoE-ISO_Rev_N.stl"))
    ap.add_argument("--step", type=float, default=1.0, help="sampling pitch, mm")
    args = ap.parse_args()
    P = load_params(args.script)
    fails = []

    def chk(name, good, detail):
        print("  [%s] %-46s %s" % ("OK " if good else "FAIL", name, detail))
        if not good:
            fails.append(name)

    print("verify_enclosure — parameters from %s" % os.path.basename(args.script))
    print("  HAT_Z %.3f   IZ1 %.2f   external height %.1f"
          % (P["HAT_Z"], P["IZ1"], P["IZ1"] + P["LID_T"] - P["OZ0"]))

    # ---- 1. bounding boxes -------------------------------------------------
    case = load_stl(args.case)
    lo, hi = case.reshape(-1, 3).min(0), case.reshape(-1, 3).max(0)
    want_case = np.array([P["OX1"] - P["OX0"] + 2 * P["TAB_L"], P["OY1"] - P["OY0"],
                          P["IZ1"] - P["OZ0"]])
    got = hi - lo
    chk("case bounding box", np.allclose(got, want_case, atol=0.05),
        "got %.2f x %.2f x %.2f, want %.2f x %.2f x %.2f" % (*got, *want_case))
    lid = load_stl(args.lid)
    lg = lid.reshape(-1, 3).max(0) - lid.reshape(-1, 3).min(0)
    want_lid = np.array([P["OX1"] - P["OX0"], P["OY1"] - P["OY0"], P["LID_T"] + P["LIP_H"]])
    chk("lid bounding box (independent of HAT_Z)", np.allclose(lg, want_lid, atol=0.05),
        "got %.2f x %.2f x %.2f, want %.2f x %.2f x %.2f" % (*lg, *want_lid))

    # printed case -> enclosure frame
    case = case - lo + np.array([P["OX0"] - P["TAB_L"], P["OY0"], P["OZ0"]])

    # ---- 2. standoff tops --------------------------------------------------
    def top_at(x, y):
        h = ray_hits_z(case, [np.array([x, y, 0.0]) + JIT])[0]
        return h.max() if h.size else float("nan")
    for bx, by in P["BOSSES_HAT"]:
        r = (P["M3_PILOT"] / 2 + P["HAT_BOSS_D"] / 2) / 2
        z = top_at(bx + r, by)
        chk("hat standoff %.1f top = HAT_Z" % bx, abs(z - P["HAT_Z"]) < 0.05,
            "top %.3f, want %.3f" % (z, P["HAT_Z"]))
    for bx, by in P["BOSSES_BOARD"]:
        r = (P["M2_PILOT"] / 2 + 3.0) / 2
        # the ray also meets the floor; the post top is the highest hit below the lid
        h = ray_hits_z(case, [np.array([bx + r, by, 0.0]) + JIT])[0]
        h = h[h < P["IZ1"] - 1]
        z = h.max() if h.size else float("nan")
        chk("ESP32 standoff (%.1f, %.1f) top = 0" % (bx, by), abs(z) < 0.05, "top %.3f" % z)

    # ---- 3. keep-outs ------------------------------------------------------
    # positive control first: a keep-out test that finds nothing is only worth
    # something if the same test finds material where material must be.
    ctrl = [np.array([104.0, -140.0, P["OZ0"] + P["FLOOR"] / 2]) + JIT,           # floor
            np.array([P["OX0"] + P["WALL"] / 2, -140.0, 10.0]) + JIT,             # -X wall
            np.array([P["IX1"] + P["WALL"] / 2, -130.0, 5.0]) + JIT]              # +X wall
    n = int(inside(case, ctrl).sum())
    chk("positive control: floor and walls read solid", n == len(ctrl), "%d of %d" % (n, len(ctrl)))
    s = args.step
    hat_env = grid(P["HAT_X0"] + .1, P["HAT_X1"] - .1, P["HAT_Y0"] + .1, P["HAT_Y1"] - .1,
                   P["HAT_Z"] + .1, P["HAT_TOP"] + 7.2, s)
    n = int(inside(case, hat_env).sum())
    chk("no case material in the hat envelope", n == 0, "%d of %d samples inside" % (n, len(hat_env)))
    tall = max([t[5] for t in P["TALL_PARTS"]] or [1.578 + 4.40])
    esp_env = grid(90.25, 118.05, -188.05, -90.1, 0.1, tall, s)
    n = int(inside(case, esp_env).sum())
    chk("no case material over the ESP32 to z %.1f" % tall, n == 0,
        "%d of %d samples inside" % (n, len(esp_env)))

    # ---- 4. jack holes open along their axes -------------------------------
    for nm, y, z, d in (("J1 barrel", P["J1_Y"], P["J1_AXIS_Z"], P["J1_HOLE_D"]),
                        ("J2 3.5 mm", P["J2_Y"], P["J2_AXIS_Z"], P["J2_HOLE_D"])):
        pts = []
        for x in np.arange(P["IX1"] - 0.5, P["OX1"] + 0.5, 0.25):
            for ang in np.linspace(0, 2 * math.pi, 16, endpoint=False):
                rr = 0.8 * d / 2
                pts.append(np.array([x, y + rr * math.cos(ang), z + rr * math.sin(ang)]) + JIT)
        n = int(inside(case, pts).sum())
        chk("%s hole open on axis z %.2f" % (nm, z), n == 0, "%d of %d samples blocked" % (n, len(pts)))

    # ---- 5. hat slab vs the tall parts -------------------------------------
    for nm, x0, y0, x1, y1, tz in P["TALL_PARTS"]:
        chk("hat underside over %s" % nm, P["HAT_Z"] - tz >= 0.5,
            "%.2f mm clear (measured top %.1f)" % (P["HAT_Z"] - tz, tz))
    if os.path.exists(args.esp):
        esp = load_stl(args.esp)
        # sample every triangle so large faces are tested, not only their corners
        k = 8
        ii, jj = np.meshgrid(np.arange(k + 1), np.arange(k + 1), indexing="ij")
        keep = (ii + jj) <= k
        wa, wb = ii[keep] / k, jj[keep] / k
        wc = 1 - wa - wb
        top = esp[:, :, 2].max(1)
        e = esp[top > P["HAT_Z"] - 3]
        pts = (wa[None, :, None] * e[:, None, 0] + wb[None, :, None] * e[:, None, 1]
               + wc[None, :, None] * e[:, None, 2]).reshape(-1, 3)
        m = ((pts[:, 0] > P["HAT_X0"]) & (pts[:, 0] < P["HAT_X1"]) &
             (pts[:, 1] > P["HAT_Y0"]) & (pts[:, 1] < P["HAT_Y1"]) &
             (pts[:, 2] > 1.7) & (pts[:, 2] < P["HAT_TOP"]))
        zt = pts[m, 2].max() if m.any() else float("nan")
        chk("vendor ESP32 mesh under the hat", not (zt > P["HAT_Z"] - 0.5),
            "tallest point %.2f, hat underside %.2f" % (zt, P["HAT_Z"]))
    else:
        print("  [--] vendor ESP32 mesh not found; check 5b SKIPPED (a reduced check, not a pass)")

    print("\nALL CHECKS PASSED" if not fails else "\n*** %d CHECK(S) FAILED ***" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
