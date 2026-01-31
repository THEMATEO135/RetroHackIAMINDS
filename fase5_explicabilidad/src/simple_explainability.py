import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.inspection import permutation_importance
import joblib

# Path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config.settings import DATA_PATH, MODELS_PATH


def main():
    print("=== Fase 5 (Simple): Explicabilidad ===")
    data_file = os.path.join(DATA_PATH, "uptc_energy_data_full.csv")
    model_file = os.path.join(MODELS_PATH, "simple_consumo_kwh.joblib")
    feature_file = os.path.join(MODELS_PATH, "simple_features.json")

    if not os.path.exists(data_file) or not os.path.exists(model_file) or not os.path.exists(feature_file):
        raise FileNotFoundError("Faltan archivos. Ejecuta simple_train.py primero.")

    df = pd.read_csv(data_file)
    with open(feature_file, "r", encoding="utf-8") as f:
        features = json.load(f)["features"]

    X = pd.get_dummies(
        df[[
            "temperatura_exterior",
            "ocupacion_estimada",
            "hora_sin", "hora_cos",
            "dia_sin", "dia_cos",
            "mes_sin", "mes_cos",
            "es_fin_semana",
            "periodo_academico",
            "sede",
            "sector"
        ]],
        columns=["sede", "sector", "periodo_academico"],
        drop_first=False
    )

    # Alinear columnas con entrenamiento
    for col in features:
        if col not in X.columns:
            X[col] = 0
    X = X[features]

    y = df["consumo_kwh"].values

    model = joblib.load(model_file)
    preds = model.predict(X)
    residuals = y - preds

    # Importancia por permutacion (muestra para simplicidad)
    sample_idx = np.random.choice(len(X), size=min(5000, len(X)), replace=False)
    result = permutation_importance(model, X.iloc[sample_idx], y[sample_idx], n_repeats=3, random_state=42)

    importances = sorted(
        zip(features, result.importances_mean),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    top_features = [
        {"feature": f, "importance": round(float(v), 6)}
        for f, v in importances[:10]
    ]

    report = {
        "timestamp": datetime.now().isoformat(),
        "top_features": top_features,
        "confianza": round(float(np.std(residuals)), 4),
        "explicacion": "Importancia por permutacion. Menor varianza del residual = mayor confianza."
    }

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_dir = os.path.join(project_root, "fase5_explicabilidad")
    os.makedirs(out_dir, exist_ok=True)

    out_file = os.path.join(out_dir, "simple_explainability.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Explicabilidad guardada en:", out_file)


if __name__ == "__main__":
    main()
