[README.md](https://github.com/user-attachments/files/28478957/README.md)
# OSRS GE Flipper

Streamlit web app for OSRS Grand Exchange flipping candidates.

Features:
- Lithuanian / English language selector
- RuneScape-style K / M / B number formatting
- Auto refresh and manual refresh
- GE tax, margin, ROI, volume and bankroll profit
- Green / red styling for rising and falling prices
- Item price trend chart using OSRS Wiki timeseries data

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload these files to GitHub and deploy with Streamlit Cloud.
Main file path: `app.py`.
