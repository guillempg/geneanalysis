def highlight_all_datasets(row):
    """
    Aplica estils a les cel·les d'un DataFrame per a streamlit.

    - Per a la majoria dels datasets, s'utilitza la columna <dataset>_genes_tag amb:
         NOT_DEG: gris clar (#edede9)
         POSSIBLE_DEG: groc clar (#fffacd)
         PREVALENT_DEG: verd clar (#e1f7d5)
    
    - Per al dataset ProteiNs, s'utilitza la columna ProteiNs_expr_pval_Patient_Ctrl amb:
         up: verd clar (#e1f7d5)
         down: groc clar (#fffacd)
    
    - A més, per a les columnes que continguin "logFCs" al nom:
         Si el valor és superior a 0, el text es mostrarà en verd.
         Si el valor és inferior a 0, el text es mostrarà en vermell.
         Es manté també el color de fons calculat segons el dataset.
    """
    styles = []
    for col in row.index:
        if col == "Gene":
            # No s'aplica estil a la columna 'Gene'
            styles.append("")
        elif "logFCs" in col:
            # Per a les columnes amb 'logFCs': assignem estil tant per al text com per al fons
            # Estil per al text segons el valor numèric
            try:
                value = float(row[col])
                if value > 0:
                    text_style = "color: green"
                elif value < 0:
                    text_style = "color: red"
                else:
                    text_style = ""
            except (ValueError, TypeError):
                text_style = ""
            # Estil per al fons si la columna segueix el patró amb "_"
            if "_" in col:
                prefix = col.split("_")[0]
                if prefix == "ProteiNs":
                    tag_val = row.get("ProteiNs_expr_pval_Patient_Ctrl", None)
                    if tag_val == "up":
                        bg_color = "#e1f7d5"  # verd clar
                    elif tag_val == "down":
                        bg_color = "#fffacd"  # groc clar
                    else:
                        bg_color = ""
                else:
                    tag_val = row.get(f"{prefix}_genes_tag", None)
                    if tag_val == "NOT_DEG":
                        bg_color = "#edede9"  # gris clar
                    elif tag_val == "POSSIBLE_DEG":
                        bg_color = "#fffacd"  # groc clar
                    elif tag_val == "PREVALENT_DEG":
                        bg_color = "#e1f7d5"  # verd clar
                    else:
                        bg_color = ""
            else:
                bg_color = ""
            # Combina els estils si n'hi ha de fons i de text
            if bg_color and text_style:
                combined_style = f"background-color: {bg_color}; {text_style}"
            elif bg_color:
                combined_style = f"background-color: {bg_color}"
            elif text_style:
                combined_style = text_style
            else:
                combined_style = ""
            styles.append(combined_style)
        elif "_" in col:
            # Aplica estil de fons segons el dataset
            prefix = col.split("_")[0]
            if prefix == "ProteiNs":
                tag_val = row.get("ProteiNs_expr_pval_Patient_Ctrl", None)
                if tag_val == "up":
                    color = "#e1f7d5"  # verd clar
                elif tag_val == "down":
                    color = "#fffacd"  # groc clar
                else:
                    color = ""
            else:
                tag_val = row.get(f"{prefix}_genes_tag", None)
                if tag_val == "NOT_DEG":
                    color = "#edede9"  # gris clar
                elif tag_val == "POSSIBLE_DEG":
                    color = "#fffacd"  # groc clar
                elif tag_val == "PREVALENT_DEG":
                    color = "#e1f7d5"  # verd clar
                else:
                    color = ""
            styles.append(f"background-color: {color}" if color else "")
        else:
            styles.append("")
    return styles

# Funció per aplicar l'estil de fons (només color, sense text) a la matriu
def highlight_matrix(row):
    styles = []
    for col in row.index:
        if col == "Gene":
            styles.append("")  # La columna 'Gene' es deixa sense estil
        else:
            val = row[col]
            color = ""
            if col == "ProteiNs":
                if val == "up":
                    color = "#e1f7d5"  # verd clar
                elif val == "down":
                    color = "#fffacd"  # groc clar
            else:
                if val == "NOT_DEG":
                    color = "#edede9"  # gris clar
                elif val == "POSSIBLE_DEG":
                    color = "#fffacd"  # groc clar
                elif val == "PREVALENT_DEG":
                    color = "#e1f7d5"  # verd clar
            if color:
                # Es mostra només el color de fons (el text es fa transparent)
                styles.append(f"background-color: {color}; color: transparent")
            else:
                styles.append("")
    return styles
