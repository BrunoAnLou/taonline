import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.app_logo import add_logo
import time
from datetime import datetime


def logo():
    add_logo('C:\\Users\\p739492\\Projetos\\TA_ONLINE\\logo-1-1.3.png', height=50)
    
def cores_sidebar():
    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                    background-color:#04014F;
            }

            .st-emotion-cache-pkbazv {
                    color: #FFFFFF
            }
            
            .st-emotion-cache-17lntkn {
                    color: #FFFFFF            
            }  
        </style>
        """, unsafe_allow_html=True
    )

    st.sidebar.markdown('<div style="position: fixed; bottom: 35px; width: 90%; color: white; font-size: 12px;"> @Planejamento Plansul</div', unsafe_allow_html=True)
    st.sidebar.markdown('<div style="position: fixed; bottom: 20px; width: 90%; color: white; font-size: 12px"></div', unsafe_allow_html=True)








