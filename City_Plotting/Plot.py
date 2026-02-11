"""
City Map Visualization Module

This module provides utilities for creating stylized map visualizations of cities
using OpenStreetMap data. It supports overlaying various transportation features
like railways, trams, and signals on top of road networks.
"""

import io
from typing import Tuple

import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
from PIL import Image

# ============================================================================
# Constants
# ============================================================================

# Export resolution in dots per inch
EXPORT_DPI = 600

# Road styling by highway type with width and color properties
ROAD_STYLES = {
    'motorway': {'width': 2.5, 'color': '#000000'},
    'trunk': {'width': 2.5, 'color': '#000000'},
    'primary': {'width': 1.5, 'color': '#222222'},
    'secondary': {'width': 1.5, 'color': '#222222'},
    'tertiary': {'width': 0.8, 'color': '#444444'},
    'default': {'width': 0.3, 'color': '#888888'},
}

# Railway features with visualization properties (color, width/size, stacking order)
RAILWAY_FEATURES = {
    'tram': {'tags': {'railway': 'tram'}, 'color': 'red', 'width': 1, 'zorder': 3},
    'rail': {'tags': {'railway': 'rail'}, 'color': 'blue', 'width': 1, 'zorder': 5},
    'narrow_gauge': {'tags': {'railway': 'narrow_gauge'}, 'color': 'cyan', 'width': 1, 'zorder': 4},
    'signal': {'tags': {'railway': 'signal'}, 'color': 'green', 'size': 4, 'zorder': 6},
}


# ============================================================================
# Utility Functions
# ============================================================================

def export_image(fig: plt.Figure) -> Image.Image:
    """
    Convert a matplotlib figure to a PIL Image object.

    Saves the figure as high-resolution PNG to a bytes buffer, then opens it
    as a PIL Image for display in the GUI.

    Args:
        fig: Matplotlib figure object to convert.

    Returns:
        PIL Image object containing the rendered figure.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=EXPORT_DPI, bbox_inches='tight')
    buf.seek(0)
    return Image.open(buf)


def get_features(place_name: str, tags: dict) -> gpd.GeoDataFrame:
    """
    Retrieve geographic features from OpenStreetMap for a given place and tags.

    Safely handles cases where no features are found by returning an empty
    GeoDataFrame to prevent errors in subsequent processing.

    Args:
        place_name: Geographic location to query (e.g., 'Berlin, Germany').
        tags: OSM tags to filter features (e.g., {'railway': 'rail'}).

    Returns:
        GeoDataFrame with matching features, or empty GeoDataFrame if none found.
    """
    try:
        features = ox.features_from_place(place_name, tags)
    except ox._errors.InsufficientResponseError:
        features = gpd.GeoDataFrame()
    return features


def get_road_style(highway_type: str) -> Tuple[float, str]:
    """
    Determine line width and color for a road based on its type.

    Maps highway classifications to visual styling to represent road hierarchy
    from major highways to residential streets.

    Args:
        highway_type: OSM highway classification tag value (e.g., 'motorway').

    Returns:
        Tuple of (width in points, color as hex string).
    """
    highway_str = str(highway_type).lower()

    # Check against predefined road styles
    for road_type, style in ROAD_STYLES.items():
        if road_type in highway_str:
            return style['width'], style['color']

    # Default to residential street styling
    return ROAD_STYLES['default']['width'], ROAD_STYLES['default']['color']


def overlay_feature(
    features: gpd.GeoDataFrame,
    ax: plt.Axes,
    feature_config: dict,
) -> None:
    """
    Overlay a geographic feature layer on an existing map.

    Handles both line/polygon features (railways) and point features (signals)
    by checking for 'size' vs 'width' properties in the configuration.

    Args:
        features: GeoDataFrame containing geographic features to overlay.
        ax: Matplotlib axes object to draw features on.
        feature_config: Configuration dict with color, width/size, and zorder.
    """
    if features.empty:
        return

    # Point features (e.g., signals) use markersize
    if 'size' in feature_config:
        features.plot(
            ax=ax,
            color=feature_config['color'],
            markersize=feature_config['size'],
            alpha=1.0,
            zorder=feature_config['zorder'],
        )
    # Line/polygon features use linewidth
    else:
        features.plot(
            ax=ax,
            color=feature_config['color'],
            linewidth=feature_config['width'],
            alpha=1.0,
            zorder=feature_config['zorder'],
        )



# ============================================================================
# Main Function
# ============================================================================

def main(place_name: str) -> Tuple[Image.Image, Image.Image]:
    """
    Generate two map visualizations of a city with transportation features.

    Creates stylized maps showing road networks with overlaid railway infrastructure.
    The first map excludes signals, the second includes them for comparison.

    Args:
        place_name: Name of the city or geographic location to map (e.g., 'Berlin, Germany').

    Returns:
        Tuple of (map_without_signals, map_with_signals) as PIL Image objects.
    """
    # Load road network graph for the specified location
    graph = ox.graph_from_place(place_name, network_type='drive')

    # Retrieve all railway features using configuration dictionary
    railway_data = {
        feature_name: get_features(place_name, config['tags'])
        for feature_name, config in RAILWAY_FEATURES.items()
    }

    # Apply road styling based on highway type
    widths = []
    colors = []
    for u, v, k, data in graph.edges(data=True, keys=True):
        width, color = get_road_style(data['highway'])
        widths.append(width)
        colors.append(color)

    # Create base map with styled roads
    fig, ax = ox.plot_graph(
        graph,
        node_size=0,
        edge_color=colors,
        edge_linewidth=widths,
        bgcolor='white',
        show=False,
        close=False,
    )

    # Overlay railway features (excluding signals)
    for feature_name, features in railway_data.items():
        if feature_name != 'signal':
            overlay_feature(features, ax, RAILWAY_FEATURES[feature_name])

    # Export map without signals for the first image
    map_without_signals = export_image(fig)

    # Add railway signals and export final map
    overlay_feature(railway_data['signal'], ax, RAILWAY_FEATURES['signal'])
    map_with_signals = export_image(fig)

    return map_without_signals, map_with_signals
