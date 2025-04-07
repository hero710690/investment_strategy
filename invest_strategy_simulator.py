import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Investment Strategy Simulator", 
    layout="wide",
    page_icon="📈")
st.title("📈 Investment Portfolio Strategy Simulator")

st.markdown("""
### 🧭 Strategy Overview & Analysis
- **Continue Holding and Contributing**: You remain invested and continue monthly contributions. This strategy takes full advantage of dollar-cost averaging and long-term compounding, but assumes you can sustain investment discipline through bear markets.

- **Stop Contributing, Hold Existing**: No further contributions are made, but you stay invested. Ideal for when cash flow is limited but you want to stay exposed to long-term market growth.

- **Take Profit, Keep Principal Only**: You realize gains and revert back to your original principal amount. Useful when you're concerned about market volatility but want to stay invested conservatively.

- **Take Profit and Keep Contributing**: You secure gains by taking profit and continue regular contributions. Combines risk reduction with ongoing growth potential and compounding benefits.

> The simulations below show how each strategy performs under varying market conditions. Percentile lines help estimate outcomes under pessimistic, median, and optimistic scenarios.
""")

with st.sidebar:
    st.markdown("""
    Simulate the potential future performance of your investment portfolio:
    - **Total Invested Amount (TWD)**: the money you have already invested.
    - **Current Return (%)**: return on your investment so far.
    - **Monthly Contribution**: the amount you plan to add each month.
    - **Simulation Period**: how many years to simulate.
    - **Bear Market Years**: simulate market downturn at the beginning.
    - **Expected Annual Return / Volatility**: assumed average performance and fluctuation.
    - **Strategy**: how you handle your portfolio going forward.

    ### Parameters
    Simulate the potential future performance of your investment portfolio:
    """)

    principal = st.number_input("Total Invested Amount (TWD)", min_value=1000, step=1000, value=100000)
    current_return_pct = st.number_input("Current Return (%)", min_value=0.0, value=5.0)
    monthly_dca = st.number_input("Monthly Contribution (TWD)", min_value=0, step=1000, value=3000)

    years = st.slider("Simulation Period (Years)", 1, 30, 10)
    bear_years = st.slider("Bear Market Years (Beginning of Period)", 0, years, 3)
    expected_return = st.slider("Expected Annual Return (%)", 0.0, 15.0, 6.0)
    volatility = st.slider("Expected Annual Volatility (%)", 0.0, 30.0, 12.0)
    bear_return = st.slider("Bear Market Return (%)", -30.0, 0.0, -5.0)
    bear_volatility = st.slider("Bear Market Volatility (%)", 0.0, 40.0, 18.0)
    simulations = st.number_input("Montecarlo simulation times", min_value=10, step=100, value=500)

all_violin_data = []
strategies = [
    "Continue Holding and Contributing",
    "Take Profit and Keep Contributing",
    "Take Profit, Keep Principal Only",
    "Stop Contributing, Hold Existing"
]

summary_stats = {}
time_series_all_strategies = {}
contribution_series_all_strategies = {}
final_value_all_strategies = {}

st.markdown("### 📊 Strategy Comparison Results")

for strategy in strategies:
    initial_value = principal * (1 + current_return_pct / 100)
    cost_basis = principal
    monthly_return = expected_return / 100 / 12
    monthly_std = volatility / 100 / np.sqrt(12)
    bear_monthly_return = bear_return / 100 / 12
    bear_monthly_std = bear_volatility / 100 / np.sqrt(12)

    months = years * 12
    bear_months = bear_years * 12
    normal_months = months - bear_months
    np.random.seed(42)
    final_values = []
    time_series_examples = []
    contribution_series_examples = []

    for _ in range(simulations):
        value = initial_value
        total_contribution = principal
        time_series = [value]
        contrib_series = [total_contribution]

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
            contrib_series.append(total_contribution)

        final_values.append(value)
        if len(time_series_examples) < 20:
            time_series_examples.append(time_series)
            contribution_series_examples.append(contrib_series)

    percentiles = np.percentile(final_values, [10, 25, 50, 75, 90])
    summary_stats[strategy] = [f"{int(v):,}" for v in percentiles]
    time_series_all_strategies[strategy] = time_series_examples
    contribution_series_all_strategies[strategy] = contribution_series_examples
    final_value_all_strategies[strategy] = final_values
    all_violin_data.extend([(strategy, v) for v in final_values])

result_df = pd.DataFrame(summary_stats, index=["10th %", "25th %", "50th %", "75th %", "90th %"]).T
st.dataframe(result_df)
st.markdown("### 📈 Sample Portfolio Growth by Strategy")
grid_rows = [st.columns(2), st.columns(2)]

for i, strategy in enumerate(strategies):
    row = grid_rows[i // 2]
    with row[i % 2]:
        fig = go.Figure()
        for ts, cs in zip(time_series_all_strategies[strategy], contribution_series_all_strategies[strategy]):
            fig.add_trace(go.Scatter(y=cs, mode='lines', name='Contribution', line=dict(dash='dot'), opacity=0.3))
            fig.add_trace(go.Scatter(y=ts, mode='lines', name='Portfolio', opacity=0.3))

        fig.update_layout(title=f"{strategy}",
                          xaxis_title="Month",
                          yaxis_title="Value (TWD)",
                          height=350,
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🎻 Final Portfolio Value Distribution - Violin Chart")
violin_df = pd.DataFrame(all_violin_data, columns=["Strategy", "Final Value"])
fig_violin, ax = plt.subplots(figsize=(12, 6))
sns.violinplot(data=violin_df, x="Strategy", y="Final Value", ax=ax)
ax.set_title("Distribution of Final Values by Strategy")
ax.set_ylabel("Final Portfolio Value (TWD)")
ax.set_xlabel("Strategy")
ax.tick_params(axis='x', rotation=20)
st.pyplot(fig_violin)



st.caption("This tool is for informational purposes only. Please assess your own risk tolerance and financial goals before making investment decisions.")
