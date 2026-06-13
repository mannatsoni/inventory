# Inventory Wastage Dashboard

A Streamlit app to explore weekly opening stock, purchases, consumption, and
closing stock for any inventory item across 2025 (53 weekly data points),
in order to assess whether purchasing is structurally outpacing consumption
(a wastage / over-ordering signal).

## Setup

1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`.

## Data

The app reads `consolidated_2025_with_metrics.csv`, which must sit in the
same folder as `app.py`. This file is the output of the consolidation
pipeline (`build_consolidated.py`) and contains one row per item per week,
with columns:

- `item`, `supplier`, `week`, `week_start`, `week_end`
- `opening_stock`, `total_purchased`, `closing_stock`, `consumption`
- `expected_closing`, `balance_diff` (data-quality flag)
- `purchase_surplus`, `stock_change`, `cumulative_surplus` (wastage metrics)

To refresh the data with a new master CSV, re-run:
```
python build_consolidated.py
```
and replace `consolidated_2025_with_metrics.csv` in this folder.

## Deploying to Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io, connect the repo, and point it at `app.py`.
3. Streamlit Cloud will install `requirements.txt` automatically.

## Features

- **Item selector** (with optional supplier filter) in the sidebar.
- **KPI cards**: total purchased, total consumed, net surplus, surplus % of consumption.
- **Main chart**: weekly purchased/consumed bars overlaid with opening/closing stock lines.
- **Cumulative surplus chart**: running drift over the year — a rising line
  flags potential over-ordering, a falling line flags stock depletion.
- **Data quality expander**: flags weeks where opening + purchased − consumed
  doesn't match closing stock (likely entry errors).
- **Raw data table** for the selected item.
