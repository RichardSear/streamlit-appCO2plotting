import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import linregress
import csv
from datetime import datetime
from matplotlib.ticker import FuncFormatter

def colon_fmt(x, pos):
    return f"{int(x)}:{int((x % 1) * 100):02d}"

def readinlocalcsv(filename):
    t_s_in = []
    CO2s_in = []
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        column_headers=reader.fieldnames
        print(column_headers)
        time_col_label=column_headers[0]
        #st.write('time column is',time_col_label)
        for row in reader:
            # Parse the datetime string
            if(time_col_label == 'Time(DD/MM/YYYY H:mm)'):
                dt = datetime.strptime(row[time_col_label], "%d/%m/%Y %H:%M")
            elif(time_col_label == 'Time(H:mm:ss)'):
                dt = datetime.strptime(row[time_col_label], "%H:%M:%S")
            elif(time_col_label == 'Time(DD/MM/YYYY H:mm:ss)'):
                dt = datetime.strptime(row[time_col_label], "%Y-%m-%d %H:%M:%S")
            elif(time_col_label == 'Time2(DD/MM/YYYY H:mm:ss)'):
                dt = datetime.strptime(row[time_col_label], "%d/%m/%Y %H:%M:%S")
            elif(time_col_label == 'Time(YYYY-MM-DD H:mm:ss)'):
                dt = datetime.strptime(row[time_col_label], "%Y-%m-%d %H:%M:%S") 
            # Compute seconds since midnight
            seconds = (
            dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)
                    ).total_seconds()
            #st.write(seconds)
            t_s_in.append(seconds)
            CO2s_in.append(row['Carbon dioxide(ppm)'])
    #
    t_s_in=np.array(t_s_in,dtype=float)
    CO2s_in=np.array(CO2s_in,dtype=float)
    return t_s_in,CO2s_in

# Initialize state
if "mode" not in st.session_state:
    st.session_state.mode = "fitting"   # default option

CO2_col_label='Carbon dioxide(ppm)'
#
t_s1,CO2s1 = readinlocalcsv("Du2024schoolCO2.csv")
t_s2,CO2s2 = readinlocalcsv("bedroom_nightCO2.csv")
t_s3,CO2s3 = readinlocalcsv("home_during_day_eveningCO2.csv")
t_s4,CO2s4 = readinlocalcsv("CO2_homethenMorristonhospital.csv")
t_s5,CO2s5 = readinlocalcsv("livingroomCO2.csv")
t_s6,CO2s6 = readinlocalcsv("officeCO2.csv")


choice = st.radio(
    "Choose an option",
    ["school", "bedroom overnight", "home during workday & evening",
     "hospital visit","living room working from home","my office"]
)

st.write("You picked:", choice)

if(choice == 'school'):
    t_s=t_s1
    CO2s=CO2s1
elif(choice == "bedroom overnight"):
    t_s=t_s2
    CO2s=CO2s2
elif(choice == 'home during workday & evening'):
    t_s=t_s3
    CO2s=CO2s3
elif(choice == "hospital visit"):
    t_s=t_s4
    CO2s=CO2s4
elif(choice == "living room working from home"):
    t_s=t_s5
    CO2s=CO2s5
elif(choice == "my office"):
    t_s=t_s6
    CO2s=CO2s6 
#
# Plot
fig, ax = plt.subplots(figsize=(5,2))
#    plt.xlim(pd.Timestamp(start_time),
#         pd.Timestamp(end_time))
st.write('read in ',len(t_s),' data points')
ax.scatter(t_s/3600.0, CO2s,color="black")#, s=30)
ax.set_xlabel('time /hour')
ax.set_ylabel('CO2   /ppm')
ax.xaxis.set_major_formatter(FuncFormatter(colon_fmt))
#plt.xticks(rotation=45)
ax.grid(True, alpha=0.3)
st.pyplot(fig)
# Button toggles the mode
if st.button("Toggle between fitting and computing fraction 2nd hand air"):
    st.session_state.mode = "infection risk" if st.session_state.mode == "fitting" else "fitting"
st.write("Current option:", st.session_state.mode)
if(st.session_state.mode == "fitting" ):
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
        st.write('fitting to ',len(t_fit_s),' data points NB should be at least 5')
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
        st.write('intercept ',round(inter),' ppm CO2 +/-',round(err_est_intercept),' ppm CO2')
        # fit line for plotting and for residuals
        CO2_fit_line = inter+(slope_h/3600.0)*t_fit_s
        # residuals
        residuals=CO2_fit_line-CO2_fit
        std_err_residuals=np.sqrt(np.sum(residuals**2)/(len(residuals)-2.0))
        st.write('standard error of fit ',round(std_err_residuals),' ppm CO2 (smaller the better the fit)')
        st.write('NB above figures after +/- are the uncertainties in the best value of slope/intercept')
#
        # Plot
        fig, ax = plt.subplots(figsize=(5,2))
        ax.scatter(t_s/3600.0, CO2s, color="black", s=30)
        ax.set_xlabel('time /hour')
        ax.set_ylabel('CO2 /ppm')
#        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # e.g., 01:00, 14:30
        #ax.set_title(f"{CO2_col_label} vs {time_col_label}")
        ax.xaxis.set_major_formatter(FuncFormatter(colon_fmt))
        #plt.xticks(rotation=45)
        # now plot fit
        ax.plot(t_fit_s/3600.0, CO2_fit_line, 
#            label=f"Fit: y = {a:.3g} exp({b:.3g} t)", 
        color="red", linewidth=2)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
else:
    # Plot
    fig, ax = plt.subplots(figsize=(5,2))
    ax.scatter(t_s/3600.0, (CO2s-410)/4.0e4 *100, color="green", s=30)
    ax.set_xlabel('time /hour')
    ax.set_ylabel('% 2nd hand')
#        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # e.g., 01:00, 14:30
    #ax.set_title(f"{CO2_col_label} vs {time_col_label}")
    ax.xaxis.set_major_formatter(FuncFormatter(colon_fmt))
    #plt.xticks(rotation=45)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    # now
    start_hour_averaging = st.number_input(
    "hour to start hour long period to average over",
    min_value=0.0,
    max_value=24.0,
    value=10.0,
    step=0.1,
    format="%.1f"
    )
    CO2_av=[]
    for i in range(0,len(t_s)):
        if(t_s[i] > start_hour_averaging*3600-1.0e-3 
            and t_s[i] < (start_hour_averaging+1.0)*3600 + 1.0e-3):
            CO2_av.append(CO2s[i])
    st.write('averaging over  ',len(CO2_av),' data points')
    avCO2=np.mean(np.array(CO2_av))
    st.write('mean CO2 ',round(avCO2),' ppm')
    st.write('mean 2nd hand fraction ',round(100*(avCO2-410.0)/4.0e4,1),' %')

    st.write('Richard Sear, Jan 2026')
    st.markdown("[Streamlit (Python) code from GitHub](https://github.com/RichardSear/streamlit-appCO2plotting)")
    st.markdown("[homepage for schools event this was written for](https://richardsear.me/schools-event-homepage-co2-flu-covid-you/)")
