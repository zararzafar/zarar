# IND320 – Data to decision (project work)

Project work for IND320 at NMBU, autumn 2026.

- **Streamlit app:** https://zarar-ind320.streamlit.app
- **Notebook:** [`IND320_part1.ipynb`](IND320_part1.ipynb)

## Part 1 – Dashboard basics
Weekly reservoir statistics for Norway (`data/reservoirs.csv`, from the course repository
`khliland/IND320`, folder `D2Dbook/data`).

| File | Purpose |
|---|---|
| `Home.py` | Front page with sidebar navigation |
| `pages/2_Data_table.py` | Table with one row per column and a `LineChartColumn` of the first month |
| `pages/3_Plot.py` | Plot with column selection (`st.selectbox`) and month range (`st.select_slider`) |
| `pages/4_About.py` | Placeholder page |
| `data_loader.py` | Shared, cached (`@st.cache_data`) loading and cleaning of the CSV |
| `IND320_part1.ipynb` | Jupyter Notebook with data reading, renaming and plots |

## Run locally
```bash
pip install -r requirements.txt
streamlit run Home.py
```
