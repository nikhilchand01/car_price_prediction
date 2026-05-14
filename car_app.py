import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Car Price Prediction",
    page_icon="🚗",
    layout="wide"
)
st.markdown("""
<style>

.main {
    padding: 1rem;
}

h1 {
    color: #e74c3c;
}

.stButton > button {
    background-color: #e74c3c;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}

/* FIX METRIC CARD */
[data-testid="stMetric"] {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #334155;
    text-align: center;
}

/* Metric label */
[data-testid="stMetricLabel"] {
    color: white !important;
    font-size: 18px;
}

/* Metric value */
[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-size: 28px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    try:
        model = joblib.load("car_prediction.pkl")
        return model
    except FileNotFoundError:
        return None

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Car_data.csv")
        return df
    except:
        return None

model = load_model()
cars = load_data()


if model is None:
    st.error("Model file not found!")
    st.stop()

if cars is None:
    st.error("Dataset file not found!")
    st.stop()


st.title("🚗 Car Price Prediction System")
st.markdown("### Get Instant Valuation For Your Used Car")

st.sidebar.header("Enter Car Details")

# Year
year = st.sidebar.slider(
    "Manufacturing Year",
    2000,
    2026,
    2018
)

# Showroom Price
price = st.sidebar.number_input(
    "Current Ex-Showroom Price (Lakhs)",
    min_value=0.0,
    max_value=100.0,
    value=5.0,
    step=1.0
)
kms_driven = st.sidebar.number_input(
    "Kilometers Driven",
    min_value=0,
    max_value=500000,
    value=30000,
    step=1000
)
fuel_type = st.sidebar.selectbox(
    "Fuel Type",
    sorted(cars['fuel_type'].unique())
)

companies = sorted(cars['company'].unique())

company = st.sidebar.selectbox(
    "Select Company",
    companies
)

car_models = sorted(
    cars[cars['company'] == company]['name'].unique()
)

car_name = st.sidebar.selectbox(
    "Select Car Model",
    car_models
)

predict_btn = st.sidebar.button(
    "Get Price Estimate"
)

if predict_btn:

    current_year = 2026
    car_age = current_year - year

    input_data = pd.DataFrame({
        "year": [year],
        "company": [company],
        "name": [car_name],
        "fuel_type": [fuel_type],
        "kms_driven": [kms_driven]
    })

    try:
        predicted_price = model.predict(input_data)[0]
        depreciation = price - predicted_price
        depreciation_percent = (
            (depreciation / price) * 100
            if price > 0 else 0
        )
        st.markdown("---")
        st.header("📊 Price Estimation Results")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Estimated Selling Price",
                f"₹ {predicted_price:.2f} L"
            )

        with col2:
            st.metric(
                "Depreciation",
                f"₹ {depreciation:.2f} L",
                delta=f"{depreciation_percent:.2f}%"
            )

        with col3:
            st.metric(
                "Car Age",
                f"{car_age} Years"
            )
        st.markdown("---")
        st.subheader("📈 Price Analysis")

        analysis_col1, analysis_col2 = st.columns([2, 1])

        with analysis_col1:

            lower_estimate = predicted_price * 0.9
            upper_estimate = predicted_price * 1.1

            st.success(
                f"""
                Expected Market Range:
                ₹ {lower_estimate:.2f}L - ₹ {upper_estimate:.2f}L
                """
            )

            st.write("### Price Factors")

            factors = []
            if car_age <= 2:
                factors.append("Very New Car - Minimal Depreciation")

            elif car_age <= 5:
                factors.append("Good Resale Value")

            elif car_age <= 10:
                factors.append("Average Market Value")

            else:
                factors.append("Older Car - Higher Depreciation")
            if kms_driven < 30000:
                factors.append("Average Mileage")

            elif kms_driven < 80000:
                factors.append("Low Mileage")

            else:
                factors.append("Bad Mileage")
            if fuel_type == "Diesel":
                factors.append("Diesel Cars Usually Have Better Highway Performance")

            elif fuel_type == "Petrol":
                factors.append("Petrol Cars Are Easier To Maintain")

            else:
                factors.append("CNG Cars Have Lower Running Cost")

            for factor in factors:
                st.markdown(f"- {factor}")
        with analysis_col2:

            max_price = max(price * 1.2, predicted_price * 1.2)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted_price,
                title={'text': "Estimated Price"},
                number={'suffix': "L"},
                gauge={
                    'axis': {'range': [0, max_price]},
                    'bar': {'color': "#e74c3c"},

                    'steps': [
                        {
                            'range': [0, max_price * 0.3],
                            'color': "lightgray"
                        },

                        {
                            'range': [max_price * 0.3, max_price * 0.7],
                            'color': "lightyellow"
                        },

                        {
                            'range': [max_price * 0.7, max_price],
                            'color': "lightgreen"
                        }
                    ],

                    'threshold': {
                        'line': {
                            'color': "blue",
                            'width': 4
                        },
                        'thickness': 0.75,
                        'value': predicted_price
                    }
                }
            ))

            fig.update_layout(
                height=320,
                margin=dict(
                    l=20,
                    r=20,
                    t=50,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        st.markdown("---")
        st.subheader("Your Car Details")

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            st.write(f"**Manufacturing Year:** {year}")
            st.write(f"**Car Age:** {car_age} years")
            st.write(f"**Kilometers Driven:** {kms_driven:,} km")

        with detail_col2:
            st.write(f"**Fuel Type:** {fuel_type}")
            st.write(f"**Company:** {company}")
            st.write(f"**Car Model:** {car_name}")
        st.markdown("---")
        st.subheader("💡 Tips To Get Better Resale Value")

        st.markdown("""
        - Keep service records updated  
        - Maintain low mileage  
        - Keep insurance active  
        - Avoid exterior damage  
        - Clean interior improves value  
        - Timely servicing increases resale value  
        """)

    except Exception as e:
        st.error(f"Prediction Error: {e}")

else:
    st.markdown("---")
    st.info(
        "Enter your car details in the sidebar and click "
        "'Get Price Estimate'"
    )

    st.subheader("Example Valuation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("### Recent Car")
        st.write("Year: 2022")
        st.write("Price: 8.5L")
        st.write("Kms: 20,000")
        st.write("Estimated: 7.2L")

    with col2:
        st.write("### Mid Range Car")
        st.write("Year: 2018")
        st.write("Price: 6.5L")
        st.write("Kms: 50,000")
        st.write("Estimated: 4.8L")

    with col3:
        st.write("### Older Car")
        st.write("Year: 2012")
        st.write("Price: 5.0L")
        st.write("Kms: 1,00,000")
        st.write("Estimated: 2.1L")
