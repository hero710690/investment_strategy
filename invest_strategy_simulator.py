import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.set_page_config(page_title="Investment Strategy Simulator", layout="centered")
st.title("📈 Investment Portfolio Strategy Simulator")

st.markdown("""
Simulate the potential future performance of your investment portfolio:
- **Total Invested Amount (TWD)**: the money you have already invested.
- **Current Return (%)**: return on your investment so far.
- **Monthly Contribution**: the amount you plan to add each month.
- **Simulation Period**: how many years to simulate.
- **Bear Market Years**: simulate market downturn at the beginning.
- **Expected Annual Return / Volatility**: assumed average performance and fluctuation.
- **Strategy**: how you handle your portfolio going forward.
""")

# User input
principal = st.number_input("Total Invested Amount (TWD)", min_value=1000, step=1000, value=100000)
current_return_pct = st.number_input("Current Return (%)", min_value=0.0, value=5.0)
monthly_dca = st.number_input("Monthly Contribution (TWD)", min_value=0, step=1000, value=3000)

years = st.slider("Simulation Period (Years)", 1, 30, 10)
bear_years = st.slider("Bear Market Years (Beginning of Period)", 0, years, 3)
expected_return = st.slider("Expected Annual Return (%)", 0.0, 15.0, 6.0)
volatility = st.slider("Expected Annual Volatility (%)", 0.0, 30.0, 12.0)
bear_return = st.slider("Bear Market Return (%)", -30.0, 0.0, -5.0)
bear_volatility = st.slider("Bear Market Volatility (%)", 0.0, 40.0, 18.0)

strategy = st.selectbox("Select Strategy", [
    "Continue Holding and Contributing",
    "Stop Contributing, Hold Existing",
    "Take Profit, Keep Principal Only",
    "Take Profit and Keep Contributing"
])

# Initial values
initial_value = principal * (1 + current_return_pct / 100)
cost_basis = principal
monthly_return = expected_return / 100 / 12
monthly_std = volatility / 100 / np.sqrt(12)
bear_monthly_return = bear_return / 100 / 12
bear_monthly_std = bear_volatility / 100 / np.sqrt(12)

simulations = 500
months = years * 12
bear_months = bear_years * 12
normal_months = months - bear_months
np.random.seed(42)
final_values = []
time_series_all = []
contribution_series_all = []

for _ in range(simulations):
    value = initial_value
    total_contribution = principal
    time_series = [value]
    contribution_series = [total_contribution]

    if strategy in ["Take Profit, Keep Principal Only", "Take Profit and Keep Contributing"]:
        value = cost_basis
        total_contribution = cost_basis

    bear_returns = np.random.normal(bear_monthly_return, bear_monthly_std, bear_months)
    normal_returns = np.random.normal(monthly_return, monthly_std, normal_months)
    all_returns = np.concatenate([bear_returns, normal_returns])

    for r in all_returns:
        if strategy in ["Continue Holding and Contributing", "Take Profit and Keep Contributing"]:
            total_contribution += monthly_dca
            value = (value + monthly_dca) * (1 + r)
        else:
            value = value * (1 + r)

        time_series.append(value)
        contribution_series.append(total_contribution)

    final_values.append(value)
    time_series_all.append(time_series)
    contribution_series_all.append(contribution_series)

# Summary table
st.markdown("### 📊 Simulation Results (500 runs)")
st.write(f"Simulation Period: {years} years | Bear Market: {bear_years} years | Strategy: {strategy}")

percentiles = np.percentile(final_values, [10, 25, 50, 75, 90])
result_table = pd.DataFrame({
    "Percentile": ["Bottom 10%", "25th Percentile", "Median", "75th Percentile", "Top 10%"],
    "Estimated Value (TWD)": [f"{int(v):,}" for v in percentiles]
})
st.table(result_table)

# Interactive chart
st.markdown("### 📈 Interactive Growth Paths (First 20 Simulations)")
fig = go.Figure()
for i in range(min(20, len(time_series_all))):
    fig.add_trace(go.Scatter(y=time_series_all[i], mode='lines', name=f"Sim {i+1}"))
    fig.add_trace(go.Scatter(y=contribution_series_all[i], mode='lines', name=f"Contribution {i+1}", line=dict(dash='dash'), showlegend=False))
fig.update_layout(title="Portfolio vs Contribution Over Time",
                  xaxis_title="Month",
                  yaxis_title="Value (TWD)",
                  showlegend=False,
                  height=500)
st.plotly_chart(fig, use_container_width=True)

# Bar chart
st.markdown("### 📊 Distribution of Final Portfolio Values")
fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
ax_bar.hist(final_values, bins=30, color='skyblue', edgecolor='black')
ax_bar.axvline(np.median(final_values), color='red', linestyle='--', label='Median')
ax_bar.set_title("Histogram of Final Portfolio Values")
ax_bar.set_xlabel("Final Value (TWD)")
ax_bar.set_ylabel("Frequency")
ax_bar.legend()
st.pyplot(fig_bar)

st.caption("This tool is for informational purposes only. Please assess your own risk tolerance and financial goals before making investment decisions.")