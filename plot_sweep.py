#!/usr/bin/env python3
"""Plot the Ri-vs-Vo sweep for the cascode bias stack and label the slope at Ri=30k.

Reads sweep.dat (columns: Ri[ohm]  vo[V]  vgs[V]  vb[V]) produced by:
    ngspice -b sweep.cir | grep '^DATA' | awk '{print $2,$3,$4,$5}' > sweep.dat
"""
import numpy as np
import matplotlib.pyplot as plt

VTH = 0.5          # V, level-1 Vth (GAMMA=0, VBS=0 for both devices)
IB  = 10e-6        # A, bias current

Ri, vo, vgs, vb = np.loadtxt("sweep.dat", unpack=True)
Ri_k = Ri / 1e3

# Saturation boundaries -------------------------------------------------------
# M1 (bottom): saturated while  VDS1 = vo >= Vov1 = vgs - VTH
# M2 (cascode): saturated while VDS2 = vgs-vo >= Vov2 = (vb-vo) - VTH
Vov1 = vgs - VTH
Vov2 = (vb - vo) - VTH
m1_sat = vo >= Vov1
m2_sat = (vgs - vo) >= Vov2
both_sat = m1_sat & m2_sat

# window edges (first/last Ri where both devices stay in saturation)
lo_edge = Ri_k[both_sat].min()
hi_edge = Ri_k[both_sat].max()

# Slope at Ri = 30k via central difference ------------------------------------
i30 = int(np.argmin(np.abs(Ri - 30e3)))
slope = (vo[i30 + 1] - vo[i30 - 1]) / (Ri[i30 + 1] - Ri[i30 - 1])  # V/ohm
Ri30, vo30 = Ri_k[i30], vo[i30]

# Figure ----------------------------------------------------------------------
plt.rcParams.update({"font.size": 11, "figure.dpi": 130})
fig, ax = plt.subplots(figsize=(9, 5.6))

# shade the both-in-saturation window
ax.axvspan(lo_edge, hi_edge, color="#2ca02c", alpha=0.10,
           label=f"both in saturation ({lo_edge:.0f}–{hi_edge:.0f} kΩ)")

# the sweep curve, colored by region validity
ax.plot(Ri_k, vo, color="#bbbbbb", lw=1.2, zorder=1)
ax.plot(Ri_k[both_sat], vo[both_sat], color="#1f5fbf", lw=2.6, zorder=3,
        label="Vo (both transistors saturated)")
ax.plot(Ri_k[~m1_sat], vo[~m1_sat], color="#d62728", lw=2.6, zorder=3,
        label="M1 in triode (Ri too small)")
ax.plot(Ri_k[~m2_sat], vo[~m2_sat], color="#ff7f0e", lw=2.6, zorder=3,
        label="M2 in triode (Ri too large)")

# tangent line at Ri = 30k
span = 22  # kohm each side for drawing the tangent
xt = np.array([Ri30 - span, Ri30 + span])
yt = vo30 + slope * ((xt - Ri30) * 1e3)   # slope is V/ohm, x in kohm
ax.plot(xt, yt, "--", color="black", lw=1.4, zorder=4)

# mark the 30k operating point
ax.plot([Ri30], [vo30], "o", color="black", ms=8, zorder=5)
ax.annotate(
    f"Ri = 30 kΩ\nVo = {vo30:.3f} V\nVbias = {vb[i30]:.3f} V\n"
    f"slope dVo/dRi = {slope*1e6:.2f} µV/Ω  (≈ IB = 10 µA)",
    xy=(Ri30, vo30), xytext=(Ri30 + 3, vo30 - 0.16),
    arrowprops=dict(arrowstyle="->", lw=1.2),
    fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc="#fffbe6", ec="#888"))

ax.set_xlabel("Ri  (kΩ)")
ax.set_ylabel("Vo  (V)  — internal cascode node")
ax.set_title("Cascode bias stack: Ri vs Vo  (VDD=1.8 V, IB=10 µA, Ibias=10 µA fixed)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left", framealpha=0.95)
ax.set_xlim(Ri_k.min(), Ri_k.max())
fig.tight_layout()
fig.savefig("ri_vs_vo.png", dpi=140)
print(f"window (both sat): {lo_edge:.0f}k .. {hi_edge:.0f}k")
print(f"slope at 30k = {slope*1e6:.3f} uV/ohm  (IB = {IB*1e6:.1f} uA)")
print("wrote ri_vs_vo.png")
