# Deploy instrukcija lietuviškai

## 1. GitHub

- Nueik į GitHub.
- Spausk `New repository`.
- Pavadinimas: `osrs-ge-flipper`.
- Pasirink `Public`.
- Spausk `Create repository`.

## 2. Įkelk failus

Į GitHub repo įkelk:

- `app.py`
- `requirements.txt`
- `README.md`
- `.streamlit/config.toml`
- `.gitignore`

GitHub puslapyje gali spausti `Add file` -> `Upload files`.

## 3. Streamlit Cloud

- Nueik į Streamlit Community Cloud.
- Prisijunk su GitHub.
- Spausk `New app`.
- Pasirink repo `osrs-ge-flipper`.
- Branch: `main`.
- Main file path: `app.py`.
- Spausk `Deploy`.

Po deploy gausi viešą nuorodą panašią į:

```text
https://osrs-ge-flipper.streamlit.app
```

## Jeigu meta klaidą

Dažniausios problemos:

1. `requirements.txt` neįkeltas į GitHub.
2. Main file path ne `app.py`.
3. Failai įkelti į subfolderį, o ne repo root.
4. Python dependency klaida - tada patikrink Streamlit logs.

