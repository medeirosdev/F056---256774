# F056 - Lista MC e ajuste, Problemas 1 e 2: metodo de aceitacao-rejeicao
# uso: python3 problema1_2_aceita_rejeita.py   (figuras vao para figuras/)

import os

import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, stats

os.makedirs("figuras", exist_ok=True)

# so uso o gerador uniforme do numpy (Mersenne-Twister / PCG64), nada de rng.normal
rng = np.random.default_rng(2026)


# =========================================================
# Problema 1 - gerador por aceitacao-rejeicao
# =========================================================
def estimar_fmax(pdf, x_min, x_max, n=100001, margem=1.05):
    # maximo numa grade fina, com uma margem de seguranca
    # (se a pdf tiver um pico mais estreito que a grade, melhor passar fmax na mao)
    x = np.linspace(x_min, x_max, n)
    return margem * np.max(pdf(x))


def aceita_rejeita(pdf, N, x_min, x_max, f_max=None, lote=100000):
    """
    Gera N numeros distribuidos segundo pdf(x) em [x_min, x_max].

    pdf    : funcao do usuario (nao precisa estar normalizada, mas tem que ser >= 0)
    f_max  : tem que ser >= max pdf(x) no intervalo. Se None, estima numa grade.

    Devolve (amostras, n_sorteios), onde n_sorteios e o numero de PARES (x, y)
    sorteados ate conseguir os N aceitos (o numero de uniformes usados e 2*n_sorteios).
    """
    if f_max is None:
        f_max = estimar_fmax(pdf, x_min, x_max)

    aceitos = []
    n_aceitos = 0
    n_sorteios = 0

    # em vez de sortear um par por vez (lento em python), sorteio lotes de pares.
    # conto os sorteios so ate o par que completou os N aceitos, entao o
    # resultado e o mesmo de fazer um por vez
    while n_aceitos < N:
        x = rng.uniform(x_min, x_max, lote)
        y = rng.uniform(0.0, f_max, lote)
        fx = pdf(x)
        if np.any(fx > f_max):
            raise ValueError(f"f_max = {f_max} e menor que a pdf em algum ponto ({fx.max()})")
        passou = fx > y

        faltam = N - n_aceitos
        idx = np.flatnonzero(passou)
        if len(idx) >= faltam:
            ultimo = idx[faltam - 1]          # par que completou os N
            aceitos.append(x[idx[:faltam]])
            n_sorteios += ultimo + 1
            n_aceitos = N
        else:
            aceitos.append(x[idx])
            n_sorteios += lote
            n_aceitos += len(idx)

    return np.concatenate(aceitos), n_sorteios


def eficiencia_esperada(pdf, x_min, x_max, f_max):
    area = integrate.quad(pdf, x_min, x_max, limit=200)[0]
    return area / ((x_max - x_min) * f_max)


def comparar_com_pdf(ax, amostras, pdf, x_min, x_max, titulo, nbins=50):
    # desenha o histograma com a pdf normalizada para o numero de eventos e faz um teste de KS
    area = integrate.quad(pdf, x_min, x_max, limit=200)[0]
    largura = (x_max - x_min) / nbins
    ax.hist(amostras, bins=nbins, range=(x_min, x_max), histtype="stepfilled", alpha=0.5, label="MC (aceita-rejeita)")
    x = np.linspace(x_min, x_max, 1000)
    ax.plot(x, len(amostras) * largura * pdf(x) / area, "r", label="PDF")
    cdf = lambda v: np.array([integrate.quad(pdf, x_min, vi, limit=200)[0] for vi in np.atleast_1d(v)]) / area
    # KS numa sub-amostra pra nao demorar com o quad
    ks = stats.kstest(amostras[:2000], cdf)
    ax.set_title(f"{titulo}\nKS p-valor = {ks.pvalue:.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("eventos / bin")
    ax.legend(fontsize=8)
    return ks.pvalue


def gauss(x, mu=0.0, sigma=1.0):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (np.sqrt(2 * np.pi) * sigma)


N = 10000
FMAX_GAUSS = 1 / np.sqrt(2 * np.pi)     # maximo da Gauss(0, 1), em x = 0

# ---- testes com outras PDFs (Problema 1) ----
def pdf_sin2(x):
    return np.sin(x) ** 2                 # nao normalizada, de proposito


def pdf_exp_trunc(x, lam=1.0):
    return lam * np.exp(-lam * x)          # exponencial truncada em [0, 5]


def pdf_bimodal(x):
    # duas gaussianas de alturas diferentes, pra testar uma pdf com dois picos
    return 0.7 * gauss(x, -2.0, 0.7) + 0.3 * gauss(x, 2.5, 1.2)


testes = [
    ("sin^2(x) em [0, pi]", pdf_sin2, 0.0, np.pi, 1.0),
    ("exp(-x) truncada em [0, 5]", pdf_exp_trunc, 0.0, 5.0, 1.0),
    ("soma de 2 gaussianas em [-6, 7]", pdf_bimodal, -6.0, 7.0, None),   # f_max estimado
]

print("=" * 70)
print("Problema 1 - outras PDFs")
print("=" * 70)
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
for a, (nome, pdf, xmin, xmax, fmax) in zip(ax, testes):
    fmax_usado = fmax if fmax is not None else estimar_fmax(pdf, xmin, xmax)
    amostras, nsort = aceita_rejeita(pdf, N, xmin, xmax, fmax_usado)
    eps = N / nsort
    eps_esp = eficiencia_esperada(pdf, xmin, xmax, fmax_usado)
    p = comparar_com_pdf(a, amostras, pdf, xmin, xmax, nome)
    print(f"{nome:32s}: f_max = {fmax_usado:.4f}, sorteios = {nsort}, eps = {eps:.4f} (esperada {eps_esp:.4f}), KS p = {p:.2f}")
plt.tight_layout()
plt.savefig("figuras/outras_pdfs.png", dpi=120)
plt.close()

# =========================================================
# Problema 2 - distribuicao normal
# =========================================================
print()
print("=" * 70)
print("Problema 2 - Gauss(0, 1), N = 10^4 aceitos")
print("=" * 70)

# (a) intervalo [-5, 5]
amostras, nsort = aceita_rejeita(gauss, N, -5.0, 5.0, FMAX_GAUSS)
eps = N / nsort
eps_esp = eficiencia_esperada(gauss, -5.0, 5.0, FMAX_GAUSS)
print(f"(a) [-5, 5]: {nsort} pares sorteados ({2 * nsort} numeros uniformes)")
print(f"    eficiencia = {eps:.4f}, esperada = {eps_esp:.4f}")
print(f"    media = {amostras.mean():.4f}, desvio = {amostras.std(ddof=1):.4f}")

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
p = comparar_com_pdf(ax[0], amostras, gauss, -5.0, 5.0, f"Gauss(0,1) em [-5, 5] - {nsort} pares para 10^4 aceitos")

# desenho dos pares aceitos e rejeitados (so os primeiros 3000)
xs = rng.uniform(-5, 5, 3000)
ys = rng.uniform(0, FMAX_GAUSS, 3000)
ok = gauss(xs) > ys
ax[1].plot(xs[ok], ys[ok], ".", ms=2, color="tab:blue", label="aceito")
ax[1].plot(xs[~ok], ys[~ok], ".", ms=2, color="tab:gray", label="rejeitado")
xx = np.linspace(-5, 5, 500)
ax[1].plot(xx, gauss(xx), "r", label="PDF")
ax[1].set_xlabel("x")
ax[1].set_ylabel("y")
ax[1].set_title(f"pares (x, y): fracao aceita = {ok.mean():.3f}")
ax[1].legend(fontsize=8, loc="upper right")
plt.tight_layout()
plt.savefig("figuras/gauss_aceita_rejeita.png", dpi=120)
plt.close()

# (b) varios intervalos
print()
print("(b) eficiencia em funcao do intervalo")
print(f"{'intervalo':>12s} {'pares':>8s} {'eps medida':>11s} {'eps esperada':>13s} {'1/(L f_max)':>12s}")
intervalos = [3.0, 5.0, 10.0]
for a in intervalos:
    _, ns = aceita_rejeita(gauss, N, -a, a, FMAX_GAUSS)
    e_esp = eficiencia_esperada(gauss, -a, a, FMAX_GAUSS)
    print(f"{f'[-{a:g}, {a:g}]':>12s} {ns:8d} {N / ns:11.4f} {e_esp:13.4f} {1 / (2 * a * FMAX_GAUSS):12.4f}")

# 100 repeticoes no intervalo [-5, 5]
n_rep = 100
nsorteios = np.array([aceita_rejeita(gauss, N, -5.0, 5.0, FMAX_GAUSS)[1] for _ in range(n_rep)])
# o numero de tentativas ate N sucessos segue uma binomial negativa:
# media = N/eps, desvio = sqrt(N (1 - eps)) / eps
media_esp = N / eps_esp
desvio_esp = np.sqrt(N * (1 - eps_esp)) / eps_esp
print()
print(f"100 repeticoes em [-5, 5]: <N_sorteios> = {nsorteios.mean():.0f} +- {nsorteios.std(ddof=1):.0f}")
print(f"    esperado (binomial negativa): {media_esp:.0f} +- {desvio_esp:.0f}")

plt.figure(figsize=(7, 5))
plt.hist(nsorteios, bins=15, histtype="stepfilled", alpha=0.6, label="100 repeticoes")
xx = np.linspace(nsorteios.min() - 300, nsorteios.max() + 300, 300)
largura = (nsorteios.max() - nsorteios.min()) / 15
plt.plot(xx, n_rep * largura * gauss(xx, media_esp, desvio_esp), "r", label="binomial negativa (aprox. gaussiana)")
plt.axvline(media_esp, color="r", ls=":")
plt.xlabel("N_sorteios (pares) para 10^4 aceitos")
plt.ylabel("repeticoes")
plt.title(f"[-5, 5]: media = {nsorteios.mean():.0f}, desvio = {nsorteios.std(ddof=1):.0f}")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig("figuras/n_sorteios_100_repeticoes.png", dpi=120)
plt.close()

# eficiencia em funcao da meia-largura do intervalo
a_lista = np.linspace(1, 12, 23)
eps_med = [N / aceita_rejeita(gauss, N, -a, a, FMAX_GAUSS)[1] for a in a_lista]
eps_teo = [eficiencia_esperada(gauss, -a, a, FMAX_GAUSS) for a in a_lista]
plt.figure(figsize=(7, 5))
plt.plot(a_lista, eps_med, "o", label="medida (10^4 aceitos)")
plt.plot(a_lista, eps_teo, "-", label="esperada")
plt.plot(a_lista, 1 / (2 * a_lista * FMAX_GAUSS), ":", label=r"$\sqrt{2\pi}/(2a)$ (area = 1)")
plt.xlabel("a  (intervalo [-a, a])")
plt.ylabel("eficiencia")
plt.ylim(0, 1)
plt.legend()
plt.tight_layout()
plt.savefig("figuras/eficiencia_vs_intervalo.png", dpi=120)
plt.close()
