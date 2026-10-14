# F056 - Lista 2, Problemas 6 e 7: Gaussiana e Teorema Central do Limite
# uso: python3 distribuicoes.py   (gera os graficos P6_*.pdf e P7_*.pdf nessa pasta)

import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, stats

rng = np.random.default_rng(42)   # semente fixa pra dar sempre o mesmo resultado


def gauss(x, mu, sigma):
    return np.exp(-(x - mu) ** 2 / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))


# =========================================================
# Problema 6 - Gaussiana
# =========================================================
x = np.linspace(-8, 8, 1000)
for mu, sigma in [(0, 1), (2, 1), (0, 2.5)]:
    plt.plot(x, gauss(x, mu, sigma), label=f"mu = {mu}, sigma = {sigma}")
plt.xlabel("x")
plt.ylabel("f(x; mu, sigma)")
plt.title("Gaussiana para varios (mu, sigma)")
plt.legend()
plt.savefig("P6_gaussianas.pdf")
plt.close()

# conferindo que a area continua 1 mesmo mudando sigma
for mu, sigma in [(0, 1), (2, 1), (0, 2.5)]:
    area = integrate.quad(gauss, -np.inf, np.inf, args=(mu, sigma))[0]
    print(f"area (mu = {mu}, sigma = {sigma}) = {area:.6f}")

# particula X ~ Gauss(200 GeV, 2 GeV)
mu_X, sigma_X = 200.0, 2.0
p205 = integrate.quad(gauss, 205, np.inf, args=(mu_X, sigma_X))[0]
p203 = integrate.quad(gauss, 203, np.inf, args=(mu_X, sigma_X))[0]
p2x203 = p203 ** 2      # as duas sao independentes -> multiplica
print(f"P(m >= 205 GeV) = {p205:.5f} = {100 * p205:.3f} %   (2.5 sigma, conferindo: {stats.norm.sf(2.5):.5f})")
print(f"P(m > 203 GeV) para uma = {p203:.5f} = {100 * p203:.3f} %   (1.5 sigma)")
print(f"P(duas com m > 203 GeV) = {p2x203:.6f} = {100 * p2x203:.3f} %")

# desenho das areas
m = np.linspace(190, 210, 1000)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for a, corte, p in zip(ax, [205, 203], [p205, p203]):
    a.plot(m, gauss(m, mu_X, sigma_X), color="k")
    mm = m[m >= corte]
    a.fill_between(mm, gauss(mm, mu_X, sigma_X), alpha=0.4)
    a.set_xlabel("m [GeV]")
    a.set_ylabel("f(m)")
    a.set_title(f"P(m > {corte} GeV) = {100 * p:.2f} %")
plt.tight_layout()
plt.savefig("P6_probabilidades.pdf")
plt.close()

# =========================================================
# Problema 7 - Teorema Central do Limite com exponenciais
# =========================================================
# x = (1/N) * soma de x_i, com x_i ~ E(x; lambda_i) = lambda_i exp(-lambda_i x)
# cada x_i tem um lambda diferente. Sorteio os lambdas uma vez so, entre 0.5 e 3.
# (numpy usa scale = 1/lambda)
n_experimentos = 100000


def media_exponenciais(N):
    lambdas = rng.uniform(0.5, 3.0, size=N)
    amostras = rng.exponential(scale=1 / lambdas, size=(n_experimentos, N))
    return amostras.mean(axis=1)


# primeiro N = 3, como o enunciado pede
x3 = media_exponenciais(3)

# depois varios N pra ver quando fica gaussiano
lista_N = [1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 500]
assimetria = []
curtose = []
amostras_N = {}
for N in lista_N:
    xs = x3 if N == 3 else media_exponenciais(N)
    amostras_N[N] = xs
    assimetria.append(stats.skew(xs))
    curtose.append(stats.kurtosis(xs))     # curtose em excesso, 0 pra gaussiana
    print(f"N = {N:4d}: assimetria = {assimetria[-1]:.3f}, curtose em excesso = {curtose[-1]:.3f}")

# histogramas com uma gaussiana de mesma media e desvio por cima
mostrar = [1, 3, 10, 30, 100, 500]
fig, ax = plt.subplots(2, 3, figsize=(15, 8))
for a, N in zip(ax.flatten(), mostrar):
    xs = amostras_N[N]
    a.hist(xs, bins=80, density=True, alpha=0.6, label="MC")
    xx = np.linspace(xs.min(), xs.max(), 300)
    a.plot(xx, gauss(xx, xs.mean(), xs.std()), "r", label="gaussiana")
    a.set_title(f"N = {N}   (assimetria = {stats.skew(xs):.2f})")
    a.set_xlabel("x")
    a.legend()
plt.tight_layout()
plt.savefig("P7_tcl_histogramas.pdf")
plt.close()

# assimetria e curtose vs N
plt.plot(lista_N, assimetria, "o-", label="assimetria")
plt.plot(lista_N, curtose, "s-", label="curtose em excesso")
plt.axhline(0, color="gray", ls=":")
plt.axhline(0.1, color="gray", ls="--")
plt.xscale("log")
plt.xlabel("N")
plt.ylabel("valor")
plt.title("Quanto a media de N exponenciais se afasta da gaussiana")
plt.legend()
plt.savefig("P7_assimetria_vs_N.pdf")
plt.close()

# escala de comparacao: com lambdas iguais a assimetria da media e 2/sqrt(N)
for N in [3, 30, 100, 400]:
    print(f"lambdas iguais, N = {N}: assimetria esperada = 2/sqrt(N) = {2 / np.sqrt(N):.3f}")
