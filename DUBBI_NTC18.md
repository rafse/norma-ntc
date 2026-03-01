# Dubbi e discrepanze NTC18

Registro dei casi in cui i dati OCR o l'interpretazione della norma presentano ambiguita'.
Ogni voce va verificata sul testo ufficiale NTC18.

## §3.4.2 — Neve, esponente formula altitudine zone IA/IM/II/III

- **Formula implementata**: q_sk = coeff * [1 + (a_s / divisore)^**2**]
- **Dato OCR** (`cap3_page_*.json`): l'esponente risultava **^3** nell'OCR
- **Interpretazione**: usato esponente **2** per tutte le zone, coerente con la formulazione NTC18 nota e con i valori attesi di q_sk
- **Motivazione**: un esponente 3 produce valori di q_sk irrealisticamente alti ad alta quota
- **Stato**: APERTO — da verificare su testo ufficiale

## §3.3.7 — Vento, formula coefficiente di esposizione OCR garbled

- **Formula implementata**: c_e(z) = k_r^2 * c_t * ln(z/z_0) * [7 + c_t * ln(z/z_0)]
- **Dato OCR**: la formula conteneva `\begin{pmatrix}` e nomi di variabili inconsistenti nei subscript
- **Interpretazione**: ricostruita la formula [3.3.7] dalla struttura nota NTC18 e dai parametri Tab. 3.3.II
- **Stato**: APERTO — da verificare su testo ufficiale

## §3.5.2 — Zona III, coefficiente T_max

- **Formula**: T_max = 42 - 0.3 * a_s / 1000  [3.5.6]
- **Dato OCR**: `cap3_page_19.json` riporta coefficiente **0.3**
- **Dubbio iniziale**: il valore 0.3 sembrava anomalo rispetto alle altre zone (I: 6, II: 2, IV: 2). Possibile errore OCR (3 letto come 0.3)?
- **Risolto**: confermato dall'utente che il valore corretto e' **0.3**
- **Stato**: CHIUSO

## §3.6.1.5.1 — Curva idrocarburi [3.6.3], esponenti OCR garbled

- **Formula attesa**: θ_g = 1080·(1 - 0.325·e^(-0.167·t) - 0.675·e^(-2.5·t)) + 20
- **Dato OCR** (`cap3_page_23.json`): `e^{-0,1671}` e `e^{-2,51}` — manca la variabile `t` negli esponenti
- **Interpretazione**: gli esponenti sono -0.167·t e -2.5·t (formula nota Eurocode EN 1991-1-2)
- **Stato**: APERTO — da verificare su testo ufficiale

## §3.6.1.5.1 — Curva esterna [3.6.4], esponenti OCR garbled

- **Formula attesa**: θ_g = 660·(1 - 0.687·e^(-0.32·t) - 0.313·e^(-3.8·t)) + 20
- **Dato OCR** (`cap3_page_23.json`): `e^{-0,321}` e `e^{-3,81}` — manca la variabile `t`
- **Interpretazione**: gli esponenti sono -0.32·t e -3.8·t (formula nota Eurocode EN 1991-1-2)
- **Stato**: APERTO — da verificare su testo ufficiale

## §2.5.3 — Tab. 2.5.1, valori ψ per Vento/Neve/Temperatura OCR sospetti

- **Valori implementati** (da Eurocode EN 1990 / NTC18 noti):
  - Vento: ψ_0=0.6, ψ_1=0.2, ψ_2=0.0
  - Neve ≤1000m: ψ_0=0.5, ψ_1=0.2, ψ_2=0.0
  - Neve >1000m: ψ_0=0.7, ψ_1=0.5, ψ_2=0.2
  - Variazioni termiche: ψ_0=0.6, ψ_1=0.5, ψ_2=0.0
- **Dato OCR** (`cap2_page_6.json`):
  - Vento: 0.5, 0.2, 0.0 (ψ_0 diverso)
  - Neve ≤1000m: 0.7, 0.5, 0.2 (sembra Neve >1000m)
  - Neve >1000m: 0.6, 0.5, 0.0 (sembra Temperatura)
  - Variazioni termiche: vuoto
- **Interpretazione**: sospetto shift di riga nella tabella OCR a partire dalla riga Vento. Le intestazioni OCR sono garbled (Ψ_Q, Ψ_bi, Ψ_bi invece di ψ_0, ψ_1, ψ_2). Usati i valori standard EN 1990 / NTC18 consolidati
- **Stato**: APERTO — da verificare su testo ufficiale

## §2.6.1 — Tab. 2.6.1, G2 favorevoli = 0.8

- **Valori implementati**: G2 favorevoli = 0.8 per tutti gli approcci (EQU, A1, A2)
- **Dato OCR** (`cap2_page_7.json`): la tabella riporta G2 favorevoli = 0.8
- **Dubbio**: in Eurocode EN 1990, G2 favorevoli e' tipicamente 0.0 quando non ben definiti. Il valore 0.8 dell'OCR potrebbe essere corretto per NTC18 o un errore OCR
- **Interpretazione**: usato 0.8 come da OCR, compatibile con una riduzione intermedia per carichi non strutturali
- **Stato**: APERTO — da verificare su testo ufficiale

## §2.5.3 — Formule [2.5.1]-[2.5.6], subscript OCR garbled

- **Formule implementate**: ricostruite dalla struttura nota NTC18/Eurocode
- **Dato OCR** (`cap2_page_6.json`): subscript inconsistenti nelle formule (es. `γ_{G1} · γ_{G2}` invece di `γ_{G1} · G_1 + γ_{G2} · G_2`, `Q_{A1}` invece di `Q_{k1}`)
- **Interpretazione**: usate le formule standard NTC18 §2.5.3
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.1.2.1.1.2 — Formula [4.1.4], subscript OCR garbled

- **Formula implementata**: f_ctd = f_ctk / gamma_c
- **Dato OCR** (`cap4_page_3.json`): `f_{td} = f_{tub} / gamma_c` e testo cita `f_{ck}` per la trazione
- **Interpretazione**: `f_tub` e' garbled da `f_ctk`, `f_td` da `f_ctd`. Usata la nomenclatura EC2/NTC18 standard
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.1.2.1.1.3 — Formula [4.1.5], subscript OCR garbled

- **Formula implementata**: f_yd = f_yk / gamma_s
- **Dato OCR** (`cap4_page_3.json`): `f_{cd} = f_{cy} / gamma_s` — l'OCR ha letto f_cd (calcestruzzo) invece di f_yd (acciaio), e f_cy invece di f_yk
- **Interpretazione**: la formula e' chiaramente per l'acciaio (gamma_s = 1.15). Usata nomenclatura corretta f_yd = f_yk / gamma_s
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.1.2.1.1.4 — Formula [4.1.7], f_ctk letto come f_ck

- **Formula implementata**: f_bk = 2.25 * eta_1 * eta_2 * f_ctk
- **Dato OCR** (`cap4_page_4.json`): `f_{hk} = 2.25 * eta_1 * eta_2 * f_{ck}` — subscript 'b' letto come 'h', e f_ctk letto come f_ck
- **Interpretazione**: la formula di aderenza usa la resistenza a trazione f_ctk, non la compressione f_ck (coerente con EC2 §8.4.2)
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.1.2.1.2.1 — Deformazioni limite, nomenclatura OCR inconsistente

- **Valori implementati**: eps_c2, eps_cu2, eps_c3, eps_cu3 (nomenclatura EC2 Table 3.1)
- **Dato OCR** (`cap4_page_4.json`): usa nomi eps_c2, eps_cu, eps_c3, eps_c4 per <= C50/60 e eps_c5, eps_cu, eps_c6, eps_c4 per > C50/60
- **Dubbio**: eps_c4 = 0.07% (0.7 per mille) non corrisponde a nessun valore standard EC2/NTC18. Esponente `^t` per eps_cu con > C50/60 dovrebbe essere `^4`
- **Interpretazione**: usati i valori e le formule standard EC2 Table 3.1, che NTC18 richiama
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.1.2.3.5.1 — Formula [4.1.23], subscript OCR garbled

- **Formula implementata**: V_Rd = max{[0.18/gamma_c * k * (100*rho_l*f_ck)^(1/3) + 0.15*sigma_cp] * bw * d, (v_min + 0.15*sigma_cp) * bw * d}
- **Dato OCR** (`cap4_page_10.json`): `rho_c` invece di `rho_l`, `f_{cd}` in piu' punti dove dovrebbe essere `f_{ck}`
- **Interpretazione**: la formula usa f_ck (caratteristica), non f_cd (progetto). Garbling dei subscript c/l e cd/ck
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.1.2.3.6 — Formule [4.1.35]-[4.1.37], labels e variabili OCR garbled

- **Formule implementate**: T_Rcd (calcestruzzo), T_Rsd (staffe), T_Rld (longitudinale) con formule standard EC2/NTC18
- **Dato OCR** (`cap4_page_12.json`): tutte e tre le formule hanno label `T_Rsd` nell'OCR. Formula [4.1.35] (calcestruzzo) mostra `A_s/s * f_yd` che sono parametri dell'acciaio, non del calcestruzzo
- **Interpretazione**: [4.1.35] e' la formula del calcestruzzo T_Rcd = 2*A*t*alpha_c*nu*f_cd*ctg(theta)/(1+ctg^2(theta)), ricostruita da EC2 §6.3.2
- **Stato**: APERTO — da verificare su testo ufficiale

## §5.1.3.5 — Formula [5.1.4], subscript OCR confusi Q/q

- **Formula implementata**: q_3 = 0.6*(2*Q_1k) + 0.10*q_1k*w_1*L, clampata [180, 900] kN
- **Dato OCR** (`cap5_page_5.json`): `q_{1k}` usato sia per il carico tandem sia per il carico distribuito (maiuscola/minuscola confuse)
- **Interpretazione**: il primo termine usa Q_1k (carico asse tandem, maiuscolo), il secondo q_1k (distribuito, minuscolo), coerente con Tab. 5.1.II
- **Stato**: APERTO — da verificare su testo ufficiale

## §5.2.2.3.3 — Frenatura ferroviaria, unita' OCR garbled

- **Formula implementata**: Q_hk = 20 kN/m * L per LM71/SW0, Q_hk = 35 kN/m * L per SW/2
- **Dato OCR** (`cap5_page_22.json`): riporta `kJ/N/m` come unita' invece di `kN/m`
- **Interpretazione**: evidente garbling OCR di kN/m → kJ/N/m. Usate le unita' corrette kN/m
- **Stato**: APERTO — da verificare su testo ufficiale

## §5.2.2.3.1 / §5.2.2.8 — Formula [5.2.10] duplicata

- **Formula implementata**: [5.2.10] = fattore riduzione centrifuga f (§5.2.2.3.1, page 21)
- **Dato OCR**: il numero [5.2.10] appare anche a page 25 per la formula a'_g = 0.6*min(a_g) + 0.4*max(a_g) (combinazione sismica)
- **Interpretazione**: probabile errore di numerazione nell'originale o nell'OCR. La seconda formula e' relativa alla combinazione sismica (§5.2.2.8) e non alla centrifuga
- **Stato**: APERTO — da verificare numerazione su testo ufficiale

## §7.3.1 — Tab. 7.3.II, subscript OCR garbled alpha_1/alpha_1

- **Valori implementati**: q_0 con moltiplicatore alpha_u/alpha_1 (rapporto sovraresistenza)
- **Dato OCR** (`cap7_page_9.json`): la tabella riporta `α_1/α_1` invece di `α_u/α_1` in tutte le voci. Il subscript "u" e' letto come "1"
- **Interpretazione**: usato alpha_u/alpha_1 come da NTC18 §7.3.1 e §7.4.3.2. Il rapporto alpha_1/alpha_1 = 1 non avrebbe senso
- **Stato**: APERTO — da verificare su testo ufficiale

## §7.3.3.1 — Formula [7.3.5a], coefficiente di correlazione CQC garbled

- **Formula implementata**: rho_ij = 8*xi^2*(1+beta)*beta^(3/2) / [(1-beta^2)^2 + 4*xi^2*beta*(1+beta)^2] (formula standard Der Kiureghian)
- **Dato OCR** (`cap7_page_12.json`): numeratore con beta^(1/2) invece di beta^(3/2), denominatore con (1-beta^2)^(1/2) invece di (1-beta^2)^2, e struttura complessiva garbled
- **Interpretazione**: usata la formula CQC standard che, per smorzamento uguale [7.3.5b], e' ampiamente nota e verificata
- **Stato**: APERTO — da verificare su testo ufficiale

## §7.3.3.2 — Formula [7.3.7], subscript OCR garbled

- **Formula implementata**: `F_i = F_h * z_i * W_i / sum(z_j * W_j)` con `F_h = S_d(T_1) * W * lambda / g`
- **Dato OCR** (`cap7_page_12.json`): formula mostra `z_i * (W_i / sum(gamma_i / W_i))` — il denominatore ha gamma_i invece di z_j e divisione invece di moltiplicazione
- **Interpretazione**: usata la formula standard NTC18 §7.3.3.2 con distribuzione proporzionale a z_i * W_i
- **Stato**: APERTO — da verificare su testo ufficiale

## §7.4.4.2.1 — Formula [7.4.4], M_h,Rd letto come M_b,Rd

- **Formula implementata**: sum(M_c,Rd) >= gamma_Rd * sum(M_b,Rd)
- **Dato OCR** (`cap7_page_19.json`): formula con `M_{h,Rd}` per le travi, testo seguente conferma "capacita' a flessione della trave convergente nel nodo"
- **Interpretazione**: `M_h,Rd` e' la notazione NTC18 per la capacita' delle travi (h = "horizontal"?). Implementata come M_b (beam) per chiarezza. Il significato e' identico
- **Stato**: CHIUSO — notazione diversa ma significato confermato dal testo

## §4.2.4.1.2.1 — Formula [4.2.7], f_tk letto come f_yk

- **Formula implementata**: N_u,Rd = 0.9 * A_net * f_tk / gamma_M2
- **Dato OCR** (`cap4_page_28.json`): la formula riporta `f_yk` invece di `f_tk` (tensione di rottura)
- **Interpretazione**: la rottura della sezione netta utilizza f_tk (rottura), non f_yk (snervamento), coerente con EC3 §6.2.3
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.2.4.1.2.6 — Formula [4.2.31], OCR garbled

- **Formula implementata**: rho = (2*V_Ed/V_c,Rd - 1)^2
- **Dato OCR** (`cap4_page_30.json`): formula garbled con struttura non riconoscibile
- **Interpretazione**: usata la formula standard EC3/NTC18 per la riduzione della resistenza flessionale in presenza di taglio elevato
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.2.4.1.2.7 — Formula [4.2.33], OCR garbled

- **Formula implementata**: M_N,y,Rd = M_pl,y,Rd * (1-n) / (1-0.5*a), limitata a M_pl,y,Rd
- **Dato OCR** (`cap4_page_31.json`): formula garbled
- **Interpretazione**: usata la formula standard EC3 §6.2.9.1(5) per profili I/H, asse forte
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.2.4.1.3.2 — Formula [4.2.49], gamma_M1 letto come f_M1

- **Formula implementata**: M_b,Rd = chi_LT * W_y * f_yk / gamma_M1
- **Dato OCR** (`cap4_page_34.json`): `f_M1` invece di `gamma_M1`
- **Interpretazione**: il coefficiente parziale e' gamma_M1 (standard EC3/NTC18)
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.2.8.1.1 — Formula [4.2.71], interazione bullone OCR garbled

- **Formula implementata**: F_v,Ed/F_v,Rd + F_t,Ed/F_t,Rd <= 1.0 (interazione lineare NTC18)
- **Dato OCR** (`cap4_page_42.json`): formula con struttura garbled
- **Interpretazione**: NTC18 usa l'interazione lineare (non il fattore 1.4 di EC3). Coerente con §4.2.8.1.1
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.2 — Tab.4.2.VII, subscript gamma_M tutti letti come M1

- **Valori implementati**: gamma_M0=1.05, gamma_M1=1.05, gamma_M2=1.25
- **Dato OCR** (`cap4_page_28.json`): tutti i subscript nella tabella risultano "M1"
- **Interpretazione**: la distinzione M0/M1/M2 e' fondamentale e universalmente nota. Usati valori standard NTC18 Tab.4.2.VII
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.5.6.1 — Tab.4.5.II, numerazione tabella garbled

- **Tabella implementata**: Tab.4.5.II (gamma_M per muratura)
- **Dato OCR** (`cap4_page_75.json`): la tabella e' etichettata "Tab. 4.5.11" (numero arabo) invece di "Tab. 4.5.II" (numero romano)
- **Interpretazione**: l'OCR legge i numeri romani (II, III, IV) come numeri arabi (11, III, IV). Usata la numerazione standard NTC18 con numeri romani
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.5.6.1 — Formula [4.5.3], subscript f_vk letto come f_k

- **Formula implementata**: f_vd = f_vk / gamma_M (resistenza a taglio)
- **Dato OCR** (`cap4_page_75.json`): la formula [4.5.3] mostra `f_k / gamma_M` identica a [4.5.2], senza distinguere il subscript 'v'
- **Interpretazione**: [4.5.3] usa f_vk (resistenza caratteristica a taglio), non f_k (compressione). L'OCR ha perso il subscript 'v'
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.5.6.2 — Eccentricita' di tolleranza e_a, formula garbled

- **Dato OCR** (`cap4_page_76.json`): riporta "eccentricità $e_s$ che è assunta almeno uguale a $h$" dove h e' l'altezza di piano
- **Dubbio**: il valore e_a = h sarebbe enormemente grande. La formula standard NTC18 e' e_a = h/200 (o h/300). L'OCR sembra aver perso il denominatore "/200"
- **Interpretazione**: non implementata la formula per e_a — l'utente dovra' calcolare l'eccentricita' di tolleranza separatamente
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.5.6.4 — Verifica semplificata, gamma_M = 4.2 sospetto

- **Formula implementata**: sigma = N/(0.65*A) <= f_k/gamma_M, con gamma_M parametrico
- **Dato OCR** (`cap4_page_77.json`): riporta "ponendo il coefficiente gamma_M = 4.2"
- **Dubbio**: gamma_M = 4.2 sembra anomalmente alto per muratura (valori tipici: 2.0-3.0 da Tab.4.5.II). Potrebbe essere un errore OCR o un riferimento alla sezione "§4.2" interpretato come numero
- **Interpretazione**: implementato con gamma_M come parametro libero, l'utente deve fornire il valore appropriato
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.4.3.1.2 — Formula [4.3.9], f_k letto invece di f_u (piolo connettore)

- **Formula implementata**: P_steel = 0.8 * f_u * (pi*d^2/4) / gamma_V
- **Dato OCR** (`cap4_page_52.json`): formula [4.3.9] usa `f_k` e il testo usa `f_{ik}` per la resistenza a rottura del piolo
- **Interpretazione**: la grandezza corretta e' f_u (resistenza a rottura dell'acciaio del piolo), non f_k. L'OCR ha confuso i subscript
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.4.3.1.2 — Formula [4.3.10], esponente 1/3 vs 1/2 (radice quadrata)

- **Formula implementata**: P_concrete = 0.29 * alpha * d^2 * sqrt(f_ck * E_cm) / gamma_V
- **Dato OCR** (`cap4_page_52.json`): riporta `(f_{ik} E_{cm})^{1/3}` (radice cubica)
- **Interpretazione**: la formula EN 1994-1-1 §6.6.3.1 usa sqrt (radice quadrata, esponente 1/2). L'OCR potrebbe aver letto 1/2 come 1/3. Inoltre f_ik dovrebbe essere f_ck
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.5.2 — Formula [4.3.17], esponente phi vs moltiplicazione

- **Formula implementata**: E_c,eff = E_cm / (1 + phi_t * N_G,Ed / N_Ed)
- **Dato OCR** (`cap4_page_55.json`): riporta `(N_{c,eff}/N_{cr})^{phi}` con phi come esponente
- **Interpretazione**: la formula EN 1994-1-1 §6.7.3.3 usa phi come moltiplicatore, non come esponente. N_c,eff = N_G,Ed, N_cr = N_Ed (OCR usa nomi diversi). L'OCR ha posizionato phi come esponente invece che come fattore
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.5.2 — Formula [4.3.19], OCR garbled (tutti i termini identici)

- **Formula implementata**: N_pl,Rk = A_a*f_yk + 0.85*A_c*f_ck + A_s*f_sk
- **Dato OCR** (`cap4_page_55.json`): `N_{pl,Rk} = A_s*f_{sk} + 0,85*A_s*f_{sk} + A_s*f_{sk}` — tutti e tre i termini hanno A_s e f_sk
- **Interpretazione**: i tre termini devono avere le aree e resistenze dei tre materiali distinti (acciaio strutturale, calcestruzzo, armatura). OCR garbled
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.5.2 — Formula [4.3.18], lambda letto come x

- **Formula implementata**: lambda_bar = sqrt(N_pl,Rk / N_cr)
- **Dato OCR** (`cap4_page_55.json`): mostra `\bar{x}` invece di `\bar{\lambda}` — la lettera greca lambda e' stata letta come x
- **Interpretazione**: e' la snellezza normalizzata lambda_bar, non x
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.5.3.1 — Formula [4.3.24], esponente lambda^2 letto come lambda

- **Formula implementata**: eta_c = max(4.9 - 18.5*lambda + 17*lambda^2, 0)
- **Dato OCR** (`cap4_page_56.json`): mostra `17\cdot\bar{\lambda}` senza l'esponente ^2, e il tutto elevato al quadrato esternamente
- **Interpretazione**: la formula EN 1994-1-1 §6.7.3.2 usa 17*lambda^2 nel polinomio, senza elevare al quadrato il risultato. L'OCR ha spostato l'esponente
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.5.4.2 — Formula [4.3.32], 235/sqrt(f_y) vs sqrt(235/f_y)

- **Formula implementata**: d/t <= 52 * sqrt(235/f_y)
- **Dato OCR** (`cap4_page_58.json`): mostra `52 \cdot \frac{235}{\sqrt{f_y}}` che darebbe 52*235/sqrt(f_y) — valori irrealistici
- **Interpretazione**: la formula corretta EN 1994-1-1 Tab.6.3 usa epsilon = sqrt(235/f_y), quindi il limite e' 52*epsilon = 52*sqrt(235/f_y)
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.3.5.4.3 — Formula [4.3.35], simbolo <= letto come x

- **Formula implementata**: M_Ed <= alpha_M * M_pl,Rd(N_Ed)
- **Dato OCR** (`cap4_page_59.json`): mostra `M_{Ed} \times \alpha_M \cdot M_{PLRg}(N_{Ed})` — il <= e' letto come x, e M_pl,Rd garbled come M_PLRg
- **Interpretazione**: e' una disequazione di verifica, non un prodotto
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.4.8.1.11 — Formula [4.4.10], OCR garbled (f_vd/f_vd invece di tau_d/f_vd)

- **Formula implementata**: (tau_tor,d / (k_sh * f_v,d))^2 + (tau_d / f_v,d)^2 <= 1
- **Dato OCR** (`cap4_page_69.json`): la formula mostra `(f_vd / f_vd)^2` nel secondo termine, che darebbe sempre 1
- **Interpretazione**: il secondo termine deve essere (tau_d / f_v,d)^2, coerente con EC5 §6.1.8 e con il significato fisico dell'interazione taglio-torsione
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.4.8.1.6 — Formula [4.4.5], subscript OCR garbled (k_tv vs k_m)

- **Dato OCR** (`cap4_page_68.json`): il testo menziona sia k_m sia k_tv per lo stesso concetto
- **Interpretazione**: il coefficiente rilevante e' k_m (0.7 rettangolare, 1.0 altro). k_tv e' menzionato per dimensioni sezione (§11.7.1.1)
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.4.8.1.8 — Formula [4.4.7a/b], termine compressione al quadrato

- **Dato OCR** (`cap4_page_68.json`): le formule [4.4.7a/b] sono racchiuse tra parentesi tonde, senza esplicito esponente quadrato sul termine sigma_c/f_c
- **Interpretazione**: NTC18 §4.4.8.1.8 prevede che il termine di compressione sia elevato al quadrato (sigma_c/f_c)^2, coerente con EC5 §6.2.4
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.4.6 — Tab. 4.4.IV, caption OCR "k_avod" invece di "k_mod"

- **Dato OCR** (`cap4_page_65.json`): la tabella e' etichettata con "k_avod" invece di "k_mod"
- **Interpretazione**: evidente garbling OCR. Il coefficiente e' k_mod (modification factor)
- **Stato**: APERTO — da verificare su testo ufficiale

## §4.4.8.1.2 — Formula [4.4.2], sigma_theta letto come sigma_t,0,d

- **Dato OCR** (`cap4_page_67.json`): la formula mostra sigma_theta,d invece di sigma_t,0,d
- **Interpretazione**: la formula e' per la verifica a trazione parallela, quindi sigma_t,0,d. L'OCR ha confuso i subscript
- **Stato**: APERTO — da verificare su testo ufficiale

## §8.5.4 — Valori numerici FC non presenti nel testo OCR

- **Valori implementati**: FC = 1.35 (LC1), FC = 1.20 (LC2), FC = 1.00 (LC3)
- **Dato OCR** (`cap8_page_4.json`): il testo menziona LC1, LC2, LC3 e "fattori di confidenza" ma i valori numerici sono in un'immagine (Picture) non OCR'd
- **Interpretazione**: valori FC da Circolare C8.5.4.1, Tab.C8.5.IV, universalmente adottati nella pratica professionale
- **Stato**: APERTO — verificare i valori FC sul testo ufficiale della Circolare
