# Tracciabilità normativa

Ogni funzione pubblica di norma-ntc è decorata con `@ntc_ref`, che registra il riferimento normativo direttamente sulla funzione.

## Come funziona

```python
from pyntc.core import get_ntc_ref
from pyntc.actions.wind import wind_base_velocity

ref = get_ntc_ref(wind_base_velocity)
print(ref)
# NtcReference(article='3.3.1', table='Tab.3.3.I', formula='3.3.1', norm='NTC18')
```

Il decoratore espone tre campi:

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| `article` | Articolo NTC18 | `"3.3.1"` |
| `table` | Tabella di riferimento | `"Tab.3.3.I"` |
| `formula` | Numero formula | `"3.3.1"` |
| `norm` | Norma di riferimento | `"NTC18"` |

## Registro dei dubbi

Le ambiguità riscontrate nella conversione OCR del testo NTC18 sono documentate in `DUBBI_NTC18.md` nel repository. Per ogni dubbio è riportata:

- La formula o tabella coinvolta
- Il valore prodotto dall'OCR
- L'interpretazione adottata
- Lo stato (APERTO / CHIUSO)

Questo file è il registro trasparente delle incertezze del progetto.

## API decoratore

::: pyntc.core.reference
