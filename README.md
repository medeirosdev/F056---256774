# F056 — Tópicos de Física Computacional VI

Exercícios resolvidos e materiais da disciplina **F056 (Unicamp)**, voltada às ferramentas
computacionais da física de altas energias: C++, ROOT, geradores de eventos, estatística,
Monte Carlo e simulação de detectores.

**Autor:** Guilherme de Medeiros

---

## Conteúdo

| | Tema | Ferramentas |
|---|---|---|
| [Exercício 01](ExerciciosResolvidos/Exercicio01) | Relatório em LaTeX sobre Git, Make e Sed | LaTeX, BibTeX, Make |
| [Exercício 02](ExerciciosResolvidos/Exercicio02) | Execução de jobs em lote e cálculo de luminosidade | C++, Bash, Python |
| [Exercício 03](ExerciciosResolvidos/Exercicio03) | Classes em C++: energia transversa faltante e traços | C++, Make |
| [Exercício 04](ExerciciosResolvidos/Exercicio04) | Geração de dados em TTree, histograma e ajuste | ROOT (macros) |
| [Exercício 05](ExerciciosResolvidos/Exercicio05) | Interface entre C++, ROOT e Python | C++, PyROOT |
| [Exercício 06](ExerciciosResolvidos/Exercicio06) | Higgs → b b̄ e backgrounds no PYTHIA8 | Pythia 8, ROOT |
| [Exercício 07](ExerciciosResolvidos/Exercicio07) | Seção de choque pp → t t̄: Pythia8 × MadGraph | Pythia 8, MadGraph5_aMC@NLO |
| [Exercício 08](ExerciciosResolvidos/Exercicio08) | Estimação de parâmetros e distribuições de probabilidade | Python, SciPy |
| [Exercício 09](ExerciciosResolvidos/Exercicio09/lista_montecarlo_ajuste) | Monte Carlo (aceitação–rejeição) e ajuste com Minuit | Python, iminuit |
| [Exercício 10](ExerciciosResolvidos/Exercicio10/lista_geant4) | Simulação de calorímetro com o exemplo B4a | Geant4, ROOT |
| [Seminário](Seminario) | Teste de hipótese: busca da partícula CSC | Python, iminuit |

Cada pasta tem um `README.md` com o enunciado resumido, como compilar ou rodar e os resultados.

---

## Seminário

**Caçando a partícula CSC** — apresentação do Exercício 4 (*Advanced hypothesis testing*) da série
de *Data Analysis* da CERN School of Computing 2024. Busca de uma ressonância em 100 000 eventos
e⁺e⁻: Monte Carlo, pseudo-experimentos, p-valor e significância, varredura em massa e intervalo de
confiança por máxima verossimilhança.

- [Apresentação (PDF)](Seminario/seminario.pdf)
- [Scripts dos testes e figuras](Seminario/Scripts)

---

## Ambiente

Os exercícios foram feitos em Linux, com ambientes conda:

| Ambiente | Conteúdo |
|---|---|
| `rootenv` | ROOT 6.40, Pythia 8.312, Python com NumPy, SciPy, Matplotlib e iminuit |
| `g4env` | Geant4 11.4.3 |

O MadGraph5_aMC@NLO 3.6.7 foi usado à parte, sem LHAPDF.

```bash
conda activate rootenv
cd ExerciciosResolvidos/Exercicio05
make
```

---

## Estrutura

```
.
├── ExerciciosResolvidos/   exercícios 01 a 10
├── Exemplos/               exemplos das aulas (optparse, json, re, make, sed, lambda, ...)
└── Seminario/              apresentação e scripts do seminário
```

---

## Próximos passos

- [ ] Criar um ambiente virtual único para todo o repositório
- [ ] Reunir em uma biblioteca Python as funções úteis para as próximas aulas
