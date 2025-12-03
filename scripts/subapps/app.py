import pandas as pd
import streamlit as st
from styling import highlight_all_datasets, highlight_matrix  # Importem la funció d'estil

st.markdown("""
    <style>
        /* Aplica un color blau clar a les xips dels multiselect */
        [data-baseweb="tag"] {
            background-color: #bae1ff !important;
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_merge_data(file_path: str) -> pd.DataFrame:
    """
    Llegeix un Excel amb múltiples fulls (decimal=',') i uneix totes les dades
    en un únic DataFrame (outer join) per la columna 'Gene'.
    La columna 'Gene' es manté sense renombrar; totes les altres columnes es renomenen amb el prefix del full.
    """
    sheets = pd.read_excel(file_path, sheet_name=None, decimal=",")
    merged_df = None

    for sheet_name, df_sheet in sheets.items():
        if df_sheet.empty:
            continue
        df_sheet = df_sheet.copy()

        # Renombrar totes les columnes excepte 'Gene'
        rename_map = {
            col: f"{sheet_name}_{col}"
            for col in df_sheet.columns
            if col != "Gene"
        }
        df_sheet = df_sheet.rename(columns=rename_map)

        # Primera fulla: la prenem tal qual, després fem el merge per 'Gene'
        if merged_df is None:
            merged_df = df_sheet
        else:
            merged_df = pd.merge(
                merged_df,
                df_sheet,
                on="Gene",
                how="outer"
            )

    return merged_df

def main():
    rows_to_show = 200
    undesired_substrings = ["id", "symbol"]
    
    st.title("GEN Explorer")
    
    # 1) Carregar el DataFrame unificat (cachejat)
    file_path = "data/Gene_data_20250312.xlsx"
    df_merged = load_and_merge_data(file_path)
    
    # Verifiquem que existeix la columna 'Gene'
    if "Gene" not in df_merged.columns:
        st.error("No s'ha trobat la columna 'Gene'. Comprova que existeixi a totes les fulles.")
        st.stop()
    
    # Exemple de filtres: barra lateral per seleccionar gens
    st.sidebar.header("Configuració de filtres")
    
    st.sidebar.subheader("Filtrar Gens")
    unique_genes = sorted(df_merged["Gene"].dropna().unique().tolist())
    selected_genes = st.sidebar.multiselect(
        "Selecciona un o varis Gens:",
        unique_genes,
        default=[]
    )
    
    # Definir el nombre màxim de decimals permesos
    decimals = 4

    # Crear el widget number_input amb el pas definit
    global_p_value = st.sidebar.number_input(
        "Umbral p-valor (s'aplicarà a les columnes pvalue)",
        value=0.05,
        step=10**-decimals,  # Defineix el pas en funció del nombre de decimals
        format=f"%.{decimals}g"  # Utilitza el format de punt flotant general
    )
    
    global_fdr = st.sidebar.number_input(
        "Umbral FDR (s'aplicarà a les columnes FDR')",
        value=0.05,
        step=10**-decimals,
        format=f"%.{decimals}g"
    )
    global_logfc = st.sidebar.number_input(
        "Umbral logFC (s'aplicarà a les columnes logFC, en valor absolut)",
        value=1.5,
        step=10**-decimals,
        format=f"%.{decimals}g"
    )

    st.sidebar.toggle("Force Y-axis to include 0", value=True, key="include_zero")

    st.sidebar.write("---")
    st.sidebar.header("Configuració per Dataset")
    
    # 3) Detectar possibles fulles (prefixos) a partir de les columnes (excepte 'Gene')
    all_columns = df_merged.columns.tolist()
    possible_sheets = set()
    for col in all_columns:
        if "_" in col:
            sheet_prefix = col.split("_")[0]
            possible_sheets.add(sheet_prefix)
    possible_sheets = sorted(list(possible_sheets))
    
    # Diccionaris per guardar configuracions per cada dataset
    pvalue_config = {}      # {sheet_name: [llista de columnes pvalue seleccionades]}
    tag_filter_config = {}  # {sheet_name: (nom_columna, [valors seleccionats])}
    
    # 1) Definir un ordre personalitzat (si encara el vols per a la lògica de la barra lateral)
    priority_list = ["iAs", "NewiNs", "AllOrgs"]
    last_dataset = ["Fibros"]
    remaining_sheets = [s for s in possible_sheets if s not in priority_list + last_dataset]
    remaining_sheets_sorted = sorted(remaining_sheets)
    ordered_sheets = priority_list + remaining_sheets_sorted + last_dataset

    # 3) Iterar sobre 'ordered_sheets' (per la barra lateral)
    for sheet_name in ordered_sheets:
        with st.sidebar.expander(f"Configuració de {sheet_name}"):
            # Seleccionem les columnes pvalue (que contenen 'pvalue' en el nom)
            metric_cols = [
                c for c in all_columns
                if c.startswith(f"{sheet_name}_") and ("pvalue" in c.lower() or "fdr" in c.lower() or "logfc" in c.lower())
            ]
            if metric_cols:
                selected_metrics = st.multiselect(
                    f"Selecciona columnes pvalue/FDR de {sheet_name}:",
                    metric_cols,
                    default=[]
                )
                pvalue_config[sheet_name] = selected_metrics
            else:
                st.write("No hi ha columnes pvalue disponibles.")

            # Filtre per tag:
            if sheet_name == "ProteiNs":
                tag_col = f"{sheet_name}_expr_pval_Patient_Ctrl"
            else:
                tag_col = f"{sheet_name}_genes_tag"
            if tag_col in all_columns:
                unique_tags = sorted(df_merged[tag_col].dropna().unique().tolist())
                selected_tags = st.multiselect(
                    f"Filtra per {tag_col}:",
                    unique_tags,
                    default=[]
                )
                tag_filter_config[sheet_name] = (tag_col, selected_tags)
            else:
                st.write(f"No s'ha trobat la columna de filtre per {sheet_name}.")
    
    # 4) Aplicar els filtres
    df_final = df_merged.copy()
    
    # Filtrar per 'Gene'
    if selected_genes:
        df_final = df_final[df_final["Gene"].isin(selected_genes)]
    
    # Filtrar per cada dataset: pvalue i tag
    for sheet_name in possible_sheets:
        # Filtrar per pvalue
        if sheet_name in pvalue_config:
            pvalue_cols = [c for c in pvalue_config[sheet_name] if "pvalue" in c.lower()]
            fdr_cols = [c for c in pvalue_config[sheet_name] if "fdr" in c.lower()]
            # Filtrar columnas de p-value con el umbral correspondiente
            for col in pvalue_cols:
                df_final[col] = pd.to_numeric(
                    df_final[col].astype(str).str.replace(",", ".", regex=False),
                    errors='coerce'
                )
                df_final = df_final[df_final[col].notna() & (df_final[col] < global_p_value)]
            
            # Filtrar columnas de FDR con el umbral correspondiente
            for col in fdr_cols:
                df_final[col] = pd.to_numeric(
                    df_final[col].astype(str).str.replace(",", ".", regex=False),
                    errors='coerce'
                )
                df_final = df_final[df_final[col].notna() & (df_final[col] < global_fdr)]
            
            # Filtrar per logFC: s'eliminen les files on el valor absolut és inferior al umbral global_logfc
            logfc_cols = [c for c in pvalue_config[sheet_name] if "logfc" in c.lower()]
            for col in logfc_cols:
                df_final[col] = pd.to_numeric(
                    df_final[col].astype(str).str.replace(",", ".", regex=False),
                    errors='coerce'
                )
                df_final = df_final[df_final[col].notna() & (df_final[col].abs() >= global_logfc)]
                
        # Filtrar per tag (gene_tag o expr_pval_Patient_Ctrl)
        if sheet_name in tag_filter_config:
            tag_col, selected_tags = tag_filter_config[sheet_name]
            if selected_tags:
                df_final = df_final[df_final[tag_col].isin(selected_tags)]
    
    # --- Selecció de quins datasets volem mostrar ---
    st.write("---")
    datasets_to_show = st.multiselect(
        "Selecciona datasets a mostrar:",
        possible_sheets,
        default=possible_sheets,  # Per defecte, tots seleccionats
    )
    
    # Definir quines columnes volem a la taula final
    cols_to_show = []
    for col in df_final.columns:
        # Comprovem que no conté subcadenes no desitjades
        if any(sub in col.lower() for sub in undesired_substrings):
            continue
        
        # "Gene" la volem sempre
        if col == "Gene":
            cols_to_show.append(col)
            continue
        
        # Només incloem la columna si el prefix està entre els datasets seleccionats
        if "_" in col:
            prefix = col.split("_")[0]
            if prefix in datasets_to_show:
                cols_to_show.append(col)
    
    # A df_final només hi deixem les columnes que volem mostrar
    df_final = df_final[cols_to_show]
    
    # 5) Mostrar el resultat
    if df_final.empty:
        st.warning("No hi ha gens que compleixin els filtres.")
    else:
        # KPI: nombre de gens únics
        num_genes_distintos = df_final["Gene"].nunique()
        formatted_num_genes = "{:,}".format(num_genes_distintos).replace(",", ".")
        st.metric(label="Gens que compleixen", value=formatted_num_genes)
        
        # Mostrem només les primeres rows_to_show files per defecte
        if df_final.shape[0] > rows_to_show:
            st.info(
                f"Només es mostren les {rows_to_show} primeres files. "
                "Descarrega el CSV per obtenir totes les files filtrades."
            )
            df_display = df_final.head(rows_to_show)
        else:
            df_display = df_final
            
        # Deixa la columna 'Gene' sense enllaços (només text)
        # Afegim una opció per activar/desactivar la visualització dels enllaços
        mostrar_links = st.checkbox("Mostrar enllaços", value=False)

        if mostrar_links:
            # Inserir la nova columna 'Link' en la segona posició amb els enllaços corresponents
            df_display.insert(1, "Link", "https://www.genecards.org/cgi-bin/carddisp.pl?gene=" + df_display["Gene"])
            column_config_main = {
                "Link": st.column_config.LinkColumn(
                    "Link",
                    display_text=r"https://www\.genecards\.org/cgi-bin/carddisp\.pl\?gene=(.*)",
                ),
            }
        else:
            column_config_main = {}
    
        column_config = {
            "Gene": st.column_config.LinkColumn(
                "Gene",  # label
                display_text=r"https://www\.genecards\.org/cgi-bin/carddisp\.pl\?gene=(.*)",
            ),
        }
        
        # --- Mostra la taula principal ---
        st.dataframe(
            df_display.style.apply(highlight_all_datasets, axis=1),
            column_config=column_config_main,
            hide_index=True,
            use_container_width=True
        )
        
        # Botó per descarregar el CSV filtrat
        csv_data = df_final.to_csv(index=False)
        st.download_button(
            label="Descarregar CSV filtrat",
            data=csv_data,
            file_name="genes_filtrats_unics.csv",
            mime="text/csv"
        )
        
        # --- Construir la matriu de colors amb el mateix ordre de df_display ---
        df_matrix = pd.DataFrame()
        df_matrix["Gene"] = df_display["Gene"]  # Primer copiem la columna 'Gene'

        # 1) Llistem, en l'ordre en què apareixen, les columnes de df_display
        #    que siguin "tag columns" (acaben en '_genes_tag' o '_expr_pval_Patient_Ctrl')
        matrix_tag_cols = []
        for c in df_display.columns:
            if c == "Gene":
                continue
            if c.endswith("_genes_tag") or c.endswith("_expr_pval_Patient_Ctrl"):
                matrix_tag_cols.append(c)

        # 2) Per cadascuna d'aquestes columnes, creem una nova columna a df_matrix
        #    anomenada com el prefix (p.ex. 'ProteiNs', 'iAs', etc.)
        for c in matrix_tag_cols:
            prefix = c.split("_")[0]
            df_matrix[prefix] = df_display[c]

        st.write("---")
        st.markdown("### Matriu de colors per dataset")
        
        # Creem el styled DataFrame i li afegim un atribut de taula per identificar-la
        styled_matrix = df_matrix.style.apply(highlight_matrix, axis=1)
        styled_matrix.set_table_attributes('class="narrow-df"')
        
        # CSS específic per ajustar l'amplada (només per les columnes de datasets, deixant 'Gene' amb ample automàtic)
        st.markdown("""
        <style>
        .narrow-df th:not(:first-child), .narrow-df td:not(:first-child) {
            max-width: 50px;
            width: 50px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # --- Mostra la matriu de colors ---
        st.dataframe(
            styled_matrix,
            hide_index=True,
            use_container_width=True
        )

if __name__ == "__main__":
    main()
