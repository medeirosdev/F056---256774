# Seminário — Caçando a partícula CSC

Apresentação do **Exercício 4** (*Advanced hypothesis testing*) da série de *Data Analysis* da
CERN School of Computing 2024 (Toni Šćulac), Problemas 1 a 5.

- `seminario.pdf` — a apresentação
- `Scripts/` — código usado para todos os números e gráficos dos slides

## Scripts

| Arquivo | O que é |
|---|---|
| `figuras.py` | faz todas as contas e gera as figuras dos slides |
| `LHC_data_2023.txt` | os dados do exercício: 100 000 valores de $m_{e^+e^-}$ (GeV) |
| `figuras/` | saída do script: as figuras (`fig_*.pdf`) e `numeros.txt` |

Para rodar:

```bash
cd Scripts
python3 figuras.py
```

Bibliotecas: `numpy`, `scipy`, `matplotlib` e `iminuit`.

## O que o script faz

1. **Problema 1** — Monte Carlo: 99% de fundo plano + 1% de gaussiana ($\sigma = 0{,}2$ GeV) em 30 GeV.
2. **Problema 2** — 10 000 *toys* só com fundo para obter $g(t\,|\,H_0)$, com
   $t = \sum_i (n_i - \nu)^2/\nu$; comparação com a $\chi^2$ de 99 graus de liberdade e
   significância esperada (mediana de 200 MC com sinal).
3. **Problema 3** — $t$ nos dados, p-valor pela $\chi^2_{99}$ e $Z = \sqrt{2}\,\mathrm{erfc}^{-1}(2p)$.
4. **Problema 4** — varredura em massa (passo de 0,05 GeV): ajuste binado de Poisson (Minuit) de
   fundo + gaussiana de 0,2 GeV e p-valor local pelo teorema de Wilks.
5. **Problema 5** — ajuste livre × previsão da CSC (1% e $\sigma = 0{,}2$ GeV fixos) e intervalo de
   confiança da massa pela varredura de $-2\Delta\ln L$.

## Resultados

| Pergunta | Resultado |
|---|---|
| significância esperada | $11{,}5\sigma$ |
| significância observada | $t = 362$, $p = 1{,}4\times10^{-31}$, $Z = 11{,}6\sigma$ |
| posição do excesso | $m = 35{,}00$ GeV ($\approx 14\sigma$ local) |
| é a CSC? | $-2\Delta\ln L = 4{,}1$ (2 g.l.), $p = 0{,}13$: compatível |
| massa | $35{,}007 \pm 0{,}025$ GeV (68%) |
