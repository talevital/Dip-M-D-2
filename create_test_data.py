import pandas as pd
import numpy as np

# Créer des données de test
np.random.seed(42)
data = {
    'ID': range(1, 101),
    'Age': np.random.normal(35, 10, 100),
    'Salary': np.random.normal(50000, 15000, 100),
    'Department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 100),
    'Experience': np.random.normal(5, 3, 100),
    'Date': pd.date_range('2023-01-01', periods=100, freq='D')
}

# Ajouter quelques outliers
data['Salary'][10] = 150000  # Outlier
data['Age'][20] = 80  # Outlier

# Ajouter quelques valeurs manquantes
data['Age'][5] = np.nan
data['Salary'][15] = np.nan

df = pd.DataFrame(data)
df.to_csv('/tmp/test_data.csv', index=False)
print("Fichier de test créé: /tmp/test_data.csv")
print(f"Shape: {df.shape}")
print(f"Colonnes: {df.columns.tolist()}")
print(f"Valeurs manquantes: {df.isnull().sum().sum()}")
