[README.md](https://github.com/user-attachments/files/28479793/README.md)
# OSRS GE Flipper v5

Simplified bilingual OSRS Grand Exchange flipping dashboard.

## What changed in v5

- Main table is now much simpler and fits better on screen.
- Full detailed table moved to a separate tab.
- Added Safe mode / lower-risk mode.
- Added risk label and risk score.
- Added stricter filters for stale trades, low 5m volume and confidence.
- Kept LT / EN language, K/M/B formatting, auto-refresh and price charts.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload/replace these files in GitHub:

- `app.py`
- `requirements.txt`
- `README.md`

Then wait for Streamlit to redeploy or reboot the app.
