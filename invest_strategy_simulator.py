import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Investment Strategy Simulator", layout="centered")
st.title("📈 Investment Portfolio Strategy Simulator")
st.markdown("Simulate potential future performance of your investment portfolio based on current returns, cost basis, and contribution strategy, including market downturns and dynamic strategies.")

# User input
principal = st.number_input("Total Invested Amount (TWD)", min_value=1000, step=1000, value=100000)
current_return_pct = st.number_input("Current Return (%)", min_value=0.0, value=70.0)
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

# Final total contribution for baseline
final_contribution = total_contribution

# Summary table
st.markdown("### 📊 Simulation Results (500 runs)")
st.write(f"Simulation Period: {years} years | Bear Market: {bear_years} years | Strategy: {strategy}")

percentiles = np.percentile(final_values, [10, 25, 50, 75, 90])
result_table = pd.DataFrame({
    "Percentile": ["Bottom 10%", "25th Percentile", "Median", "75th Percentile", "Top 10%"],
    "Estimated Value (TWD)": [f"{int(v):,}" for v in percentiles]
})
st.table(result_table)

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(final_values, bins=30, color='skyblue', edgecolor='black')
ax.axvline(np.median(final_values), color='red', linestyle='--', label='Median')
ax.axvline(final_contribution, color='black', linestyle=':', label='Final Total Contribution')
ax.set_title("Distribution of Final Portfolio Values")
ax.set_xlabel("Final Value (TWD)")
ax.set_ylabel("Frequency")
ax.legend()
st.pyplot(fig)

# Time series chart
st.markdown("### 📈 Sample Growth Paths (First 20 Simulations)")
fig2, ax2 = plt.subplots(figsize=(8, 4))
for ts, cs in zip(time_series_all[:20], contribution_series_all[:20]):
    ax2.plot(ts, alpha=0.4)
    ax2.plot(cs, color='gray', linestyle='--', alpha=0.3)
ax2.axhline(final_contribution, color='black', linestyle=':', label='Final Total Contribution')
ax2.set_title("Portfolio Growth Over Time")
ax2.set_xlabel("Month")
ax2.set_ylabel("Portfolio Value (TWD)")
ax2.legend()
st.pyplot(fig2)

st.caption("This tool is for informational purposes only. Please assess your own risk tolerance and financial goals before making investment decisions.")
