import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import io

# --- Calculation functions ---

def calculate_lumpsum(principal, rate, years):
    total_value = principal * (1 + rate/100) ** years
    returns = total_value - principal
    return principal, returns, total_value

def calculate_sip(monthly_investment, rate, years):
    months = years * 12
    monthly_rate = rate / (12 * 100)
    total_value = monthly_investment * ((((1 + monthly_rate) ** months) - 1) / monthly_rate) * (1 + monthly_rate)
    invested_amount = monthly_investment * months
    returns = total_value - invested_amount
    return invested_amount, returns, total_value

# def calculate_sip(monthly_investment, rate, years):
#     months = years * 12  # Total number of months
#     monthly_rate = rate / (12 * 100)  # Monthly interest rate
    
#     # Corrected future value formula for SIP
#     total_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    
#     # Total invested amount (monthly investment multiplied by number of months)
#     invested_amount = monthly_investment * months
    
#     # Returns is the difference between total value and invested amount
#     returns = total_value - invested_amount
    
#     return invested_amount, returns, total_value

def yearwise_projection_lumpsum(principal, rate, years):
    data = []
    for year in range(1, years + 1):
        value = principal * (1 + rate/100) ** year
        data.append({"Year": year, "Value (₹)": value})
    return pd.DataFrame(data)

def yearwise_projection_sip(monthly_investment, rate, years):
    data = []
    monthly_rate = rate / (12 * 100)
    total_value = 0
    for month in range(1, years * 12 + 1):
        total_value = total_value * (1 + monthly_rate) + monthly_investment
        if month % 12 == 0:
            data.append({"Year": month // 12, "Value (₹)": total_value})
    return pd.DataFrame(data)

# --- Streamlit app ---

st.set_page_config(page_title="Investment Calculator", page_icon="💰", layout="wide")
st.title("💸 Investment Returns Calculator")
st.caption("Plan your wealth smartly! Calculate your Lumpsum and SIP returns 📈")

# --- Theme Toggle ---

dark_mode = st.toggle("🌗 Dark Mode", value=False)

# --- Session State for Reset functionality ---

if "reset" not in st.session_state:
    st.session_state.reset = False

# --- Reset functionality --- 
def reset_all():
    # Reset the session state for the sliders and inputs
    st.session_state["principal_slider"] = 800000
    st.session_state["sip_slider"] = 10000
    st.session_state["rate_slider"] = 12.0
    st.session_state["years_slider"] = 10
    # Reset the input fields
    st.session_state["principal_input"] = 800000
    st.session_state["sip_input"] = 10000
    st.session_state["rate_input"] = 12.0
    st.session_state["years_input"] = 10
    # Set the reset flag to True to trigger the rerun
    st.session_state.reset = True

# --- Investment Type Selection ---

col_type, col_reset = st.columns([6,1])

with col_type:
    investment_type = st.radio("Select Investment Type:", ("Lumpsum", "SIP"), horizontal=True, key="investment_type")

with col_reset:
    if st.button("🔄 Reset All"):
        reset_all()

# Only process the reset logic once and let Streamlit handle the rerun itself
if st.session_state.reset:
    # Reset the flag to avoid infinite reruns
    st.session_state.reset = False
    # No need for st.experimental_rerun() here, Streamlit will re-render on its own

st.markdown("---")

# --- Inputs Section ---

col1, col2, col3 = st.columns(3)

with col1:
    if investment_type == "Lumpsum":
        principal_slider = st.slider("Total Investment (₹)", 10000, 100000000, 800000, step=10000, key="principal_slider")
        principal_input = st.number_input("Or type amount (₹)", min_value=10000, max_value=100000000, value=principal_slider, step=10000, key="principal_input")
        principal = principal_input
    else:
        principal_slider = st.slider("Monthly SIP Amount (₹)", 500, 200000, 10000, step=500, key="sip_slider")
        principal_input = st.number_input("Or type SIP amount (₹)", min_value=500, max_value=200000, value=principal_slider, step=500, key="sip_input")
        principal = principal_input

with col2:
    rate_slider = st.slider("Expected Return Rate (% p.a)", 1.0, 100.0, 12.0, step=0.1, key="rate_slider")
    rate_input = st.number_input("Or type return rate (%)", min_value=1.0, max_value=100.0, value=rate_slider, step=0.1, key="rate_input")
    rate = rate_input

with col3:
    years_slider = st.slider("Investment Time Period (Years)", 1, 30, 10, key="years_slider")
    years_input = st.number_input("Or type years", min_value=1, max_value=30, value=years_slider, step=1, key="years_input")
    years = years_input

st.markdown("---")

# --- Calculation based on Selection ---

if investment_type == "Lumpsum":
    invested, returns, total = calculate_lumpsum(principal, rate, years)
    df_projection = yearwise_projection_lumpsum(principal, rate, years)
else:
    invested, returns, total = calculate_sip(principal, rate, years)
    df_projection = yearwise_projection_sip(principal, rate, years)

def format_in_inr(amount):
    """Formats the number in Indian currency format (lakhs, crores) without showing 'L' or 'Cr'."""
    return f"₹{amount:,.0f}".replace(",", ".")

# --- Results and Donut Chart side by side ---

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📊 Investment Summary")

    st.metric("Invested Amount (₹)", f"{invested:,.2f}")
    #st.metric("Invested Amount (₹)", format_in_inr(invested))
    st.metric("Estimated Returns (₹)", f"{returns:,.2f}")
    st.metric("Total Value (₹)", f"{total:,.2f}")

with right_col:
    fig, ax = plt.subplots(figsize=(3, 3))
    colors = ['#00BFFF', '#32CD32']

    if dark_mode:
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#0e1117')

    wedges, texts, autotexts = ax.pie(
        [invested, returns],
        labels=["Invested", "Returns"],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.4)
    )

    for text in texts + autotexts:
        text.set_color('white' if dark_mode else 'black')

    ax.axis('equal')

    centre_circle = plt.Circle((0,0),0.70,fc=('#0e1117' if dark_mode else 'white'))
    fig.gca().add_artist(centre_circle)

    st.pyplot(fig)

st.markdown("---")

# --- Interactive Yearwise Projection Chart ---

st.subheader("📈 Year-wise Growth Chart")

bar_color = "#FFA15A" if dark_mode else "#636EFA"

fig_bar = px.bar(
    df_projection,
    x="Year",
    y="Value (₹)",
    text_auto=".2s",
    labels={"Value (₹)": "Value (₹)", "Year": "Year"},
    color_discrete_sequence=[bar_color],
    hover_data={"Value (₹)": ":,.2f"},
)

fig_bar.update_traces(
    hovertemplate="<b>Year %{x}</b><br>Value: ₹%{y:,.2f}",
    marker_line_width=1.5,
    marker_line_color="white",
)

fig_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="#0e1117" if dark_mode else "white",
    font_color="white" if dark_mode else "black",
    yaxis_tickformat=",",
    bargap=0.2,
)

st.plotly_chart(fig_bar, use_container_width=True)

# --- Download CSV option ---

csv_buffer = io.StringIO()
df_projection.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 Download Projection as CSV",
    data=csv_buffer.getvalue(),
    file_name="investment_projection.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Made with ❤️ using Streamlit, Matplotlib and Plotly")
