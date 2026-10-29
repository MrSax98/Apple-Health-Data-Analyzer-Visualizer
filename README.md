# Apple Health Data Analyzer & Visualizer

Script Python che analizza i dati esportati da Apple Salute, concentrandosi sugli allenamenti (`Workout` in `export.xml`) e sui percorsi GPS (`.gpx`), e produce tre grafici con Matplotlib.

**Creato da:** me, con l'aiuto di Gemini.

## Grafici

1. **Tipi di allenamento:** barre orizzontali dei 15 tipi più frequenti.
2. **Durata nel tempo:** dispersione della durata di ogni allenamento, colorata per tipo (top 7 + Other).
3. **Mappa e altimetria:** mappa 2D e profilo altimetrico del primo percorso GPX trovato in `workout-routes/`.

Se manca `export.xml` o la cartella `workout-routes/`, i grafici corrispondenti vengono saltati con un avviso.

## 1. Esporta i dati da Apple Salute

1. Apri l'app **Salute** sull'iPhone e tocca la tua **immagine del profilo** in alto a destra.
2. Scorri fino a **Esporta tutti i dati di Salute** e tocca **Esporta** (può richiedere tempo).
3. Trasferisci lo zip sul computer e **decomprimilo**: ottieni la cartella `apple_health_export` con `export.xml`, `export_cda.xml` e `workout-routes/`.

## 2. Setup

```bash
git clone https://github.com/MrSax98/Apple-Health-Data-Analyzer-Visualizer.git
cd Apple-Health-Data-Analyzer-Visualizer
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copia la cartella `apple_health_export` accanto a `main.py`, oppure indica il percorso con `--data-dir`. La cartella è in `.gitignore`: **non fare commit dei tuoi dati di salute**.

## 3. Uso

```bash
python main.py                                  # mostra i grafici in finestre
python main.py --save-dir grafici               # salva i PNG in grafici/
python main.py --data-dir /percorso/export      # cartella dati in un altro posto
```

## 4. Test

```bash
pip install -r requirements-dev.txt
python -m pytest
```

I test usano file XML e GPX sintetici creati al volo: non servono i tuoi dati.

## Struttura

| File | Contenuto |
|---|---|
| `main.py` | parsing di XML e GPX, funzioni di grafico, interfaccia a riga di comando |
| `tests/test_main.py` | test di distanza, parsing e grafici |
| `requirements.txt` / `requirements-dev.txt` | dipendenze di esecuzione / di sviluppo |
