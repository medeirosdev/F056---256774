#!/usr/bin/env python3
# F056 - Lista Geant4, Exercicio 1: comparacao quantitativa entre e-, proton e alfa de 10 GeV
# nos dois absorvedores (Pb e agua), a partir da ntuple B4 (Eabs, Egap, Labs, Lgap por evento).
#
# uso: python3 estatistica_ex1.py saidas/ex1_estat -o figuras

import argparse
import glob
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E0 = 10000.0   # MeV
PARTICULAS = [("e-", "eletron"), ("proton", "proton"), ("alpha", "alfa")]
MATERIAIS = [("G4_Pb", "Pb"), ("G4_WATER", "agua")]


def ler_b4(diretorio):
    arquivos = sorted(glob.glob(os.path.join(diretorio, "calo_output_nt_B4_t*.csv")))
    if not arquivos:
        raise SystemExit(f"nenhum calo_output_nt_B4_t*.csv em {diretorio}")
    return pd.concat([pd.read_csv(f, comment="#", header=None, names=["Eabs", "Egap", "Labs", "Lgap"])
                      for f in arquivos], ignore_index=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diretorio", help="diretorio com as subpastas <material>_<particula>")
    parser.add_argument("-o", "--saida", default="figuras", help="diretorio das figuras")
    args = parser.parse_args()
    os.makedirs(args.saida, exist_ok=True)

    print(f"{'material':>8s} {'particula':>9s} {'N':>4s} {'<Eabs> MeV':>11s} {'<Egap> MeV':>11s} "
          f"{'<Etot>/E0':>10s} {'rms/E0':>7s} {'Egap/Etot':>9s} {'frac. MIP':>9s} {'Emip MeV':>8s} {'<Lgap> mm':>9s}")

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    for a, (mat, nome_mat) in zip(ax, MATERIAIS):
        for part, nome in PARTICULAS:
            d = ler_b4(os.path.join(args.diretorio, f"{mat}_{part}"))
            etot = d["Eabs"] + d["Egap"]
            # "MIP": a particula atravessou o calorimetro sem interacao nuclear, so ionizando.
            # Esses eventos formam o pico estreito de energia mais baixa; acho a posicao dele
            # (moda num histograma em escala log) e conto os eventos com Etot < 1.5 x moda.
            # Para o eletron (sempre chuveiro EM) nao se aplica.
            if part == "e-":
                frac_mip = np.nan
            else:
                cont, bordas = np.histogram(np.log10(etot), bins=80)
                moda = 10 ** (0.5 * (bordas[np.argmax(cont)] + bordas[np.argmax(cont) + 1]))
                frac_mip = np.mean(etot < 1.5 * moda)
            print(f"{nome_mat:>8s} {nome:>9s} {len(d):4d} {d['Eabs'].mean():11.1f} {d['Egap'].mean():11.1f} "
                  f"{etot.mean() / E0:10.4f} {etot.std() / E0:7.4f} {(d['Egap'] / etot).mean():9.4f} "
                  f"{frac_mip:9.2f} {(moda if part != 'e-' else np.nan):8.1f} {d['Lgap'].mean():9.1f}")
            a.hist(etot / 1000.0, bins=np.logspace(-2, np.log10(12), 60), histtype="step", lw=1.8,
                   label=f"{nome} (<E> = {etot.mean() / 1000:.2f} GeV)")
        a.set_xscale("log")
        a.set_yscale("log")
        a.set_xlabel("energia depositada no calorimetro (absorvedor + LAr) [GeV]")
        a.set_ylabel("eventos")
        a.set_title(f"10 GeV, absorvedor {nome_mat} (500 eventos cada)")
        a.legend(fontsize=9)
        a.grid(alpha=0.3)
    plt.tight_layout()
    saida = os.path.join(args.saida, "ex1_energia_depositada.png")
    plt.savefig(saida, dpi=130)
    print(f"figura: {saida}")


if __name__ == "__main__":
    main()
