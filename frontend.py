import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# PAGE CONFIGURATION - ORANGE BRAND COLORS
# ============================================================
st.set_page_config(
    page_title="Down-sell Simulator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Orange Brand Colors
ORANGE_PRIMARY = "#FF7900"  # Orange main color
ORANGE_DARK = "#C05000"      # Dark orange
ORANGE_LIGHT = "#FFB573"     # Light orange
WHITE = "#FFFFFF"
BLACK = "#000000"
GRAY_LIGHT = "#F5F5F5"
GRAY_MEDIUM = "#E0E0E0"
GRAY_DARK = "#333333"

# Custom CSS for Orange theme
st.markdown(f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {WHITE};
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {BLACK} !important;
        font-weight: 600 !important;
    }}
    
    /* Sidebar */
    .css-1d391kg, .css-163ttbj {{
        background-color: {GRAY_LIGHT};
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {ORANGE_PRIMARY};
        color: {WHITE};
        border: none;
        border-radius: 5px;
        font-weight: 500;
    }}
    .stButton > button:hover {{
        background-color: {ORANGE_DARK};
        color: {WHITE};
    }}
    
    /* Metrics */
    .css-1xarl3l {{
        background-color: {GRAY_LIGHT};
        border-left: 4px solid {ORANGE_PRIMARY};
        border-radius: 5px;
        padding: 10px;
    }}
    
    /* Dividers */
    hr {{
        border-top: 2px solid {ORANGE_PRIMARY};
        opacity: 0.3;
    }}
    
    /* Info boxes */
    .stAlert {{
        background-color: {GRAY_LIGHT};
        border-left: 4px solid {ORANGE_PRIMARY};
    }}
    
    /* Success boxes */
    .stSuccess {{
        background-color: {GRAY_LIGHT};
        border-left: 4px solid {ORANGE_PRIMARY};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {GRAY_LIGHT};
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        color: {BLACK};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {ORANGE_PRIMARY} !important;
        color: {WHITE} !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {GRAY_LIGHT};
        color: {BLACK};
        border-radius: 5px;
    }}
    
    /* Custom metric cards */
    .metric-card {{
        background-color: {GRAY_LIGHT};
        border-left: 4px solid {ORANGE_PRIMARY};
        border-radius: 5px;
        padding: 15px;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .metric-label {{
        color: {GRAY_DARK};
        font-size: 14px;
        font-weight: 500;
    }}
    .metric-value {{
        color: {BLACK};
        font-size: 28px;
        font-weight: 700;
    }}
    
    /* ROI card */
    .roi-card {{
        background-color: {ORANGE_PRIMARY};
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: {WHITE};
        margin: 10px 0;
    }}
    .roi-card h2 {{
        color: {WHITE} !important;
        margin: 0;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE AND INTRODUCTION
# ============================================================
st.title("📱 Down-sell Simulator")
st.markdown(f"""
<div style='background-color: {GRAY_LIGHT}; padding: 15px; border-radius: 5px; border-left: 4px solid {ORANGE_PRIMARY};'>
    This application simulates the economic impact of different targeting strategies 
    for customers at risk of down-sell (ARPU decrease ≥ 25%).
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD STATIC DATA (YOUR STATISTICS)
# ============================================================

@st.cache_data
def load_data():
    # Global statistics
    total_clients = 857_141
    total_test = 171_429
    taux_down_global = 0.4041  # 40.41%
    
    # Decile data (from your analysis)
    deciles_data = pd.DataFrame({
        'decile': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'clients': [17142, 17142, 17142, 17142, 17142, 17142, 17142, 17142, 17142, 17151],
        'downs': [15687, 10827, 8948, 7729, 6799, 5836, 4840, 3929, 2946, 1729],
        'rate': [0.9151, 0.6316, 0.5220, 0.4509, 0.3966, 0.3405, 0.2823, 0.2292, 0.1719, 0.1008],
        'lift': [2.265, 1.563, 1.292, 1.116, 0.982, 0.843, 0.699, 0.567, 0.425, 0.249]
    })
    
    # Predefined thresholds
    thresholds_data = pd.DataFrame({
        'threshold': [0.3, 0.4, 0.423, 0.5, 0.6, 0.7],
        'targeted_clients': [129296, 101454, 95000, 78705, 54280, 29634],
        'pct_clients': [75.4, 59.2, 55.4, 45.9, 31.7, 17.3],
        'targeted_downs': [61462, 53705, 50000, 45773, 35163, 22377]
    })
    
    return {
        'total_clients': total_clients,
        'total_test': total_test,
        'global_down_rate': taux_down_global,
        'deciles': deciles_data,
        'thresholds': thresholds_data
    }

data = load_data()

# ============================================================
# SIDEBAR - SIMULATION PARAMETERS
# ============================================================

with st.sidebar:
    st.markdown(f"""
    <div style='background-color: {ORANGE_PRIMARY}; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='color: {WHITE}; margin: 0; text-align: center;'>⚙️ PARAMETERS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Economic parameters
    st.markdown("### 💰 Economic Settings")
    
    action_cost = st.slider(
        "Cost per action (FCFA)",
        min_value=100, max_value=1000, value=250, step=50,
        help="Cost to contact a customer (SMS, call, offer...)"
    )
    
    value_saved = st.slider(
        "Customer value saved (FCFA)",
        min_value=5000, max_value=50000, value=25000, step=1000,
        help="Annual value preserved if customer doesn't down-sell"
    )
    
    effectiveness = st.slider(
        "Action effectiveness (%)",
        min_value=1, max_value=30, value=12, step=1,
        help="Percentage of contacted down-sellers actually retained"
    ) / 100
    
    st.markdown("---")
    
    # Targeting mode
    st.markdown("### 🎯 Targeting Mode")
    target_mode = st.radio(
        "Select mode",
        ["By Decile", "By Threshold", "Custom"],
        index=0
    )
    
    st.markdown("---")
    
    # Info box
    st.markdown(f"""
    <div style='background-color: {GRAY_LIGHT}; padding: 10px; border-radius: 5px; border-left: 4px solid {ORANGE_PRIMARY};'>
        <strong>📊 Test Sample:</strong><br>
        {data['total_test']:,} customers<br>
        Global down-sell rate: {data['global_down_rate']*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_roi(clients, down_rate, cost_per_action, value_saved, effectiveness):
    """
    Calculate ROI for a given segment
    """
    expected_down = clients * down_rate
    total_cost = clients * cost_per_action
    retained = expected_down * effectiveness
    value = retained * value_saved
    net_benefit = value - total_cost
    roi = (net_benefit / total_cost * 100) if total_cost > 0 else 0
    
    return {
        'clients': clients,
        'expected_down': expected_down,
        'total_cost': total_cost,
        'retained': retained,
        'value_saved': value,
        'net_benefit': net_benefit,
        'roi': roi
    }

def metric_card(label, value, help_text=""):
    """Custom metric card with Orange styling"""
    return f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value}</div>
        {f"<div style='color: {GRAY_DARK}; font-size: 12px;'>{help_text}</div>" if help_text else ""}
    </div>
    """

# ============================================================
# GLOBAL KPIS
# ============================================================

st.markdown("### 📊 Key Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(metric_card(
        "Global Down-sell Rate",
        f"{data['global_down_rate']*100:.1f}%",
        "Test sample"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(metric_card(
        "Analyzed Customers",
        f"{data['total_test']:,}",
        "Test sample"
    ), unsafe_allow_html=True)

with col3:
    total_downs = int(data['total_test'] * data['global_down_rate'])
    st.markdown(metric_card(
        "Total Down-sellers",
        f"{total_downs:,}",
        "In test sample"
    ), unsafe_allow_html=True)

with col4:
    roi_d1 = calculate_roi(17142, 0.9151, action_cost, value_saved, effectiveness)['roi']
    st.markdown(metric_card(
        "Max ROI Possible",
        f"{roi_d1:.0f}%",
        "Decile 1 with current parameters"
    ), unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ============================================================
# MODE 1: BY DECILE
# ============================================================

if target_mode == "By Decile":
    st.markdown("### 📊 Decile Analysis")
    
    # Decile selection
    selected_deciles = st.multiselect(
        "Select deciles to target",
        options=data['deciles']['decile'].tolist(),
        default=[1, 2, 3],
        format_func=lambda x: f"Decile {x}"
    )
    
    if selected_deciles:
        # Filter selected deciles
        filtered = data['deciles'][data['deciles']['decile'].isin(selected_deciles)]
        
        # Cumulative calculations
        total_clients = filtered['clients'].sum()
        total_downs = filtered['downs'].sum()
        avg_rate = total_downs / total_clients
        
        # Calculate ROI
        results = calculate_roi(
            total_clients, avg_rate,
            action_cost, value_saved, effectiveness
        )
        
        # Results in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(metric_card(
                "Targeted Clients",
                f"{results['clients']:,}"
            ), unsafe_allow_html=True)
            st.markdown(metric_card(
                "Down Rate in Target",
                f"{avg_rate*100:.1f}%"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(metric_card(
                "Down-sellers Targeted",
                f"{results['expected_down']:.0f}"
            ), unsafe_allow_html=True)
            st.markdown(metric_card(
                "Customers Saved",
                f"{results['retained']:.0f}"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(metric_card(
                "Investment",
                f"{results['total_cost']:,.0f} FCFA"
            ), unsafe_allow_html=True)
            st.markdown(metric_card(
                "Net Benefit",
                f"{results['net_benefit']:,.0f} FCFA"
            ), unsafe_allow_html=True)
        
        # ROI Card
        roi_color = ORANGE_PRIMARY if results['roi'] > 0 else GRAY_DARK
        st.markdown(f"""
        <div class='roi-card' style='background-color: {roi_color};'>
            <h2>ROI: {results['roi']:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Decile chart
        fig = px.bar(
            data['deciles'],
            x='decile',
            y='rate',
            title="Down-sell Rate by Decile",
            labels={'rate': 'Down-sell Rate', 'decile': 'Decile'},
            color='rate',
            color_continuous_scale=[[0, WHITE], [1, ORANGE_PRIMARY]]
        )
        fig.add_hline(
            y=data['global_down_rate'],
            line_dash="dash",
            line_color=BLACK,
            annotation_text=f"Average: {data['global_down_rate']*100:.1f}%"
        )
        fig.update_layout(
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            font_color=BLACK
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# MODE 2: BY THRESHOLD
# ============================================================

elif target_mode == "By Threshold":
    st.markdown("### 🎯 Threshold Analysis")
    
    # Threshold selector
    threshold = st.slider(
        "Select probability threshold",
        min_value=0.0, max_value=1.0, value=0.7, step=0.05
    )
    
    # Find closest threshold in data
    thresholds = data['thresholds']['threshold'].tolist()
    closest = min(thresholds, key=lambda x: abs(x - threshold))
    
    # Get data for this threshold
    threshold_data = data['thresholds'][data['thresholds']['threshold'] == closest].iloc[0]
    
    # Calculate ROI
    results = calculate_roi(
        threshold_data['targeted_clients'],
        threshold_data['targeted_downs'] / threshold_data['targeted_clients'],
        action_cost, value_saved, effectiveness
    )
    
    # Two-column comparison of optimal thresholds
    st.markdown("### ⚖️ Optimal Thresholds Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: {GRAY_LIGHT}; padding: 15px; border-radius: 5px; border-left: 4px solid {ORANGE_PRIMARY};'>
            <h4 style='color: {BLACK};'>🔵 Threshold 0.423 (F1 Optimal)</h4>
        """, unsafe_allow_html=True)
        
        t423 = data['thresholds'][data['thresholds']['threshold'] == 0.423].iloc[0]
        r423 = calculate_roi(
            t423['targeted_clients'],
            t423['targeted_downs'] / t423['targeted_clients'],
            action_cost, value_saved, effectiveness
        )
        
        st.markdown(metric_card("Targeted Clients", f"{r423['clients']:,}"), unsafe_allow_html=True)
        st.markdown(metric_card("Net Benefit", f"{r423['net_benefit']:,.0f} FCFA"), unsafe_allow_html=True)
        st.markdown(metric_card("ROI", f"{r423['roi']:.1f}%"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: {GRAY_LIGHT}; padding: 15px; border-radius: 5px; border-left: 4px solid {ORANGE_PRIMARY};'>
            <h4 style='color: {BLACK};'>🟢 Threshold 0.7 (ROI Optimal)</h4>
        """, unsafe_allow_html=True)
        
        t7 = data['thresholds'][data['thresholds']['threshold'] == 0.7].iloc[0]
        r7 = calculate_roi(
            t7['targeted_clients'],
            t7['targeted_downs'] / t7['targeted_clients'],
            action_cost, value_saved, effectiveness
        )
        
        st.markdown(metric_card("Targeted Clients", f"{r7['clients']:,}"), unsafe_allow_html=True)
        st.markdown(metric_card("Net Benefit", f"{r7['net_benefit']:,.0f} FCFA"), unsafe_allow_html=True)
        st.markdown(metric_card("ROI", f"{r7['roi']:.1f}%"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ROI vs Threshold chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Calculate ROI for all thresholds
    rois = []
    for _, row in data['thresholds'].iterrows():
        r = calculate_roi(
            row['targeted_clients'],
            row['targeted_downs'] / row['targeted_clients'],
            action_cost, value_saved, effectiveness
        )
        rois.append(r['roi'])
    
    fig.add_trace(
        go.Scatter(
            x=data['thresholds']['threshold'],
            y=rois,
            mode='lines+markers',
            name='ROI',
            line=dict(color=ORANGE_PRIMARY, width=3),
            marker=dict(color=ORANGE_DARK, size=8)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=data['thresholds']['threshold'],
            y=data['thresholds']['targeted_clients'],
            name='Targeted Clients',
            marker_color=ORANGE_LIGHT,
            opacity=0.6
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title="ROI and Targeting Volume by Threshold",
        xaxis_title="Threshold",
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font_color=BLACK,
        hovermode='x unified'
    )
    fig.update_yaxes(title_text="ROI (%)", secondary_y=False, gridcolor=GRAY_MEDIUM)
    fig.update_yaxes(title_text="Targeted Clients", secondary_y=True, gridcolor=GRAY_MEDIUM)
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# MODE 3: CUSTOM
# ============================================================

else:
    st.markdown("### ⚙️ Custom Simulation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_clients = st.number_input(
            "Number of clients to target",
            min_value=1000, max_value=100000, value=30000, step=1000
        )
    
    with col2:
        target_rate = st.slider(
            "Down-sell rate in target (%)",
            min_value=10, max_value=100, value=70, step=5
        ) / 100
    
    # Calculate
    results = calculate_roi(
        n_clients, target_rate,
        action_cost, value_saved, effectiveness
    )
    
    # Display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(metric_card("Investment", f"{results['total_cost']:,.0f} FCFA"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("Net Benefit", f"{results['net_benefit']:,.0f} FCFA"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("ROI", f"{results['roi']:.1f}%"), unsafe_allow_html=True)
    
    # Break-even threshold
    breakeven = (action_cost / (value_saved * effectiveness)) * 100
    st.markdown(f"""
    <div style='background-color: {GRAY_LIGHT}; padding: 15px; border-radius: 5px; border-left: 4px solid {ORANGE_PRIMARY}; margin-top: 20px;'>
        <strong>💡 Break-even analysis:</strong> You need at least <strong>{breakeven:.1f}%</strong> down-sell rate 
        to be profitable with these parameters.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# REFERENCE TABLES
# ============================================================

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 📋 Reference Data")

tab1, tab2, tab3 = st.tabs(["📊 Deciles", "🎯 Thresholds", "📈 Metrics"])

with tab1:
    df_display = data['deciles'].copy()
    df_display['rate'] = df_display['rate'].apply(lambda x: f"{x*100:.1f}%")
    df_display['lift'] = df_display['lift'].apply(lambda x: f"{x:.2f}")
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

with tab2:
    df_display = data['thresholds'].copy()
    df_display['pct_clients'] = df_display['pct_clients'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown(f"""
    <div style='background-color: {GRAY_LIGHT}; padding: 15px; border-radius: 5px;'>
        <ul style='color: {BLACK};'>
            <li><strong>Total analyzed population:</strong> {data['total_clients']:,} customers</li>
            <li><strong>Test sample:</strong> {data['total_test']:,} customers</li>
            <li><strong>Global down-sell rate:</strong> {data['global_down_rate']*100:.1f}%</li>
            <li><strong>Optimal F1 threshold:</strong> 0.423</li>
            <li><strong>Optimal ROI threshold:</strong> 0.7</li>
            <li><strong>Decile 1:</strong> {data['deciles'].iloc[0]['rate']*100:.1f}% down-sell rate</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# EXPORT SECTION
# ============================================================

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 📥 Export Results")

if st.button("📊 Generate Simulation Report", use_container_width=True):
    # Create summary DataFrame
    summary = pd.DataFrame({
        'Parameter': [
            'Cost per action',
            'Value saved',
            'Effectiveness',
            'Global down rate',
            'ROI Decile 1',
            'ROI Deciles 1-3',
            'ROI Threshold 0.7'
        ],
        'Value': [
            f"{action_cost} FCFA",
            f"{value_saved} FCFA",
            f"{effectiveness*100:.0f}%",
            f"{data['global_down_rate']*100:.1f}%",
            f"{calculate_roi(17142, 0.9151, action_cost, value_saved, effectiveness)['roi']:.1f}%",
            f"{calculate_roi(51426, 0.689, action_cost, value_saved, effectiveness)['roi']:.1f}%",
            f"{calculate_roi(29634, 0.755, action_cost, value_saved, effectiveness)['roi']:.1f}%"
        ]
    })
    
    csv = summary.to_csv(index=False)
    st.download_button(
        label="📥 Download Report (CSV)",
        data=csv,
        file_name="down_sell_simulation.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============================================================
# METHODOLOGICAL NOTES
# ============================================================

with st.expander("📌 Methodological Notes"):
    st.markdown(f"""
    <div style='background-color: {GRAY_LIGHT}; padding: 15px; border-radius: 5px;'>
        <ul style='color: {BLACK};'>
            <li><strong>Population:</strong> Analysis based on 857k customers with known M1-M2 variation</li>
            <li><strong>Test sample:</strong> 171k customers (20% of analyzed population)</li>
            <li><strong>Global down-sell rate:</strong> 40.4% in this sample</li>
            <li><strong>Retention hypothesis:</strong> {effectiveness*100:.0f}% of contacted down-sellers are saved (adjustable)</li>
            <li><strong>Saved value:</strong> {value_saved:,} FCFA per customer (estimated annual ARPU)</li>
            <li><strong>Contact cost:</strong> {action_cost} FCFA per customer</li>
        </ul>
        <p style='color: {GRAY_DARK}; margin-top: 10px;'>
            Simulations are based on actual statistics from your XGBoost model.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: {GRAY_DARK}; padding: 10px;'>
    <strong>Orange Down-sell Simulator</strong> v1.0 | Interactive Dashboard
</div>
""", unsafe_allow_html=True)