import streamlit as st
import pandas as pd
from abacusai import PredictionClient
import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# SQL Server connection parameters
SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Dummy credentials for demonstration purposes
# In production, use a secure method for handling credentials
USER_CREDENTIALS = {
    "Adarsh": "password1",
    "admin": "password123",
    "user2": "password2",
    # Add more users as needed
}

def check_login(username, password):
    """
    Validate user credentials.
    """
    return USER_CREDENTIALS.get(username) == password

def login_ui():
    """
    Display the login interface.
    """
    st.title("Login Page")
    st.markdown("Please enter your username and password to continue.")
    
    # Create a form for login
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
    
    if login_button:
        if check_login(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}! You have successfully logged in.")
            # Rerun to refresh the UI after login
            st.experimental_rerun()
        else:
            st.error("Invalid username or password. Please try again.")

def create_table_if_not_exists():
    """
    Create necessary tables in the SQL Server database if they do not exist.
    """
    try:
        conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        )
        cursor = conn.cursor()

        # SQL statements to create tables if they don't exist
        create_yield_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='yield_prediction' AND xtype='U')
        CREATE TABLE yield_prediction (
            id INT IDENTITY(1,1) PRIMARY KEY,
            Debtor INT,
            Revaluation_of_the_fall_ NVARCHAR(3),
            Aluminum____ FLOAT,
            Heavy_Metals____ FLOAT,
            Waste____ FLOAT,
            Particle_Size__Coarse___ FLOAT,
            Quality_Score FLOAT,
            Weight__tons_ FLOAT,
            Final_Payment FLOAT,
            Initial_Aluminum____ FLOAT,
            Initial_Heavy_Metals____ FLOAT,
            Vendor_Quality_History FLOAT,
            Processing_Efficiency____ FLOAT,
            Predicted_Yield FLOAT,
            Prediction_Result FLOAT
        )
        """

        create_supply_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='supply_forecasting' AND xtype='U')
        CREATE TABLE supply_forecasting (
            id INT IDENTITY(1,1) PRIMARY KEY,
            Processing_Efficiency FLOAT,
            Initial_Heavy_Metals FLOAT,
            Initial_Sand FLOAT,
            Initial_Ash FLOAT,
            Vendor_Quality_History FLOAT,
            Vendor_Consistency FLOAT,
            Debit_EUR FLOAT,
            Prediction_Result FLOAT
        )
        """

        create_demand_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='demand_forecasting' AND xtype='U')
        CREATE TABLE demand_forecasting (
            id INT IDENTITY(1,1) PRIMARY KEY,
            Processing_Efficiency FLOAT,
            Vendor_Quality_History FLOAT,
            Vendor_Consistency FLOAT,
            Credit_EUR FLOAT,
            Aluminum_Percentage FLOAT,
            Heavy_Metals_Percentage FLOAT,
            Prediction_Result FLOAT
        )
        """

        # Execute table creation queries
        cursor.execute(create_yield_table_sql)
        cursor.execute(create_supply_table_sql)
        cursor.execute(create_demand_table_sql)
        conn.commit()

        cursor.close()
        conn.close()
        st.success("Database tables are set up successfully.")
    except Exception as e:
        st.error(f"Error creating tables: {str(e)}")

def save_to_database(data, table_name):
    """
    Save the provided data dictionary to the specified table in the database.
    """
    try:
        conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        )
        cursor = conn.cursor()

        # Prepare the SQL INSERT statement
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        # Execute the INSERT statement with data values
        cursor.execute(sql, list(data.values()))
        conn.commit()

        cursor.close()
        conn.close()
        st.success(f"Data successfully saved to {table_name} table.")
    except Exception as e:
        st.error(f"Error saving data to database: {str(e)}")

def yield_prediction(client):
    """
    Handle Yield Prediction functionality.
    """
    with st.form(key="yield_form"):
        st.subheader("Yield Prediction Inputs")
        debtor = st.number_input("Debtor", value=101420)
        revaluation = st.selectbox("Revaluation of the fall", ["Yes", "No"])
        aluminum = st.number_input("Aluminum (%)", value=0.94677069, format="%.8f")
        heavy_metals = st.number_input("Heavy Metals (%)", value=0.522112512, format="%.8f")
        waste = st.number_input("Waste (%)", value=17.93416494, format="%.8f")
        particle_size = st.number_input("Particle Size (Coarse %)", value=62.53498913, format="%.8f")
        quality_score = st.number_input("Quality Score", value=1.430019099, format="%.9f")
        weight = st.number_input("Weight (tons)", value=6.034453448, format="%.9f")
        final_payment = st.number_input("Final Payment", value=245.7865421, format="%.7f")
        initial_aluminum = st.number_input("Initial Aluminum (%)", value=86.73194899, format="%.8f")
        initial_heavy_metals = st.number_input("Initial Heavy Metals (%)", value=6.268629711, format="%.9f")
        vendor_quality_history = st.number_input("Vendor Quality History", value=0.476514816, format="%.9f")
        processing_efficiency = st.number_input("Processing Efficiency (%)", value=84.10809734, format="%.8f")
        predicted_yield = st.number_input("Predicted Yield", value=0.859382026, format="%.9f")

        # Submit button
        submitted = st.form_submit_button("Make Yield Prediction")

        if submitted:
            query_data = {
                "Debtor": debtor,
                "Revaluation_of_the_fall_": revaluation,
                "Aluminum____": aluminum,
                "Heavy_Metals____": heavy_metals,
                "Waste____": waste,
                "Particle_Size__Coarse___": particle_size,
                "Quality_Score": quality_score,
                "Weight__tons_": weight,
                "Final_Payment": final_payment,
                "Initial_Aluminum____": initial_aluminum,
                "Initial_Heavy_Metals____": initial_heavy_metals,
                "Vendor_Quality_History": vendor_quality_history,
                "Processing_Efficiency____": processing_efficiency,
                "Predicted_Yield": predicted_yield
            }

            st.subheader("Input Data for Yield Prediction")
            df = pd.DataFrame([query_data])
            st.dataframe(df)

            # Make prediction
            with st.spinner("Predicting..."):
                try:
                    result = client.predict(
                        deployment_token='6ce9c79a7fc64986a07a927e6d034954',
                        deployment_id='f2294f1c',
                        query_data=query_data
                    )
                    yield_value = result.get('Yield____', 0)
                    st.success(f"Yield Prediction result: {yield_value:.6f}")

                    # Add prediction result to query_data
                    query_data["Prediction_Result"] = yield_value

                    # Save data to database
                    save_to_database(query_data, "yield_prediction")
                    st.info("Yield prediction data and result saved to database.")

                except Exception as e:
                    st.error(f"An error occurred during prediction: {str(e)}")

def supply_forecasting(client):
    """
    Handle Supply Forecasting functionality.
    """
    with st.form(key="supply_form"):
        st.subheader("Supply Forecasting Inputs")
        processing_efficiency = st.number_input("Processing Efficiency (%)", value=85.0, format="%.2f")
        initial_heavy_metals = st.number_input("Initial Heavy Metals (%)", value=0.5, format="%.2f")
        initial_sand = st.number_input("Initial Sand (%)", value=0.2, format="%.2f")
        initial_ash = st.number_input("Initial Ash (%)", value=0.1, format="%.2f")
        vendor_quality_history = st.number_input("Vendor Quality History", value=0.8, format="%.2f")
        vendor_consistency = st.number_input("Vendor Consistency", value=0.9, format="%.2f")
        debit_eur = st.number_input("Debit EUR", value=800.0, format="%.2f")

        # Submit button
        submitted_supply = st.form_submit_button("Make Supply Forecasting Prediction")

        if submitted_supply:
            query_data_supply = {
                "Processing_Efficiency": processing_efficiency,
                "Initial_Heavy_Metals": initial_heavy_metals,
                "Initial_Sand": initial_sand,
                "Initial_Ash": initial_ash,
                "Vendor_Quality_History": vendor_quality_history,
                "Vendor_Consistency": vendor_consistency,
                "Debit_EUR": debit_eur
            }

            st.subheader("Input Data for Supply Forecasting")
            df_supply = pd.DataFrame([query_data_supply])
            st.dataframe(df_supply)

            # Make prediction
            with st.spinner("Predicting..."):
                try:
                    result_supply = client.predict(
                        deployment_token='2bd28aeb7feb4f39af5744e84ff7d045',
                        deployment_id='5bd37cb30',
                        query_data=query_data_supply
                    )

                    supply_forecast_value = result_supply.get('Supply____', 0)
                    #st.success(f"Supply Forecasting result: {supply_forecast_value:.6f}")
                    st.write(result_supply)
                    # Add prediction result to query_data_supply
                    query_data_supply["Prediction_Result"] = supply_forecast_value

                    # Save data to database
                    save_to_database(query_data_supply, "supply_forecasting")
                    st.info("Supply forecasting data and result saved to database.")

                except Exception as e:
                    st.error(f"An error occurred during prediction: {str(e)}")

def demand_forecasting(client):
    """
    Handle Demand Forecasting functionality.
    """
    with st.form(key="demand_form"):
        st.subheader("Demand Forecasting Inputs")
        processing_efficiency_demand = st.number_input("Processing Efficiency (%)", value=80.0, format="%.2f")
        vendor_quality_history_demand = st.number_input("Vendor Quality History", value=0.7, format="%.2f")
        vendor_consistency_demand = st.number_input("Vendor Consistency", value=0.85, format="%.2f")
        credit_eur = st.number_input("Credit EUR", value=1000.0, format="%.2f")
        aluminum_percentage = st.number_input("Aluminum Percentage (%)", value=0.8, format="%.2f")
        heavy_metals_percentage = st.number_input("Heavy Metals Percentage (%)", value=0.5, format="%.2f")

        # Submit button
        submitted_demand = st.form_submit_button("Make Demand Forecasting Prediction")

        if submitted_demand:
            query_data_demand = {
                "Processing_Efficiency": processing_efficiency_demand,
                "Vendor_Quality_History": vendor_quality_history_demand,
                "Vendor_Consistency": vendor_consistency_demand,
                "Credit_EUR": credit_eur,
                "Aluminum_Percentage": aluminum_percentage,
                "Heavy_Metals_Percentage": heavy_metals_percentage
            }

            st.subheader("Input Data for Demand Forecasting")
            df_demand = pd.DataFrame([query_data_demand])
            st.dataframe(df_demand)

            # Make prediction
            with st.spinner("Predicting..."):
                try:
                    result_demand = client.predict(
                        deployment_token='1a596afec22b49a3aaa5bee16442bad7',
                        deployment_id='39f0bb614',
                        query_data=query_data_demand
                    )

                    demand_forecast_value = result_demand.get('Demand____', 0)
                    #st.success(f"Demand Forecasting result: {demand_forecast_value:.6f}")
                    st.write(result_demand)

                    # Add prediction result to query_data_demand
                    query_data_demand["Prediction_Result"] = demand_forecast_value

                    # Save data to database
                    save_to_database(query_data_demand, "demand_forecasting")
                    st.info("Demand forecasting data and result saved to database.")

                except Exception as e:
                    st.error(f"An error occurred during prediction: {str(e)}")

def main():
    """
    Main function to run the Streamlit app.
    """
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        # Display the main application
        st.title("RECCO Prediction Interface")

        # Ensure the necessary tables exist in the database
        create_table_if_not_exists()

        # Display the username in the sidebar
        st.sidebar.header(f"Welcome, {st.session_state['username']}!")
        logout_button = st.sidebar.button("Logout")

        if logout_button:
            st.session_state["logged_in"] = False
            st.session_state.pop("username", None)
            st.success("You have been logged out.")
            # Rerun to refresh the UI after logout
            st.experimental_rerun()

        # Sidebar for model selection
        st.sidebar.header("Predicted Models")
        model_type = st.sidebar.radio("Select a model to predict:", ["Yield Prediction", "Supply Forecasting", "Demand Forecasting"])

        # Initialize the PredictionClient
        client = PredictionClient()

        # Display the appropriate model based on user selection
        if model_type == "Yield Prediction":
            yield_prediction(client)
        elif model_type == "Supply Forecasting":
            supply_forecasting(client)
        elif model_type == "Demand Forecasting":
            demand_forecasting(client)
    else:
        # Display the login UI
        login_ui()

if __name__ == "__main__":
    main()
