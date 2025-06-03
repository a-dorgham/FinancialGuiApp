# FinancialGuiApp

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![Plotly](https://img.shields.io/badge/Plotting-Plotly-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**FinancialGuiApp** is a cross-platform, Python-based graphical user interface (GUI) designed for analyzing and visualizing financial time-series data. Developed with PyQt6 and Plotly, it offers an interactive platform for traders, analysts, and researchers to import, process, and explore financial datasets such as stock and forex prices. The app features real-time candlestick charting, technical indicators (RSI, MACD, Stochastic Oscillator), peak/valley detection, and trading simulations.

---

## 🔧 Features

- 🖥️ **User-Friendly GUI**: Built with PyQt6 for seamless interaction.
- 📊 **Dynamic Visualization**: Real-time candlestick charts with **Plotly**.
- 📈 **Technical Analysis Tools**: Includes Moving Averages, RSI, MACD, and Stochastic Oscillator.
- 🔍 **Signal Detection**: Identifies peaks and valleys as buy/sell signals.
- 🔄 **Auto-Increment**: Simulates live data flow with configurable intervals.
- 💼 **Trade Simulation**: Manual and automatic trade execution (Buy/Sell/Close).
- 💾 **Configuration Management**: Persistent file path tracking via `config.json`.
- 📤 **Export to Excel**: Save trade history for further analysis.
- 🌐 **Embedded HTTP Server**: Hosts Plotly JS locally for visualization.

---

## 📁 Project Structure

```text
financial_gui_app/
├── .gitignore
├── LICENSE
├── README.md
├── main.py
├── requirements.txt
├── setup.py
├── docs/
├── src/
│   ├── main.py
│   ├── assets/
│   │   ├── images/
│   │   └── styles/
│   │       └── app.qss
│   ├── core/
│   │   ├── controllers.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── utils.py
│   ├── data/
│   │   ├── GBP_USD_M15.pkl
│   │   ├── config.json
│   │   ├── config_manager.py
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── dialogs/
│   │   │   └── settings_dialog.py
│   │   └── widgets/
│   │       ├── control_panel.py
│   │       ├── message_box.py
│   │       ├── plot_view.py
│   └── utils/
│       ├── http_server_thread.py
│       ├── output_stream.py
│       ├── plotly-3.0.1.min.js
└── tests/
    ├── integration/
    │   └── test_gui_interaction.py
    └── unit/
        ├── test_controllers.py
        └── test_models.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Recommended: virtual environment
- Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Dependencies include**:
- PyQt6
- pandas
- numpy
- plotly
- scipy
- scikit-learn
- openpyxl

---

## ▶️ Running the App

```bash
python main.py
```

The GUI will open with controls for importing data, visualizing charts, and simulating trades.

---

## 📚 Usage

1. **Import Data**: Load `.pkl` files from `src/data/` with `Time` and `Close` columns.
2. **Set Time Range**: Choose start, end, and current dates with an increment value (e.g., 15 minutes).
3. **Plot and Increment**: Click **Increment/Plot** or enable **Auto Increment** to stream data.
4. **Trade Simulation**: Use **Buy**, **Sell**, or **Close Trade**, or toggle **Auto Trade**.
5. **Export**: Save trade data as Excel for offline analysis.
6. **Visual Feedback**: The plot shows technical indicators, peaks, valleys, and trade positions.

---

## 🛠 Developer Notes

### Key Files

- `main.py`: Entry point, initializes the main window and server.
- `control_panel.py`: Manages user input and simulation controls.
- `plot_view.py`: Embeds Plotly chart with data overlays.
- `controllers.py`: Handles trading logic and simulation.
- `config_manager.py`: Reads/writes configuration settings.
- `http_server_thread.py`: Local server for Plotly JS.

### Indicators

- MA (50-period)
- RSI (14-period)
- MACD (12, 26, 9)
- Stochastic (%K, %D)
- Peak/valley detection via `scipy.signal.find_peaks`

---

## 🧪 Testing

No formal test suite yet. Manual testing recommended:

- Load valid `.pkl` data
- Use time slider and increment controls
- Try manual and auto trading
- Export to Excel
- Check logs for feedback/errors

---

## 📸 Screenshots

> _Main Application View_
> _Data Import Dialog_
> _Auto Increment in Action_

(*Screenshots to be added*)

---

## 🌐 Roadmap

- Support for JSON/SQL input
- More technical indicators
- Real-time streaming (WebSocket)
- Smarter trading logic
- Optimized rendering for large datasets
- Unit testing framework

---

## 🤝 Contributing

Contributions are welcome!

```bash
git clone https://github.com/your-repo/FinancialGuiApp.git
cd FinancialGuiApp
git checkout -b feature-name
# Make changes
git commit -m "Add feature"
git push origin feature-name
```

Then open a pull request.

---

## 📜 License

MIT License

---


## 📬 Contact

For bug reports, feature requests, or collaboration:

- **GitHub Issues**: [FinancialApp Issues](https://github.com/a-dorgham/FEAnalysisApp/issues)
- **Email**: a.k.y.dorgham@gmail.com
- **Connect**: [LinkedIn](https://www.linkedin.com/in/abdeldorgham) | [GoogleScholar](https://scholar.google.com/citations?user=EOwjslcAAAAJ&hl=en)  | [ResearchGate](https://www.researchgate.net/profile/Abdel-Dorgham-2) | [ORCiD](https://orcid.org/0000-0001-9119-5111)
