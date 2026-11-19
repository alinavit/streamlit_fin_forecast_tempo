import change_forecast
import cheat_cheet
import streamlit as st

page = st.sidebar.radio(
    "Menu",
    ["Change Expected Costs By Department", "cheat sheet"]
)


if __name__ == "__main__":
    if page == "Change Expected Costs By Department":
        change_forecast.run_change_forecast_page()
    elif page == "cheat sheet" :
        cheat_cheet.home()

