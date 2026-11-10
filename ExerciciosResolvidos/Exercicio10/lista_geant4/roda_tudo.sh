#!/bin/bash
# Compila o B4a modificado e roda todas as simulacoes e analises da lista.
# uso (com o ambiente do Geant4 carregado, ex.: conda activate g4env):
#   bash roda_tudo.sh            # tudo
#   bash roda_tudo.sh figuras    # so as figuras do Exercicio 1
#   bash roda_tudo.sh estat      # so a estatistica e-/p/alfa do Exercicio 1
#   bash roda_tudo.sh perfil     # so as simulacoes do Exercicio 2
#   bash roda_tudo.sh analise    # so a analise (python) do Exercicio 2
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
ETAPA="${1:-tudo}"
EXE="$AQUI/build/exampleB4a"
N_EST=500        # eventos por configuracao na estatistica do Exercicio 1

# ---- compilacao ----
if [ ! -x "$EXE" ] || [ "$ETAPA" = "tudo" ]; then
    mkdir -p "$AQUI/build"
    (cd "$AQUI/build" && cmake "$AQUI/B4a" -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" > cmake.log && make -j4)
fi

# roda uma macro num diretorio de saida (as macros sao copiadas para la, porque o
# caminho do repositorio tem espaco e o /control/execute nao aceita)
rodar() {   # rodar <diretorio> <macro> [linhas de alias...]
    local nome="$1"; local dir="$AQUI/saidas/$1"; local macro="$2"; shift 2
    mkdir -p "$dir"; cp "$AQUI"/macros/*.mac "$dir"/
    if [ $# -gt 0 ]; then printf '%s\n' "$@" > "$dir/$macro"; fi
    (cd "$dir" && "$EXE" -m "$macro" > "${macro%.mac}.log" 2>&1)
    echo "  ok: saidas/$nome/${macro%.mac}.log"
}

if [ "$ETAPA" = "tudo" ] || [ "$ETAPA" = "figuras" ]; then
    echo "== Exercicio 1(b)(c): figuras"
    mkdir -p "$AQUI/figuras"
    for m in eletron proton alfa; do
        for mat in Pb agua; do
            rodar ex1_figuras ${m}_10GeV_${mat}.mac
            cp "$AQUI/saidas/ex1_figuras/${m}_10GeV_${mat}.png" "$AQUI/figuras/"
        done
    done
    # figuras extras: 20 eventos sobrepostos para os hadrons (1 evento so nao e representativo)
    for m in proton alfa; do
        for mat in Pb agua; do
            rodar ex1_figuras ${m}_10GeV_${mat}_20eventos.mac
            cp "$AQUI/saidas/ex1_figuras/${m}_10GeV_${mat}_20eventos.png" "$AQUI/figuras/"
        done
    done
fi

if [ "$ETAPA" = "tudo" ] || [ "$ETAPA" = "estat" ]; then
    echo "== Exercicio 1: estatistica de deposicao ($N_EST eventos cada)"
    for mat in G4_Pb G4_WATER; do
        for p in e- proton alpha; do
            rodar "ex1_estat/${mat}_${p}" est.mac "/control/alias material $mat" \
                "/control/alias particula $p" "/control/alias neventos $N_EST" "/control/execute estatistica.mac"
        done
    done
    python3 "$AQUI/estatistica_ex1.py" "$AQUI/saidas/ex1_estat" -o "$AQUI/figuras"
fi

if [ "$ETAPA" = "tudo" ] || [ "$ETAPA" = "perfil" ]; then
    echo "== Exercicio 2: 1000 eletrons de 10 GeV (chumbo e agua)"
    rodar ex2_Pb perfil_Pb.mac
    rodar ex2_agua perfil_agua.mac
fi

if [ "$ETAPA" = "tudo" ] || [ "$ETAPA" = "analise" ]; then
    echo "== Exercicio 2: analise"
    python3 "$AQUI/perfil_longitudinal.py" \
        --pb "$AQUI/saidas/ex2_Pb/calo_output_nt_CaloHits_t*.csv" \
        --agua "$AQUI/saidas/ex2_agua/calo_output_nt_CaloHits_t*.csv" \
        --pb-eventos "$AQUI/saidas/ex2_Pb/calo_output_nt_B4_t*.csv" \
        --agua-eventos "$AQUI/saidas/ex2_agua/calo_output_nt_B4_t*.csv" \
        --saida "$AQUI/figuras" | tee "$AQUI/resultados_ex2.txt"
fi
