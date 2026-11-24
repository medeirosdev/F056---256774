#!/usr/bin/env python3
# Gera as figuras e os numeros do seminario (Exercicio 4 de Data Analysis, CSC 2024)
# uso: python3 figuras.py   (precisa de numpy, scipy, matplotlib e iminuit)
# le LHC_data_2023.txt desta pasta e salva as figuras e os numeros em figuras/

import os
import re

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import erfcinv
from iminuit import Minuit

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(AQUI, "LHC_data_2023.txt")
SAIDA = os.path.join(AQUI, "figuras")
os.makedirs(SAIDA, exist_ok=True)
LO, HI, NB = 20.0, 40.0, 100          # bins de 0,2 GeV
AZUL, LARANJA, TINTA, CINZA = "#2a6fb0", "#e8772e", "#23373b", "#8a9499"

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 13,
    "axes.edgecolor": CINZA, "axes.labelcolor": TINTA, "xtick.color": TINTA, "ytick.color": TINTA,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#e6e8e8", "grid.linewidth": 0.8, "legend.frameon": False,
})
LARGO, ESTREITO = (6.4, 4.3), (4.6, 3.4)
Z = lambda p: np.sqrt(2) * erfcinv(2 * p)
saida = []


def salvar(nome):
    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA, nome))
    plt.close()


# =====================================================================
# Exercicio 4 com os dados
# =====================================================================
# so as linhas com numero (o arquivo original do Indico tinha linhas de texto no topo)
m = np.array([float(l) for l in open(ARQUIVO) if re.fullmatch(r"\s*[0-9.eE+-]+\s*", l)])
N = len(m)
n, b = np.histogram(m, NB, (LO, HI))
c = 0.5 * (b[1:] + b[:-1])
w = b[1] - b[0]
nu0 = N / NB
t_stat = lambda k: np.sum((k - nu0) ** 2 / nu0)       # chi2 de Pearson contra o fundo plano

# --- Problema 1: como seria a CSC (m escolhida = 30 GeV, 1% dos eventos, sigma = 0,2 GeV)
rng = np.random.default_rng(2024)
M_EX = 30.0
mc = np.concatenate([rng.uniform(LO, HI, int(0.99 * N)), rng.normal(M_EX, 0.2, int(0.01 * N))])
nmc = np.histogram(mc, NB, (LO, HI))[0]
fig, ax = plt.subplots(figsize=LARGO)
ax.errorbar(c, nmc, yerr=np.sqrt(nmc), fmt="o", ms=4, color=AZUL, elinewidth=1.2, label="MC: fundo + CSC")
ax.axhline(nu0, color=TINTA, lw=2, ls="--", label=r"só fundo ($H_0$)")
ax.set_xlabel(r"massa invariante $m_{e^+e^-}$ [GeV]")
ax.set_ylabel("eventos / 0,2 GeV")
ax.set_xlim(LO, HI)
ax.set_ylim(800, 1520)
ax.legend(loc="upper left")
salvar("fig_mc_csc.pdf")

# --- toys so com fundo -> g(t|H0)
toys = np.array([t_stat(np.histogram(rng.uniform(LO, HI, N), NB, (LO, HI))[0]) for _ in range(10000)])
t5 = stats.chi2.isf(stats.norm.sf(5), NB - 1)

# --- Problema 2: sensibilidade esperada (mediana de 200 MC com sinal)
t_esp = np.median([t_stat(np.histogram(np.concatenate([rng.uniform(LO, HI, int(0.99 * N)),
                                                       rng.normal(M_EX, 0.2, int(0.01 * N))]), NB, (LO, HI))[0])
                   for _ in range(200)])
p_esp = stats.chi2.sf(t_esp, NB - 1)
saida.append(f"toys: media = {toys.mean():.1f}, desvio = {toys.std():.1f}, max = {toys.max():.1f}, "
             f"fracao >= t_esp = {np.mean(toys >= t_esp)}")
saida.append(f"esperado: t = {t_esp:.1f}, p = {p_esp:.2e}, Z = {Z(p_esp):.2f}; t para 5 sigma = {t5:.1f}")

fig, ax = plt.subplots(figsize=LARGO)
ax.hist(toys, bins=60, density=True, color=AZUL, alpha=0.75, edgecolor="white", linewidth=0.6,
        label=r"10 000 pseudo-experimentos com $H_0$")
x = np.linspace(40, 400, 600)
ax.plot(x, stats.chi2.pdf(x, NB - 1), color=TINTA, lw=2, label=r"$\chi^2$ com 99 graus de liberdade")
ax.axvline(t5, ymax=0.66, color=CINZA, lw=1.5, ls=":")
ax.text(t5 + 4, 0.010, f"5σ\n(t = {t5:.0f})", color=TINTA, fontsize=11, va="top")
ax.axvline(t_esp, ymax=0.66, color=LARANJA, lw=3)
ax.text(t_esp - 6, 0.010, f"esperado com\nCSC: t = {t_esp:.0f}", color=TINTA, fontsize=11, ha="right", va="top")
ax.set_xlabel("estatística de teste t")
ax.set_ylabel(r"densidade  $g(t\,|\,H_0)$")
ax.set_xlim(40, 400)
ax.set_ylim(0, 0.044)
ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.02))
salvar("fig_toys.pdf")

# --- g(t|H0) sozinho, para explicar o que e (slide proprio)
dentro = np.mean((toys > 70) & (toys < 130))
saida.append(f"toys entre 70 e 130: {100 * dentro:.1f}%")
fig, ax = plt.subplots(figsize=LARGO)
ax.axvspan(70, 130, color=CINZA, alpha=0.15, lw=0)
alt = ax.hist(toys, bins=np.arange(40, 201, 3), color=AZUL, alpha=0.8, edgecolor="white", linewidth=0.6)[0]
ax.text(100, 975, f"{100 * dentro:.0f}% dos toys entre 70 e 130",
        ha="center", va="top", fontsize=11, color=TINTA)
ax.annotate(f"no meio:\nt ≈ {toys.mean():.0f}", xy=(101, alt.max()), xytext=(140, 640), fontsize=11,
            color=TINTA, arrowprops=dict(arrowstyle="->", color=TINTA))
ax.annotate(f"maior dos 10 000:\nt = {toys.max():.0f}", xy=(toys.max(), 5), xytext=(155, 230),
            fontsize=11, color=TINTA, arrowprops=dict(arrowstyle="->", color=TINTA))
ax.set_xlabel("estatística de teste t (um valor por toy)")
ax.set_ylabel("número de toys")
ax.set_xlim(40, 200)
ax.set_ylim(0, 1000)
salvar("fig_g_h0.pdf")

# --- a solucao: a formula chi2_99 continua onde os toys acabam (escala log)
fig, ax = plt.subplots(figsize=LARGO)
hb = np.arange(40, 201, 4)
dens = np.histogram(toys, hb, density=True)[0]
ok = dens > 0
ax.semilogy(0.5 * (hb[1:] + hb[:-1])[ok], dens[ok], "o", ms=5, color=AZUL, label="10 000 toys")
xg = np.linspace(40, 400, 800)
ax.semilogy(xg, stats.chi2.pdf(xg, NB - 1), color=TINTA, lw=2, label=r"fórmula: $\chi^2$ com 99 g.l.")
ax.axvspan(toys.max(), 400, color=CINZA, alpha=0.15, lw=0)
ax.text(toys.max() + 6, 1e-15, "aqui não há\nnenhum toy:\nsó a fórmula", fontsize=11, color=TINTA, va="top")
ax.axvline(t_esp, ymax=0.72, color=LARANJA, lw=2.5)
mant, expo = f"{p_esp:.1e}".split("e")
ax.annotate(f"t esperado com CSC = {t_esp:.0f}\n" + rf"$p \approx {mant.replace('.', '{,}')}\times10^{{{int(expo)}}}$",
            xy=(t_esp, stats.chi2.pdf(t_esp, NB - 1)), xytext=(175, 1e-29), fontsize=11, color=TINTA,
            arrowprops=dict(arrowstyle="->", color=TINTA))
ax.set_xlabel("estatística de teste t")
ax.set_ylabel(r"$g(t\,|\,H_0)$  (escala log)")
ax.set_xlim(40, 400)
ax.set_ylim(1e-33, 1)
ax.legend(loc="upper right")
salvar("fig_assintotica.pdf")

# --- Problema 3: abrir os dados
t_obs = t_stat(n)
p_obs = stats.chi2.sf(t_obs, NB - 1)
saida.append(f"observado: t = {t_obs:.1f}, p = {p_obs:.2e}, Z = {Z(p_obs):.2f}")
fig, ax = plt.subplots(figsize=LARGO)
ax.errorbar(c, n, yerr=np.sqrt(n), fmt="o", ms=4, color=AZUL, elinewidth=1.2, label="dados CMS 2021–2023")
ax.axhline(nu0, color=TINTA, lw=2, ls="--", label=r"só fundo ($H_0$): 1000 eventos/bin")
ax.set_xlabel(r"massa invariante $m_{e^+e^-}$ [GeV]")
ax.set_ylabel("eventos / 0,2 GeV")
ax.set_xlim(LO, HI)
ax.set_ylim(800, 1520)
ax.legend(loc="upper left")
salvar("fig_dados.pdf")


# --- ajustes (ML binado de Poisson)
def nll(A, mu, s, B):
    nu = B * w / (HI - LO) + A * np.diff(stats.norm.cdf(b, mu, s))
    return np.sum(nu - n * np.log(nu))


def ajustar(fixos=(), **ini):
    f = Minuit(nll, **ini)
    f.errordef = Minuit.LIKELIHOOD
    f.limits["s"] = (0.01, 5)
    f.limits["A"] = (0, None)
    for k in fixos:
        f.fixed[k] = True
    f.migrad()
    return f


livre = ajustar(A=1000, mu=35, s=0.2, B=N - 1000)
livre.hesse()
nll0 = nll(0, 30, 1, N)

# --- Problema 4: varredura do p-valor local (sigma = 0,2 GeV fixo, rendimento livre >= 0)
ms = np.arange(20.4, 39.61, 0.05)
p_loc = []
for mm in ms:
    f = ajustar(("mu", "s"), A=50, mu=mm, s=0.2, B=N - 50)
    q0 = max(0.0, 2 * (nll0 - f.fval))
    p_loc.append(0.5 * stats.chi2.sf(q0, 1))
p_loc = np.array(p_loc)
i_min = np.argmin(p_loc)
saida.append(f"varredura: minimo em m = {ms[i_min]:.2f} GeV, p = {p_loc[i_min]:.1e}, Z = {Z(p_loc[i_min]):.1f}; "
             f"Z > 3 so entre {ms[Z(p_loc) > 3].min():.2f} e {ms[Z(p_loc) > 3].max():.2f} GeV")
fig, ax = plt.subplots(figsize=LARGO)
ax.semilogy(ms, np.clip(p_loc, 1e-50, 1), color=AZUL, lw=2, label="p-valor local observado")
for zz in (3, 5, 10):
    pz = stats.norm.sf(zz)
    ax.axhline(pz, color=CINZA, lw=1, ls=":")
    ax.text(20.5, pz * 2.5, f"{zz}σ", color=TINTA, fontsize=11)
ax.annotate(f"mínimo: m = {ms[i_min]:.2f} GeV\n(≈ {Z(p_loc[i_min]):.0f}σ local)", xy=(ms[i_min], p_loc[i_min]),
            xytext=(27.0, 1e-40), fontsize=11, color=TINTA, arrowprops=dict(arrowstyle="->", color=TINTA))
ax.set_xlabel(r"massa testada $m_{e^+e^-}$ [GeV]")
ax.set_ylabel("p-valor local")
ax.set_xlim(LO, HI)
ax.set_ylim(1e-50, 2)
ax.legend(loc="lower left")
salvar("fig_scan_p.pdf")

# --- Problema 5: e a CSC? (rendimento = 1% e sigma = 0,2 GeV fixos) x ajuste livre
csc = ajustar(("A", "s"), A=0.01 * N, mu=35, s=0.2, B=0.99 * N)
d2 = 2 * (csc.fval - livre.fval)
p_csc = stats.chi2.sf(d2, 2)
for k in ["A", "mu", "s", "B"]:
    saida.append(f"ajuste livre {k} = {livre.values[k]:.4f} +- {livre.errors[k]:.4f}")
saida.append(f"Z_local (ajuste livre) = {np.sqrt(2 * (nll0 - livre.fval)):.2f}")
saida.append(f"CSC (A = 1000, s = 0,2 fixos) x livre: -2 dlnL = {d2:.2f}, 2 gl, p = {p_csc:.2f}")

z0, z1 = 30, 40
sel = (c > z0) & (c < z1)
xx = np.linspace(z0, z1, 1000)
fundo = livre.values["B"] * w / (HI - LO)
modelo = fundo + livre.values["A"] * w * stats.norm.pdf(xx, livre.values["mu"], livre.values["s"])
modelo_csc = csc.values["B"] * w / (HI - LO) + 0.01 * N * w * stats.norm.pdf(xx, csc.values["mu"], 0.2)
fig, ax = plt.subplots(figsize=ESTREITO)
ax.errorbar(c[sel], n[sel], yerr=np.sqrt(n[sel]), fmt="o", ms=5, color=AZUL, elinewidth=1.2, label="dados")
ax.plot(xx, modelo, color=LARANJA, lw=2.5, label="ajuste livre")
ax.plot(xx, modelo_csc, color=TINTA, lw=1.5, ls="--", label="previsão CSC\n(1%, σ = 0,2 GeV)")
ax.set_xlabel(r"massa invariante $m_{e^+e^-}$ [GeV]")
ax.set_ylabel("eventos / 0,2 GeV")
ax.set_xlim(z0 - 0.2, z1)
ax.set_ylim(850, 1650)
ax.legend(loc="upper right", fontsize=10)
salvar("fig_ajuste.pdf")

# --- intervalo de confianca da massa pela varredura de -2 ln L 
mg = np.linspace(34.92, 35.095, 36)
perfil = np.array([2 * (ajustar(("mu",), A=986, mu=mm, s=0.236, B=N - 986).fval - livre.fval) for mm in mg])
esq, dir_ = mg < livre.values["mu"], mg > livre.values["mu"]
lim = {}
for nivel in (1, 4):
    lim[nivel] = (np.interp(nivel, perfil[esq][::-1], mg[esq][::-1]), np.interp(nivel, perfil[dir_], mg[dir_]))
mu_hat = livre.values["mu"]
saida.append(f"massa: {mu_hat:.4f} GeV, 68%: [{lim[1][0]:.4f}, {lim[1][1]:.4f}], 95%: [{lim[4][0]:.4f}, {lim[4][1]:.4f}]")
fig, ax = plt.subplots(figsize=ESTREITO)
mf = np.linspace(mg[0], mg[-1], 400)
ax.plot(mf, np.interp(mf, mg, perfil), color=AZUL, lw=2.5)
for nivel, rot in ((1, "68%"), (4, "95%")):
    ax.plot(lim[nivel], [nivel, nivel], color=LARANJA, lw=2.5)
    ax.text(lim[nivel][1] + 0.004, nivel, rot, color=TINTA, fontsize=11, va="center")
ax.axvline(mu_hat, color=CINZA, lw=1, ls=":")
ax.set_xlabel(r"massa $m$ [GeV]")
ax.set_ylabel(r"$-2\,\Delta \ln L$")
ax.set_ylim(0, 8)
ax.set_xticks([34.95, 35.00, 35.05])
salvar("fig_scan_m.pdf")

with open(os.path.join(SAIDA, "numeros.txt"), "w") as out:
    out.write(f"eventos = {N}\n" + "\n".join(saida) + "\n")
print(open(os.path.join(SAIDA, "numeros.txt")).read())
