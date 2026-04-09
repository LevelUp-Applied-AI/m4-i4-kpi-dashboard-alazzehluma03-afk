import sys
import os
import json
import pandas as pd
import plotly.graph_objects as go

# حل مشكلة الـ Import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analysis import connect_db, extract_data, compute_kpis

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def get_status_color(actual, threshold):
    if actual >= threshold: return "green"
    elif actual >= threshold * 0.8: return "yellow"
    else: return "red"

def create_monitoring_dashboard():
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)
    df = kpis["df"]
    config = load_config()
    thresh = config["thresholds"]

    # تجهيز البيانات للمؤشرات الخمسة
    # 1. Total Revenue
    # 2. MoM Growth
    # 3. Average Order Value (AOV)
    # 4. Total Orders
    # 5. Unique Customers
    
    metrics_data = [
        {"label": "Total Revenue", "actual": kpis["total_revenue"], "target": thresh["total_revenue"], "suffix": " JOD"},
        {"label": "MoM Growth", "actual": kpis["mom_growth"].iloc[-1], "target": thresh["mom_growth"], "suffix": "%"},
        {"label": "Avg Order Value", "actual": kpis["aov_by_city"].mean(), "target": thresh["aov"], "suffix": " JOD"},
        {"label": "Total Orders", "actual": len(df["order_id"].unique()), "target": thresh["total_orders"], "suffix": ""},
        {"label": "Unique Customers", "actual": len(df["customer_id"].unique()), "target": thresh["unique_customers"], "suffix": ""}
    ]

    fig = go.Figure()

    for i, m in enumerate(metrics_data):
        color = get_status_color(m["actual"], m["target"])
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = m["actual"],
            title = {'text': m["label"]},
            delta = {'reference': m["target"]},
            domain = {'row': i // 3, 'column': i % 3},
            gauge = {
                'axis': {'range': [None, m["target"] * 1.5]},
                'bar': {'color': color},
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': m["target"]}
            },
            number = {'suffix': m["suffix"]}
        ))

    # إضافة Dropdown Filter (مثال بسيط لتغيير الـ Title كمقدمة للفلاتر المعقدة)
    fig.update_layout(
        grid = {'rows': 2, 'columns': 3, 'pattern': "independent"},
        title = "Amman Market: 5-KPI Real-time Monitoring",
        updatemenus=[{
            "buttons": [
                {"method": "relayout", "label": "All Cities", "args": [{"title": "Monitoring: All Cities"}]},
                {"method": "relayout", "label": "Amman Only", "args": [{"title": "Monitoring: Amman Focus"}]}
            ],
            "direction": "down",
            "showactive": True,
            "x": 0.1, "y": 1.15
        }]
    )

    os.makedirs("output", exist_ok=True)
    fig.write_html("output/monitoring_gauge.html")
    print("✅ 5-KPI Dashboard with Filters created in output/monitoring_gauge.html")

if __name__ == "__main__":
    create_monitoring_dashboard()