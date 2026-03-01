# norma-ntc

**norma-ntc** è una libreria Python open source per la verifica strutturale secondo le NTC 2018 (D.M. 17/01/2018).

## Installazione

```bash
pip install norma-ntc
```

## Caratteristiche

- **Tracciabilità normativa**: ogni funzione pubblica riporta il riferimento a articolo, tabella e formula NTC18 tramite il decoratore `@ntc_ref`
- **Test-driven**: 1142 test, copertura completa delle tabelle normative
- **Pipeline chiara**: pyntc produce gli input al solutore (azioni) e verifica gli output (checks) — non è un solutore FEM
- **Dipendenze minime**: solo NumPy (core), SciPy (opzionale)

## Architettura

```
[NTC 2018] → pyntc.actions → [Solutore FEM] → pyntc.checks → [Relazione]
```

| Modulo | Sezione | Descrizione |
|--------|---------|-------------|
| `actions.loads` | §3.1 | Pesi propri, partizioni, carichi variabili |
| `actions.wind` | §3.3 | Azione del vento |
| `actions.snow` | §3.4 | Azione della neve |
| `actions.seismic` | §3.2 | Azione sismica |
| `actions.temperature` | §3.5 | Azioni termiche |
| `actions.fire` | §3.6 | Azioni da incendio |
| `actions.combinations` | §2.5.3 | Combinazioni SLU/SLE |
| `checks.concrete` | §4.1 | Verifiche cemento armato |
| `checks.steel` | §4.2 | Verifiche acciaio |
| `checks.composite` | §4.3 | Verifiche acciaio-calcestruzzo |
| `checks.timber` | §4.4 | Verifiche legno |
| `checks.masonry` | §4.5 | Verifiche muratura |
| `checks.bridges` | Cap. 5 | Carichi sui ponti |
| `checks.geotechnical` | Cap. 6 | Verifiche geotecniche |
| `checks.seismic_design` | Cap. 7 | Progettazione sismica |
| `checks.existing_buildings` | Cap. 8 | Edifici esistenti |

## Disclaimer

Questa libreria non sostituisce il giudizio professionale dell'ingegnere strutturista. La verifica finale è responsabilità del progettista.
