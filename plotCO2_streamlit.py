import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import linregress
import csv
from datetime import datetime

uploaded = st.file_uploader("Upload a CSV", type="csv")

if uploaded:
    # Decode bytes → text
    text = uploaded.read().decode("utf-8").splitlines()

    reader = csv.DictReader(text)
    column_headers=reader.fieldnames
    print(column_headers)
    time_col_label=column_headers[0]
    st.write('time column is',time_col_label)
    CO2_col_label='Carbon dioxide(ppm)'
    t_s = []
    CO2s = []
    for row in reader:
        # Parse the datetime string
        if(time_col_label == 'Time(DD/MM/YYYY H:mm)'):
            dt = datetime.strptime(row[time_col_label], "%d/%m/%Y %H:%M")
        elif(time_col_label == 'Time(H:mm:ss)'):
            dt = datetime.strptime(row[time_col_label], "%H:%M:%S")
        elif(time_col_label == 'Time(DD/MM/YYYY H:mm:ss)'):
            dt = datetime.strptime(row[time_col_label], "%Y-%m-%d %H:%M:%S")
            
        # Compute seconds since midnight
        seconds = (
            dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds()
        #st.write(seconds)
        t_s.append(seconds)
        CO2s.append(row['Carbon dioxide(ppm)'])
    t_s=np.array(t_s,dtype=float)
    CO2s=np.array(CO2s,dtype=float)
#    for i in range(0,len(t_s)):
#        print(t_s[i]/3600.0,CO2s[i])
#    st.write(CO2s.dtype)
    '''
    plot day's data
    '''
    # Plot
    fig, ax = plt.subplots(figsize=(5,3))
#    plt.xlim(pd.Timestamp(start_time),
#         pd.Timestamp(end_time))
    st.write('read in ',len(t_s),' data points')
    ax.scatter(t_s/3600.0, CO2s,color="black")#, s=30)
    ax.set_xlabel('time /hour')
    ax.set_ylabel('CO2   /ppm')
    #ax.set_title(f"{CO2_col_label} vs {time_col_label}")
#    plt.ylim([0,2000])
#    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    '''
    fit
    '''
    # Define the start and end limits using datetime objects
    start_hour = st.number_input(
    "hour to start range for fitting",
    min_value=0.0,
    max_value=24.0,
    step=0.1,
    format="%.1f"
    )
    end_hour = st.number_input(
    "hour to end range for fitting",
    min_value=0.0,
    max_value=24.0,
    step=0.1,
    format="%.1f"
    )
    if st.button("fit!"):
        st.write(r'All models are wrong, but some are useful - George Box ')
        start_time = start_hour*3600
        end_time = end_hour*3600
        t_fit_s=[]
        CO2_fit=[]
        for i in range(0,len(t_s)):
            if(t_s[i] > start_time-1.0e-3 and t_s[i] < end_time + 1.0e-3):
                t_fit_s.append(t_s[i])
                CO2_fit.append(CO2s[i])
        t_fit_s=np.array(t_fit_s)
        CO2_fit=np.array(CO2_fit)
        st.write('fitting to ',len(t_fit_s),' data points')
        # ---------------------------------------------------------
        # Fit of straight line
        # ---------------------------------------------------------
        result = linregress(t_fit_s, CO2_fit)
#        st.write(result)
        inter=result.intercept
        # convert slope to ppm/h from ppm/s
        slope_h=result.slope*3600.0
        # convert
        err_est_slope=result.stderr*3600.0
        st.write('fit of straight line to data over specified range')
        st.write('slope ',round(slope_h,1),' ppm CO2 per hour +/-',round(err_est_slope,1),' ppm per hour')
        # intercept
        err_est_intercept=result.intercept_stderr
        st.write('intercept ',round(inter),' ppm CO2 +/-',round(err_est_intercept),' ppm')
        CO2_fit_line = inter+(slope_h/3600.0)*t_fit_s
#
        # Plot
        fig, ax = plt.subplots(figsize=(5,3))

        ax.scatter(t_s/3600.0, CO2s, color="black", s=30)
        ax.set_xlabel('time /hour')
        ax.set_ylabel('CO2 /ppm')
#        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # e.g., 01:00, 14:30
        #ax.set_title(f"{CO2_col_label} vs {time_col_label}")

        plt.xticks(rotation=45)
        # now plot fit
        ax.plot(t_fit_s/3600.0, CO2_fit_line, 
    #            label=f"Fit: y = {a:.3g} exp({b:.3g} t)", 
            color="red", linewidth=2)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    

    st.write('Richard Sear, Jan 2026')
    st.markdown("[Streamlit (Python) code from GitHub](https://github.com/RichardSear/streamlit-appCO2plotting)")
   
