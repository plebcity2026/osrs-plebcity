[README.md](https://github.com/user-attachments/files/28479326/README.md)
# OSRS GE Flipper Dashboard v4

Streamlit web app for Old School RuneScape Grand Exchange flipping.

## Features

- LT / EN language switch
- RuneScape-style number formatting: 100K, 1.5M, 2.5B
- Auto refresh
- Manual refresh
- GE tax calculation
- Suggested buy near / sell near prices based on latest low/high trades
- Bought / sold volume columns for 5m and 1h
- Confidence score based on volume, recent trade freshness, ROI, profit after tax and 5m margin
- Green / red price movement colors
- Price trend charts with 24h, 7d, 30d and 1y views
- CSV export

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload these files to GitHub and deploy with Streamlit Community Cloud:

- app.py
- requirements.txt
- README.md
- .streamlit/config.toml

Main file path:

```text
app.py
```
