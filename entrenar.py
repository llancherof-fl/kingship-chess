import sys, pandas as pd, numpy as np #Una nota para mis compañeros que lo quieran correr, instale primero numpy y pandas
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
d = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "base_entrenamiento.csv")
X = d.drop(columns=["campeon", "partida", "anio"]); y = d["campeon"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
modelo = make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(32, 16), alpha=1e-3,
                       max_iter=600, early_stopping=True, random_state=1))
modelo.fit(Xtr, ytr)
p = modelo.predict(Xte)
print("Exactitud en prueba:", round(accuracy_score(yte, p) * 100, 1), "%  (azar = 20 %)")
cl = sorted(y.unique())
print(pd.DataFrame(confusion_matrix(yte, p, labels=cl), index=cl, columns=cl))
print(classification_report(yte, p, digits=3))
