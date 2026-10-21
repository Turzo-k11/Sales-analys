# Power BI Upgrade – Supermart Sales Analysis

## What's in this package
- `SupermartGrocerySales_PowerBI_Clean.csv`: 9,994 original rows with consistent ISO dates (YYYY-MM-DD) and added Year/Month/Year Month sorting helpers. Original ID, Sales, Profit, Discount and every other source column retained.
- `DAX_Measures.txt`: 11 ready-to-add Power BI DAX measures.
- `DAX_Calendar.txt`: Power BI calendar table and relationship instructions.
- `Supermart_Theme.json`: importable report colors and typography.
- `Dashboard_Design_Preview.png`: **visual concept**, not an updated screenshot or an edited PBIX.

## Steps in Power BI Desktop
1. Save a copy of your original `projekt.pbix` before any changes.
2. In **Home > Transform data**, inspect the `SupermartGrocerySales` query and its source. The original PBIX may have embedded/imported data. To refresh using this cleaned CSV, edit the query's Source step to point at `SupermartGrocerySales_PowerBI_Clean.csv`, or load the CSV as a new table and then update your visuals if necessary. Do not inadvertently create duplicate fact tables.
3. Set `Order Date` to Date (not Text), Sales/Profit to decimal/whole numeric as needed and Discount to decimal percentage.
4. Create the Calendar table by pasting `DAX_Calendar.txt`'s formula into **Modeling > New table**. Create the indicated relationship, mark it as a date table and set sort-by-column properties.
5. Add each measure from `DAX_Measures.txt` individually via **Modeling > New measure**. Format margins, discounts and YoY as percentages. Avoid SUM of Discount as a KPI.
6. Use **View > Themes > Browse for themes** to import `Supermart_Theme.json`.
7. Rename the three existing report pages:
   - `Overview test` -> `Executive Overview`
   - `Sales` -> `Product & Region Performance`
   - `Customer ` -> `Customer & Discount Analysis`
8. Rebuild pages following the proposed layouts below. Check totals against overview: Sales=14,956,982, Profit=3,747,121.20, Orders=9,994, Margin=25.05%.
9. Validate Date slicers, Category and Region slicers and cross-filter behaviour before publishing.

## Suggested page layouts
### Page 1: Executive Overview
**Top KPI cards**: Total Sales / Total Profit / Profit Margin % / Total Orders / Average Order Value.
**Charts**: line chart Calendar[Year Month] vs Total Sales; bar chart Category vs Total Sales; bar chart Region vs Total Profit; monthly Profit and Sales comparison.
**Slicers**: Calendar[Year], Region. Keep clean consistent number formatting.

### Page 2: Product & Region Performance
**Charts**: Categories vs Sales and Profit; Sub Category sorted by Total Sales (Top 10); Region x Category matrix with Sales, Profit, Profit Margin %; Region comparisons.
**Slicers**: Year, Region, Category. Highlight high sales + low margin categories for actionable insight.

### Page 3: Customer & Discount Analysis
**Cards**: Total Customers / Average Order Value / Average Discount %.
**Charts**: Top 10 Customer Name by Total Sales; Discount bands vs Profit Margin %; scatter plot Discount vs Profit, customer/category context.
**Important**: Discount vs Profit correlation in this data is approximately zero; don't claim a causal impact from the scatter plot alone. Customer Name is not a guaranteed stable customer ID.

## Data-model caveats
- This source file has 9,994 rows and 9,994 distinct Order IDs. Record count equals order count here, but the two metrics mean different things in general.
- The CSV has **no Quantity column**; do not label row counts as 'number of products sold'.
- Source date formats are mixed: hyphen values DD-MM-YYYY and slash values MM/DD/YYYY. This prepared CSV resolves both into YYYY-MM-DD.
- `Profit / Sales` is aggregated profit margin, not the average of row-wise margins.
- `Sales YoY %` needs a continuous Date table and will return blank when no comparable prior year exists.
- Dataset provides region names, not geographic coordinates; don't make unsupported precise location maps.

## Reproducibility check
Compare original and prepared CSV: same 9,994 rows, Sales total 14,956,982 and Profit total 3,747,121.20. No missing or invalid dates.

## Limitations
This package is intended for **manual import into Power BI Desktop**. The original `projekt.pbix` is not modified in this archive because securely editing its imported semantic model and report visuals without Power BI Desktop is not reliably supported here.
