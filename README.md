# Apple Health Data Analyzer & Visualizer

Questo script Python analizza i dati esportati da Apple Salute (Health App), focalizzandosi sugli allenamenti (`Workout`) e sui percorsi GPS (`.gpx`), per generare alcune visualizzazioni di base.

**Creato da:** Me + uso di Gemini

## Funzionalità Principali

* Legge il file `export.xml` dall'esportazione di Apple Salute.
* Estrae i dati riassuntivi degli allenamenti (tipo, durata, calorie, distanza, date).
* Legge tutti i file `.gpx` presenti nella sottocartella `workout-routes/`.
* Genera 3 grafici utilizzando Matplotlib:
    1.  **Tipi di Allenamento:** Grafico a barre dei 15 tipi di allenamento più frequenti.
    2.  **Durata Allenamenti nel Tempo:** Grafico a dispersione che mostra la durata di ciascun allenamento nel tempo, colorato per tipo (Top 7 + Altri).
    3.  **Mappa e Altimetria Percorso:** Grafico combinato che mostra la mappa 2D e il profilo altimetrico del primo percorso GPX trovato.

## Prerequisiti

* **Python 3:** Assicurati di avere Python 3 installato ([https://www.python.org/](https://www.python.org/)).
* **Pip:** Il package installer per Python, di solito incluso con Python.
* **Dati Esportati da Apple Salute:** Vedi sezione successiva.

## 1. Ottenere i Tuoi Dati da Apple Salute

Per usare questo script, devi prima esportare i tuoi dati dall'app Salute sul tuo iPhone:

1.  Apri l'app **Salute** sul tuo iPhone.
2.  Tocca l'**immagine del tuo profilo** o le tue iniziali in alto a destra.
3.  Scorri verso il basso e tocca **Esporta tutti i dati di Salute**.
4.  Tocca **Esporta**. Il processo potrebbe richiedere del tempo.
5.  Una volta completato, ti verrà presentato un file zip (`Esportazione-salute.zip` o simile). Salvalo o trasferiscilo sul tuo computer (es. tramite AirDrop, iCloud Drive, Email, etc.).
6.  **Decomprimi** il file zip. Otterrai una cartella chiamata `apple_health_export` (o simile, potrebbe variare leggermente con la lingua/versione iOS). Questa cartella contiene `export.xml`, `export_cda.xml` e la sottocartella `workout-routes/`.

## 2. Setup del Progetto

1.  **Clona o Scarica il Repository:**
    ```bash
    git clone <URL_DEL_TUO_FUTURO_REPOSITORY>
    cd <NOME_REPOSITORY>
    ```
    Oppure scarica lo zip da GitHub e decomprimilo.

2.  **Posiziona i Tuoi Dati:**
    * **IMPORTANTE:** Prendi la cartella `apple_health_export` che hai ottenuto al Passo 1 e **copiala/spostala all'interno** della cartella del progetto clonata/scaricata, allo stesso livello del file `main.py`.
    * La struttura dovrà essere:
        ```
        tuo-repository/
        ├── .gitignore
        ├── main.py
        ├── README.md
        ├── requirements.txt
        └── apple_health_export/   <-- La TUA cartella dati qui!
            ├── export.xml
            ├── workout-routes/
            │   ├── route_....gpx
            │   └── ...
            └── export_cda.xml
        ```
    * **NON FARE COMMIT DELLA CARTELLA `apple_health_export`!** È ignorata da `.gitignore`.

3.  **Crea un Ambiente Virtuale (Consigliato):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Su macOS/Linux
    # venv\Scripts\activate    # Su Windows
    ```

4.  **Installa le Dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

## 3. Utilizzo

Una volta completato il setup e attivato l'ambiente virtuale (se creato), esegui lo script Python dal terminale, stando nella cartella principale del progetto:

```bash
python main.py
