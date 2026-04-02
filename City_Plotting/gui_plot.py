"""
City Plotting GUI Application

A customizable GUI application for plotting city data using customtkinter.
Displays city plots side-by-side with automatic image scaling and dark mode.
"""

import customtkinter as ctk
import Plot
import city_name_check

# ============================================================================
# Configuration Constants
# ============================================================================

# Image and Layout Configuration
IMAGE_HEIGHT_RATIO = 0.65  # Aspect ratio for resizing images (width to height)

# UI Layout
BUTTON_ROW = 0
CONTENT_ROW = 1
LEFT_COLUMN = 0
RIGHT_COLUMN = 1

# Theme and Styling
THEME_FILE = "City_Plotting/orange.json"
STOP_BUTTON_HOVER_COLOR = "#B85820"
WINDOW_TITLE = "City Plotter"

# Dialog Configuration
DIALOG_TITLE = "City"
DIALOG_TITLE_COUNTRY = "Country"
DIALOG_TEXT = "Enter city name:"


# Button Labels
START_BUTTON_LABEL = "Start"
STOP_BUTTON_LABEL = "Stop Program"

# Padding and Grid Configuration
BUTTON_PADDING_Y = 5
LABEL_PADDING_Y = 5
LABEL_PADDING_X = 0


# ============================================================================
# Global Variables
# ============================================================================

app = None
input_dialog = None
input_dialog_country = None
plot_image_1 = None
plot_image_2 = None
plot_label_1 = None
plot_label_2 = None


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_image_size(image, max_size):
    """
    Calculate resized image dimensions while maintaining aspect ratio.
    
    Args:
        image: PIL Image object with width and height attributes
        max_size: Maximum size constraint (in pixels)
    
    Returns:
        Tuple of (width, height) for the resized image
    """
    image_ratio = image.width / image.height
    if image_ratio > 1:  # Image is wider than tall
        return (int(max_size * image_ratio), max_size)
    else:  # Image is taller than wide
        return (max_size, int(max_size / image_ratio))



def get_country_name(city_name):
    """
    Retrieve the country name for a given city using city_name_check module.
    
    Args:
        city_name: Name of the city to look up
    
    if more than one country is found for the city, prompts the user to select one.
    when a valid country is selected, calls display_plots with the combined city and country name.
    and when an invalid country is selected, shows an error message box and prompts the user to try again.
    """
    global input_dialog_country
    country = ""

    countries = city_name_check.country_check(city_name)
    DIALOG_TEXT_COUNTRY = f"Enter country name: \nMultiple countries {countries} found for '{city_name}'. Please specify:"

    if len(countries) > 1:
        while country.capitalize() not in countries:
            input_dialog_country = ctk.CTkInputDialog(
                title=DIALOG_TITLE_COUNTRY,
                text=DIALOG_TEXT_COUNTRY,
            )
            country = input_dialog_country.get_input()

            if country.capitalize() in countries:
                display_plots(f"{city_name}, {country.capitalize()}")
            else:
                DIALOG_TEXT_COUNTRY = f"Invalid country name: '{country}'. Please try again. \nOptions: {countries}"
    
    elif len(countries) == 1:
        display_plots(f"{city_name}, {countries[0]}")

# ============================================================================
# Event Handlers
# ============================================================================

def start_plotting():
    """
    Display input dialog for city name and initiate the plotting process.
    
    Prompts the user to enter a city name and country, then triggers
    the plotting workflow.
    """
    global input_dialog
    max_height = app.winfo_height() * IMAGE_HEIGHT_RATIO
    print("Maximum image size:", max_height)
    
    input_dialog = ctk.CTkInputDialog(
        title=DIALOG_TITLE,
        text=DIALOG_TEXT,
    )
    name = input_dialog.get_input()
    get_country_name(name)


def display_plots(place_name):
    """
    Retrieve city data, generate plots, and display them in the GUI.
    
    Fetches plot images from Plot.py, resizes them to fit the window
    while maintaining aspect ratio, converts them to CTkImage format,
    and updates the GUI labels.
    
    Args:
        dialog: CTkInputDialog object containing user input
    """
    global plot_image_1, plot_image_2
    
    # Get city name from user input
    #place_name = dialog.get_input()

    # Generate plots from Plot.py
    plot_image_1, plot_image_2 = Plot.main(place_name)
    
    # Calculate maximum image size based on window height
    max_size = app.winfo_height() * IMAGE_HEIGHT_RATIO
    
    # Calculate dimensions for both images while maintaining aspect ratio
    size_1 = calculate_image_size(plot_image_1, max_size)
    size_2 = calculate_image_size(plot_image_2, max_size)
    
    # Convert PIL images to CustomTkinter compatible format
    plot_image_1 = ctk.CTkImage(plot_image_1, size=size_1)
    plot_image_2 = ctk.CTkImage(plot_image_2, size=size_2)
    
    # Update GUI labels with resized images
    plot_label_1.configure(image=plot_image_1)
    plot_label_2.configure(image=plot_image_2)


def on_closing():
    """Close the application gracefully."""
    app.quit()



# ============================================================================
# Application Setup
# ============================================================================

def initialize_app():
    """
    Initialize and configure the main application window.
    
    Sets up the theme, layout, and UI elements.
    """
    global app, plot_label_1, plot_label_2
    
    # Configure appearance and theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(THEME_FILE)
    
    # Initialize main window
    app = ctk.CTk()
    app.title(WINDOW_TITLE)
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.after(0, lambda: app.state('zoomed'))  # Maximize window on startup
    
    # Configure grid layout to make content expandable
    app.grid_rowconfigure(CONTENT_ROW, weight=1)
    app.grid_columnconfigure((LEFT_COLUMN, RIGHT_COLUMN), weight=1)
    
    # Create and configure "Start" button
    start_button = ctk.CTkButton(
        app,
        text=START_BUTTON_LABEL,
        command=start_plotting
    )
    start_button.grid(
        row=BUTTON_ROW,
        column=LEFT_COLUMN,
        padx=LABEL_PADDING_X,
        pady=BUTTON_PADDING_Y,
        sticky="ew"
    )
    
    # Create and configure "Stop Program" button
    stop_button = ctk.CTkButton(
        app,
        text=STOP_BUTTON_LABEL,
        hover_color=STOP_BUTTON_HOVER_COLOR,
        command=on_closing
    )
    stop_button.grid(
        row=BUTTON_ROW,
        column=RIGHT_COLUMN,
        padx=LABEL_PADDING_X,
        pady=BUTTON_PADDING_Y,
        sticky="ew"
    )
    
    # Create label for first plot image
    plot_label_1 = ctk.CTkLabel(app, text="")
    plot_label_1.grid(
        row=CONTENT_ROW,
        column=LEFT_COLUMN,
        padx=LABEL_PADDING_X,
        pady=LABEL_PADDING_Y,
        sticky="nsew"
    )
    
    # Create label for second plot image
    plot_label_2 = ctk.CTkLabel(app, text="")
    plot_label_2.grid(
        row=CONTENT_ROW,
        column=RIGHT_COLUMN,
        padx=LABEL_PADDING_X,
        pady=LABEL_PADDING_Y,
        sticky="nsew"
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """Initialize and run the application."""
    initialize_app()
    app.mainloop()