# ============================================================
#  PHASE 2 — Descriptive Statistics & Univariate Analysis
#  Paste each CELL separately in Colab and run one by one
# ============================================================


# ────────────────────────────────────────────────────────────
# CELL 1 — Import libraries & reconnect to database
# ────────────────────────────────────────────────────────────
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# Connect to the database we created in Phase 1
conn = sqlite3.connect("ecommerce.db")

# Load all four tables into DataFrames
customers   = pd.read_sql("SELECT * FROM customers",   conn)
products    = pd.read_sql("SELECT * FROM products",    conn)
orders      = pd.read_sql("SELECT * FROM orders",      conn)
order_items = pd.read_sql("SELECT * FROM order_items", conn)

print("✅ Connected! Tables loaded successfully.")
print(f"   customers: {customers.shape}  | products: {products.shape}")
print(f"   orders:    {orders.shape}     | order_items: {order_items.shape}")


# ────────────────────────────────────────────────────────────
# CELL 2 — Summary statistics for NUMERICAL columns
# ────────────────────────────────────────────────────────────

print("=" * 60)
print("NUMERICAL SUMMARY — CUSTOMERS TABLE")
print("=" * 60)
print(customers[["age"]].describe().round(2))

print("\n" + "=" * 60)
print("NUMERICAL SUMMARY — PRODUCTS TABLE")
print("=" * 60)
print(products[["price", "cost_price"]].describe().round(2))

print("\n" + "=" * 60)
print("NUMERICAL SUMMARY — ORDER ITEMS TABLE")
print("=" * 60)
print(order_items[["quantity", "unit_price"]].describe().round(2))

# Compute revenue per order item and show its stats
order_items["revenue"] = order_items["quantity"] * order_items["unit_price"]
print("\n" + "=" * 60)
print("DERIVED COLUMN: revenue (quantity × unit_price)")
print("=" * 60)
print(order_items[["revenue"]].describe().round(2))

# Manual interpretation printout
print("\n📌 KEY INTERPRETATIONS:")
print(f"   Average customer age       : {customers['age'].mean():.1f} years")
print(f"   Youngest / Oldest customer : {customers['age'].min()} / {customers['age'].max()} years")
print(f"   Average product price      : ₹{products['price'].mean():.2f}")
print(f"   Cheapest / Priciest product: ₹{products['price'].min():.2f} / ₹{products['price'].max():.2f}")
print(f"   Average order quantity     : {order_items['quantity'].mean():.1f} units")
print(f"   Average revenue per item   : ₹{order_items['revenue'].mean():.2f}")


# ────────────────────────────────────────────────────────────
# CELL 3 — Summary statistics for CATEGORICAL columns
# ────────────────────────────────────────────────────────────

print("=" * 60)
print("CATEGORICAL SUMMARY — CUSTOMERS TABLE")
print("=" * 60)

print("\n📍 City distribution:")
print(customers["city"].value_counts())

print("\n👥 Gender distribution:")
print(customers["gender"].value_counts())

print("\n" + "=" * 60)
print("CATEGORICAL SUMMARY — PRODUCTS TABLE")
print("=" * 60)
print("\n🏷️ Products per category:")
print(products["category"].value_counts())

print("\n" + "=" * 60)
print("CATEGORICAL SUMMARY — ORDERS TABLE")
print("=" * 60)
print("\n📦 Order status counts:")
print(orders["status"].value_counts())
print("\n📊 Order status percentages:")
print((orders["status"].value_counts(normalize=True) * 100).round(1).astype(str) + "%")


# ────────────────────────────────────────────────────────────
# CELL 4 — HISTOGRAM: Age distribution of customers
# ────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(customers["age"], bins=15, color="#5B5EA6", edgecolor="white", linewidth=0.8)

ax.set_title("Age Distribution of Customers", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Age (years)", fontsize=12)
ax.set_ylabel("Number of Customers", fontsize=12)
ax.axvline(customers["age"].mean(), color="#E8593C", linestyle="--", linewidth=1.8,
           label=f"Mean age = {customers['age'].mean():.1f}")
ax.axvline(customers["age"].median(), color="#1D9E75", linestyle="--", linewidth=1.8,
           label=f"Median age = {customers['age'].median():.1f}")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("hist_age.png", dpi=150)
plt.show()
print("✅ Saved as hist_age.png")

# INTERPRETATION
print("\n📌 INTERPRETATION:")
print(f"   The age distribution is roughly {'uniform' if abs(customers['age'].mean() - customers['age'].median()) < 2 else 'skewed'}.")
print(f"   Most customers are between {int(customers['age'].quantile(0.25))} and {int(customers['age'].quantile(0.75))} years old (middle 50%).")
print(f"   Mean ({customers['age'].mean():.1f}) ≈ Median ({customers['age'].median():.1f}) → no strong skew.")


# ────────────────────────────────────────────────────────────
# CELL 5 — HISTOGRAM: Product price distribution
# ────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(products["price"], bins=15, color="#1D9E75", edgecolor="white", linewidth=0.8)

ax.set_title("Product Price Distribution", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Price (₹)", fontsize=12)
ax.set_ylabel("Number of Products", fontsize=12)
ax.axvline(products["price"].mean(), color="#E8593C", linestyle="--", linewidth=1.8,
           label=f"Mean = ₹{products['price'].mean():.0f}")
ax.axvline(products["price"].median(), color="#5B5EA6", linestyle="--", linewidth=1.8,
           label=f"Median = ₹{products['price'].median():.0f}")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("hist_price.png", dpi=150)
plt.show()
print("✅ Saved as hist_price.png")

print("\n📌 INTERPRETATION:")
print(f"   Wide price range: ₹{products['price'].min():.0f} to ₹{products['price'].max():.0f}")
print(f"   Mean (₹{products['price'].mean():.0f}) vs Median (₹{products['price'].median():.0f})")
if products["price"].mean() > products["price"].median():
    print("   Mean > Median → right-skewed (a few very expensive products pull the average up).")
else:
    print("   Mean ≈ Median → roughly symmetric distribution.")


# ────────────────────────────────────────────────────────────
# CELL 6 — BAR CHART: Orders by status
# ────────────────────────────────────────────────────────────

status_counts = orders["status"].value_counts()
colors = {"Completed": "#1D9E75", "Pending": "#EF9F27", "Cancelled": "#E24B4A"}
bar_colors = [colors.get(s, "#888") for s in status_counts.index]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(status_counts.index, status_counts.values, color=bar_colors,
              edgecolor="white", linewidth=0.8, width=0.5)

# Add count labels on top of each bar
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
            str(int(bar.get_height())), ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_title("Order Count by Status", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Order Status", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.set_ylim(0, status_counts.max() * 1.15)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("bar_order_status.png", dpi=150)
plt.show()
print("✅ Saved as bar_order_status.png")

print("\n📌 INTERPRETATION:")
completed_pct = (status_counts.get("Completed", 0) / len(orders) * 100)
cancelled_pct = (status_counts.get("Cancelled", 0) / len(orders) * 100)
print(f"   {completed_pct:.1f}% of orders are Completed — healthy fulfilment rate.")
print(f"   {cancelled_pct:.1f}% of orders are Cancelled — worth investigating why.")


# ────────────────────────────────────────────────────────────
# CELL 7 — BAR CHART: Customers by city
# ────────────────────────────────────────────────────────────

city_counts = customers["city"].value_counts()

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(city_counts.index, city_counts.values, color="#5B5EA6",
              edgecolor="white", linewidth=0.8)

for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
            str(int(bar.get_height())), ha="center", va="bottom", fontsize=10)

ax.set_title("Number of Customers per City", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("City", fontsize=12)
ax.set_ylabel("Number of Customers", fontsize=12)
ax.set_ylim(0, city_counts.max() * 1.15)
plt.xticks(rotation=30, ha="right")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("bar_customers_city.png", dpi=150)
plt.show()
print("✅ Saved as bar_customers_city.png")

print("\n📌 INTERPRETATION:")
print(f"   Top city: {city_counts.index[0]} with {city_counts.iloc[0]} customers.")
print(f"   Distribution is fairly even — customers spread across all 10 cities.")


# ────────────────────────────────────────────────────────────
# CELL 8 — BAR CHART: Products by category
# ────────────────────────────────────────────────────────────

cat_counts = products["category"].value_counts()
cat_colors = ["#1D9E75","#5B5EA6","#EF9F27","#E24B4A",
              "#185FA5","#BA7517","#D85A30","#639922"]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(cat_counts.index, cat_counts.values,
               color=cat_colors[:len(cat_counts)], edgecolor="white", linewidth=0.8)

for bar in bars:
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
            str(int(bar.get_width())), va="center", fontsize=10)

ax.set_title("Number of Products per Category", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Number of Products", fontsize=12)
ax.set_xlim(0, cat_counts.max() * 1.2)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("bar_products_category.png", dpi=150)
plt.show()
print("✅ Saved as bar_products_category.png")


# ────────────────────────────────────────────────────────────
# CELL 9 — HISTOGRAM: Monthly order trend (bonus!)
# ────────────────────────────────────────────────────────────

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["month"] = orders["order_date"].dt.to_period("M")
monthly_orders = orders.groupby("month").size()

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(monthly_orders.index.astype(str), monthly_orders.values,
       color="#185FA5", edgecolor="white", linewidth=0.8)
ax.plot(monthly_orders.index.astype(str), monthly_orders.values,
        color="#E8593C", marker="o", linewidth=2, markersize=5, label="Trend line")

ax.set_title("Monthly Order Volume — 2023", fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
plt.xticks(rotation=45, ha="right")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("bar_monthly_orders.png", dpi=150)
plt.show()
print("✅ Saved as bar_monthly_orders.png")

print("\n📌 INTERPRETATION:")
peak_month = monthly_orders.idxmax()
print(f"   Peak month: {peak_month} with {monthly_orders.max()} orders.")
print(f"   Slowest month: {monthly_orders.idxmin()} with {monthly_orders.min()} orders.")

conn.close()
print("\n\n🎉 Phase 2 complete! All charts saved as PNG files.")
print("   Check the Colab file panel (folder icon) to download them.")
print("\n   Files saved:")
for f in ["hist_age.png","hist_price.png","bar_order_status.png",
          "bar_customers_city.png","bar_products_category.png","bar_monthly_orders.png"]:
    print(f"   📊 {f}")
