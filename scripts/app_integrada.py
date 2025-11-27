import streamlit as st

# 1) Configuració de la pàgina: wide mode
st.set_page_config(layout="wide")

from subapps import app
from subapps import app_boxplot

def main():
    opcions = ["GEN Explorer", "GEN Boxplots"]
    eleccio = st.sidebar.radio("Pàgines:", opcions, index=0)

    if eleccio == "GEN Explorer":
        app.main()
    else:
        app_boxplot.main()

if __name__ == "__main__":
    main()