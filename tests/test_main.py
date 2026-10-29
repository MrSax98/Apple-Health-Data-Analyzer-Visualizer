import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

import main

EXPORT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<HealthData>
  <Workout workoutActivityType="HKWorkoutActivityTypeRunning" duration="30" durationUnit="min"
           totalDistance="5" totalEnergyBurned="300"
           creationDate="2025-01-02 08:00:00 +0100" startDate="2025-01-02 07:00:00 +0100" endDate="2025-01-02 07:30:00 +0100">
    <MetadataEntry key="HKIndoorWorkout" value="0"/>
  </Workout>
  <Workout workoutActivityType="HKWorkoutActivityTypeWalking" duration="1800" durationUnit="sec"
           creationDate="2025-01-01 08:00:00 +0100" startDate="2025-01-01 07:00:00 +0100" endDate="2025-01-01 07:30:00 +0100"/>
</HealthData>
"""


def gpx_text(points):
    body = "".join(
        f'<trkpt lat="{lat}" lon="{lon}"><ele>{ele}</ele><time>2025-01-01T07:0{i}:00Z</time></trkpt>'
        for i, (lat, lon, ele) in enumerate(points)
    )
    return f'<?xml version="1.0"?><gpx version="1.1" creator="t" xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg>{body}</trkseg></trk></gpx>'


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "export.xml").write_text(EXPORT_XML, encoding="utf-8")
    routes = tmp_path / "workout-routes"
    routes.mkdir()
    (routes / "route_1.gpx").write_text(gpx_text([(41.90, 12.49, 20), (41.91, 12.50, 35), (41.92, 12.51, 30)]))
    (routes / "rotto.gpx").write_text("<gpx><non chiuso")
    return tmp_path


def test_haversine_roma_milano():
    km = main.haversine_km([41.9028, 45.4642], [12.4964, 9.1900])
    assert km == pytest.approx([477.0], rel=0.01)


def test_haversine_punti_coincidenti_e_un_solo_punto():
    assert main.haversine_km([10, 10], [20, 20]).tolist() == [0.0]
    assert main.haversine_km([10], [20]).size == 0


def test_parse_workouts_pulisce_tipi_e_unita(data_dir):
    df = main.parse_workouts(data_dir / "export.xml")
    assert list(df["TipoAllenamento"]) == ["Walking", "Running"]  # ordinati per data
    assert list(df["DurataMin"]) == [30.0, 30.0]  # 1800 sec -> 30 min
    assert df["DataInizio"].is_monotonic_increasing
    assert df.loc[1, "IndoorWorkout"] == "0"  # metadato senza prefisso HK


def test_parse_workouts_senza_allenamenti(tmp_path):
    xml = tmp_path / "export.xml"
    xml.write_text("<HealthData/>")
    assert main.parse_workouts(xml).empty


def test_parse_gpx_routes_salta_file_non_validi(data_dir, capsys):
    routes = main.parse_gpx_routes(data_dir / "workout-routes")
    assert list(routes) == ["route_1"]
    assert len(routes["route_1"]) == 3
    assert "rotto.gpx" in capsys.readouterr().out


def test_plot_route_crea_mappa_e_altimetria(data_dir):
    """Regressione: il colore ' Sostituisc' faceva fallire sempre il grafico altimetrico."""
    df = main.parse_gpx_routes(data_dir / "workout-routes")["route_1"]
    fig = main.plot_route(df, "route_1")
    assert len(fig.axes) == 2
    assert len(fig.axes[1].lines) == 1


def test_plot_route_con_meno_di_due_punti():
    df = pd.DataFrame({"latitude": [1.0], "longitude": [1.0], "elevation": [1.0], "time": [pd.Timestamp("2025-01-01", tz="UTC")]})
    assert main.plot_route(df, "x") is None


def test_build_figures_e_salvataggio(data_dir, tmp_path):
    figures = main.build_figures(data_dir)
    assert set(figures) == {"tipi_allenamento", "durata_nel_tempo", "percorso"}


def test_build_figures_cartella_vuota(tmp_path, capsys):
    assert main.build_figures(tmp_path) == {}
    assert "non trovato" in capsys.readouterr().out
