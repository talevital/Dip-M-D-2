import pandas as pd
from sqlalchemy import create_engine

# === Connexion PostgreSQL ===
USER = "postgres"
PASSWORD = "admin"
HOST = "localhost"
PORT = "5432"
DBNAME = "ma_base_dip"
engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")

# === Fonction pour rendre les colonnes uniques et compatibles Postgres ===
def make_unique_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        # Nettoyage basique
        col = str(col).strip().replace(" ", "_").replace("'", "")
        col = col.replace("(", "").replace(")", "").replace(",", "").replace(";", "")
        
        # Tronquer si trop long (Postgres limite à 63, mais on garde plus de place)
        col = col[:150]  # limite étendue à 150 caractères
        
        # Gérer doublons
        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0
        new_cols.append(col)
    return new_cols

# === Charger Excel ===
fichier_excel = "20250731_Data_UEMOA COMPLET_0.xlsx"
xls = pd.ExcelFile(fichier_excel)
print("Feuilles détectées :", xls.sheet_names)

for sheet_name in xls.sheet_names:
    print(f"📥 Lecture de la feuille : {sheet_name}")
    df = pd.read_excel(fichier_excel, sheet_name=sheet_name)

    # Appliquer la fonction
    old_cols = df.columns.tolist()
    df.columns = make_unique_columns(df.columns)
    print("Colonnes renommées :")
    for old, new in zip(old_cols, df.columns):
        if old != new:
            print(f"   {old}  ➝  {new}")

    # Export vers PostgreSQL
    nom_table = sheet_name.strip().replace(" ", "_").lower()
    # Tronquer le nom de table si trop long (limite à 150 caractères)
    nom_table = nom_table[:150]
    df.to_sql(nom_table, engine, if_exists="replace", index=False)
    print(f"✅ Données insérées dans la table : {nom_table}")
