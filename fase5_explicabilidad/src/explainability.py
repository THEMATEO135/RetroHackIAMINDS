"""
Explicabilidad del Modelo (XAI) - UPTC Energy AI
IAMinds 2026 Hackathon

Implementa SHAP y LIME para interpretar predicciones del modelo
"""
import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Explicabilidad
import shap
from lime import lime_tabular

# Visualizacion
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI

# Sklearn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

import joblib

# Path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config.settings import DATA_PATH, MODELS_PATH, SEDES, SECTORES


class ModelExplainer:
    """Clase para explicabilidad de modelos con SHAP y LIME"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.shap_explainer = None
        self.lime_explainer = None
        self.feature_names = None
        self.X_train = None

    def load_and_prepare_data(self, filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """Carga y prepara datos para explicabilidad"""
        print("Cargando datos para explicabilidad...")

        df = pd.read_csv(filepath, parse_dates=["timestamp"])

        # Features numericos
        self.feature_names = [
            "hora", "dia_semana", "mes",
            "temperatura_exterior", "ocupacion_estimada",
            "es_fin_semana"
        ]

        # Agregar one-hot encoding para sede y sector
        df_encoded = pd.get_dummies(df[["sede", "sector"]], prefix=["sede", "sector"])
        self.feature_names.extend(df_encoded.columns.tolist())

        # Preparar X e y
        X = df[["hora", "dia_semana", "mes", "temperatura_exterior", "ocupacion_estimada"]]
        X["es_fin_semana"] = df["es_fin_semana"].astype(int)
        X = pd.concat([X, df_encoded], axis=1)

        y = df["consumo_kwh"].values

        # Escalar
        X_scaled = self.scaler.fit_transform(X)

        print(f"Datos preparados: {X_scaled.shape}")
        return X_scaled, y

    def train_interpretable_model(self, X: np.ndarray, y: np.ndarray):
        """Entrena modelo interpretable (Random Forest) para explicabilidad"""
        print("\nEntrenando modelo interpretable...")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.X_train = X_train

        # Random Forest es mas facil de interpretar
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train, y_train)

        # Evaluar
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        print(f"R2 Train: {train_score:.4f}")
        print(f"R2 Test: {test_score:.4f}")

        # Guardar modelo
        model_path = os.path.join(MODELS_PATH, "explainable_model.pkl")
        os.makedirs(MODELS_PATH, exist_ok=True)
        joblib.dump(self.model, model_path)
        print(f"Modelo guardado: {model_path}")

        return self.model

    # ==================== SHAP ====================

    def setup_shap_explainer(self):
        """Configura SHAP explainer"""
        print("\nConfigurando SHAP explainer...")

        # Usar muestra para eficiencia
        background = shap.sample(self.X_train, 100)

        self.shap_explainer = shap.TreeExplainer(self.model)
        print("SHAP explainer configurado")

    def explain_with_shap(self, X: np.ndarray) -> shap.Explanation:
        """Genera explicaciones SHAP para instancias"""
        if self.shap_explainer is None:
            self.setup_shap_explainer()

        shap_values = self.shap_explainer.shap_values(X)
        return shap_values

    def get_feature_importance_shap(self, X: np.ndarray) -> pd.DataFrame:
        """Calcula importancia de features con SHAP"""
        shap_values = self.explain_with_shap(X)

        # Importancia media absoluta
        importance = np.abs(shap_values).mean(axis=0)

        df_importance = pd.DataFrame({
            "feature": self.feature_names,
            "importance": importance
        }).sort_values("importance", ascending=False)

        return df_importance

    def plot_shap_summary(self, X: np.ndarray, save_path: str = None):
        """Genera grafico resumen SHAP"""
        shap_values = self.explain_with_shap(X)

        plt.figure(figsize=(12, 8))
        shap.summary_plot(
            shap_values,
            X,
            feature_names=self.feature_names,
            show=False
        )
        plt.title("SHAP Feature Importance - UPTC Energy AI")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Grafico guardado: {save_path}")
        plt.close()

    def plot_shap_waterfall(self, X_instance: np.ndarray, idx: int = 0, save_path: str = None):
        """Genera grafico waterfall SHAP para una instancia"""
        shap_values = self.explain_with_shap(X_instance)

        plt.figure(figsize=(10, 6))

        # Crear Explanation object
        explanation = shap.Explanation(
            values=shap_values[idx],
            base_values=self.shap_explainer.expected_value,
            data=X_instance[idx],
            feature_names=self.feature_names
        )

        shap.waterfall_plot(explanation, show=False)
        plt.title(f"Explicacion SHAP - Instancia {idx}")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Grafico guardado: {save_path}")
        plt.close()

    def explain_prediction_shap(self, X_instance: np.ndarray) -> Dict:
        """Genera explicacion textual de una prediccion con SHAP"""
        shap_values = self.explain_with_shap(X_instance.reshape(1, -1))[0]
        prediction = self.model.predict(X_instance.reshape(1, -1))[0]
        base_value = self.shap_explainer.expected_value

        # Ordenar features por impacto
        feature_impacts = list(zip(self.feature_names, shap_values, X_instance))
        feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)

        # Generar explicacion
        explanation = {
            "prediccion": round(prediction, 2),
            "valor_base": round(base_value, 2),
            "confianza": round(min(100, 100 - abs(prediction - base_value) / base_value * 100), 1),
            "factores_principales": [],
            "explicacion_texto": ""
        }

        texto = f"El consumo predicho es {prediction:.1f} kWh. "
        texto += f"El valor base esperado es {base_value:.1f} kWh. "

        if prediction > base_value:
            texto += "El consumo es MAYOR al esperado debido a: "
        else:
            texto += "El consumo es MENOR al esperado debido a: "

        for feature, impact, value in feature_impacts[:5]:
            direction = "aumenta" if impact > 0 else "reduce"
            explanation["factores_principales"].append({
                "feature": feature,
                "valor": round(value, 2) if isinstance(value, (int, float)) else value,
                "impacto": round(impact, 4),
                "efecto": direction
            })
            texto += f"\n  - {feature} ({direction} {abs(impact):.2f} kWh)"

        explanation["explicacion_texto"] = texto

        return explanation

    # ==================== LIME ====================

    def setup_lime_explainer(self, X_train: np.ndarray):
        """Configura LIME explainer"""
        print("\nConfigurando LIME explainer...")

        self.lime_explainer = lime_tabular.LimeTabularExplainer(
            training_data=X_train,
            feature_names=self.feature_names,
            mode='regression',
            random_state=42
        )
        print("LIME explainer configurado")

    def explain_with_lime(self, X_instance: np.ndarray, num_features: int = 10):
        """Genera explicacion LIME para una instancia"""
        if self.lime_explainer is None:
            self.setup_lime_explainer(self.X_train)

        exp = self.lime_explainer.explain_instance(
            X_instance,
            self.model.predict,
            num_features=num_features
        )
        return exp

    def plot_lime_explanation(self, X_instance: np.ndarray, save_path: str = None):
        """Genera grafico de explicacion LIME"""
        exp = self.explain_with_lime(X_instance)

        fig = exp.as_pyplot_figure()
        fig.set_size_inches(12, 6)
        plt.title("Explicacion LIME - UPTC Energy AI")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Grafico guardado: {save_path}")
        plt.close()

    def explain_prediction_lime(self, X_instance: np.ndarray) -> Dict:
        """Genera explicacion textual con LIME"""
        exp = self.explain_with_lime(X_instance)
        prediction = self.model.predict(X_instance.reshape(1, -1))[0]

        # Obtener reglas
        rules = exp.as_list()

        explanation = {
            "prediccion": round(prediction, 2),
            "reglas": [],
            "explicacion_texto": ""
        }

        texto = f"El consumo predicho es {prediction:.1f} kWh.\n\nFactores que influyen:\n"

        for rule, weight in rules[:7]:
            direction = "+" if weight > 0 else "-"
            explanation["reglas"].append({
                "condicion": rule,
                "peso": round(weight, 4)
            })
            texto += f"  {direction} {rule}: {abs(weight):.2f} kWh\n"

        explanation["explicacion_texto"] = texto

        return explanation

    # ==================== METRICAS DE IMPACTO ====================

    def calculate_impact_metrics(self, df: pd.DataFrame, recommendations: List[Dict]) -> Dict:
        """Calcula metricas de impacto de las recomendaciones"""
        metrics = {
            "reduccion_kwh_proyectada": 0,
            "reduccion_co2_kg": 0,
            "ahorro_cop": 0,
            "porcentaje_reduccion": 0
        }

        consumo_actual = df["consumo_kwh"].sum()

        for rec in recommendations:
            metrics["reduccion_kwh_proyectada"] += rec.get("ahorro_kwh_mes", 0)
            metrics["reduccion_co2_kg"] += rec.get("ahorro_co2_kg", 0)
            metrics["ahorro_cop"] += rec.get("ahorro_cop", 0)

        if consumo_actual > 0:
            metrics["porcentaje_reduccion"] = round(
                metrics["reduccion_kwh_proyectada"] / consumo_actual * 100, 2
            )

        return metrics

    # ==================== REPORTE ====================

    def generate_explainability_report(
        self,
        X_sample: np.ndarray,
        output_path: str
    ) -> str:
        """Genera reporte completo de explicabilidad"""
        os.makedirs(output_path, exist_ok=True)

        report = []
        report.append("=" * 60)
        report.append("REPORTE DE EXPLICABILIDAD - UPTC ENERGY AI")
        report.append("IAMinds 2026 Hackathon")
        report.append("=" * 60)
        report.append("")

        # 1. Importancia de features global
        report.append("1. IMPORTANCIA GLOBAL DE FEATURES (SHAP)")
        report.append("-" * 40)

        importance_df = self.get_feature_importance_shap(X_sample[:1000])
        for _, row in importance_df.head(10).iterrows():
            report.append(f"   {row['feature']}: {row['importance']:.4f}")
        report.append("")

        # Guardar grafico
        self.plot_shap_summary(X_sample[:500], os.path.join(output_path, "shap_summary.png"))
        report.append(f"   Grafico guardado: shap_summary.png")
        report.append("")

        # 2. Explicacion de instancias ejemplo
        report.append("2. EXPLICACIONES DE PREDICCIONES INDIVIDUALES")
        report.append("-" * 40)

        for i in range(3):
            idx = np.random.randint(0, len(X_sample))
            exp = self.explain_prediction_shap(X_sample[idx])

            report.append(f"\n   Instancia {i+1}:")
            report.append(f"   Prediccion: {exp['prediccion']} kWh")
            report.append(f"   Confianza: {exp['confianza']}%")
            report.append("   Factores principales:")
            for factor in exp["factores_principales"][:3]:
                report.append(f"      - {factor['feature']}: {factor['efecto']} {abs(factor['impacto']):.2f} kWh")

            # Guardar waterfall
            self.plot_shap_waterfall(
                X_sample[idx:idx+1],
                0,
                os.path.join(output_path, f"shap_waterfall_{i+1}.png")
            )

        report.append("")

        # 3. Nivel de confianza del modelo
        report.append("3. NIVEL DE CONFIANZA DEL MODELO")
        report.append("-" * 40)

        predictions = self.model.predict(X_sample[:1000])
        std_pred = np.std(predictions)
        mean_pred = np.mean(predictions)

        report.append(f"   Prediccion promedio: {mean_pred:.2f} kWh")
        report.append(f"   Desviacion estandar: {std_pred:.2f} kWh")
        report.append(f"   Coeficiente de variacion: {std_pred/mean_pred*100:.1f}%")
        report.append("")

        # 4. Recomendaciones de uso
        report.append("4. RECOMENDACIONES PARA INTERPRETAR RESULTADOS")
        report.append("-" * 40)
        report.append("   - Las predicciones son mas confiables en horas pico (8am-6pm)")
        report.append("   - Mayor incertidumbre en periodos de vacaciones")
        report.append("   - Anomalias con SHAP impact > 2 std requieren revision")
        report.append("   - Actualizar modelo cada semestre con nuevos datos")
        report.append("")

        # Guardar reporte
        report_text = "\n".join(report)
        report_file = os.path.join(output_path, "explainability_report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)

        print(f"\nReporte guardado: {report_file}")
        return report_text


def main():
    """Funcion principal"""
    print("=" * 60)
    print("UPTC Energy AI - Explicabilidad del Modelo (XAI)")
    print("IAMinds 2026 Hackathon")
    print("=" * 60)

    # Cargar datos
    data_file = os.path.join(DATA_PATH, "uptc_energy_data_full.csv")
    if not os.path.exists(data_file):
        print("ERROR: No se encontro archivo de datos")
        print("Ejecute primero: python fase1_modelado_predictivo/src/generate_data.py")
        return

    explainer = ModelExplainer()

    # Preparar datos
    X, y = explainer.load_and_prepare_data(data_file)

    # Usar muestra para demo
    sample_size = min(50000, len(X))
    indices = np.random.choice(len(X), sample_size, replace=False)
    X_sample = X[indices]
    y_sample = y[indices]

    # Entrenar modelo
    explainer.train_interpretable_model(X_sample, y_sample)

    # Configurar explainers
    explainer.setup_shap_explainer()

    # Generar reporte
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "reports"
    )
    report = explainer.generate_explainability_report(X_sample[:5000], output_path)
    print(report)

    # Ejemplo de explicacion individual
    print("\n" + "=" * 60)
    print("EJEMPLO DE EXPLICACION INDIVIDUAL")
    print("=" * 60)

    idx = np.random.randint(0, len(X_sample))
    exp_shap = explainer.explain_prediction_shap(X_sample[idx])
    print(exp_shap["explicacion_texto"])

    print("\n" + "=" * 60)
    print("Analisis de explicabilidad completado!")
    print("=" * 60)


if __name__ == "__main__":
    main()
