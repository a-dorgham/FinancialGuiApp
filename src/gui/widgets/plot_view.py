# ---------------------------------------------
# PLOT VIEW WIDGET
# ---------------------------------------------
from typing import Optional, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import plotly.graph_objects as go
from plotly.io import to_json
import tempfile
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from src.core.utils import load_data, add_features, find_peaks_and_valleys, plot_with_peaks
from src.data.config_manager import ConfigManager
from src.core.controllers import TradeController
from typing import Any


class PlotView(QWebEngineView):
    """Widget for displaying Plotly charts."""

    def __init__(self, parent: Optional[QWidget], trade_controller: TradeController, 
                 control_panel: Optional[Any] = None) -> None:
        """
        Initialize the plot view widget.

        Args:
            parent (Optional[QWidget]): The parent widget (MainWindow).
            trade_controller (TradeController): The controller for trade operations.
            control_panel (Optional[ControlPanel]): The control panel for GUI updates.
        """
        super().__init__(parent)
        self.fig: Optional[go.Figure] = None
        self.df: Optional[pd.DataFrame] = None
        self.initialized = False
        self.current_date: Optional[str] = None
        self.config_manager = ConfigManager()
        self.trade_controller = trade_controller
        self.control_panel = control_panel
        self.html_file = None

    # ---------------------------------------------
    # PLOT MANAGEMENT
    # ---------------------------------------------
    
    def load_and_plot_data(self, file_path: str, start_date: str, end_date: str) -> None:
        """
        Load data from a file and plot it.

        Args:
            file_path (str): Path to the data file.
            start_date (str): Start date in 'YYYY-MM-DD HH:MM' format.
            end_date (str): End date in 'YYYY-MM-DD HH:MM' format.
        """
        try:
            df = load_data(file_path, start_date, end_date)
            if df is None or df.empty:
                print(f"No data loaded from {file_path} for {start_date} to {end_date}")
                return

            self.df = df
            self.df['Signal'] = find_peaks_and_valleys(df_window=self.df[['Time', 'Close']], 
                                                       distance=5, prominence=0.1)
            min_value = self.df['Close'].min()
            max_value = self.df['Close'].max()

            self.fig = go.Figure()
            self.fig = plot_with_peaks(self.df, fig=self.fig, plotData=True, plotMA=False, 
                                      plotPeaks=False, figShow=False)

            if self.control_panel:
                self.control_panel.ylim_min_edit.setText(f"{min_value:.3f}")
                self.control_panel.ylim_max_edit.setText(f"{max_value:.3f}")
            self.update_plotly_canvas()
        except Exception as e:
            print(f"Error loading and plotting data: {e}")

    def increment_plot(self, start_date: str, end_date: str, current_date: str, increment: str, 
                    x_limits: Tuple[str, str], y_limits: Tuple[str, str], 
                    auto_trade: bool, increment_x_limits: bool) -> bool:
        """
        Increment the plot's current date and update the display while maintaining zoom state.

        Args:
            start_date (str): The start date in 'YYYY-MM-DD HH:MM' format.
            end_date (str): The end date in 'YYYY-MM-DD HH:MM' format.
            current_date (str): The current date in 'YYYY-MM-DD HH:MM' format.
            increment (str): The increment in minutes.
            x_limits (Tuple[str, str]): The x-axis limits (min, max).
            y_limits (Tuple[str, str]): The y-axis limits (min, max).
            auto_trade (bool): Whether to perform auto trading.
            increment_x_limits (bool): Whether to increment x-axis limits.

        Returns:
            bool: True if end of data is reached (current_date >= end_date), False otherwise.
        """
        try:
            file_path = self.config_manager.get_data_path()
            if not os.path.exists(file_path):
                print(f"Data file not found: {file_path}")
                return False

            if not self.fig:
                self.fig = go.Figure()

            # Calculate new datetime
            current_datetime = datetime.strptime(current_date, "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            increment_minutes = int(increment)
            new_datetime = current_datetime + timedelta(minutes=increment_minutes)
            new_current_date = new_datetime.strftime("%Y-%m-%d %H:%M")

            if new_datetime >= end_datetime:
                return True

            self.fig.update_layout(title="Financial Data", autosize=True)

            # JavaScript to get current precise zoom state
            def handle_current_ranges(result: str):
                try:
                    ranges = json.loads(result) if result else None
                    current_x_range = ranges.get("xRange") if ranges else None
                    current_y_range = ranges.get("yRange") if ranges else None

                    # Store original zoom state
                    original_x_range = current_x_range
                    original_y_range = current_y_range

                    if self.control_panel:
                        self.control_panel.current_date_edit.setText(new_current_date)

                        if increment_x_limits and original_x_range:
                            # Calculate exact time difference to maintain zoom window size
                            x_min = datetime.fromisoformat(original_x_range[0].split(".")[0])
                            x_max = datetime.fromisoformat(original_x_range[1].split(".")[0])
                            window_size = x_max - x_min
                            
                            # Increment both limits by the same amount
                            new_x_min = x_min + timedelta(minutes=increment_minutes)
                            new_x_max = new_x_min + window_size
                            
                            # Format new limits
                            new_xlim_min = new_x_min.strftime("%Y-%m-%d %H:%M")
                            new_xlim_max = new_x_max.strftime("%Y-%m-%d %H:%M")
                            
                            # Update control panel
                            self.control_panel.xlim_min_edit.setText(new_xlim_min)
                            self.control_panel.xlim_max_edit.setText(new_xlim_max)
                            
                            # Use these new limits for the plot
                            current_x_range = [new_xlim_min, new_xlim_max]

                    self.current_date = new_current_date

                    # Load and process data
                    df = load_data(file_path, start_date, end_date)
                    if df is None or df.empty:
                        print(f"No data loaded from {file_path} for {start_date} to {end_date}")
                        return

                    df['Signal'] = find_peaks_and_valleys(df_window=df[['Time', 'Close']], 
                                                        distance=5, prominence=0.1)
                    min_value = df['Close'].min()
                    max_value = df['Close'].max()

                    # Update plot
                    self.fig.data = []
                    self.fig = plot_with_peaks(df, fig=self.fig, plotData=True, 
                                            plotMA=False, plotPeaks=False, figShow=False)
                    self.fig.add_scatter(x=[self.current_date, self.current_date], 
                                        y=[min_value, max_value],
                                        mode='lines', line=dict(color='orange', width=1.5))

                    # Load detailed data
                    df = load_data(file_path, start_date, self.current_date)
                    if df is None or df.empty:
                        print(f"No data loaded from {file_path} for {start_date} to {self.current_date}")
                        return

                    df, _, _, _ = add_features(df)
                    self.df = df.copy()
                    self.fig = plot_with_peaks(df, fig=self.fig, plotData=False, 
                                            plotMA=True, plotPeaks=True, figShow=False)

                    # Apply the original or updated zoom state
                    if original_x_range or current_x_range:
                        self.fig.update_xaxes(range=current_x_range if increment_x_limits else original_x_range)
                    if original_y_range:
                        self.fig.update_yaxes(range=original_y_range)

                    self.update_plotly_canvas()

                    if auto_trade:
                        new_data_point = self.df[self.df['Time'] == current_datetime]
                        if not new_data_point.empty:
                            df_window = self.df.tail(50).copy().reset_index(drop=True)
                            self.trade_controller.auto_trade(df_window, current_datetime)

                except Exception as e:
                    print(f"Error in increment plot callback: {e}")

            # Get current precise zoom state
            script = """
            (function() {
                var plot = document.getElementById('plot');
                if (!plot || !plot.layout) return null;
                return JSON.stringify({
                    xRange: plot.layout.xaxis.range,
                    yRange: plot.layout.yaxis.range
                });
            })();
            """
            self.page().runJavaScript(script, handle_current_ranges)

        except Exception as e:
            print(f"Error in increment_plot: {e}")
            return False

        return False
    
    def update_plot_size(self) -> None:
        """Update the figure size to match the QWebEngineView size."""
        self.resize(1200, 800)
        try:
            if self.fig:
                self.fig.update_layout(
                    width=self.width()+1,
                    height=self.height()+1
                )
        except Exception as e:
            print(f"Error updating plot size: {e}")
            
    def set_limits(self, x_limits: Tuple[str, str] = None, y_limits: Tuple[str, str] = None) -> None:
        """
        Set the x and y limits of the plot.

        Args:
            x_limits (Tuple[str, str]): The x-axis limits (min, max).
            y_limits (Tuple[str, str]): The y-axis limits (min, max).
        """
        try:
            if self.fig:
                if x_limits:
                    self.fig.update_xaxes(range=x_limits)
                if y_limits:
                    self.fig.update_yaxes(range=y_limits)
                self.update_plotly_canvas()
        except Exception as e:
            print(f"Error setting limits: {e}")


    def set_limits_from_figure(self) -> None:
        """Set the zoomed x and y limits from the Plotly figure asynchronously."""
        script = """
        (function() {
            var xRange = null;
            var yRange = null;
            var plotElement = document.querySelector('[id="plot"]');
            if (window.Plotly && Plotly.Plots && plotElement) {
                xRange = plotElement.layout.xaxis.range;
                yRange = plotElement.layout.yaxis.range;
            }
            return JSON.stringify({ xRange: xRange, yRange: yRange });
        })();
        """

        def handle_limits(result: str) -> None:
            try:
                ranges = json.loads(result)
                x_range = ranges.get("xRange", None)
                y_range = ranges.get("yRange", None)

                if x_range and y_range:
                    x_min = datetime.fromisoformat(x_range[0].split(".")[0]).strftime("%Y-%m-%d %H:%M")
                    x_max = datetime.fromisoformat(x_range[1].split(".")[0]).strftime("%Y-%m-%d %H:%M")
                    self.control_panel.xlim_min_edit.setText(x_min)
                    self.control_panel.xlim_max_edit.setText(x_max)
                    self.control_panel.ylim_min_edit.setText(f"{y_range[0]:.3f}")
                    self.control_panel.ylim_max_edit.setText(f"{y_range[1]:.3f}")
                    self.set_limits(x_range, y_range)
                else:
                    #print("No zoomed limits available.")
                    pass
            except Exception as e:
                pass
                # print(f"Error processing limits: {e}")

        try:
            self.page().runJavaScript(script, handle_limits)
        except Exception as e:
            pass
            #print(f"Error executing JavaScript to get limits: {e}")

    def _generate_html_with_plotly(self, fig: Optional[go.Figure] = None, 
                               plot_id: str = "plot", 
                               server_url: str = "http://localhost:8000") -> str:
        """
        Generate HTML string with Plotly JavaScript for dynamic plot rendering.

        Args:
            fig (Optional[go.Figure]): The Plotly figure to render, defaults to self.fig.
            plot_id (str): The ID of the plot div.
            server_url (str): The URL of the local HTTP server serving Plotly JS.

        Returns:
            str: The generated HTML content.
        """
        try:
            plotly_script = f'<script src="{server_url}/plotly-3.0.1.min.js"></script>'
            json_data = to_json(fig) if fig else '{"data": [], "layout": {}}'
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                {plotly_script}
                <style>
                    html, body, #container {{
                        width: 100%;
                        height: 100%;
                        margin: 0;
                        padding: 0;
                        overflow: hidden;
                    }}
                    #{plot_id} {{
                        width: 100%;
                        height: 100%;
                    }}
                </style>
            </head>
            <body>
                <div id="container">
                    <div id="{plot_id}"></div>
                </div>
                <script>
                    window.ResultsPlotting = window.ResultsPlotting || {{}};
                    document.addEventListener("DOMContentLoaded", function() {{
                        var fig = {json_data};
                        var graphDiv = document.getElementById('{plot_id}');
                        Plotly.newPlot(graphDiv, fig.data, fig.layout);
                        window.plotLoaded = true;
                        window.graph3d = graphDiv;
                        graphDiv.on('plotly_relayout', function(eventData) {{
                            if (eventData["scene.camera"]) {{
                                window.currentCamera = eventData["scene.camera"];
                            }}
                        }});
                        window.ResultsPlotting.updatePlot = function (newData) {{
                            if (window.plotLoaded) {{
                                if (window.currentCamera) {{
                                    newData.layout.scene.camera = window.currentCamera;
                                }}
                                Plotly.react(graphDiv, newData.data, newData.layout);
                            }}
                        }};
                        window.zoomToFit = function () {{
                            if (window.graph3d) {{
                                Plotly.relayout(window.graph3d, {{
                                    'scene.xaxis.autorange': true,
                                    'scene.yaxis.autorange': true,
                                    'scene.zaxis.autorange': true
                                }});
                            }}
                        }};
                        window.resizePlot = function() {{
                            if (window.graph3d) {{
                                Plotly.relayout(window.graph3d, {{ autosize: true }});
                            }}
                        }};
                        window.addEventListener("resize", window.resizePlot);
                    }});
                </script>
            </body>
            </html>
            """
            return html_content
        except Exception as e:
            print(f"Error generating HTML with Plotly: {e}")
            return ""

    def update_plotly_canvas(self, fig: Optional[go.Figure] = None) -> None:
        """
        Update the Plotly canvas with the current figure, preserving camera view.

        Args:
            fig (Optional[go.Figure]): The Plotly figure to update, defaults to self.fig.
        """
        try:
            fig = fig or self.fig
            if not fig:
                raise ValueError("No figure provided for canvas update.")
            if not hasattr(self, "initialized") or not self.initialized:
                html_content = self._generate_html_with_plotly(fig)
                self.setHtml(html_content)
                self.initialized = True
            else:
                capture_camera_script = """
                    (function() {
                        return window.currentCamera ? JSON.stringify(window.currentCamera) : null;
                    })();
                """

                def apply_update(camera_data: str) -> None:
                    try:
                        if camera_data and camera_data != "null":
                            camera_json = json.loads(camera_data)
                            fig.update_layout(scene=dict(camera=camera_json))
                        json_data_with_camera = to_json(fig)
                        update_script = f"""
                        setTimeout(function() {{
                            if (typeof window.ResultsPlotting.updatePlot === 'function') {{
                                window.ResultsPlotting.updatePlot({json_data_with_camera});
                            }}
                        }}, 0);
                        """
                        self.page().runJavaScript(update_script)
                    except Exception as e:
                        print(f"Error updating Plotly canvas: {e}")

                self.page().runJavaScript(capture_camera_script, apply_update)
        except Exception as e:
            print(f"Error in update_plotly_canvas: {e}")

    