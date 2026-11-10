#!/usr/bin/env python3
"""
F056 - Lista Geant4, Exercicio 2: perfil longitudinal do chuveiro eletromagnetico no B4a.

Le os CSV da ntuple CaloHits (um por thread: Edep_MeV, Layer, x, y, z, EventID, IsGap) e,
opcionalmente, os da ntuple B4 (Eabs, Egap, Labs, Lgap por evento), e faz:
  (a) o perfil do codigo-base (media por registro, 10 mm por camada / X0 = 5.6 mm)
  (b) o perfil corrigido: soma por camada DENTRO de cada evento e depois media/desvio entre eventos
  (c) profundidade em unidades do X0 efetivo do calorimetro de amostragem
  (d) ajuste da parametrizacao gama dE/dt = E0 b (bt)^(a-1) e^(-bt) / Gamma(a)
  (e) contencao (fracao de E0 no absorvedor, no LAr e no total)
  (f) comparacao chumbo x agua

uso:
  python3 perfil_longitudinal.py --pb 'saidas/ex2_Pb/calo_output_nt_CaloHits_t*.csv' \\
      --agua 'saidas/ex2_agua/calo_output_nt_CaloHits_t*.csv' --saida figuras
  (as aspas sao importantes: o glob e expandido pelo programa)
"""

import argparse
import glob
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import gammainc, gammaln

# ------------------------------------------------------------------
# Geometria do B4a (DetectorConstruction.cc) e materiais (X0 impresso pelo Geant4)
# ------------------------------------------------------------------
N_CAMADAS = 10
ESP_ABS_MM = 10.0          # absoThickness
ESP_GAP_MM = 5.0           # gapThickness (argonio liquido)
ESP_CAMADA_MM = ESP_ABS_MM + ESP_GAP_MM   # 15 mm, e nao 10 mm como no codigo-base
E0_MEV = 10000.0

X0_MM = {"Pb": 5.61253, "agua": 360.8, "LAr": 140.639}   # G4Material::GetRadlen()
EC_MEV = {"Pb": 7.43, "agua": 78.33}                     # energia critica (PDG, e-)
X0_CODIGO_BASE = {"Pb": 5.6, "agua": 361.0}              # o que o enunciado usa


def x0_efetivo(absorvedor):
    """1/X0_ef = sum_i f_i / X0_i, com f_i a fracao da espessura de cada material na camada."""
    t_por_camada = ESP_ABS_MM / X0_MM[absorvedor] + ESP_GAP_MM / X0_MM["LAr"]   # em X0
    return ESP_CAMADA_MM / t_por_camada, t_por_camada


# ------------------------------------------------------------------
# Leitura (arquivo por arquivo, agregando, pra nao carregar ~1 GB de uma vez)
# ------------------------------------------------------------------
COLUNAS = ["Edep_MeV", "Layer", "x", "y", "z", "EventID", "IsGap"]


def ler_hits(padrao):
    arquivos = sorted(glob.glob(padrao))
    if not arquivos:
        sys.exit(f"nenhum arquivo para o padrao {padrao}")
    soma_evento = []          # soma de Edep por (evento, camada, absorvedor/gap)
    hits_camada = []          # soma e numero de registros por camada (para o codigo-base)
    for f in arquivos:
        df = pd.read_csv(f, comment="#", header=None, names=COLUNAS,
                         usecols=["Edep_MeV", "Layer", "EventID", "IsGap"],
                         dtype={"Edep_MeV": np.float64, "Layer": np.int16, "EventID": np.int32, "IsGap": np.int8})
        soma_evento.append(df.groupby(["EventID", "Layer", "IsGap"])["Edep_MeV"].sum())
        hits_camada.append(df.groupby("Layer")["Edep_MeV"].agg(["sum", "count"]))
        print(f"  {f.split('/')[-1]}: {len(df)} registros, {df['EventID'].nunique()} eventos")
    soma = pd.concat(soma_evento).groupby(level=[0, 1, 2]).sum()
    hits = pd.concat(hits_camada).groupby(level=0).sum()
    return soma, hits


def matriz_eventos(soma):
    """matriz (eventos x camadas) da energia depositada por camada em cada evento (abs + gap)."""
    por_camada = soma.groupby(level=["EventID", "Layer"]).sum().unstack("Layer", fill_value=0.0)
    return por_camada.reindex(columns=range(N_CAMADAS), fill_value=0.0)


def ler_b4(padrao):
    arquivos = sorted(glob.glob(padrao)) if padrao else []
    if not arquivos:
        return None
    return pd.concat([pd.read_csv(f, comment="#", header=None, names=["Eabs", "Egap", "Labs", "Lgap"])
                      for f in arquivos], ignore_index=True)


# ------------------------------------------------------------------
# Parametrizacao gama, integrada em cada camada
# ------------------------------------------------------------------
def energia_camadas(t_bordas, A, a, b):
    """Energia em cada camada = A * [P(a, b t_sup) - P(a, b t_inf)], P = gama incompleta regularizada.
    E a integral exata de A b (bt)^(a-1) e^(-bt) / Gamma(a) dentro da camada (as camadas tem 1.8 X0,
    entao avaliar dE/dt so no centro seria uma aproximacao grosseira)."""
    P = gammainc(a, b * np.asarray(t_bordas))
    return A * np.diff(P)


def dE_dt(t, A, a, b):
    """Eq. (2): A b (bt)^(a-1) e^(-bt) / Gamma(a) (calculada em log para nao estourar)."""
    return A * b * np.exp((a - 1) * np.log(b * t) - b * t - gammaln(a))


def ajustar(t_bordas, e_media, e_erro, fixar_E0=False):
    if fixar_E0:
        f = lambda tb, a, b: energia_camadas(tb, E0_MEV, a, b)
        p0, lim = [4.0, 0.5], ([1.01, 0.01], [50.0, 5.0])
    else:
        f = energia_camadas
        p0, lim = [0.9 * E0_MEV, 4.0, 0.5], ([0.0, 1.01, 0.01], [2 * E0_MEV, 50.0, 5.0])
    popt, pcov = curve_fit(lambda _x, *p: f(t_bordas, *p), np.arange(N_CAMADAS), e_media,
                           p0=p0, sigma=e_erro, absolute_sigma=True, bounds=lim)
    if fixar_E0:
        popt = np.concatenate([[E0_MEV], popt])
        cov = np.zeros((3, 3)); cov[1:, 1:] = pcov; pcov = cov
    A, a, b = popt
    # t_max = (a-1)/b e a incerteza por propagacao (com a correlacao entre a e b)
    tmax = (a - 1) / b
    grad = np.array([0.0, 1 / b, -(a - 1) / b ** 2])
    s_tmax = np.sqrt(grad @ pcov @ grad)
    chi2 = np.sum(((e_media - energia_camadas(t_bordas, *popt)) / e_erro) ** 2)
    ndof = N_CAMADAS - (2 if fixar_E0 else 3)
    return popt, np.sqrt(np.diag(pcov)), tmax, s_tmax, chi2, ndof


# ------------------------------------------------------------------
# Analise de um material
# ------------------------------------------------------------------
def analisar(nome, padrao_hits, padrao_b4):
    print()
    print("=" * 78)
    print(f"Absorvedor: {nome}")
    print("=" * 78)
    soma, hits = ler_hits(padrao_hits)
    M = matriz_eventos(soma)
    n_ev = len(M)
    print(f"eventos com deposicao: {n_ev}")

    r = {"nome": nome, "n_ev": n_ev}

    # (a) codigo-base: media de Edep por REGISTRO em cada camada, 10 mm por camada / X0
    r["base_media_hit"] = (hits["sum"] / hits["count"]).reindex(range(N_CAMADAS))
    r["base_t"] = np.arange(N_CAMADAS) * 10.0 / X0_CODIGO_BASE[nome]
    r["hits_por_evento"] = (hits["count"] / n_ev).reindex(range(N_CAMADAS))

    # (b) soma por camada dentro de cada evento, depois media e desvio entre eventos
    r["media"] = M.mean(axis=0).values
    r["desvio"] = M.std(axis=0, ddof=1).values
    r["erro_media"] = r["desvio"] / np.sqrt(n_ev)

    # (c) profundidade em X0 efetivo
    x0ef, t_camada = x0_efetivo(nome)
    r["x0ef"], r["t_camada"] = x0ef, t_camada
    r["t_bordas"] = np.arange(N_CAMADAS + 1) * t_camada
    r["t_centro"] = (np.arange(N_CAMADAS) + 0.5) * t_camada

    # (e) contencao a partir dos hits (absorvedor / gap)
    por_vol = soma.groupby(level="IsGap").sum() / n_ev
    r["f_abs_hits"] = por_vol.get(0, 0.0) / E0_MEV
    r["f_gap_hits"] = por_vol.get(1, 0.0) / E0_MEV
    b4 = ler_b4(padrao_b4)
    if b4 is not None:
        r["f_abs"] = b4["Eabs"].mean() / E0_MEV
        r["f_gap"] = b4["Egap"].mean() / E0_MEV
        r["f_tot"] = (b4["Eabs"] + b4["Egap"]).mean() / E0_MEV
        r["f_tot_rms"] = (b4["Eabs"] + b4["Egap"]).std() / E0_MEV
        r["fs"] = (b4["Egap"] / (b4["Eabs"] + b4["Egap"])).mean()
    r["f_ultima"] = r["media"][-1] / E0_MEV

    print(f"X0 efetivo = {ESP_CAMADA_MM:.0f} mm / ({ESP_ABS_MM:.0f}/{X0_MM[nome]:.2f} + {ESP_GAP_MM:.0f}/{X0_MM['LAr']:.1f}) "
          f"= {x0ef:.2f} mm  ->  {t_camada:.4f} X0 por camada, {N_CAMADAS * t_camada:.2f} X0 no total")
    print(f"codigo-base: {10.0 / X0_CODIGO_BASE[nome]:.4f} X0 por camada "
          f"(erro de {100 * (10.0 / X0_CODIGO_BASE[nome] / t_camada - 1):+.1f} %)")
    print()
    print(f"{'camada':>6s} {'t_centro':>8s} {'<E> MeV':>10s} {'desvio':>9s} {'erro med.':>9s} "
          f"{'<E>/hit':>9s} {'hits/ev':>8s}")
    for i in range(N_CAMADAS):
        print(f"{i:6d} {r['t_centro'][i]:8.2f} {r['media'][i]:10.1f} {r['desvio'][i]:9.1f} "
              f"{r['erro_media'][i]:9.2f} {r['base_media_hit'].iloc[i]:9.4f} {r['hits_por_evento'].iloc[i]:8.0f}")
    print(f"soma das camadas = {r['media'].sum():.1f} MeV = {r['media'].sum() / E0_MEV:.4f} E0")
    if b4 is not None:
        print(f"contencao (ntuple B4): total = {r['f_tot']:.4f} +- {r['f_tot_rms']:.4f} (rms) de E0, "
              f"absorvedor = {r['f_abs']:.4f}, LAr = {r['f_gap']:.4f}, fracao de amostragem = {r['fs']:.4f}")
    print(f"contencao (hits):      absorvedor = {r['f_abs_hits']:.4f}, LAr = {r['f_gap_hits']:.4f}")
    print(f"fracao de E0 na ultima camada = {r['f_ultima']:.4f}")

    # (d) ajuste
    if nome == "Pb":
        tmax_est = np.log(E0_MEV / EC_MEV[nome]) - 0.5
        r["tmax_est"] = tmax_est
        for fixo in (False, True):
            popt, perr, tmax, s_tmax, chi2, ndof = ajustar(r["t_bordas"], r["media"], r["erro_media"], fixo)
            rot = "E0 fixo = 10 GeV" if fixo else "normalizacao A livre"
            print()
            print(f"ajuste ({rot}):")
            print(f"  A = {popt[0]:.1f} +- {perr[0]:.1f} MeV,  a = {popt[1]:.4f} +- {perr[1]:.4f},  "
                  f"b = {popt[2]:.4f} +- {perr[2]:.4f}")
            print(f"  t_max = (a-1)/b = {tmax:.3f} +- {s_tmax:.3f} X0   (estimativa ln(E0/Ec) - 0.5 = {tmax_est:.3f})")
            print(f"  chi2/ndof = {chi2:.1f}/{ndof} = {chi2 / ndof:.2f}")
            fora = 1 - gammainc(popt[1], popt[2] * r["t_bordas"][-1])
            print(f"  fracao do perfil ajustado alem de {r['t_bordas'][-1]:.1f} X0 (vazamento longitudinal) = {fora:.4f}")
            r["ajuste_fixo" if fixo else "ajuste"] = dict(popt=popt, perr=perr, tmax=tmax, s_tmax=s_tmax,
                                                          chi2=chi2, ndof=ndof, fora=fora)
    return r


# ------------------------------------------------------------------
# Figuras
# ------------------------------------------------------------------
def figura_codigo_base(r, saida):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    ax[0].plot(r["base_t"], r["base_media_hit"], "o-", label="codigo-base: media por registro (hit)")
    ax[0].set_xlabel(r"Profundidade [$X_0$] (codigo-base: camada $\times$ 10 mm / 5.6 mm)")
    ax[0].set_ylabel("<dE/dz> (MeV por registro)")
    ax[0].set_title("(a) Perfil do codigo-base (Pb, 1000 e$^-$ de 10 GeV)")
    ax[0].legend()
    ax[0].grid(alpha=0.3)

    # comparacao de forma: tudo normalizado pelo maximo
    a2 = ax[1]
    a2.plot(r["t_centro"], r["media"] / r["media"].max(), "o-", label="energia total por camada e por evento (correto)")
    a2.plot(r["t_centro"], r["base_media_hit"] / r["base_media_hit"].max(), "s--", label="media por registro (codigo-base)")
    a2.plot(r["t_centro"], r["hits_por_evento"] / r["hits_por_evento"].max(), "^:", label="numero de registros por evento")
    a2.set_xlabel(r"Profundidade no centro da camada [$X_{0,\mathrm{ef}}$ = %.2f mm]" % r["x0ef"])
    a2.set_ylabel("normalizado pelo maximo")
    a2.set_title("(b) Por que a media por registro distorce o perfil")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{saida}/perfil_codigo_base.png", dpi=130)
    plt.close()


def figura_perfil(r, saida):
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    t = r["t_centro"]
    larg = r["t_camada"]
    ax.errorbar(t, r["media"] / larg, yerr=r["desvio"] / larg, xerr=larg / 2, fmt="none", ecolor="lightgray",
                elinewidth=6, label="desvio padrao entre eventos")
    ax.errorbar(t, r["media"] / larg, yerr=r["erro_media"] / larg, fmt="ko", ms=5, capsize=3,
                label=f"media de {r['n_ev']} eventos (erro da media)")
    tt = np.linspace(0.01, 25, 500)
    for chave, estilo, rot in [("ajuste", "r-", "ajuste gama (A livre)"), ("ajuste_fixo", "b--", "ajuste gama (E0 = 10 GeV fixo)")]:
        A, a, b = r[chave]["popt"]
        dedt = dE_dt(tt, A, a, b)
        ax.plot(tt, dedt, estilo, lw=1.5,
                label=f"{rot}: a = {a:.2f}, b = {b:.3f}, $t_{{max}}$ = {r[chave]['tmax']:.2f} $X_0$")
    ax.axvline(r["tmax_est"], color="gray", ls=":", label=f"$\\ln(E_0/E_c) - 0.5$ = {r['tmax_est']:.2f} $X_0$")
    ax.axvline(r["t_bordas"][-1], color="purple", ls="-.", lw=1, label=f"fim do calorimetro ({r['t_bordas'][-1]:.1f} $X_0$)")
    ax.set_xlabel(r"Profundidade t [$X_{0,\mathrm{ef}}$]  ($X_{0,\mathrm{ef}}$ = %.2f mm, 1 camada = %.3f $X_0$)" % (r["x0ef"], larg))
    ax.set_ylabel(r"$\langle dE/dt \rangle$ [MeV / $X_0$]")
    ax.set_title("Perfil longitudinal do chuveiro EM: e$^-$ 10 GeV, Pb + LAr")
    ax.set_xlim(0, 25)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{saida}/perfil_longitudinal_Pb.png", dpi=130)
    plt.close()


def figura_comparacao(rpb, rag, saida):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    for r, cor in [(rpb, "C0"), (rag, "C1")]:
        rot = f"{r['nome']} ({r['t_camada']:.3f} $X_0$/camada)"
        ax[0].errorbar(r["t_centro"], r["media"] / r["t_camada"], yerr=r["erro_media"] / r["t_camada"],
                       fmt="o-", color=cor, capsize=3, label=rot)
        ax[1].errorbar(np.arange(N_CAMADAS), r["media"], yerr=r["erro_media"], fmt="o-", color=cor,
                       capsize=3, label=rot)
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xlabel(r"Profundidade t [$X_{0,\mathrm{ef}}$ de cada calorimetro]")
    ax[0].set_ylabel(r"$\langle dE/dt \rangle$ [MeV / $X_0$]")
    ax[0].set_title("Perfil em unidades de $X_0$")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("camada (0 = entrada; cada camada = 10 mm absorvedor + 5 mm LAr)")
    ax[1].set_ylabel(r"$\langle E \rangle$ por camada e por evento [MeV]")
    ax[1].set_title("Perfil por camada (mesma geometria)")
    for a in ax:
        a.legend(fontsize=9)
        a.grid(alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(f"{saida}/perfil_Pb_vs_agua.png", dpi=130)
    plt.close()


def main():
    p = argparse.ArgumentParser(description="Perfil longitudinal do chuveiro EM no B4a (Exercicio 2)")
    p.add_argument("--pb", required=True, help="padrao (glob) dos CSV CaloHits com absorvedor de chumbo")
    p.add_argument("--agua", help="padrao (glob) dos CSV CaloHits com absorvedor de agua")
    p.add_argument("--pb-eventos", help="padrao dos CSV da ntuple B4 (Eabs, Egap) com chumbo")
    p.add_argument("--agua-eventos", help="padrao dos CSV da ntuple B4 com agua")
    p.add_argument("--saida", default="figuras", help="diretorio das figuras")
    args = p.parse_args()

    rpb = analisar("Pb", args.pb, args.pb_eventos)
    figura_codigo_base(rpb, args.saida)
    figura_perfil(rpb, args.saida)
    if args.agua:
        rag = analisar("agua", args.agua, args.agua_eventos)
        figura_comparacao(rpb, rag, args.saida)
    print(f"\nfiguras em {args.saida}/")


if __name__ == "__main__":
    main()
