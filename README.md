# Consumer Complaint Dashboard

This repo contains:
- **enhanced_consumer_dashboard.html** – interactive Plotly dashboard
- **build_dashboard.py** – script to regenerate the dashboard from the original Excel source

## Rebuild the Dashboard
```bash
pip install pandas plotly calamine
python build_dashboard.py "Excel 2 - mod_Consumer complaint analysis.xlsx"
```
The generated HTML is self-contained, so you can push it to GitHub Pages for an instant live view.

## Data
The file `Excel 2 - mod_Consumer complaint analysis.xlsx` must be present in the same directory.
