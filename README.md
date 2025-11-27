# 🧬 GEN Explorer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

Una aplicació web interactiva construïda amb [Streamlit](https://streamlit.io/) per explorar dades multi-òmiques a nivell gènic a partir de fitxers Excel amb múltiples fulls. Perfecte per a investigadors i bioinformàtics que treballen amb dades d’expressió gènica.

[English](#english) | [Català](#català)

## 🌟 Característiques principals

- **Dues eines integrades:**
  - **GEN Explorer**: Interfície principal per a l’exploració i filtratge de dades
  - **GEN Boxplots**: Anàlisi visual de l’expressió gènica a través de datasets
- **Integració intel·ligent de dades:**
  - Fusió automàtica de múltiples fulls d’Excel per la columna `Gene`
  - Suport per a valors decimals amb separador coma (format europeu)
- **Sistema de filtratge potent:**
  - Llindars globals:
    - Tall de **p-value**
    - Llindar de **FDR** (Taxa de Falsos Positius)
    - **|logFC|** (valor absolut del log Fold Change)
  - Filtres específics per dataset (etiquetes, p-values, FDRs, logFCs)
- **Funcionalitats interactives:**
  - Selector multi-gen
  - Visualització dinàmica de dades
  - Integració amb GeneCards per a cada gen
  - Exportació de dades filtrades
  - Matriu visual d’etiquetes a través de datasets
- **Estilització intel·ligent:**
  - Codificació de colors per nivells d’expressió
  - Diferenciació visual de DEGs (gens diferencialment expressats)
  - Ressaltat intuïtiu basat en etiquetes

## Com executar l’aplicació fent servir Docker

1. Assegura’t de tenir [Docker Desktop](https://www.docker.com/products/docker-desktop/) instal·lat.
2. A Windows, un cop instalat Docker Desktop, arranca'l i si cal actualitzar WSL, obre una terminal i executa 
la comanda `wsl --update` tal i com t'indica Docker Desktop.
3. Executa l'arxiu run_geneanalysis2.bat (Windows). S'ha de canviar la ruta on es troben els arxius d'Excel que vols fer servir,
la imatge de Docker no les conté.
4. Obre un navegador web a la URL "http://localhost:8501"


## 📁 Estructura del projecte

```
projecte_monica/
├── data/                          # Arxius d'Excel amb les dades (buit a GitHub)
├── scripts/
│   ├── app_integrada.py           # Integrador principal de l’aplicació
│   ├── styling.py                 # Funcions d’estilització de taules
│   ├── requirements.txt           # Dependències Python
│   └── subapps/
│       ├── app.py                 # Aplicació principal GEN Explorer
│       └── app_boxplot.py         # Visualització GEN Boxplots
└── README.md
```

## 📑 Guia d’integració de datasets

### Afegir nous datasets

L’aplicació suporta dos tipus de formats de datasets:

1. **Datasets estàndard d’expressió gènica:**
   - Nom dels fulls: qualsevol nom descriptiu (per exemple, `iAs`, `iPSCs`, `Fibros`)
   - Columnes requerides:
     - `Gene` (obligatori): identificador gènic per a la fusió
     - `*_pvalue`: columna de p-value
     - `*_FDR`: columna de taxa de falsos positius
     - `*_logFC`: columna de log Fold Change
     - `*_genes_tag`: etiquetes de classificació amb valors:
       - `NOT_DEG`: no diferencialment expressat
       - `POSSIBLE_DEG`: possiblement diferencialment expressat
       - `PREVALENT_DEG`: diferencialment expressat prevalent
2. **Datasets d’expressió proteica:**
   - Nom del full: ha de ser `ProteiNs` (nom exacte)
   - Columnes requerides:
     - `Gene` (obligatori): identificador gènic per a la fusió
     - `ProteiNs_expr_pval_Patient_Ctrl`: p-values d’expressió amb valors:
       - `up`: proteïnes sobreexpressades
       - `down`: proteïnes subexpressades
     - Altres columnes estàndard (`pvalue`, `FDR`, `logFC`)

### Convencions de nomenclatura de columnes:
- Totes les columnes excepte `Gene` s’afegiran automàticament amb el prefix del nom del full
- Exemple per al full "iAs":
  ```
  Gene | pvalue → iAs_pvalue
  Gene | FDR → iAs_FDR
  Gene | logFC → iAs_logFC
  Gene | genes_tag → iAs_genes_tag
  ```
- Per al full de proteïnes ("ProteiNs"):
  ```
  Gene | expr_pval_Patient_Ctrl → ProteiNs_expr_pval_Patient_Ctrl
  ```

### Notes d’integració:
- L’aplicació detecta i aplica automàticament l’estilització correcta segons el tipus de dataset
- Les dades de proteïnes tenen una visualització especial als boxplots (etiquetats com “Log2 abundances”)
- Tots els valors numèrics han d’utilitzar coma (,) com a separador decimal
- Els noms de columna són sensibles a majúscules i minúscules
- Mantingueu la coherència dels noms dels datasets entre diferents fitxers Excel per a comparacions als boxplots

### Estilització visual:
- Els datasets estàndard utilitzen codificació de colors:
  - `NOT_DEG`: gris clar (#edede9)
  - `POSSIBLE_DEG`: groc clar (#fffacd)
  - `PREVALENT_DEG`: verd clar (#e1f7d5)
- Els datasets de proteïnes utilitzen:
  - `up`: verd clar (#e1f7d5)
  - `down`: groc clar (#fffacd)

## 🚀 Execució

### Requisits

- Python >= 3.8
- Paquets: `pandas`, `streamlit`, `openpyxl`

### Instal·lació i execució

```bash
# Crear entorn virtual (opcional)
python -m venv venv
source venv/bin/activate  # o .\\venv\\Scripts\\activate en Windows

# Instal·lar dependències
pip install -r requirements.txt

# Llançar l'aplicació
streamlit run scripts/subapps/app.py
```

📌 Format del fitxer Excel  
 • Ha de contenir diversos fulls, cadascun amb:  
 • Una columna Gene comuna (clau de fusió)  
 • Columnes addicionals com pvalue, FDR, logFC, *_genes_tag o *_expr_pval_Patient_Ctrl  
 • Les dades numèriques poden estar amb coma (,) com a separador decimal  


🧠 Notes tècniques  
 • L’aplicació cacheja el fitxer Excel per optimitzar el rendiment (@st.cache_data)  
 • El filtratge per logFC es fa sobre el valor absolut segons el llindar indicat  
 • Els desplegables de la barra lateral es construeixen automàticament a partir dels prefixos de fulls  

## 🌐 Desplegament al núvol amb Streamlit Community Cloud

### Prerequisits
- Compte gratuït a **Streamlit Community Cloud**.
- Repositori **públic** a GitHub amb aquest projecte.
- Fitxer `scripts/requirements.txt` amb totes les dependències.

### Passos de desplegament
1. **Publica el codi a GitHub.**
   - Inclou tot el directori del projecte i assegura’t que `scripts/requirements.txt` hi és.
2. **Crea l’aplicació a Streamlit.**
   - Accedeix a [streamlit.io] i fes clic a **Create app**.
   - Connecta el teu compte de GitHub i selecciona **repo**, **branch** (p. ex. `main`) i el **camí de l’app**: `scripts/subapps/app.py`.
3. **Dependències.**
   - Streamlit instal·larà automàticament les dependències des de `scripts/requirements.txt`.
4. **Variables d’entorn i secrets (opcional).**
   - A **Settings → Secrets**, afegeix claus o credencials si en necessites. *No* comprometis secrets al repo.
5. **Dades d’entrada.**
   - Per a fitxers petits, pots versionar-los al repo (`data/`).
   - Per a fitxers grans, usa `st.file_uploader` o emmagatzematge extern (p. ex., bucket) i carrega’ls en temps real.
6. **Caché i rendiment.**
   - Usa `@st.cache_data` per evitar rellegir i fusionar Excel a cada execució.
7. **Desplega i comprova logs.**
   - Un cop creada, l’app es construirà i quedarà accessible amb una URL pública. Consulta **Logs** si hi ha errors.

### Què permet el compte gratuït
- **Desplegar apps públiques** basades en repos **públics** de GitHub.
- **Recursos limitats** i **hibernació per inactivitat**: l’app pot aturar-se quan no s’usa i reactivar-se al primer accés.
- **Emmagatzematge efímer**: el sistema de fitxers del contenidor es restableix en reinicis/desplegaments; no el facis servir com a magatzem persistent.
- **Límits d’execució i memòria**: optimitza la lectura de Excel i evita càrregues innecessàries.
- **Concurrència limitada**: millor evita operacions molt pesades al fil principal.

> **Alternativa**: si necessites apps privades o més control, prepara un `Dockerfile` i executa-ho en un servidor propi o en un PaaS (p. ex., Fly.io, Google Cloud Run).


🛠️ Desenvolupament

Si vols afegir funcionalitats:  
 • Els filtres es defineixen a la barra lateral (st.sidebar)  
 • Les columnes seleccionables per pvalue/FDR/logFC es gestionen amb la variable metric_cols  
 • El filtratge es fa dataset per dataset dins del bucle que recorre possible_sheets  
