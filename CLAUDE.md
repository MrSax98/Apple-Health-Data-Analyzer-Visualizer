# Apple Health Data Analyzer

Script Python (`main.py`) per analizzare allenamenti e percorsi GPS esportati da Apple Salute.

- Test: `python -m pytest` (dati sintetici, grafici con backend `Agg`).
- Esecuzione senza finestre: `MPLBACKEND=Agg python main.py --data-dir <cartella> --save-dir <out>`.
- Mai committare `apple_health_export/` (dati personali di salute) né i PNG generati.
- Logica nelle funzioni di `main.py`, nessun codice a livello modulo oltre alle costanti; le funzioni di grafico restituiscono la `Figure` (o `None` se mancano dati).
- Gli errori si catturano per tipo (`GPXXMLSyntaxException`, `OSError`), non con `except Exception`.
- Testo utente e commenti in italiano.
