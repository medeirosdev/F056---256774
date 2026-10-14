# F056 - Lista 2: Estimacao de parametros (tempo de vida, decay.txt)
# uso: python3 estimacao.py   (gera os graficos P*.pdf nessa pasta)

import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy.optimize import minimize_scalar, brentq

t = np.loadtxt("decay.txt")
N = len(t)
print("N =", N, " min =", t.min(), " max =", t.max(), " media =", round(t.mean(), 4))


def pdf_exp(t, tau):
    return np.exp(-t / tau) / tau


# =========================================================
# Problema 1 - histograma
# =========================================================
# os tempos estao arredondados em 0.01 s, entao bin menor que isso nao faz sentido.
# comparei 3 escolhas: poucos bins, raiz(N) e Freedman-Diaconis
iqr = np.percentile(t, 75) - np.percentile(t, 25)
largura_fd = 2 * iqr / N ** (1 / 3)
nbins_fd = int(np.ceil((t.max() - t.min()) / largura_fd))
nbins_raiz = int(np.sqrt(N))
print("Freedman-Diaconis: largura =", round(largura_fd, 3), "s ->", nbins_fd, "bins")
print("raiz(N):", nbins_raiz, "bins")

fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
for a, nb, nome in zip(ax, [10, nbins_fd, nbins_raiz], ["10 bins", "Freedman-Diaconis", "raiz(N)"]):
    cont, bordas = np.histogram(t, bins=nb, range=(0, t.max()))
    centros = 0.5 * (bordas[1:] + bordas[:-1])
    a.errorbar(centros, cont, yerr=np.sqrt(cont), fmt="o", ms=3)
    a.set_yscale("log")
    a.set_xlabel("t [s]")
    a.set_ylabel("eventos / bin")
    a.set_title(f"{nome}: {nb} bins de {bordas[1] - bordas[0]:.3f} s")
plt.tight_layout()
plt.savefig("P1_histograma.pdf")
plt.close()

# =========================================================
# Problema 2 - PDF exponencial para varios tau
# =========================================================
x = np.linspace(0, 8, 500)
for tau in [0.5, 1.0, 1.5, 2.0, 3.0]:
    plt.plot(x, pdf_exp(x, tau), label=f"tau = {tau} s")
plt.xlabel("t [s]")
plt.ylabel("f(t; tau)")
plt.legend()
plt.title("PDF exponencial")
plt.savefig("P2_pdf_tau.pdf")
plt.close()

# P(t <= 1 s) com tau = 1.5 s (escolhi esse porque fica perto da media dos dados)
tau_h = 1.5
p_num = integrate.quad(lambda s: pdf_exp(s, tau_h), 0, 1)[0]
p_ana = 1 - np.exp(-1 / tau_h)
print(f"P(t <= 1 s | tau = {tau_h}) = {p_num:.4f}  (analitico: {p_ana:.4f})")

# =========================================================
# Problema 3 - verossimilhanca
# =========================================================
def L(tau, dados):
    # produto direto das pdfs (do jeito que o enunciado pede)
    return np.prod(pdf_exp(dados, tau))

print("L(tau=1.25) com todos os dados =", L(1.25, t))   # da 0.0 -> underflow
# cada fator e ~ e^-1/1.25 ~ 0.3, entao o produto de 10000 deles e ~ 10^-5000,
# muito menor que o menor double (~1e-308). Por isso usa log.

# uma medida so, t = 1 s
taus = np.linspace(0.05, 6, 600)
L1 = [L(tau, np.array([1.0])) for tau in taus]
plt.plot(taus, L1)
plt.axvline(1.0, ls="--", color="gray")
plt.xlabel("tau [s]")
plt.ylabel("L(tau | t = 1 s)")
plt.title("Verossimilhanca para uma medida t = 1 s")
plt.savefig("P3_L_uma_medida.pdf")
plt.close()
print("maximo de L para t = 1 s em tau =", round(taus[np.argmax(L1)], 3))

# =========================================================
# Problema 4 - -2 lnL com todos os dados
# =========================================================
def m2lnL(tau):
    # -2 ln L = 2 N ln(tau) + 2 sum(t) / tau
    return 2 * N * np.log(tau) + 2 * np.sum(t) / tau

# derivando e igualando a zero: tau_hat = media dos t
tau_hat = np.mean(t)
sigma_tau = tau_hat / np.sqrt(N)        # da segunda derivada: 1/sigma^2 = N/tau^2
print(f"analitico: tau = {tau_hat:.4f} +- {sigma_tau:.4f} s")

taus = np.linspace(1.18, 1.33, 500)
y = m2lnL(taus) - m2lnL(tau_hat)
plt.plot(taus, y)
plt.axhline(1, ls="--", color="gray")
plt.axvline(tau_hat - sigma_tau, ls=":", color="gray")
plt.axvline(tau_hat + sigma_tau, ls=":", color="gray")
plt.xlabel("tau [s]")
plt.ylabel("-2 lnL - (-2 lnL)_min")
plt.title(f"tau = {tau_hat:.3f} +- {sigma_tau:.3f} s")
plt.savefig("P4_m2lnL.pdf")
plt.close()

# =========================================================
# Problema 5 - mesma coisa so que numerico
# =========================================================
res = minimize_scalar(m2lnL, bounds=(0.5, 3.0), method="bounded", options={"xatol": 1e-8})
tau_num = res.x
minimo = res.fun
# pontos onde -2lnL sobe 1 em relacao ao minimo
f = lambda tau: m2lnL(tau) - minimo - 1
tau_baixo = brentq(f, 0.5, tau_num)
tau_cima = brentq(f, tau_num, 3.0)
print(f"numerico: tau = {tau_num:.4f} -{tau_num - tau_baixo:.4f} +{tau_cima - tau_num:.4f} s")

# ajuste binado so pra comparar (Poisson em cada bin, 100 bins)
cont, bordas = np.histogram(t, bins=100, range=(0, 12.6))

def m2lnL_binado(tau):
    nu = N * (np.exp(-bordas[:-1] / tau) - np.exp(-bordas[1:] / tau))
    return -2 * np.sum(cont * np.log(nu) - nu)

res_b = minimize_scalar(m2lnL_binado, bounds=(0.5, 3.0), method="bounded")
print(f"binado (100 bins): tau = {res_b.x:.4f} s")

plt.plot(taus, m2lnL(taus) - minimo, label="nao binado")
plt.plot(taus, [m2lnL_binado(tau) - res_b.fun for tau in taus], "--", label="binado (100 bins)")
plt.axhline(1, ls=":", color="gray")
plt.axvline(tau_baixo, ls=":", color="gray")
plt.axvline(tau_cima, ls=":", color="gray")
plt.xlabel("tau [s]")
plt.ylabel("delta(-2 lnL)")
plt.legend()
plt.title("Ajuste numerico")
plt.savefig("P5_ajuste_numerico.pdf")
plt.close()

# conferindo o ajuste em cima do histograma
centros = 0.5 * (bordas[1:] + bordas[:-1])
plt.errorbar(centros, cont, yerr=np.sqrt(cont), fmt="o", ms=3, label="dados")
plt.plot(centros, N * (bordas[1] - bordas[0]) * pdf_exp(centros, tau_num), label=f"exp, tau = {tau_num:.3f} s")
plt.yscale("log")
plt.xlabel("t [s]")
plt.ylabel("eventos / bin")
plt.legend()
plt.savefig("P5_ajuste_histograma.pdf")
plt.close()
