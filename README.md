# OSRS GE Flipper

Viešam deploy paruošta Streamlit programa, kuri rodo OSRS Grand Exchange flipping kandidatus.

## Paleisti lokaliai

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy į Streamlit Community Cloud

1. Susikurk GitHub accountą.
2. Sukurk naują public repository, pvz. `osrs-ge-flipper`.
3. Įkelk visus šio aplanko failus į repo.
4. Eik į Streamlit Community Cloud.
5. Spausk New app.
6. Pasirink GitHub repo.
7. Main file path: `app.py`.
8. Deploy.

## Failai

- `app.py` - pagrindinė web programa
- `requirements.txt` - Python bibliotekos hostingui
- `.streamlit/config.toml` - Streamlit UI nustatymai
- `.gitignore` - failai, kurių nereikia kelti į GitHub

## Pastaba

Tai yra flipping scanner, ne garantuotas pelnas. Kainos ir marginai OSRS GE gali greitai pasikeisti.
