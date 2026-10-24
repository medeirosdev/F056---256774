# Roda o ajuste_higgs_v2.py ORIGINAL (sem mexer nele) e salva a figura em figuras/ajuste_original.png
# O original usa plt.show(); aqui troco o show por um savefig.
# uso: python3 roda_original.py caminho/para/ajuste_higgs_v2.py [pythia_higgs.root] | tee saida_original.txt

import runpy
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    sys.exit("uso: python3 roda_original.py caminho/para/ajuste_higgs_v2.py [pythia_higgs.root]")

programa = sys.argv[1]
plt.show = lambda: plt.savefig("figuras/ajuste_original.png", dpi=120)
sys.argv = [programa] + sys.argv[2:]
runpy.run_path(programa, run_name="__main__")
