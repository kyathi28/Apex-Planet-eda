# ============================================================
#  PHASE 4 — Multivariate Analysis & Correlation
#  Scatter plots · Heatmaps · Pair plots · Correlation matrix
#  Paste each CELL separately in Colab and run one by one
# ============================================================


# ────────────────────────────────────────────────────────────
# CELL 1 — Install seaborn & import all libraries
# ────────────────────────────────────────────────────────────
!pip install seaborn --quiet

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# Set a clean visual style for all charts
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 130

conn = sqlite3.connect("ecommerce.db")
print("✅ Libraries loaded. Connected to ecommerce.db.")


# ────────────────────────────────────────────────────────────
# CELL 2 — Build the master analysis dataframe
#           (joins all 4 tables into one flat table)
# ────────────────────────────────────────────────────────────

sql_master = """
SELECT
    c.customer_id,
    c.age,
    c.city,
    c.gender,
    p.category,
    p.price,
    p.cost_price,
    ROUND(p.price - p.cost_price, 2)             AS profit_per_unit,
    ROUND((p.price - p.cost_price)*100.0/p.price,2) AS margin_pct,
    oi.quantity,
    ROUND(oi.quantity * oi.unit_price, 2)         AS line_revenue,
    o.status,
    strftime('%m', o.order_date)                  AS order_month
FROM customers c
JOIN orders      o   ON c.customer_id = o.customer_id
JOIN order_items oi  ON o.order_id    = oi.order_id
JOIN products    p   ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
"""

df = pd.read_sql(sql_master, conn)

# Add age groups for grouping later
df["age_group"] = pd.cut(df["age"],
                          bins=[17, 25, 35, 45, 55, 100],
                          labels=["18-25","26-35","36-45","46-55","56+"])

print(f"✅ Master dataframe created: {df.shape[0]} rows × {df.shape[1]} columns")
print("\nColumn list:")
print(df.dtypes)
print("\nFirst 3 rows:")
print(df.head(3).to_string(index=False))


# ────────────────────────────────────────────────────────────
# CELL 3 — SCATTER PLOT 1
#           Age vs Line Revenue — do older customers spend more?
# ────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 6))

# Color-code each point by product category
categories = df["category"].unique()
colors = sns.color_palette("tab10", len(categories))
color_map = dict(zip(categories, colors))

for cat in categories:
    subset = df[df["category"] == cat]
    ax.scatter(subset["age"], subset["line_revenue"],
               alpha=0.4, s=25, label=cat,
               color=color_map[cat])

# Add a linear trend line
z = np.polyfit(df["age"], df["line_revenue"], 1)
p = np.poly1d(z)
x_line = np.linspace(df["age"].min(), df["age"].max(), 100)
ax.plot(x_line, p(x_line), color="red", linewidth=2,
        linestyle="--", label="Trend line")

ax.set_title("Age vs Purchase Revenue — Coloured by Category",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Customer Age (years)")
ax.set_ylabel("Line Revenue (₹)")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("scatter_age_vs_revenue.png", dpi=150, bbox_inches="tight")
plt.show()

# Pearson correlation
corr_age_rev = df["age"].corr(df["line_revenue"])
print(f"\n📌 Pearson Correlation (age vs revenue): {corr_age_rev:.3f}")
if abs(corr_age_rev) < 0.2:
    print("   → Weak/no correlation: age alone does not predict spend amount.")
elif abs(corr_age_rev) < 0.5:
    print("   → Moderate correlation: some relationship between age and spend.")
else:
    print("   → Strong correlation: age is a good predictor of spend.")
print("✅ Saved: scatter_age_vs_revenue.png")


# ────────────────────────────────────────────────────────────
# CELL 4 — SCATTER PLOT 2
#           Product Price vs Profit Margin
# ────────────────────────────────────────────────────────────

# Aggregate to product level (one point per product)
product_df = pd.read_sql("""
    SELECT name, category, price, cost_price,
           ROUND((price - cost_price)*100.0/price, 2) AS margin_pct
    FROM products
""", conn)

fig, ax = plt.subplots(figsize=(9, 6))

for cat in product_df["category"].unique():
    sub = product_df[product_df["category"] == cat]
    ax.scatter(sub["price"], sub["margin_pct"],
               s=80, alpha=0.8, label=cat)

z2 = np.polyfit(product_df["price"], product_df["margin_pct"], 1)
p2 = np.poly1d(z2)
x2 = np.linspace(product_df["price"].min(), product_df["price"].max(), 100)
ax.plot(x2, p2(x2), color="red", linestyle="--", linewidth=1.8, label="Trend")

ax.set_title("Product Price vs Profit Margin %",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Selling Price (₹)")
ax.set_ylabel("Profit Margin (%)")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("scatter_price_vs_margin.png", dpi=150, bbox_inches="tight")
plt.show()

corr_pm = product_df["price"].corr(product_df["margin_pct"])
print(f"\n📌 Pearson Correlation (price vs margin): {corr_pm:.3f}")
print("   Higher-priced products don't necessarily have higher margins —")
print("   margin depends on cost structure, not just selling price.")
print("✅ Saved: scatter_price_vs_margin.png")


# ────────────────────────────────────────────────────────────
# CELL 5 — SCATTER PLOT 3
#           Quantity Ordered vs Line Revenue
# ────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 6))

scatter = ax.scatter(df["quantity"], df["line_revenue"],
                     c=df["price"], cmap="YlOrRd",
                     alpha=0.5, s=30)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Unit Price (₹)", fontsize=10)

ax.set_title("Quantity Ordered vs Line Revenue\n(colour = unit price)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Quantity Ordered")
ax.set_ylabel("Line Revenue (₹)")
plt.tight_layout()
plt.savefig("scatter_qty_vs_revenue.png", dpi=150)
plt.show()

corr_qr = df["quantity"].corr(df["line_revenue"])
print(f"\n📌 Pearson Correlation (quantity vs revenue): {corr_qr:.3f}")
print("   Strong positive correlation expected — more units = more revenue.")
print("   Dark red dots = high-priced items generate more revenue even at low qty.")
print("✅ Saved: scatter_qty_vs_revenue.png")


# ────────────────────────────────────────────────────────────
# CELL 6 — CORRELATION HEATMAP
#           Shows correlation between ALL numeric variables
# ────────────────────────────────────────────────────────────

numeric_cols = ["age", "price", "cost_price", "profit_per_unit",
                "margin_pct", "quantity", "line_revenue"]
corr_matrix = df[numeric_cols].corr().round(2)

print("Correlation Matrix:")
print(corr_matrix)

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))   # hide upper triangle

sns.heatmap(corr_matrix,
            mask=mask,
            annot=True,
            fmt=".2f",
            cmap="RdYlGn",
            center=0,
            vmin=-1, vmax=1,
            linewidths=0.5,
            linecolor="white",
            square=True,
            ax=ax)

ax.set_title("Correlation Heatmap — All Numerical Variables",
             fontsize=13, fontweight="bold", pad=14)
plt.tight_layout()
plt.savefig("heatmap_correlation.png", dpi=150)
plt.show()

print("\n📌 HOW TO READ THIS HEATMAP:")
print("   +1.0 (dark green) = perfect positive correlation")
print("    0.0 (yellow)     = no relationship")
print("   -1.0 (dark red)   = perfect negative correlation")
print("\n   Key findings to report:")
for col1 in numeric_cols:
    for col2 in numeric_cols:
        if col1 < col2:
            val = corr_matrix.loc[col1, col2]
            if abs(val) >= 0.6:
                direction = "positive" if val > 0 else "negative"
                print(f"   → {col1} vs {col2}: {val:.2f} ({direction} — report this!)")
print("✅ Saved: heatmap_correlation.png")


# ────────────────────────────────────────────────────────────
# CELL 7 — PAIR PLOT
#           Grid of scatter + distribution plots for key variables
# ────────────────────────────────────────────────────────────

pair_df = df[["age", "price", "quantity", "line_revenue", "category"]].copy()

# Keep top 4 categories for readability
top4 = df["category"].value_counts().head(4).index.tolist()
pair_df = pair_df[pair_df["category"].isin(top4)]

g = sns.pairplot(pair_df,
                 hue="category",
                 vars=["age", "price", "quantity", "line_revenue"],
                 diag_kind="kde",
                 plot_kws={"alpha": 0.4, "s": 20},
                 height=2.4)

g.figure.suptitle("Pair Plot — Age, Price, Quantity, Revenue by Category",
                   y=1.02, fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("pairplot_key_variables.png", dpi=130, bbox_inches="tight")
plt.show()

print("\n📌 HOW TO READ A PAIR PLOT:")
print("   • Diagonal = distribution of each variable (KDE curve)")
print("   • Off-diagonal = scatter plot between two variables")
print("   • Each colour = one product category")
print("   • Clusters of one colour = that category behaves differently")
print("✅ Saved: pairplot_key_variables.png")


# ────────────────────────────────────────────────────────────
# CELL 8 — HEATMAP 2: Revenue by City × Category
#           (shows which city buys which category most)
# ────────────────────────────────────────────────────────────

pivot = df.groupby(["city", "category"])["line_revenue"].sum().unstack(fill_value=0)
pivot = pivot.round(0)

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(pivot,
            annot=True,
            fmt=".0f",
            cmap="YlGnBu",
            linewidths=0.4,
            linecolor="white",
            ax=ax)

ax.set_title("Total Revenue — City × Product Category",
             fontsize=13, fontweight="bold", pad=14)
ax.set_xlabel("Product Category")
ax.set_ylabel("City")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("heatmap_city_category.png", dpi=150)
plt.show()

print("\n📌 INTERPRETATION:")
print("   Dark blue cells = high revenue combination.")
print("   Light cells = low revenue — possible growth opportunity.")
top_combo = pivot.stack().idxmax()
print(f"   Highest revenue combo: {top_combo[0]} × {top_combo[1]}")
print("   Use this to plan city-specific product promotions.")
print("✅ Saved: heatmap_city_category.png")


# ────────────────────────────────────────────────────────────
# CELL 9 — BOX PLOT: Revenue distribution by age group
#           (shows spread and outliers per group)
# ────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x="age_group", y="line_revenue",
            palette="Set2", ax=ax, order=["18-25","26-35","36-45","46-55","56+"])

ax.set_title("Revenue Distribution by Age Group (Box Plot)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Age Group")
ax.set_ylabel("Line Revenue (₹)")
plt.tight_layout()
plt.savefig("boxplot_revenue_age_group.png", dpi=150)
plt.show()

print("\n📌 HOW TO READ A BOX PLOT:")
print("   • Box centre line = median revenue for that age group")
print("   • Box edges      = 25th and 75th percentile (middle 50% of data)")
print("   • Whiskers       = range excluding outliers")
print("   • Dots beyond whiskers = outliers (unusually high spenders)")
print("\n   Which age group has the widest box? That group has the")
print("   most variation in spending — both low and high spenders.")
print("✅ Saved: boxplot_revenue_age_group.png")


# ────────────────────────────────────────────────────────────
# CELL 10 — FINAL SUMMARY
# ────────────────────────────────────────────────────────────

conn.close()

print("\n" + "=" * 65)
print("  🎉 PHASE 4 COMPLETE — Multivariate Analysis Done!")
print("=" * 65)
files = [
    ("scatter_age_vs_revenue.png",      "Scatter — Age vs Revenue (coloured by category)"),
    ("scatter_price_vs_margin.png",     "Scatter — Price vs Profit Margin"),
    ("scatter_qty_vs_revenue.png",      "Scatter — Quantity vs Revenue (coloured by price)"),
    ("heatmap_correlation.png",         "Heatmap — Correlation matrix of all numerics"),
    ("pairplot_key_variables.png",      "Pair plot — Age, Price, Qty, Revenue by Category"),
    ("heatmap_city_category.png",       "Heatmap — Revenue by City × Category"),
    ("boxplot_revenue_age_group.png",   "Box plot — Revenue spread by Age Group"),
]
for fname, desc in files:
    print(f"  📊 {fname}")
    print(f"     {desc}")

print("\n  Concepts covered in Phase 4:")
print("  → Pearson correlation coefficient")
print("  → Scatter plots with trend lines")
print("  → Correlation heatmap (triangular)")
print("  → Pair plots (grid of scatter + KDE)")
print("  → Pivot heatmap (City × Category)")
print("  → Box plots with outlier detection")
