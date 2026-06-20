# =========================================================
# 🌾 SMART CROP YIELD PREDICTION SYSTEM
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import time
import pickle
import plotly.express as px
import bcrypt
from reportlab.pdfgen import canvas
from io import BytesIO
from db import get_connection
import mysql.connector
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
import io

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart Crop Yield Prediction",
    page_icon="🌾",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background-image:
    linear-gradient(rgba(0,0,0,0.72), rgba(0,0,0,0.72)),
    url("https://images.unsplash.com/photo-1500937386664-56d1dfef3854");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

header[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.block-container {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364);
}

section[data-testid="stSidebar"] * {
    color: white !important;
    font-weight: 600 !important;
}

h1, h2, h3, h4, h5, h6,
p, label, div, span {
    color: white !important;
    font-weight: 600 !important;
}

.login-box {
    background: rgba(255,255,255,0.10);
    padding: 40px;
    border-radius: 25px;
    backdrop-filter: blur(12px);
    box-shadow: 0px 8px 30px rgba(0,0,0,0.5);
}

.card {
    background: rgba(255,255,255,0.12);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0px 5px 25px rgba(0,0,0,0.4);
    transition: 0.3s;
    backdrop-filter: blur(8px);
}

.card:hover {
    transform: translateY(-5px);
}

.stButton>button {
    background: linear-gradient(to right, #11998e, #38ef7d);
    color: white !important;
    border: none;
    border-radius: 12px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    width: 100%;
}

.stTextInput input,
.stNumberInput input,
textarea {
    background-color: rgba(255,255,255,0.95) !important;
    color: black !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 12px !important;
    color: black !important;
}

.stSelectbox div[data-baseweb="select"] span {
    color: black !important;
    font-weight: 700 !important;
}

.result-box {
    background: linear-gradient(to right, #11998e, #38ef7d);
    padding: 35px;
    border-radius: 25px;
    text-align: center;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.4);
}

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    color: white;
}

.sub-title {
    text-align: center;
    font-size: 22px;
    color: #dfffe0;
    font-weight: 600;
}

.js-plotly-plot .plotly text {
    fill: white !important;
    font-weight: bold !important;
}

[data-testid="stDataFrame"] * {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
        st.session_state.username = ""

if "model_trained" not in st.session_state:
    st.session_state.model_trained = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv("crop_yield.csv")

df = load_data()

# =========================================================
# AGRICULTURE Q&A
# =========================================================

agri_answers = {

    "which crop is suitable for loamy soil":
    "Loamy soil is highly suitable for wheat, maize, sugarcane, cotton, pulses, and vegetables. It contains balanced nutrients and retains moisture effectively. Farmers prefer loamy soil because it supports strong root development and high crop productivity.",

    "which crop grows well in winter season":
    "Wheat, mustard, peas, barley, and gram grow well during winter. These crops require cool temperatures and moderate irrigation for healthy growth. Winter crops are commonly called Rabi crops in India.",

    "best crop for high rainfall areas":
    "Rice is one of the best crops for high rainfall regions. It requires continuous water supply and humid weather for proper growth. Clayey soil and monsoon climate are highly suitable for rice farming.",

    "which crop needs less water":
    "Millets, pulses, sorghum, and groundnut require less water compared to crops like rice and sugarcane. These drought-resistant crops are suitable for dry regions and help conserve water.",

    "how to improve soil fertility":
    "Soil fertility can be improved by using organic manure, compost, crop rotation, and biofertilizers. Soil testing also helps farmers understand nutrient deficiencies and improve soil health effectively."
}

# =========================================================
# CROP RECOMMENDATION
# =========================================================

def recommend_crop(soil, season, rainfall):

    soil = soil.lower()
    season = season.lower()

    if soil == "loamy" and season == "winter":
        return "🌾 Wheat"

    elif soil == "clayey" and rainfall > 1200:
        return "🌾 Rice"

    elif soil == "black":
        return "🧵 Cotton"

    elif soil == "sandy":
        return "🥜 Groundnut"

    elif season == "summer":
        return "🌽 Maize"

    else:
        return "🌱 Millets"
#ADMIN PAGE
def admin_login_page():

    st.title("👨‍💼 Admin Login")

    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")

    if st.button("Admin Login"):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM admins WHERE username=%s",
            (username,)
        )

        admin = cursor.fetchone()

        cursor.close()
        conn.close()

        if admin:

            stored_hash = admin[0]

            if bcrypt.checkpw(
                password.encode(),
                stored_hash.encode()
            ):

                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.role = "admin"
                st.session_state.username = username

                st.success("Admin Login Successful")
                st.rerun()

        st.error("Invalid Admin Credentials")
# =========================================================
# LOGIN PAGE
# =========================================================
def login_page():

    st.markdown(
        "<div class='main-title'>🌾 Crop Yield Prediction System</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sub-title'>AI Powered Agriculture Application</div>",
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.2,1])

    with col2:

        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )

            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:

                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = username

                time.sleep(1)

                st.rerun()

            else:
                st.error("Invalid Username or Password")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    st.sidebar.title("🌾 Crop AI")

    page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Train Model",
        "Prediction",
        "Prediction History",
        "AI Assistant",
        "Logout"
    ]
)

    return page

# =========================================================
# DASHBOARD
# =========================================================

def dashboard_page():

    st.markdown(
        "<div class='main-title'>📊 Dashboard</div>",
        unsafe_allow_html=True
    )

    total_crops = df["Crop"].nunique()
    total_states = df["State"].nunique()
    avg_yield = round(df["Yield"].mean(), 2)
    best_crop = df.groupby("Crop")["Yield"].mean().idxmax()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class='card'>
        <h2>🌾</h2>
        <h1>{total_crops}</h1>
        <p>Total Crops</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='card'>
        <h2>🗺️</h2>
        <h1>{total_states}</h1>
        <p>Total States</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='card'>
        <h2>📈</h2>
        <h1>{avg_yield}</h1>
        <p>Average Yield</p>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class='card'>
        <h2>🏆</h2>
        <h1>{best_crop}</h1>
        <p>Best Crop</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # BAR CHART

    top_crop = (
        df.groupby("Crop")["Yield"]
        .mean()
        .sort_values(ascending=True)
        .tail(10)
    )

    fig1 = px.bar(
        x=top_crop.values,
        y=top_crop.index,
        orientation='h',
        text=top_crop.values,
        title="🌾 Top 10 Crops by Yield"
    )

    fig1.update_layout(
        paper_bgcolor='rgba(0,0,0,0.35)',
        plot_bgcolor='rgba(0,0,0,0.25)',
        font=dict(color='white', size=14)
    )

    st.plotly_chart(fig1, width='stretch')

    # YEARLY PRODUCTION

    yearly = (
        df.groupby("Crop_Year")["Production"]
        .sum()
        .reset_index()
    )

    fig2 = px.line(
        yearly,
        x="Crop_Year",
        y="Production",
        markers=True,
        title="📈 Yearly Production Trend"
    )

    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0.35)',
        plot_bgcolor='rgba(0,0,0,0.25)',
        font=dict(color='white', size=14)
    )

    st.plotly_chart(fig2, width='stretch')

    # SEASON PIE CHART

    season_data = (
        df["Season"]
        .value_counts()
        .reset_index()
    )

    season_data.columns = ["Season", "Count"]

    fig3 = px.pie(
        season_data,
        names="Season",
        values="Count",
        title="🌦️ Crop Distribution by Season",
        hole=0.4
    )

    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0.35)',
        font=dict(color='white', size=14)
    )

    st.plotly_chart(fig3, width='stretch')

    st.subheader("📋 Dataset Preview")

    st.dataframe(df.head(10), width='stretch')

# =========================================================
# TRAIN MODEL PAGE
# =========================================================

def train_model_page():

    st.markdown(
        "<div class='main-title'>🤖 Train Model</div>",
        unsafe_allow_html=True
    )

    if st.button("Train Model"):

        progress = st.progress(0)

        for i in range(100):
            time.sleep(0.02)
            progress.progress(i + 1)

        data = df.copy()

        crop_encoder = LabelEncoder()
        season_encoder = LabelEncoder()
        state_encoder = LabelEncoder()

        data["Crop"] = crop_encoder.fit_transform(data["Crop"])
        data["Season"] = season_encoder.fit_transform(data["Season"])
        data["State"] = state_encoder.fit_transform(data["State"])

        X = data.drop("Yield", axis=1)
        y = data["Yield"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        pickle.dump(model, open("model.pkl", "wb"))

        st.session_state.model = model
        st.session_state.crop_encoder = crop_encoder
        st.session_state.season_encoder = season_encoder
        st.session_state.state_encoder = state_encoder

        st.session_state.model_trained = True

        st.success("✅ Model Trained Successfully")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("R² Score", round(r2, 2))
        c2.metric("MAE", round(mae, 2))
        c3.metric("MSE", round(mse, 2))
        c4.metric("RMSE", round(rmse, 2))

# =========================================================
# PREDICTION PAGE
# =========================================================

def prediction_page():

    st.markdown(
        "<div class='main-title'>🌾 Yield Prediction</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.model_trained:

        st.warning("⚠️ Please Train the Model First")
        return

    model = st.session_state.model

    crop_encoder = st.session_state.crop_encoder
    season_encoder = st.session_state.season_encoder
    state_encoder = st.session_state.state_encoder

    col1, col2 = st.columns(2)

    with col1:

        crop = st.selectbox(
            "Crop",
            sorted(df["Crop"].unique())
        )

        year = st.number_input(
            "Crop Year",
            1990,
            2035,
            2025
        )

        season = st.selectbox(
            "Season",
            sorted(df["Season"].unique())
        )

        state = st.selectbox(
            "State",
            sorted(df["State"].unique())
        )

        soil = st.selectbox(
            "Soil Type",
            ["Loamy", "Clayey", "Black", "Sandy"]
        )

        area = st.number_input(
            "Area",
            min_value=0.0,
            value=1000.0
        )

    with col2:

        production = st.number_input(
            "Production",
            min_value=0.0,
            value=1000.0
        )

        rainfall = st.number_input(
            "Annual Rainfall",
            min_value=0.0,
            value=1000.0
        )

        fertilizer = st.number_input(
            "Fertilizer",
            min_value=0.0,
            value=500.0
        )

        pesticide = st.number_input(
            "Pesticide",
            min_value=0.0,
            value=100.0
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Predict Yield"):
       crop_encoded = crop_encoder.transform([crop])[0]
    season_encoded = season_encoder.transform([season])[0]
    state_encoded = state_encoder.transform([state])[0]

    input_data = np.array([[
        crop_encoded,
        year,
        season_encoded,
        state_encoded,
        area,
        production,
        rainfall,
        fertilizer,
        pesticide
    ]])

    # CREATE prediction FIRST
    prediction = model.predict(input_data)[0]

    # THEN save to database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions
        (username, crop, state_name, predicted_yield)
        VALUES (%s, %s, %s, %s)
    """, (
        st.session_state.username,
        crop,
        state,
        float(prediction)
    ))

    conn.commit()
    cursor.close()
    conn.close()

    # THEN recommendation
    recommended_crop = recommend_crop(
        soil,
        season,
        rainfall
    )
    if prediction < 1:
            category = "Low Yield"

    elif prediction < 3:
            category = "Medium Yield"

    else:
            category = "High Yield"

    st.markdown(f"""
        <div class='result-box'>

        <h1>🌾 Prediction Result</h1>

        <h2>Predicted Yield: {prediction:.2f}</h2>

        <h3>📈 Yield Category: {category}</h3>

        <h3>🌱 Recommended Crop: {recommended_crop}</h3>

        </div>
        """, unsafe_allow_html=True)

# =========================================================
# PREDICTION HISTORY
# =========================================================

def prediction_history_page():

    st.markdown(
        "<div class='main-title'>📜 Prediction History</div>",
        unsafe_allow_html=True
    )

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT crop,
                   state_name,
                   predicted_yield,
                   prediction_date
            FROM predictions
            WHERE username=%s
            ORDER BY prediction_date DESC
        """, (st.session_state.username,))

        records = cursor.fetchall()

        cursor.close()
        conn.close()

        if records:

            history_df = pd.DataFrame(
                records,
                columns=[
                    "Crop",
                    "State",
                    "Predicted Yield",
                    "Date"
                ]
            )

            st.dataframe(
                history_df,
                use_container_width=True
            )

            # =========================
            # PDF DOWNLOAD
            # =========================

            pdf_buffer = io.BytesIO()

            doc = SimpleDocTemplate(pdf_buffer)

            table_data = [history_df.columns.tolist()] + history_df.values.tolist()

            table = Table(table_data)

            table.setStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])

            doc.build([table])

            pdf_buffer.seek(0)

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_buffer.getvalue(),
                file_name="prediction_history.pdf",
                mime="application/pdf"
            )

        else:
            st.info("No prediction history found.")

    except Exception as e:
        st.error(f"Error: {e}")

# =========================================================
# AI ASSISTANT PAGE
# =========================================================
def ai_assistant_page():

    st.markdown(
        "<div class='main-title'>🤖 AI Agriculture Assistant</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sub-title'>Ask agriculture related questions</div>",
        unsafe_allow_html=True
    )

    question = st.text_area(
        "Enter Your Question",
        placeholder="Example: Which crop grows well in winter season?"
    )

    if st.button("💬 Get Answer"):

        question = question.strip().lower()

        if question == "":
            st.warning("Please enter a question.")

        else:

            found = False

            for q, ans in agri_answers.items():

                if question in q.lower():

                    st.markdown(f"""
                    <div class='result-box'>

                    <h2>{q.title()}</h2>

                    <p style='font-size:18px; line-height:1.8;'>
                    {ans}
                    </p>

                    </div>
                    """, unsafe_allow_html=True)

                    found = True
                    break

            if not found:

                st.markdown("""
                <div class='result-box'>

                <h2>🌾 Agriculture Assistant</h2>

                <p style='font-size:18px; line-height:1.8;'>
                Sorry, this question is not available in the offline database.
                Please ask agriculture related questions.
                </p>

                </div>
                """, unsafe_allow_html=True)
            

# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard():

    st.title("👨‍💼 Admin Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Total Users", total_users)

    with c2:
        st.metric("Total Predictions", total_predictions)

    st.subheader("Registered Users")

    users_df = pd.read_sql(
        "SELECT id, username FROM users",
        conn
    )

    st.dataframe(users_df)

    st.subheader("Prediction Records")

    pred_df = pd.read_sql(
        "SELECT * FROM predictions",
        conn
    )

    st.dataframe(pred_df)

    cursor.close()
    conn.close()

# =========================================================
# MAIN APP
# =========================================================

if not st.session_state.logged_in:

    login_page()

else:

    page = sidebar()

    if page == "Dashboard":
        dashboard_page()

    elif page == "Train Model":
        train_model_page()

    elif page == "Prediction":
        prediction_page()

    elif page == "Prediction History":
        prediction_history_page()

    elif page == "AI Assistant":
        ai_assistant_page()

    elif page == "Logout":

        st.session_state.logged_in = False
        st.session_state.model_trained = False
        st.rerun()