import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd

def get_features(place_name, tags):
    try:
        features = ox.features_from_place(place_name, tags)
    except ox._errors.InsufficientResponseError: # Catch the imported error directly
        # Create an empty GeoDataFrame if no features are found to avoid further errors
        features = gpd.GeoDataFrame()
    return features

# 1. Stadt definieren
place_name = "Berlin, Germany"

# 2. Graph laden
graph = ox.graph_from_place(place_name, network_type='drive')

#get Features
tag_tram = {"railway": "tram"}
trams = get_features(place_name, tag_tram)
tag_train = {"railway": "rail"}
trains = get_features(place_name, tag_train)
tag_train_narrow = {"railway": "narrow_gauge"}
trains_narrow = get_features(place_name, tag_train_narrow)
tag_signals = {"railway": "signal"}
signals = get_features(place_name, tag_signals)

# 3. Logik für Dicke und Farbe definieren
def get_edge_style(highway_type):
    # Hauptstraßen (Motorway, Trunk) - Tiefschwarz und dick
    if 'motorway' in str(highway_type) or 'trunk' in str(highway_type):
        return 2.5, '#000000'
    # Wichtige Stadtstraßen (Primary, Secondary) - Schwarz und mittel
    elif 'primary' in str(highway_type) or 'secondary' in str(highway_type):
        return 1.5, '#222222'
    # Kleinere Erschließungsstraßen (Tertiary) - Dunkelgrau und dünner
    elif 'tertiary' in str(highway_type):
        return 0.8, '#444444'
    # Alles andere (Wohnstraßen, Gassen) - Hellgrau und hauchdünn
    else:
        return 0.3, '#888888'

# 4. Listen für Dicke und Farbe erstellen
widths = []
colors = []

for u, v, k, data in graph.edges(data=True, keys=True):
    w, c = get_edge_style(data['highway'])
    widths.append(w)
    colors.append(c)

# 5. Plotten mit beiden Listen
fig, ax = ox.plot_graph(
    graph,
    node_size=0,
    edge_color=colors,     # Liste mit Farwerten
    edge_linewidth=widths, # Liste mit Stärken
    bgcolor='white',
    show=False,
    close=False
)

# 5. Straßenbahnen hinzufügen
# Wir prüfen, ob überhaupt Tram-Daten gefunden wurden
if not trams.empty:
    # Wir filtern nur Linienobjekte (LineString/MultiLineString)
    trams.plot(ax=ax, color='red', linewidth=1, alpha=1.0, zorder=3)


#adding Trains
if not trains.empty:
    # Wir filtern nur Linienobjekte (LineString/MultiLineString)
    trains.plot(ax=ax, color='blue', linewidth=1, alpha=1.0, zorder=5)

#adding Trains narrow Gauge
if not trains_narrow.empty:
    # Wir filtern nur Linienobjekte (LineString/MultiLineString)
    trains_narrow.plot(ax=ax, color='cyan', linewidth=1, alpha=1.0, zorder=4)

#save without signals
fig.savefig("stadt.png", dpi=600, bbox_inches='tight')



#adding Signals
if not signals.empty:
    # Wir filtern nur Linienobjekte (LineString/MultiLineString)
    # Kleine Markergröße für Signale setzen
    signals.plot(ax=ax, color='green', markersize=4, alpha=1.0, zorder=6)
# save with signals
fig.savefig("stadt_with_signals.png", dpi=600, bbox_inches='tight')

plt.show()