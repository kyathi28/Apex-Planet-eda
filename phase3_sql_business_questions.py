# ============================================================
#  PHASE 3 — SQL for Business Questions
#  7 real business questions answered with SQL queries
#  Paste each CELL separately in Colab and run one by one
# ============================================================


# ────────────────────────────────────────────────────────────
# CELL 1 — Setup: connect and create a helper print function
# ────────────────────────────────────────────────────────────
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("ecommerce.db")

def run_query(title, sql, interpretation):
    """Run a SQL query, print results nicely, and show interpretation."""
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)
    df = pd.read_sql(sql, conn)
    print(df.to_string(index=False))
    print(f"\n📌 INSIGHT: {interpretation}")
    print()
    return df

print("✅ Connected to ecommerce.db — ready for SQL queries!")


# ────────────────────────────────────────────────────────────
# CELL 2 — QUESTION 1
# "What are the top 5 products by total revenue?"
# Concepts used: JOIN, GROUP BY, ORDER BY, LIMIT, aggregation
# ────────────────────────────────────────────────────────────

sql_q1 = """
SELECT
    p.name                                    AS product_name,
    p.category,
    SUM(oi.quantity * oi.unit_price)          AS total_revenue,
    SUM(oi.quantity)                          AS units_sold
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.product_id, p.name, p.category
ORDER BY total_revenue DESC
LIMIT 5;
"""

df_q1 = run_query(
    "Q1 — Top 5 Products by Revenue (Completed Orders Only)",
    sql_q1,
    "These 5 products generate the highest revenue. "
    "Focus marketing and stock priority on these items."
)

# Chart for Q1
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(df_q1["product_name"][::-1], df_q1["total_revenue"][::-1],
        color="#5B5EA6", edgecolor="white")
ax.set_title("Top 5 Products by Revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Total Revenue (₹)")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("q1_top5_products.png", dpi=150)
plt.show()
print("✅ Chart saved: q1_top5_products.png")


# ────────────────────────────────────────────────────────────
# CELL 3 — QUESTION 2
# "What is the monthly revenue trend throughout 2023?"
# Concepts: strftime (date functions), GROUP BY, ORDER BY
# ────────────────────────────────────────────────────────────

sql_q2 = """
SELECT
    strftime('%Y-%m', o.order_date)           AS month,
    COUNT(DISTINCT o.order_id)                AS total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY month
ORDER BY month;
"""

df_q2 = run_query(
    "Q2 — Monthly Revenue Trend (2023)",
    sql_q2,
    "Identifies peak and slow revenue months. "
    "Use this to plan seasonal promotions and inventory."
)

# Chart for Q2
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(df_q2["month"], df_q2["monthly_revenue"],
       color="#1D9E75", edgecolor="white", label="Revenue")
ax.plot(df_q2["month"], df_q2["monthly_revenue"],
        color="#E8593C", marker="o", linewidth=2, label="Trend")
ax.set_title("Monthly Revenue Trend — 2023", fontsize=13, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₹)")
plt.xticks(rotation=45, ha="right")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("q2_monthly_revenue.png", dpi=150)
plt.show()
print("✅ Chart saved: q2_monthly_revenue.png")


# ────────────────────────────────────────────────────────────
# CELL 4 — QUESTION 3
# "Which product category generates the most revenue?"
# Concepts: JOIN, GROUP BY, aggregate functions, percentage calc
# ────────────────────────────────────────────────────────────

sql_q3 = """
SELECT
    p.category,
    COUNT(DISTINCT o.order_id)                  AS total_orders,
    SUM(oi.quantity)                            AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price) * 100.0
        / SUM(SUM(oi.quantity * oi.unit_price)) OVER (), 1
    )                                           AS revenue_pct
FROM order_items oi
JOIN products p  ON oi.product_id = p.product_id
JOIN orders   o  ON oi.order_id   = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.category
ORDER BY total_revenue DESC;
"""

df_q3 = run_query(
    "Q3 — Revenue by Product Category",
    sql_q3,
    "Shows which categories drive the business. "
    "High-revenue categories deserve more shelf space and promotions."
)

# Chart for Q3 — Pie chart
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(df_q3["total_revenue"], labels=df_q3["category"],
       autopct="%1.1f%%", startangle=140,
       colors=["#5B5EA6","#1D9E75","#EF9F27","#E24B4A",
               "#185FA5","#BA7517","#D85A30","#639922"])
ax.set_title("Revenue Share by Category", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("q3_category_revenue.png", dpi=150)
plt.show()
print("✅ Chart saved: q3_category_revenue.png")


# ────────────────────────────────────────────────────────────
# CELL 5 — QUESTION 4
# "Who are the top 10 customers by total spend?"
# Concepts: Multi-table JOIN (3 tables), GROUP BY, ORDER BY
# ────────────────────────────────────────────────────────────

sql_q4 = """
SELECT
    c.customer_id,
    c.name,
    c.city,
    c.age,
    COUNT(DISTINCT o.order_id)                  AS total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_spend
FROM customers c
JOIN orders     o   ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id    = oi.order_id
WHERE o.status = 'Completed'
GROUP BY c.customer_id, c.name, c.city, c.age
ORDER BY total_spend DESC
LIMIT 10;
"""

df_q4 = run_query(
    "Q4 — Top 10 Customers by Total Spend",
    sql_q4,
    "These are your VIP customers. "
    "Loyalty programmes and personalised offers should target this group."
)

# Chart for Q4
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(df_q4["name"][::-1], df_q4["total_spend"][::-1],
        color="#E8593C", edgecolor="white")
ax.set_title("Top 10 Customers by Total Spend", fontsize=13, fontweight="bold")
ax.set_xlabel("Total Spend (₹)")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("q4_top_customers.png", dpi=150)
plt.show()
print("✅ Chart saved: q4_top_customers.png")


# ────────────────────────────────────────────────────────────
# CELL 6 — QUESTION 5
# "What is the order cancellation rate by city?"
# Concepts: CASE WHEN, GROUP BY, percentage calculation
# ────────────────────────────────────────────────────────────

sql_q5 = """
SELECT
    c.city,
    COUNT(o.order_id)                                        AS total_orders,
    SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(
        SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0
        / COUNT(o.order_id), 1
    )                                                        AS cancellation_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
ORDER BY cancellation_rate_pct DESC;
"""

df_q5 = run_query(
    "Q5 — Order Cancellation Rate by City",
    sql_q5,
    "Cities with high cancellation rates may have delivery or "
    "service issues. Investigate root causes in those locations."
)

# Chart for Q5
fig, ax = plt.subplots(figsize=(10, 5))
colors_q5 = ["#E24B4A" if r > 15 else "#EF9F27" if r > 10 else "#1D9E75"
             for r in df_q5["cancellation_rate_pct"]]
bars = ax.bar(df_q5["city"], df_q5["cancellation_rate_pct"],
              color=colors_q5, edgecolor="white")
ax.axhline(df_q5["cancellation_rate_pct"].mean(), color="#5B5EA6",
           linestyle="--", linewidth=1.5,
           label=f"Avg = {df_q5['cancellation_rate_pct'].mean():.1f}%")
ax.set_title("Cancellation Rate by City (%)", fontsize=13, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)")
plt.xticks(rotation=30, ha="right")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("q5_cancellation_city.png", dpi=150)
plt.show()
print("✅ Chart saved: q5_cancellation_city.png")


# ────────────────────────────────────────────────────────────
# CELL 7 — QUESTION 6
# "What is the average order value (AOV) by customer age group?"
# Concepts: CASE WHEN for bucketing, JOIN, GROUP BY, AVG
# ────────────────────────────────────────────────────────────

sql_q6 = """
SELECT
    CASE
        WHEN c.age BETWEEN 18 AND 25 THEN '18–25'
        WHEN c.age BETWEEN 26 AND 35 THEN '26–35'
        WHEN c.age BETWEEN 36 AND 45 THEN '36–45'
        WHEN c.age BETWEEN 46 AND 55 THEN '46–55'
        ELSE '56+'
    END                                                     AS age_group,
    COUNT(DISTINCT o.order_id)                              AS total_orders,
    ROUND(AVG(oi.quantity * oi.unit_price), 2)              AS avg_order_value,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)              AS total_revenue
FROM customers c
JOIN orders      o  ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id    = oi.order_id
WHERE o.status = 'Completed'
GROUP BY age_group
ORDER BY age_group;
"""

df_q6 = run_query(
    "Q6 — Average Order Value by Customer Age Group",
    sql_q6,
    "Reveals which age group spends the most per order. "
    "Helps tailor product recommendations and ad targeting."
)

# Chart for Q6
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(df_q6["age_group"], df_q6["avg_order_value"],
       color="#185FA5", edgecolor="white", width=0.5)
ax.set_title("Average Order Value by Age Group", fontsize=13, fontweight="bold")
ax.set_xlabel("Age Group")
ax.set_ylabel("Avg Order Value (₹)")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("q6_aov_age_group.png", dpi=150)
plt.show()
print("✅ Chart saved: q6_aov_age_group.png")


# ────────────────────────────────────────────────────────────
# CELL 8 — QUESTION 7
# "What is the profit margin per product category?"
# Concepts: JOIN, computed columns, ROUND, ORDER BY
# ────────────────────────────────────────────────────────────

sql_q7 = """
SELECT
    p.category,
    ROUND(AVG(p.price), 2)                              AS avg_selling_price,
    ROUND(AVG(p.cost_price), 2)                         AS avg_cost_price,
    ROUND(AVG(p.price - p.cost_price), 2)               AS avg_profit_per_unit,
    ROUND(
        AVG((p.price - p.cost_price) * 100.0 / p.price)
    , 1)                                                AS profit_margin_pct
FROM products p
GROUP BY p.category
ORDER BY profit_margin_pct DESC;
"""

df_q7 = run_query(
    "Q7 — Profit Margin by Product Category",
    sql_q7,
    "Categories with highest margin are most profitable per sale. "
    "Pair with Q3 (revenue) to identify the best overall categories."
)

# Chart for Q7
fig, ax = plt.subplots(figsize=(10, 5))
bar_colors_q7 = ["#1D9E75" if m >= 40 else "#EF9F27" if m >= 30 else "#E24B4A"
                 for m in df_q7["profit_margin_pct"]]
bars = ax.bar(df_q7["category"], df_q7["profit_margin_pct"],
              color=bar_colors_q7, edgecolor="white")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
            f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=9)
ax.set_title("Profit Margin % by Category", fontsize=13, fontweight="bold")
ax.set_xlabel("Category")
ax.set_ylabel("Profit Margin (%)")
plt.xticks(rotation=30, ha="right")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("q7_profit_margin.png", dpi=150)
plt.show()
print("✅ Chart saved: q7_profit_margin.png")

conn.close()

# ────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  🎉 PHASE 3 COMPLETE — All 7 Business Questions Answered!")
print("=" * 65)
questions = [
    "Q1 — Top 5 products by revenue",
    "Q2 — Monthly revenue trend",
    "Q3 — Revenue by product category",
    "Q4 — Top 10 customers by spend",
    "Q5 — Cancellation rate by city",
    "Q6 — Avg order value by age group",
    "Q7 — Profit margin by category",
]
charts = [
    "q1_top5_products.png",
    "q2_monthly_revenue.png",
    "q3_category_revenue.png",
    "q4_top_customers.png",
    "q5_cancellation_city.png",
    "q6_aov_age_group.png",
    "q7_profit_margin.png",
]
for q, c in zip(questions, charts):
    print(f"  ✅ {q}  →  📊 {c}")

print("\n  SQL concepts used across all queries:")
print("  → SELECT, FROM, WHERE, GROUP BY, ORDER BY, LIMIT")
print("  → JOIN (2-table and 3-table joins)")
print("  → Aggregate functions: SUM, COUNT, AVG, ROUND")
print("  → CASE WHEN for conditional logic & bucketing")
print("  → Window function: SUM(...) OVER () for percentages")
print("  → strftime() for date formatting")
