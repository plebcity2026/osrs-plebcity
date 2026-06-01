[README.md](https://github.com/user-attachments/files/28480150/README.md)
# OSRS GE Flipper v6

Streamlit web app for Old School RuneScape Grand Exchange flipping.

## Features

- LT / EN language switch
- Simple recommended flips table
- Full advanced table
- Market Pulse tab:
  - Most bought 1h
  - Most sold 1h
  - Strongest buy pressure
  - Strongest sell pressure
  - AI-style rule-based notes
- Confidence and risk labels
- 5m / 1h volume filters
- Price chart with green/red trend line
- Auto refresh
- RuneScape style number formatting: K / M / B

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload these files to GitHub and deploy on Streamlit Community Cloud:

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
