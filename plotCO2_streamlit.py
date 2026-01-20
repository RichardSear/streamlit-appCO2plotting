import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit
from scipy.stats import linregress

# ---------------------------------------------------------
# 4. Define exponential model
# ---------------------------------------------------------
def exp_model(t, a, b, c):
    return a * np.exp(-t/b) + c

def pandas_to_xy_for_fitting(start_time_dtformat,end_time_dtformat):
    # ---------------------------------------------------------
    # 2. Filter to the requested time window
    # ---------------------------------------------------------
    times=df[time_col_label]
    mask = (times >= start_time) & (times <= end_time)
    df_fit = df.loc[mask].copy()
    # ---------------------------------------------------------
    # 3. Convert datetime to numeric (hours since start of window)
    # ---------------------------------------------------------
    t0 = df_fit[time_col_label].min()
    t_hs = (df_fit[time_col_label] - t0).dt.total_seconds() / 3600.0
    y = df_fit[CO2_col_label].values
    #
    # Convert numeric axis back to datetime for plotting
    t_fit = np.linspace(t_hs.min(), t_hs.max(), 300)
    t_fit_dt = t0 + pd.to_timedelta(t_fit, unit="h")
    # now return
    return t_hs,y,t_fit,t_fit_dt

st.title("CSV Plotter with Datetime X‑Axis")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Load CSV
    df = pd.read_csv(uploaded_file)
    time_col_label = df.columns[0]
#    st.write('first column heading ',time_col_label)
    CO2_col_label=df.columns[1]
#    st.write('CO2 column label ',CO2_col_label)
    df[time_col_label] = pd.to_datetime(df[time_col_label], format="%Y-%m-%d %H:%M:%S")
    st.write("Preview of uploaded data:")
    st.write(df.head())
    '''
    plot day's data
    '''
    # Plot
    fig, ax = plt.subplots(figsize=(5,3))
    start_time = dt.datetime(2026, 1, 16, 9)
    end_time = dt.datetime(2026, 1, 16, 23)
    plt.xlim(pd.Timestamp(start_time),
         pd.Timestamp(end_time))
    ax.scatter(df[time_col_label], df[CO2_col_label], 
               label="Data", color="black", s=30)
    ax.set_xlabel('time')
    ax.set_ylabel(CO2_col_label)
    #ax.set_title(f"{CO2_col_label} vs {time_col_label}")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # e.g., 01:00, 14:30
    plt.xticks(rotation=45)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    '''
    fit
    '''
    # Define the start and end limits using datetime objects
    start_hour = st.number_input(
    "hour to start range for fitting (must be integer)",
    min_value=0,
    max_value=100000,
    step=1,
    format="%d"
    )
    end_hour = st.number_input(
    "hour to end range for fitting (must be integer)",
    min_value=0,
    max_value=100000,
    step=1,
    format="%d"
    )
    if st.button("fit!"):
        st.write(r'All models are wrong, but some are useful - George Box ')
        start_time = dt.datetime(2026, 1, 16, start_hour)
        end_time = dt.datetime(2026, 1, 16, end_hour)

        t_h,CO2s,t_fit,t_fit_dt=pandas_to_xy_for_fitting(start_time,end_time)

    # ---------------------------------------------------------
    # 5. Fit of exponential
    # ---------------------------------------------------------
        popt, pcov = curve_fit(exp_model, t_h, CO2s, p0=(100.0, 2.0,400))
#
        relax_time_h=popt[1]
        #print(pcov)
        err_est_h=np.sqrt(pcov[1,1])
        st.write('relaxation time ',round(relax_time_h,2),' h +/-',round(err_est_h,2))
        steady_state_CO2=popt[2]
        err_est_SS=np.sqrt(pcov[0,0])
        st.write('steady state CO2 ',round(steady_state_CO2),' ppm +/-',round(err_est_SS))
        delta_CO2=popt[0]
        err_est_delta=np.sqrt(pcov[2,2])
        st.write('Delta CO2 ',round(delta_CO2),' ppm +/-',round(err_est_delta))
        CO2_fit1 = exp_model(t_fit, delta_CO2, relax_time_h, steady_state_CO2)
        # ---------------------------------------------------------
        # Fit of straight line
        # ---------------------------------------------------------
        result = linregress(t_h, CO2s)
        st.write(result)
        inter=result.intercept
        slope_h=result.slope
        #
        err_est_slope=result.stderr
        st.write('slope ',round(slope_h,1),' ppm CO2 per h +/-',round(err_est_slope,1))
        CO2_fit2 = inter+slope_h*t_fit
#
        # Plot
        fig, ax = plt.subplots(figsize=(5,3))
        start_time = dt.datetime(2026, 1, 16, 9)
        end_time = dt.datetime(2026, 1, 16, 23)
        plt.xlim(pd.Timestamp(start_time),
        pd.Timestamp(end_time))
        ax.scatter(df[time_col_label], df[CO2_col_label], 
                label="Data", color="black", s=30)
        ax.set_xlabel('time')
        ax.set_ylabel(CO2_col_label)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # e.g., 01:00, 14:30

        #ax.set_title(f"{CO2_col_label} vs {time_col_label}")

        plt.xticks(rotation=45)
        # now plot fit
        ax.plot(t_fit_dt, CO2_fit1, 
    #            label=f"Fit: y = {a:.3g} exp({b:.3g} t)", 
            color="red", linewidth=2)
        ax.plot(t_fit_dt, CO2_fit2, 
#            label=f"Fit: y = {a:.3g} exp({b:.3g} t)", 
            color="blue", linewidth=2)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    

    st.write('Richard Sear, Jan 2026')
    st.markdown("[Streamlit (Python) code from GitHub](https://github.com/RichardSear/Stokes-Einstein-D-calc)")
