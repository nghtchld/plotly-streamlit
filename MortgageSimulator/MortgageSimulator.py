# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 17:12:17 2021
@author: Teo Bee Guan
Updated on Wed Jan 19 2022
@author: nghtchld
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import numpy_financial as npf

st.set_page_config(layout="wide", 
    page_title="Loan Repayment Simulator")

st.title("Mortgage and Loan Repayment Simulator")
st.text('Compare your loan repayments under various scenarios.')

# **Sidebar**
#st.subheader("Loan Value")
home_value = st.sidebar.slider("Enter your loan value($): ", min_value=100000, max_value=1500000, step=5000, value=552000, format='%f')

#st.subheader("Loan Interest Rate")
interest_rate = st.sidebar.slider("Enter your loan interest rate(%): ", min_value=1.0, max_value=10.0, step=0.01, value=2.37, format='%f')

#st.subheader("Minimum LVR (down payment percent")
down_payment_percent = st.sidebar.slider("Enter your down payment percent(%): ", min_value=5.0, max_value=50.0, value=0.0, format='%f')

#st.subheader("Target Payment Period (Years)")
payment_years = st.sidebar.slider("Enter your target payment period (years): ", min_value=3, max_value=30, step=1, value=30, format='%d')

#st.subheader("Payment Frequency")
payment_frequency = st.sidebar.selectbox("Enter your periodic payment frequency (from list): ", ('Monthly','Fortnightly','Weekly'), index = 1) 


# Input variable processing and calculations
down_payment = home_value* (down_payment_percent / 100)
loan_amount = home_value - down_payment
interest_rate = interest_rate / 100

# calculates number of repayments using one year as 365.25 days or 12 months. 
# TODO improve this to use proper datetime functions so we can get dates on visuals
# TODO when datetime functions are added then also add a starting date input field
# TODO when datetime functions are added then also add time to pay of in YY-MM and end date to the # **Outputs** section below 
if payment_frequency == 'Monthly':
    period = 'Month'
    annual_periods = 12
    payment_length = payment_years * annual_periods
elif payment_frequency == 'Fortnightly':
    period = 'Fortnight'
    annual_periods = round(365.25 / 14, 2)
    payment_length = int(round(payment_years * 365.25 / 14, 0))
elif payment_frequency == 'Weekly':
    period = 'Week'
    annual_periods = round(365.25 / 7, 2)
    payment_length = int(round(payment_years * 365.25 / 7, 0))

periodic_interest_rate = (1+interest_rate)**(1/annual_periods) - 1
periodic_installment = -1*npf.pmt(periodic_interest_rate , payment_length, loan_amount)

# Amortization and repayments visual and table calculations
principal_remaining = np.zeros(payment_length)
interest_pay_arr = np.zeros(payment_length)
principal_pay_arr = np.zeros(payment_length)
total_pay_arr = np.zeros(payment_length)

for i in range(0, payment_length):
    
    if i == 0:
        previous_principal_remaining = loan_amount
    else:
        previous_principal_remaining = principal_remaining[i-1]
        
    interest_payment = round(previous_principal_remaining*periodic_interest_rate, 2)
    principal_payment = round(periodic_installment - interest_payment, 2)
    
    if previous_principal_remaining - principal_payment < 0:
        principal_payment = previous_principal_remaining
    
    interest_pay_arr[i] = interest_payment 
    principal_pay_arr[i] = principal_payment
    principal_remaining[i] = previous_principal_remaining - principal_payment
    total_pay_arr[i] = (i + 1) * principal_payment
    

period_num = np.arange(payment_length)
period_num = period_num + 1

principal_remaining = np.around(principal_remaining, decimals=2)

# Equity and interest totals calculations
cumulative_home_equity = np.cumsum(principal_pay_arr)
cumulative_interest_paid = np.cumsum(interest_pay_arr)


# **Content**
col1, col2 = st.columns([2,4])

with col1:
    st.header("**Loan Details**")

# **Outputs**
    st.subheader(f"Loan Amount: ${int(loan_amount):,}")
    if down_payment > 0:
        st.subheader(f"Down Payment: ${round(down_payment,2):,)}")
    st.subheader(f"{payment_frequency} Installment: ${round(periodic_installment, 2):,}")
    st.subheader(f"Total Interest: ${round(cumulative_interest_paid[-1], 2):,}")
    st.subheader(f"Total Repayment: ${round(cumulative_interest_paid[-1] + cumulative_home_equity[-1], 2):,}")

# **Visuals**
with col2:
    #st.header("**Loan Equity (With Constant Market Value)**")
    
    # Visual: Equity and interest totals calculations
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=period_num, 
            y=total_pay_arr,
            name="Total Repayment"
        )
    )

    fig.add_trace(
            go.Scatter(
                x=period_num, 
                y=cumulative_home_equity,
                name="Cumulative Equity"
            )
        )

    fig.add_trace(
            go.Scatter(
                x=period_num, 
                y=cumulative_interest_paid,
                name="Cumulative Interest Paid"
            )
        )

    fig.update_layout(title='Cumulative Loan Equity Over Time',
                    xaxis_title=period,
                    yaxis_title='Amount($)',
                    height= 500,
                    width = 1200,
                    legend= dict(
                            orientation="v",
                            yanchor='top',
                            y=0.98,
                            xanchor= 'left',
                            x= 0.01
                        )
                    )


    st.plotly_chart(fig, use_container_width=True)


st.markdown("---")


st.header("**Mortgage loan Amortization**")
# Visual: Amortization and individual repayments 
fig = make_subplots(
    rows=1, cols=2,
    vertical_spacing=0.03,
    specs=[
        [{"type": "table"}, {"type": "scatter"}]
        ]
)

fig.add_trace(
        go.Table(
            header=dict(
                    values=['Month', 'Principal Payment($)', 'Interest Payment($)', 'Remaining Principal($)']
                ),
            cells = dict(
                    values =[period_num, principal_pay_arr, interest_pay_arr, principal_remaining]
                )
            ),
        row=1, col=1
    )

fig.add_trace(
        go.Scatter(
                x=period_num,
                y=principal_pay_arr,
                name= "Principal Payment"
            ),
        row=1, col=2
    )

fig.append_trace(
        go.Scatter(
            x=period_num, 
            y=interest_pay_arr,
            name="Interest Payment"
        ),
        row=1, col=2
    )

fig.update_layout(title='Mortgage Installment Payment Over Months',
                xaxis_title=period,
                yaxis_title='Amount($)',
                height= 800,
                width = 1200,
                legend= dict(
                        orientation="v",
                        yanchor='top',
                        y=0.98,
                        xanchor= 'left',
                        x= 0.58
                    )
                )

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# Asset value growth visual
st.header("**Forecast Asset Value Growth**")

st.subheader("Forecast Growth (Per Year)")
forecast_growth = st.number_input("Enter your forecast growth rate(%): ",  format='%f')

growth_per_month = (forecast_growth / 12.0) / 100 
growth_array = np.full(payment_length, growth_per_month)
forecast_cumulative_growth = np.cumprod(1+growth_array)
forecast_home_value= home_value*forecast_cumulative_growth
cumulative_percent_owned = (down_payment_percent/100) + (cumulative_home_equity/home_value)
forecast_home_equity = cumulative_percent_owned*forecast_home_value

fig = go.Figure()
fig.add_trace(
        go.Scatter(
            x=period_num, 
            y=forecast_home_value,
            name="Forecast Home Value"
        )
    )

fig.add_trace(
        go.Scatter(
            x=period_num, 
            y=forecast_home_equity,
            name="Forecast Home Equity Owned"
        )
    )

fig.add_trace(
        go.Scatter(
            x=period_num, 
            y=principal_remaining,
            name="Remaining Principal"
        )
    )

fig.update_layout(title='Forecast Home Value Vs Forecast Home Equity Over Time',
                   xaxis_title='Month',
                   yaxis_title='Amount($)',
                   height= 500,
                   width = 1200,
                   legend= dict(
                           orientation="h",
                           yanchor='top',
                           y=1.14,
                           xanchor= 'left',
                           x= 0.01
                       )
                  )

st.plotly_chart(fig, use_container_width=True)
