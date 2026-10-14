# estatistica_intro - Problemas 6 e 7 (Lista 2)

```
python3 distribuicoes.py
```

Gera `P6_gaussianas.pdf`, `P6_probabilidades.pdf`, `P7_tcl_histogramas.pdf` e `P7_assimetria_vs_N.pdf`.

## Problema 6 - Gaussiana

f(x; mu, sigma) = 1/(sigma sqrt(2 pi)) exp(-(x - mu)² / (2 sigma²))

Desenhei para (mu, sigma) = (0, 1), (2, 1) e (0, 2.5) (`P6_gaussianas.pdf`):

- **mu** só desloca a curva no eixo x, a forma continua igual. É onde fica o pico (média = moda = mediana).
- **sigma** muda a largura: sigma maior deixa a curva mais larga e mais baixa (o pico vale 1/(sigma sqrt(2 pi))),
  porque a área continua sendo 1 (conferi com `quad`, dá 1.000000 nos três casos).

Partícula X ~ Gauss(mu = 200 GeV, sigma = 2 GeV) (`P6_probabilidades.pdf`):

| | em sigmas | probabilidade |
|---|---|---|
| m >= 205 GeV | 2.5 sigma acima | **0.621 %** |
| uma com m > 203 GeV | 1.5 sigma acima | 6.681 % |
| duas independentes com m > 203 GeV | - | (0.06681)² = **0.446 %** |

Para as duas partículas multipliquei as probabilidades porque elas são produzidas de forma independente.

## Problema 7 - Teorema Central do Limite

Cada x_i é sorteado de uma exponencial E(x; lambda_i) = lambda_i e^(-lambda_i x), com os lambda_i diferentes entre si
(sorteei uniformemente entre 0.5 e 3). Fiz 100000 "experimentos" para cada N e olhei a distribuição de
x = (1/N) sum(x_i).

Para medir o quanto parece gaussiana usei a assimetria (skewness) e a curtose em excesso, que valem 0 para uma
gaussiana (com 100000 experimentos a incerteza na assimetria é ~0.008):

| N | assimetria | curtose em excesso |
|---|---|---|
| 1 | 1.97 | 5.66 |
| 3 | 1.26 | 2.46 |
| 10 | 0.82 | 1.14 |
| 30 | 0.55 | 0.53 |
| 100 | 0.28 | 0.16 |
| 200 | 0.20 | 0.04 |
| 500 | 0.11 | 0.02 |

**N = 3:** ainda não parece gaussiana. A distribuição sai de zero, sobe rápido e tem uma cauda longa para a direita,
igual à exponencial, só que menos extrema (`P7_tcl_histogramas.pdf`).

**Quando passa a parecer gaussiana:** a olho, a partir de **N ~ 30** a gaussiana de mesma média e desvio já fica
bem em cima do histograma, só sobra um pouco de assimetria no pico e na cauda da direita. Se o critério for mais
rigoroso (assimetria < 0.1), precisa de N ~ 500 ou mais (em N = 500 ainda deu 0.11). Então a resposta depende do quanto se exige: a forma
gaussiana "aparece" em N ~ 30, mas a cauda demora bem mais para convergir.

Isso é o que se espera: para exponenciais com o mesmo lambda a assimetria da média é 2/sqrt(N) (1.15 para N = 3,
0.37 para N = 30, 0.1 só em N = 400), ou seja ela cai devagar, como 1/sqrt(N). Com lambdas diferentes o TCL continua
valendo (os x_i são independentes e nenhum domina a variância da soma), só que os termos com lambda pequeno
pesam mais e por isso a convergência foi um pouco mais lenta que no caso de lambdas iguais.
