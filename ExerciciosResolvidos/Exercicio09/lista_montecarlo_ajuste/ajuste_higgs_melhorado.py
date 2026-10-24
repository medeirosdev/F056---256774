#!/usr/bin/env python3
# F056 - Lista MC e ajuste, Problema 3: versao melhorada do ajuste_higgs_v2.py
#
# uso: python3 ajuste_higgs_melhorado.py [pythia_higgs.root]
#
# Mudancas em relacao ao original (detalhes no README.md):
#   (1) alem do chi2 de Neyman do original (sigma_i^2 = max(n_i, 1)), tem o chi2 de Pearson
#       (sigma_i^2 = previsao) e o chi2 de verossimilhanca de Poisson (Baker-Cousins), e a
#       previsao de cada bin e a INTEGRAL do modelo no bin (pelas CDFs), nao f(centro) * largura
#   (2) o mesmo valor inicial (mu = 125 GeV) em todos os ajustes + varredura de valores iniciais
#   (3) imprime chi2/ndof e p-valor, e para o programa se o ajuste final nao for valido
#   (4) estudo com NBINS entre 50 e 1000 (tabela + figuras/estudo_nbins.png)
#   (5) pico da Breit-Wigner (bw_mu) pode ficar livre
#   (6) outras formas de sinal: Crystal Ball e soma de duas gaussianas

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from iminuit import Minuit
from scipy import stats


# ============================================================
# Configuracoes
# ============================================================

ARQUIVO_ROOT = "pythia_higgs.root"
NOME_ARVORE = "events"
NOME_RAMO = "mH"

MMIN = 50.0
MMAX = 400.0

NBINS_ORIGINAL = 1000                       # o que o programa original usa
NBINS = 350                                 # bins de 1 GeV para o GOF e para as figuras
NBINS_ESTUDO = [50, 100, 175, 350, 500, 700, 1000]

BW_MU = 91.0                                # valor (inicial ou fixo) do pico da Breit-Wigner
MU_INICIAL = 125.0                          # mesmo valor inicial de mu em TODOS os ajustes
MU_INICIAIS_TESTE = [80.0, 92.0, 100.0, 110.0, 125.0, 140.0]

os.makedirs("figuras", exist_ok=True)


# ============================================================
# Leitura do arquivo ROOT
# ============================================================

def ler_dados_root(nome_arquivo, nome_arvore, nome_ramo):
    import ROOT

    if not os.path.exists(nome_arquivo):
        sys.exit(f"Arquivo {nome_arquivo} nao encontrado (ele nao vai no repositorio, "
                 f"copie do diretorio Exemplos/Estatistica/Example_2_Higgs do professor)")

    # RDataFrame le o ramo inteiro de uma vez (bem mais rapido que o loop em python)
    df = ROOT.RDataFrame(nome_arvore, nome_arquivo)
    dados = df.AsNumpy([nome_ramo])[nome_ramo].astype(float)

    dados = dados[(dados >= MMIN) & (dados <= MMAX)]
    if len(dados) == 0:
        sys.exit("Nenhum evento no intervalo selecionado.")
    return dados


# ============================================================
# Formas (PDF e CDF), normalizadas depois no intervalo [MMIN, MMAX]
# ============================================================
# Para cada forma guardo a pdf e a cdf. A cdf serve para:
#  - normalizar no intervalo: N = cdf(MMAX) - cdf(MMIN)
#  - calcular a fracao exata de eventos em cada bin: cdf(b_i+1) - cdf(b_i)

# ---- sinais ----
def pdf_gauss(x, mu, sigma):
    return stats.norm.pdf(x, mu, sigma)


def cdf_gauss(x, mu, sigma):
    return stats.norm.cdf(x, mu, sigma)


def pdf_cb(x, mu, sigma, alpha, n):
    # Crystal Ball: nucleo gaussiano + cauda em lei de potencia para massas menores
    # (a perda de energia por radiacao de estado final so empurra a massa para baixo)
    return stats.crystalball.pdf(x, alpha, n, loc=mu, scale=sigma)


def cdf_cb(x, mu, sigma, alpha, n):
    return stats.crystalball.cdf(x, alpha, n, loc=mu, scale=sigma)


def pdf_2gauss(x, mu, sigma, mu2, sigma2, f):
    # f = fracao do sinal no pico estreito
    return f * stats.norm.pdf(x, mu, sigma) + (1 - f) * stats.norm.pdf(x, mu2, sigma2)


def cdf_2gauss(x, mu, sigma, mu2, sigma2, f):
    return f * stats.norm.cdf(x, mu, sigma) + (1 - f) * stats.norm.cdf(x, mu2, sigma2)


def pdf_fsr(x, mu, sigma, mu2, sigma2, f):
    # pico estreito em mu + cauda de radiacao (FSR) que so existe ABAIXO de mu:
    # gaussiana larga truncada em m <= mu. A FSR so tira energia dos b, entao m_bb nunca
    # fica acima da massa do Higgs (a nao ser pela largura do pico)
    cauda = np.where(x <= mu, stats.norm.pdf(x, mu2, sigma2), 0.0) / stats.norm.cdf(mu, mu2, sigma2)
    return f * stats.norm.pdf(x, mu, sigma) + (1 - f) * cauda


def cdf_fsr(x, mu, sigma, mu2, sigma2, f):
    cauda = stats.norm.cdf(np.minimum(x, mu), mu2, sigma2) / stats.norm.cdf(mu, mu2, sigma2)
    return f * stats.norm.cdf(x, mu, sigma) + (1 - f) * cauda


# nome: (parametros, pdf, cdf, valores iniciais, limites)
# Na CB e nas 2 gaussianas restrinjo o nucleo a perto de 125 GeV e a parte larga a ficar
# abaixo dele: sem isso, na primeira tentativa a gaussiana "estreita" foi parar em 58 GeV com
# sigma = 24 GeV, ou seja virou mais um background e o "sinal" deixou de ser o Higgs.
SINAIS = {
    "gauss": (
        ["mu", "sigma"], pdf_gauss, cdf_gauss,
        dict(mu=MU_INICIAL, sigma=4.0),
        dict(mu=(MMIN, MMAX), sigma=(1.e-3, 50.0)),
    ),
    "cb": (
        ["mu", "sigma", "alpha", "n"], pdf_cb, cdf_cb,
        dict(mu=MU_INICIAL, sigma=1.0, alpha=1.0, n=3.0),
        dict(mu=(115.0, 135.0), sigma=(1.e-3, 20.0), alpha=(0.05, 10.0), n=(1.05, 100.0)),
    ),
    "2gauss": (
        ["mu", "sigma", "mu2", "sigma2", "f"], pdf_2gauss, cdf_2gauss,
        dict(mu=MU_INICIAL, sigma=0.5, mu2=113.0, sigma2=6.0, f=0.1),
        dict(mu=(115.0, 135.0), sigma=(1.e-3, 10.0), mu2=(90.0, 125.0), sigma2=(1.0, 30.0), f=(0.0, 1.0)),
    ),
    "pico+fsr": (
        ["mu", "sigma", "mu2", "sigma2", "f"], pdf_fsr, cdf_fsr,
        dict(mu=MU_INICIAL, sigma=0.5, mu2=113.0, sigma2=6.0, f=0.1),
        dict(mu=(115.0, 135.0), sigma=(1.e-3, 10.0), mu2=(60.0, 135.0), sigma2=(1.0, 50.0), f=(0.0, 1.0)),
    ),
}


# ---- backgrounds ----
def pdf_bw(x, m0, gamma):
    return gamma / (2 * np.pi) / ((x - m0) ** 2 + gamma ** 2 / 4)


def cdf_bw(x, m0, gamma):
    return np.arctan(2 * (x - m0) / gamma) / np.pi


def pdf_exp(x, tau):
    return np.exp(-(x - MMIN) / tau) / tau


def cdf_exp(x, tau):
    return -np.exp(-(x - MMIN) / tau)


# ============================================================
# Modelo: s * f_s + b_bw * f_bw + b_exp * f_exp
# ============================================================

class Modelo:

    def __init__(self, sinal="gauss", bw_livre=False):
        self.sinal = sinal
        self.bw_livre = bw_livre
        self.par_sinal, self.pdf_s, self.cdf_s, self.ini_sinal, self.lim_sinal = SINAIS[sinal]
        self.nomes = self.par_sinal + ["bw_mu", "bw_gamma", "tau", "s", "b_bw", "b_exp"]
        self.k = len(self.par_sinal)

    def descricao(self):
        return f"sinal {self.sinal}, BW {'livre' if self.bw_livre else 'fixa em 91 GeV'}"

    def separa(self, p):
        p = list(p)
        ps = p[:self.k]
        bw_mu, bw_gamma, tau, s, b_bw, b_exp = p[self.k:]
        return ps, bw_mu, bw_gamma, tau, s, b_bw, b_exp

    @staticmethod
    def _norma(cdf, *p):
        return cdf(MMAX, *p) - cdf(MMIN, *p)

    def componentes(self, x, p):
        # densidades em eventos / GeV de cada componente
        ps, bw_mu, bw_gamma, tau, s, b_bw, b_exp = self.separa(p)
        sinal = s * self.pdf_s(x, *ps) / self._norma(self.cdf_s, *ps)
        bw = b_bw * pdf_bw(x, bw_mu, bw_gamma) / self._norma(cdf_bw, bw_mu, bw_gamma)
        ex = b_exp * pdf_exp(x, tau) / self._norma(cdf_exp, tau)
        return sinal, bw, ex

    def densidade(self, x, p):
        return sum(self.componentes(x, p))

    def por_bin(self, bordas, p):
        # numero esperado de eventos em cada bin = integral exata do modelo no bin
        ps, bw_mu, bw_gamma, tau, s, b_bw, b_exp = self.separa(p)

        def fracao(cdf, *q):
            v = cdf(bordas, *q)
            return np.diff(v) / (v[-1] - v[0])

        return (s * fracao(self.cdf_s, *ps)
                + b_bw * fracao(cdf_bw, bw_mu, bw_gamma)
                + b_exp * fracao(cdf_exp, tau))


# ============================================================
# Funcoes de custo
# ============================================================

def custo_ml(modelo, dados):
    # -ln L estendida (nao binada), igual a do original
    def nll(*p):
        ps, bw_mu, bw_gamma, tau, s, b_bw, b_exp = modelo.separa(p)
        dens = np.maximum(modelo.densidade(dados, p), 1.e-300)
        return (s + b_bw + b_exp) - np.sum(np.log(dens))
    return nll


def custo_neyman(modelo, contagens, bordas):
    # o chi2 do original: previsao = f(centro) * largura, sigma_i^2 = max(n_i, 1)
    centros = 0.5 * (bordas[1:] + bordas[:-1])
    largura = bordas[1] - bordas[0]
    variancia = np.maximum(contagens, 1.0)

    def chi2(*p):
        previsao = modelo.densidade(centros, p) * largura
        return np.sum((contagens - previsao) ** 2 / variancia)
    return chi2


def custo_pearson(modelo, contagens, bordas):
    # sigma_i^2 = previsao do modelo (nao depende da flutuacao do proprio bin)
    def chi2(*p):
        previsao = np.maximum(modelo.por_bin(bordas, p), 1.e-300)
        return np.sum((contagens - previsao) ** 2 / previsao)
    return chi2


def chi2_poisson(contagens, previsao):
    # chi2 de razao de verossimilhanca de Poisson (Baker & Cousins 1984):
    # 2 * sum[ nu - n + n ln(n / nu) ]. Vale para bins com poucas contagens (inclusive 0)
    # e o valor no minimo segue aproximadamente uma chi2 com ndof graus de liberdade
    previsao = np.maximum(previsao, 1.e-300)
    termo_log = np.where(contagens > 0, contagens * np.log(np.where(contagens > 0, contagens, 1) / previsao), 0.0)
    return 2.0 * np.sum(previsao - contagens + termo_log)


def custo_poisson(modelo, contagens, bordas):
    def chi2(*p):
        return chi2_poisson(contagens, modelo.por_bin(bordas, p))
    return chi2


METODOS_BINADOS = {
    "neyman": ("chi2 Neyman (original)", custo_neyman),
    "pearson": ("chi2 Pearson", custo_pearson),
    "poisson": ("chi2 Poisson (Baker-Cousins)", custo_poisson),
}


# ============================================================
# Minuit
# ============================================================

def valores_iniciais(modelo, n_total, mu_inicial=MU_INICIAL):
    ini = dict(modelo.ini_sinal)
    ini["mu"] = mu_inicial
    # mesmos valores iniciais do original para os backgrounds e rendimentos
    ini.update(bw_mu=BW_MU, bw_gamma=5.0, tau=50.0,
               s=0.27 * n_total, b_bw=0.30 * n_total, b_exp=0.43 * n_total)
    return [ini[nome] for nome in modelo.nomes]


def ajustar(funcao, modelo, n_total, errordef, mu_inicial=MU_INICIAL, inicio=None):
    # inicio: valores de outro ajuste para usar como ponto de partida
    ini = valores_iniciais(modelo, n_total, mu_inicial) if inicio is None else list(inicio)
    fit = Minuit(funcao, *ini, name=modelo.nomes)

    for nome, lim in modelo.lim_sinal.items():
        fit.limits[nome] = lim
    fit.limits["bw_mu"] = (60.0, 130.0)
    fit.limits["bw_gamma"] = (1.e-4, 100.0)
    fit.limits["tau"] = (1.e-3, 1000.0)
    for nome in ["s", "b_bw", "b_exp"]:
        fit.limits[nome] = (0.0, None)

    if not modelo.bw_livre:
        fit.fixed["bw_mu"] = True

    fit.errordef = errordef
    fit.strategy = 1
    fit.migrad(ncall=100000)
    if fit.valid:
        fit.hesse()
    return fit


def verificar(fit, titulo, parar=True):
    # (3) no original so aparecia um aviso; aqui o programa para se o ajuste final nao convergiu
    if fit.valid and fit.accurate:
        return True
    print(f"\n*** ajuste '{titulo}' NAO e valido (valid={fit.valid}, matriz de cov. precisa={fit.accurate}) ***")
    print(fit.fmin)
    if parar:
        sys.exit("Interrompendo: nao faz sentido usar os parametros de um ajuste que nao convergiu.")
    return False


def qualidade(chi2, nbins, fit):
    ndof = nbins - fit.nfit
    return chi2, ndof, stats.chi2.sf(chi2, ndof)


def gof_ml(modelo, fit, dados, nbins=NBINS):
    # o ajuste nao binado nao tem chi2 proprio; para ter uma medida de qualidade
    # calculo o chi2 de Poisson dos parametros do ML num histograma de nbins
    contagens, bordas = np.histogram(dados, bins=nbins, range=(MMIN, MMAX))
    return qualidade(chi2_poisson(contagens, modelo.por_bin(bordas, fit.values)), nbins, fit)


def imprimir_resultados(titulo, fit, gof=None):
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)
    for nome in fit.parameters:
        fixo = " (fixo)" if fit.fixed[nome] else ""
        print(f"{nome:>10s} = {fit.values[nome]:14.6f} +/- {fit.errors[nome]:.6f}{fixo}")
    print(f"funcao minima = {fit.fval:.3f}   valido = {fit.valid}   chamadas = {fit.nfcn}")
    if gof is not None:
        chi2, ndof, p = gof
        print(f"chi2/ndof = {chi2:.1f}/{ndof} = {chi2 / ndof:.2f}   p-valor = {p:.3g}")


# ============================================================
# Graficos
# ============================================================

def grafico_ajuste(dados, modelo, fit, nome_arquivo, titulo, fit_extra=None, modelo_extra=None, rotulo_extra=None):
    contagens, bordas = np.histogram(dados, bins=NBINS, range=(MMIN, MMAX))
    centros = 0.5 * (bordas[1:] + bordas[:-1])
    largura = bordas[1] - bordas[0]
    previsao = modelo.por_bin(bordas, fit.values)
    pulls = (contagens - previsao) / np.sqrt(np.maximum(previsao, 1.0))

    # pontos extras em volta do pico (o nucleo das 2 gaussianas tem sigma de poucos MeV)
    mu = fit.values["mu"]
    x = np.sort(np.concatenate([np.linspace(MMIN, MMAX, 4000), np.linspace(mu - 0.05, mu + 0.05, 401)]))
    sinal, bw, ex = (c * largura for c in modelo.componentes(x, fit.values))

    fig = plt.figure(figsize=(14, 8))
    grade = fig.add_gridspec(2, 2, height_ratios=[3, 1], width_ratios=[1.6, 1])
    ax = fig.add_subplot(grade[0, 0])
    az = fig.add_subplot(grade[0, 1])
    ap = fig.add_subplot(grade[1, :])

    for a in (ax, az):
        a.errorbar(centros, contagens, yerr=np.sqrt(np.maximum(contagens, 1.0)), fmt="ko", ms=2, label="dados")
        a.stairs(previsao, bordas, color="b", lw=1.5, label="modelo (integral no bin)")
        a.plot(x, sinal, "g-", lw=1.2, label=f"sinal ({modelo.sinal})")
        a.plot(x, bw, "m:", lw=2, label="Breit-Wigner")
        a.plot(x, ex, "c:", lw=2, label="exponencial")
        if fit_extra is not None:
            a.stairs(modelo_extra.por_bin(bordas, fit_extra.values), bordas, color="r", ls="--", lw=1.2, label=rotulo_extra)
        a.set_xlabel(r"$m\;(\mathrm{GeV})$")
        a.set_ylabel(f"eventos / {largura:.0f} GeV")
        a.grid(alpha=0.25)
    ax.set_yscale("log")
    ax.set_ylim(10, 3 * contagens.max())
    ax.set_title(titulo)
    ax.legend(fontsize=8)
    az.set_xlim(95, 135)
    janela = (centros > 95) & (centros < 135)
    az.set_ylim(0, 1.5 * contagens[janela].max())
    az.set_title("zoom na regiao do Higgs (escala linear, pico estreito cortado)")

    ap.axhline(0, color="k", lw=0.8)
    ap.plot(centros, pulls, "k.", ms=3)
    ap.set_ylim(-15, 15)
    ap.set_xlabel(r"$m\;(\mathrm{GeV})$")
    ap.set_ylabel(r"(n - $\nu$) / $\sqrt{\nu}$")
    ap.grid(alpha=0.25)

    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=120)
    plt.close()


def grafico_nbins(tabela, ml, nome_arquivo):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
    estilos = {"neyman": "o-", "pearson": "s--", "poisson": "^-."}
    for a, par, rot in zip(ax, ["mu", "sigma", "s"], [r"$\mu$ (GeV)", r"$\sigma$ (GeV)", "s (eventos de sinal)"]):
        for metodo, (titulo, _) in METODOS_BINADOS.items():
            linhas = [l for l in tabela if l["metodo"] == metodo]
            nb = np.array([l["nbins"] for l in linhas])
            v = np.array([l["valores"][par] for l in linhas])
            e = np.array([l["erros"][par] for l in linhas])
            a.errorbar(nb, v, yerr=e, fmt=estilos[metodo], ms=5, capsize=3, label=titulo)
        a.axhline(ml.values[par], color="k", lw=1)
        a.axhspan(ml.values[par] - ml.errors[par], ml.values[par] + ml.errors[par], color="gray", alpha=0.3,
                  label="ML nao binado")
        a.set_xscale("log")
        a.set_xlabel("NBINS")
        a.set_ylabel(rot)
        a.grid(alpha=0.25)
    ax[0].legend(fontsize=8)
    fig.suptitle("Modelo original (gaussiana + BW fixa + exponencial), mu inicial = 125 GeV")
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=120)
    plt.close()


# ============================================================
# Programa principal
# ============================================================

def main():
    nome_arquivo = sys.argv[1] if len(sys.argv) > 1 else ARQUIVO_ROOT
    dados = ler_dados_root(nome_arquivo, NOME_ARVORE, NOME_RAMO)
    n_total = len(dados)
    print(f"Arquivo utilizado: {nome_arquivo}")
    print(f"Numero de eventos em [{MMIN:.0f}, {MMAX:.0f}] GeV: {n_total}")

    original = Modelo("gauss", bw_livre=False)

    # --------------------------------------------------------
    # (2) dependencia com o valor inicial de mu (modelo original)
    # --------------------------------------------------------
    print()
    print("=" * 70)
    print("(2) Valor inicial de mu - modelo original")
    print("    ML nao binado e chi2 de Neyman com NBINS = 1000 (como no original)")
    print("=" * 70)
    cont_orig, bordas_orig = np.histogram(dados, bins=NBINS_ORIGINAL, range=(MMIN, MMAX))
    print(f"{'mu inicial':>10s} | {'ML: mu':>8s} {'sigma':>7s} {'-lnL':>14s} | {'Neyman: mu':>10s} {'sigma':>7s} {'chi2':>10s}")
    for mu0 in MU_INICIAIS_TESTE:
        f_ml = ajustar(custo_ml(original, dados), original, n_total, Minuit.LIKELIHOOD, mu0)
        f_ch = ajustar(custo_neyman(original, cont_orig, bordas_orig), original, n_total, Minuit.LEAST_SQUARES, mu0)
        print(f"{mu0:10.0f} | {f_ml.values['mu']:8.2f} {f_ml.values['sigma']:7.2f} {f_ml.fval:14.1f} | "
              f"{f_ch.values['mu']:10.2f} {f_ch.values['sigma']:7.2f} {f_ch.fval:10.1f}"
              f"{'' if f_ml.valid and f_ch.valid else '  (algum invalido)'}")

    # --------------------------------------------------------
    # ajuste ML do modelo original, agora com mu inicial = 125 (referencia)
    # --------------------------------------------------------
    ml_orig = ajustar(custo_ml(original, dados), original, n_total, Minuit.LIKELIHOOD)
    verificar(ml_orig, "ML original")
    imprimir_resultados("ML nao binado - modelo original (mu inicial 125)", ml_orig, gof_ml(original, ml_orig, dados))

    # --------------------------------------------------------
    # (1), (3) e (4) estudo com NBINS para os tres chi2
    # --------------------------------------------------------
    print()
    print("=" * 70)
    print("(1)(3)(4) Ajustes binados do modelo original em funcao de NBINS (mu inicial = 125)")
    print("=" * 70)
    print(f"ML (nao depende de NBINS): mu = {ml_orig.values['mu']:.3f} +- {ml_orig.errors['mu']:.3f}, "
          f"sigma = {ml_orig.values['sigma']:.3f} +- {ml_orig.errors['sigma']:.3f}, "
          f"s = {ml_orig.values['s']:.0f} +- {ml_orig.errors['s']:.0f}")
    print(f"{'metodo':>8s} {'NBINS':>6s} {'mu':>17s} {'sigma':>15s} {'s':>18s} {'chi2/ndof':>10s} {'p-valor':>9s} {'valido':>6s}")
    tabela = []
    for metodo, (titulo, construtor) in METODOS_BINADOS.items():
        for nb in NBINS_ESTUDO:
            contagens, bordas = np.histogram(dados, bins=nb, range=(MMIN, MMAX))
            f = ajustar(construtor(original, contagens, bordas), original, n_total, Minuit.LEAST_SQUARES)
            chi2, ndof, p = qualidade(f.fval, nb, f)
            tabela.append(dict(metodo=metodo, nbins=nb, valores=dict(f.values.to_dict()),
                               erros=dict(f.errors.to_dict()), valido=f.valid))
            v, e = f.values, f.errors
            print(f"{metodo:>8s} {nb:6d} {v['mu']:8.2f} +- {e['mu']:5.2f} {v['sigma']:6.2f} +- {e['sigma']:5.2f} "
                  f"{v['s']:8.0f} +- {e['s']:6.0f} {chi2 / ndof:10.2f} {p:9.2g} {str(f.valid):>6s}")
    grafico_nbins(tabela, ml_orig, "figuras/estudo_nbins.png")

    # --------------------------------------------------------
    # (5) pico da Breit-Wigner livre
    # (6) outras formas de sinal
    # --------------------------------------------------------
    print()
    print("=" * 70)
    print("(5)(6) ML nao binado com outras formas de sinal e com o pico da BW livre")
    print("=" * 70)
    # O pico de 125 GeV tem largura de poucos MeV. Partindo direto de sigma ~ 0.5 GeV o Migrad
    # no ML nao binado perde esse pico (f -> 0). Entao primeiro faco um ajuste binado rapido
    # (chi2 de Poisson, bins de 0.5 GeV) e uso o resultado como ponto de partida do ML.
    cont_semente, bordas_semente = np.histogram(dados, bins=700, range=(MMIN, MMAX))
    resultados = []
    for sinal, bw_livre in [("gauss", False), ("gauss", True), ("cb", True), ("2gauss", True), ("pico+fsr", True)]:
        modelo = Modelo(sinal, bw_livre)
        if (sinal, bw_livre) == ("gauss", False):
            fit = ml_orig
        else:
            semente = ajustar(custo_poisson(modelo, cont_semente, bordas_semente), modelo, n_total,
                              Minuit.LEAST_SQUARES)
            fit = ajustar(custo_ml(modelo, dados), modelo, n_total, Minuit.LIKELIHOOD, inicio=semente.values)
        verificar(fit, modelo.descricao(), parar=False)
        gof = gof_ml(modelo, fit, dados)
        imprimir_resultados(f"ML - {modelo.descricao()}", fit, gof)
        resultados.append((modelo, fit, gof))

    print()
    ref = resultados[0][1].fval
    print(f"{'modelo':>36s} {'npar':>5s} {'2*Delta(-lnL)':>14s} {'chi2/ndof (1 GeV)':>18s} {'s':>16s}")
    for modelo, fit, (chi2, ndof, p) in resultados:
        print(f"{modelo.descricao():>36s} {fit.nfit:5d} {2 * (fit.fval - ref):14.1f} {chi2 / ndof:18.2f} "
              f"{fit.values['s']:8.0f} +- {fit.errors['s']:5.0f}")

    # o melhor modelo e o de menor -lnL (os modelos tem numero de parametros diferente,
    # mas as diferencas de -2lnL sao de milhares, muito maiores que o numero de parametros)
    modelo_m, fit_m, gof_m = min(resultados, key=lambda r: r[1].fval)
    verificar(fit_m, f"melhor modelo ({modelo_m.descricao()})", parar=True)
    print(f"\nMelhor modelo: {modelo_m.descricao()}")

    grafico_ajuste(dados, original, ml_orig, "figuras/ajuste_original_ml_1gev.png",
                   "Modelo original (gaussiana + BW fixa + exp), ML nao binado")
    grafico_ajuste(dados, modelo_m, fit_m, "figuras/ajuste_melhorado.png",
                   f"Ajuste melhorado: {modelo_m.descricao()}, ML nao binado",
                   fit_extra=ml_orig, modelo_extra=original, rotulo_extra="modelo original (ML)")

    # mesmo modelo com o chi2 de Poisson, pra conferir que binado e nao binado concordam
    contagens, bordas = np.histogram(dados, bins=NBINS, range=(MMIN, MMAX))
    f_bin = ajustar(custo_poisson(modelo_m, contagens, bordas), modelo_m, n_total, Minuit.LEAST_SQUARES,
                    inicio=fit_m.values)
    verificar(f_bin, "melhor modelo, chi2 de Poisson", parar=False)
    imprimir_resultados(f"chi2 Poisson (NBINS = {NBINS}) - {modelo_m.descricao()}", f_bin,
                        qualidade(f_bin.fval, NBINS, f_bin))


if __name__ == "__main__":
    main()
