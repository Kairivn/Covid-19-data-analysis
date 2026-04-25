# 🦠 COVID-19 India Cases Explorer

An interactive **Streamlit** dashboard for exploring COVID-19 case data across India and its states/union territories.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-ff4b4b?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **National KPIs** | Confirmed, active, recovered, deaths, recovery rate, and CFR at a glance |
| **Region Drill-Down** | Select any state/UT to see region-specific metrics and its share of national totals |
| **Daily New Cases** | Bar chart with 7-day rolling average for both cases and deaths |
| **Cumulative Trends** | Multi-line time series of all case types |
| **Regional Comparison** | Top 15 states by any metric — bar, line, or donut chart |
| **State Heatmap** | Month × state heatmap showing metric intensity over time |
| **Recovery & CFR Rates** | Side-by-side bar charts comparing recovery and fatality rates |
| **Weekly Growth Rate** | Area chart showing week-over-week growth in confirmed cases |
| **Downloadable Data** | Export the state-level summary table as CSV |

---

## 📁 Project Structure

```
COVID-19 analysis/
├── analysis.py              # Streamlit dashboard
├── covid_india_cases.csv    # Dataset (~30 K rows)
├── requirements.txt         # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**

### Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/COVID-19-India-Explorer.git
cd COVID-19-India-Explorer

# Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
streamlit run analysis.py
```

The app will open in your browser at **http://localhost:8501**.

---

## 📊 Dataset

The bundled `covid_india_cases.csv` contains daily COVID-19 figures for India, its 36 states/UTs, and the World.

| Column | Description |
|--------|-------------|
| `Date` | Reporting date (DD/MM/YYYY) |
| `Region` | India / state name / World |
| `Confirmed Cases` | Cumulative confirmed |
| `Active Cases` | Currently active |
| `Cured/Discharged` | Cumulative recoveries |
| `Death` | Cumulative deaths |

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — app framework
- **[Pandas](https://pandas.pydata.org/)** — data wrangling
- **[Plotly](https://plotly.com/python/)** — interactive charts
- **[NumPy](https://numpy.org/)** — numeric helpers

---

## 📜 License

This project is released under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/awesome-chart`)
3. Commit your changes (`git commit -m 'Add awesome chart'`)
4. Push to the branch (`git push origin feature/awesome-chart`)
5. Open a Pull Request
