# F056 - Lista 2: Estimação de Parâmetros

Dados: `decay.txt`, N = 10000 medidas do tempo de decaimento (em s, arredondadas em 0.01 s).
Média = 1.2532 s, mínimo 0.00 s, máximo 12.53 s.

- Problemas 1 a 5: `estimacao.py` (nessa pasta)
- Problemas 6 e 7: `estatistica_intro/distribuicoes.py` (respostas no `estatistica_intro/README.md`)

## Como rodar

```
python3 estimacao.py
cd estatistica_intro && python3 distribuicoes.py
```

Só precisa de numpy, scipy e matplotlib. Os gráficos saem em .pdf na própria pasta.

## Problema 1 - histograma (`P1_histograma.pdf`)

Desenhei o histograma com 3 escolhas de bin, com barra de erro sqrt(n) e eixo y em log:

| escolha | nº de bins | largura |
|---|---|---|
| poucos bins | 10 | 1.25 s |
| Freedman-Diaconis (2·IQR/N^(1/3)) | 99 | 0.127 s |
| raiz(N) | 100 | 0.125 s |

Com 10 bins quase toda a informação cai nos 2-3 primeiros bins e não dá pra ver a forma direito. Com bins muito
finos cada bin fica com poucos eventos e a flutuação de Poisson domina, e também não faz sentido usar bin menor
que 0.01 s porque os dados estão arredondados nisso (ia aparecer bin vazio entre valores). Fiquei com ~100 bins
(Freedman-Diaconis e raiz(N) dão praticamente o mesmo): os bins do começo têm centenas de eventos, então
sigma = sqrt(n) é uma boa aproximação gaussiana, e só a cauda (t > 8 s) fica com poucos eventos por bin.

PDF teórica: **exponencial**, f(t; tau) = (1/tau) e^(-t/tau). O decaimento tem probabilidade constante por unidade
de tempo e não tem memória (a chance de decair agora não depende de quanto tempo já passou), e isso leva
direto na exponencial. No gráfico com y em log os pontos ficam numa reta, que é o que se espera de uma exponencial.

## Problema 2 - PDF para vários tau (`P2_pdf_tau.pdf`)

Desenhei para tau = 0.5, 1, 1.5, 2 e 3 s. Quanto maior o tau, mais devagar a curva cai e mais "achatada" ela
fica: o valor em t = 0 é 1/tau (menor pra tau grande) e a média da distribuição é o próprio tau. A área é sempre 1.

Probabilidade de medir t <= 1 s com tau = 1.5 s (escolhi esse porque é perto da média dos dados):

P(t <= 1 s) = 1 - e^(-1/1.5) = **0.4866** (deu o mesmo integrando numericamente com `scipy.integrate.quad`).

## Problema 3 - verossimilhança (`P3_L_uma_medida.pdf`)

Para N medidas independentes:

L(tau) = prod (1/tau) e^(-t_i/tau) = tau^(-N) exp(-sum(t_i)/tau)

Dá pra achar o máximo analiticamente (derivando o log, ver Problema 4), mas calcular L direto pelo produto não
funciona: cada fator é da ordem de 0.3, e o produto de 10000 deles é ~10^-5000, bem abaixo do menor double
(~10^-308). No código `L(1.25)` com todos os dados dá **0.0** (underflow). Por isso na prática se usa ln L.

Para uma medida só, t = 1 s: L(tau) = (1/tau) e^(-1/tau). O máximo está em **tau = 1 s** (dL/dtau = 0 dá tau = t),
no gráfico deu 1.004 por causa do passo da grade. Faz sentido, para N = 1 o estimador é a própria medida.

## Problema 4 - -2 ln L (`P4_m2lnL.pdf`)

-2 ln L(tau) = 2N ln(tau) + 2 sum(t_i)/tau

Derivando e igualando a zero: tau_hat = sum(t_i)/N, ou seja a média dos tempos. A incerteza sai da segunda
derivada (ou do ponto onde -2 ln L sobe 1): 1/sigma² = N/tau², sigma = tau_hat/sqrt(N).

**tau = 1.253 ± 0.013 s** (1.2532 ± 0.0125 s)

É um ajuste **não binado** (unbinned), porque usa cada t_i individualmente pela soma, sem passar pelo histograma.

## Problema 5 - ajuste numérico (`P5_ajuste_numerico.pdf`, `P5_ajuste_histograma.pdf`)

Minimizei -2 ln L com `scipy.optimize.minimize_scalar` e achei os pontos em que a curva sobe 1 em relação ao
mínimo com `brentq`:

**tau = 1.2532 (-0.0124 / +0.0126) s**

Bate com o analítico. A incerteza sai levemente assimétrica porque -2 ln L não é exatamente uma parábola em tau
(cresce mais devagar pro lado de tau grande), mas com N = 10000 a diferença é pequena. A vantagem do jeito
numérico é que funciona igual quando não tem solução fechada.

Só pra comparar fiz também um ajuste binado (Poisson em 100 bins): tau = 1.2545 s, praticamente igual ao não
binado. No `P5_ajuste_histograma.pdf` a exponencial com o tau ajustado está por cima do histograma.
