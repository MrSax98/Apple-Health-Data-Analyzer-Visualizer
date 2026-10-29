"""Analisi dei dati di Apple Salute: allenamenti (export.xml) e percorsi GPS (.gpx).

Uso:
    python main.py [--data-dir apple_health_export] [--save-dir grafici]
"""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import gpxpy
import gpxpy.gpx
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "apple_health_export"
EARTH_RADIUS_KM = 6371.0
TOP_TYPES_BAR = 15
TOP_TYPES_SCATTER = 7

RENAMES = {
    "workoutActivityType": "TipoAllenamento",
    "duration": "DurataMin",
    "totalDistance": "DistanzaKm",
    "totalEnergyBurned": "CalorieKcal",
    "startDate": "DataInizio",
    "endDate": "DataFine",
}

plt.style.use("ggplot")


def haversine_km(lat, lon):
    """Distanza in km tra punti GPS consecutivi (array di lunghezza n -> n-1)."""
    lat, lon = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    dlat, dlon = np.diff(lat), np.diff(lon)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def parse_workouts(xml_path):
    """Legge gli elementi <Workout> di export.xml e restituisce un DataFrame pulito."""
    root = ET.parse(xml_path).getroot()
    rows = []
    for workout in root.findall(".//Workout"):
        row = dict(workout.attrib)
        for meta in workout.findall(".//MetadataEntry"):
            row[meta.attrib["key"].replace("HK", "")] = meta.attrib["value"]
        rows.append(row)
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    for col in ("creationDate", "startDate", "endDate"):
        if col in df:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ("duration", "totalDistance", "totalEnergyBurned"):
        if col in df:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.extract(r"(\d+\.?\d*)", expand=False), errors="coerce"
            )
    if "workoutActivityType" in df:
        df["workoutActivityType"] = df["workoutActivityType"].str.replace("HKWorkoutActivityType", "")
    if "durationUnit" in df and "duration" in df:
        in_seconds = df["durationUnit"] == "sec"
        df.loc[in_seconds, "duration"] = df.loc[in_seconds, "duration"] / 60.0

    df = df.rename(columns=RENAMES)
    return df.sort_values("DataInizio").reset_index(drop=True)


def parse_gpx_file(gpx_path):
    """Restituisce i punti di un file GPX come DataFrame (latitude, longitude, elevation, time)."""
    with open(gpx_path, encoding="utf-8") as f:
        gpx = gpxpy.parse(f)
    points = [
        {"latitude": p.latitude, "longitude": p.longitude, "elevation": p.elevation, "time": p.time}
        for track in gpx.tracks
        for segment in track.segments
        for p in segment.points
    ]
    df = pd.DataFrame(points)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        df["elevation"] = pd.to_numeric(df["elevation"], errors="coerce")
    return df


def parse_gpx_routes(routes_dir):
    """Legge tutti i .gpx di una cartella: {nome file: DataFrame}. I file non validi vengono segnalati e saltati."""
    routes = {}
    for path in sorted(p for p in routes_dir.iterdir() if p.suffix.lower() == ".gpx"):
        try:
            df = parse_gpx_file(path)
        except (gpxpy.gpx.GPXXMLSyntaxException, OSError) as e:
            print(f"ATTENZIONE: {path.name} non leggibile: {e}")
            continue
        if not df.empty:
            routes[path.stem] = df
    return routes


def plot_workout_types(df):
    """Barre orizzontali dei tipi di allenamento più frequenti."""
    counts = df["TipoAllenamento"].value_counts().nlargest(TOP_TYPES_BAR).sort_values()
    fig, ax = plt.subplots(figsize=(11, 8))
    bars = ax.barh(counts.index, counts.values, color=plt.cm.viridis(np.linspace(0.4, 0.9, len(counts))))
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_title(f"Tipi di Allenamento Più Frequenti (Top {TOP_TYPES_BAR})", fontsize=14)
    ax.set_xlabel("Numero di Sessioni")
    ax.set_ylabel("Tipo di Allenamento")
    ax.margins(x=0.1)
    fig.tight_layout()
    return fig


def plot_duration_over_time(df):
    """Durata di ogni allenamento nel tempo, colorata per tipo (top 7 + Other)."""
    data = df.dropna(subset=["DataInizio", "DurataMin", "TipoAllenamento"]).copy()
    if data.empty:
        return None
    top = data["TipoAllenamento"].value_counts().nlargest(TOP_TYPES_SCATTER).index.tolist()
    data["TipoPlot"] = data["TipoAllenamento"].where(data["TipoAllenamento"].isin(top), "Other")
    order = top + (["Other"] if (data["TipoPlot"] == "Other").any() else [])
    cmap = plt.get_cmap("tab10")

    fig, ax = plt.subplots(figsize=(15, 8))
    for i, tipo in enumerate(order):
        subset = data[data["TipoPlot"] == tipo]
        ax.scatter(subset["DataInizio"], subset["DurataMin"], label=tipo, alpha=0.7, s=30, color=cmap(i % 10))
    ax.set_title(f"Durata Allenamenti nel Tempo per Tipo (Top {TOP_TYPES_SCATTER} + Other)", fontsize=14)
    ax.set_xlabel("Data")
    ax.set_ylabel("Durata (minuti)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=12))
    fig.autofmt_xdate(rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(title="Tipo Allenamento", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    fig.tight_layout(rect=[0, 0, 0.88, 1])
    return fig


def plot_route(df, name):
    """Mappa 2D del percorso GPX e profilo altimetrico."""
    route = df.dropna(subset=["latitude", "longitude", "elevation"]).sort_values("time").reset_index(drop=True)
    if len(route) < 2:
        return None
    route["km"] = np.concatenate([[0.0], np.cumsum(haversine_km(route["latitude"], route["longitude"]))])

    fig, (ax_map, ax_ele) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]})
    fig.suptitle(f"Percorso e Altimetria: {name}", fontsize=16)

    ax_map.plot(route["longitude"], route["latitude"], color="dodgerblue", linewidth=2, label="Percorso")
    ax_map.plot(route["longitude"].iloc[0], route["latitude"].iloc[0], "o", color="lime", markersize=8, label="Inizio", zorder=5)
    ax_map.plot(route["longitude"].iloc[-1], route["latitude"].iloc[-1], "o", color="red", markersize=8, label="Fine", zorder=5)
    ax_map.set(xlabel="Longitudine", ylabel="Latitudine", title="Mappa Percorso")
    ax_map.axis("equal")
    ax_map.grid(True, linestyle=":", alpha=0.7)
    ax_map.legend(fontsize=9)

    ax_ele.plot(route["km"], route["elevation"], color="forestgreen", linewidth=1.5)
    ax_ele.fill_between(route["km"], route["elevation"], alpha=0.2, color="forestgreen")
    ax_ele.set(xlabel="Distanza Cumulativa (km)", ylabel="Altitudine (m)", title="Profilo Altimetrico")
    ax_ele.grid(True, linestyle=":", alpha=0.7)
    ax_ele.set_xlim(0, max(route["km"].iloc[-1], 1e-3))
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig


def build_figures(data_dir):
    """Crea i grafici disponibili con i dati presenti in data_dir: {nome: Figure}."""
    figures = {}

    xml_path = data_dir / "export.xml"
    if xml_path.is_file():
        workouts = parse_workouts(xml_path)
        if not workouts.empty:
            figures["tipi_allenamento"] = plot_workout_types(workouts)
            figures["durata_nel_tempo"] = plot_duration_over_time(workouts)
    else:
        print(f"ATTENZIONE: {xml_path} non trovato, grafici sugli allenamenti saltati.")

    routes_dir = data_dir / "workout-routes"
    if routes_dir.is_dir():
        routes = parse_gpx_routes(routes_dir)
        if routes:
            name, df = next(iter(routes.items()))
            figures["percorso"] = plot_route(df, name)
    else:
        print(f"ATTENZIONE: {routes_dir} non trovata, grafico del percorso saltato.")

    return {name: fig for name, fig in figures.items() if fig is not None}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="cartella esportata da Apple Salute")
    parser.add_argument("--save-dir", type=Path, help="salva i grafici come PNG in questa cartella invece di mostrarli")
    args = parser.parse_args()

    if not args.data_dir.is_dir():
        parser.error(f"cartella dati non trovata: {args.data_dir}")

    figures = build_figures(args.data_dir)
    if not figures:
        print("Nessun grafico generato.")
        return

    if args.save_dir:
        args.save_dir.mkdir(parents=True, exist_ok=True)
        for name, fig in figures.items():
            fig.savefig(args.save_dir / f"{name}.png", dpi=150)
        print(f"Salvati {len(figures)} grafici in {args.save_dir}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
