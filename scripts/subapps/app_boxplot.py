import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_sheets_info(file_paths):
    """
    Carrega només la columna 'Gene' de cada full i retorna:
      - Llista global ordenada de gens
      - Diccionari que mapeja {nom_full: file_path}
    """
    tots_gens = set()
    sheets_info = {}  # Map: nom_full -> file_path
    
    for file_path in file_paths:
        xls = pd.ExcelFile(file_path)
        for nom_full in xls.sheet_names:
            try:
                # Llegim només la columna 'Gene' per evitar carregar tot el full
                df_temp = pd.read_excel(file_path, sheet_name=nom_full, usecols=['Gene'])
            except ValueError:
                # El full pot no tenir la columna 'Gene'
                continue
            df_temp = df_temp.dropna(subset=['Gene'])
            df_temp['Gene'] = df_temp['Gene'].astype(str)
            tots_gens.update(df_temp['Gene'].unique().tolist())
            sheets_info[nom_full] = file_path

    return sorted(tots_gens), sheets_info

@st.cache_data
def load_full_sheet(file_path, sheet_name):
    """
    Carrega el full complet d'un Excel (totes les columnes).
    Retorna un DataFrame amb la columna 'Gene' com a string (si existeix).
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, decimal=",")
    if 'Gene' in df.columns:
        df['Gene'] = df['Gene'].astype(str)
    return df

def main():
    st.title("GEN Boxplots")

    # 1) Rutes dels fitxers Excel
    file_paths = [
        "data/data_normalized_counts.xlsx",
        "data/data_norm_counts_orgs.xlsx"
    ]

    # 2) Carrega la informació mínima (només la columna 'Gene')
    tots_gens, sheets_info = load_sheets_info(file_paths)
    if not sheets_info:
        st.error("No s'han trobat fulles amb la columna 'Gene' als fitxers.")
        return

    # 3) Selecció de gens (a la barra lateral)
    selected_genes = st.sidebar.multiselect(
        "Selecciona gens:",
        tots_gens,
        default=[]
    )

    # 4) Selecció de datasets (a la barra lateral)
    # Ordenem els datasets segons l'ordre fix: iNs, iAs, iPSCs, Fibros, i després la resta (ordenada alfabèticament)
    preferred_order = ["iNs", "iAs", "iPSCs", "Fibros"]
    preferred_datasets = [ds for ds in preferred_order if ds in sheets_info]
    other_datasets = [ds for ds in sheets_info.keys() if ds not in preferred_order]
    other_datasets = sorted(other_datasets)
    all_dataset_names = preferred_datasets + other_datasets

    selected_datasets = st.sidebar.multiselect(
        "Selecciona datasets:",
        all_dataset_names,
        default=all_dataset_names
    )

    # 5) Si no s'ha seleccionat com a mínim un gen i un dataset, no es fa res
    if not selected_genes or not selected_datasets:
        st.info("Selecciona com a mínim un gen i un dataset per veure els boxplots.")
        return

    # 6) Per cada gen seleccionat, es mostren els boxplots de cada dataset en files (màxim 4 per fila)
    for gene in selected_genes:
        st.markdown(f"## Gen: {gene}")
        # Processem els datasets en grups de 4 per crear files
        for i in range(0, len(selected_datasets), 4):
            dataset_chunk = selected_datasets[i:i+4]
            cols = st.columns(len(dataset_chunk))
            for j, dataset_name in enumerate(dataset_chunk):
                with cols[j]:
                    file_path = sheets_info[dataset_name]
                    df_full = load_full_sheet(file_path, dataset_name)
                    
                    if 'Gene' not in df_full.columns:
                        st.warning(f"El dataset **{dataset_name}** no té la columna 'Gene'.")
                        continue

                    # Filtra pel gen seleccionat
                    df_gene = df_full[df_full['Gene'] == gene].copy()
                    if df_gene.empty:
                        st.warning(f"El gen **{gene}** no apareix a **{dataset_name}**.")
                        continue

                    # Transformació a format llarg
                    df_melted = df_gene.melt(
                        id_vars='Gene',
                        var_name='Sample',
                        value_name='Expression'
                    )

                    # Creem 'Condition' a partir de 'Sample'
                    df_melted['Condition'] = df_melted['Sample'].str.split('_').str[-1]

                    # Convertim a majúscules (per evitar confusions p/P o c/C)
                    df_melted['Condition'] = df_melted['Condition'].str.upper()

                    # Assegurem que 'Expression' sigui numèrica
                    df_melted['Expression'] = pd.to_numeric(df_melted['Expression'], errors='coerce')
                    df_melted.dropna(subset=['Expression'], inplace=True)

                    if df_melted.empty:
                        st.warning(f"El gen **{gene}** a **{dataset_name}** té valors no numèrics o tots NaN.")
                        continue

                    # Calculem la mitjana d'expressió per mostra
                    sample_means = df_melted.groupby(['Sample', 'Condition'])['Expression'].mean().reset_index()

                    # Creem el boxplot amb títol "Dataset - Gen" i amb l'ordre fix de 'Condition': C, P
                    fig = px.box(
                        sample_means,
                        x='Condition',
                        y='Expression',
                        color='Condition',
                        points='all',
                        hover_data=['Sample'],
                        title=f"{dataset_name} : {gene}",
                        category_orders={"Condition": ["C", "P"]},
                        color_discrete_map={"C": "#bae1ff", "P": "#daf7a6"},
                        labels={'Expression': 'Log2 abundances' if dataset_name == "ProteiNs" else 'mRNA Expression <br> (Normalized Read Counts)'}
                    )
                    fig.update_traces(
                        jitter=0,
                        pointpos=0,
                        marker=dict(size=10, opacity=0.8),
                        line=dict(width=1)
                    )

                    # Els gràfics estan centrats a Y=0 a menys que l'usuari indiqui el contrari
                    if st.session_state.get("include_zero", True):
                        fig.update_yaxes(rangemode="tozero")

                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
