"""
UPTC Energy AI - FastAPI Backend
Sirve predicciones del modelo LSTM y consultas con Ollama
"""
import os
from datetime import datetime
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_PATH, "fase1_modelado_predictivo", "models")
DATA_PATH = os.path.join(BASE_PATH, "consumos_uptc_hackday")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

app = FastAPI(
    title="UPTC Energy AI API",
    description="API para prediccion de consumo energetico y recomendaciones",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_pickle(name):
    return joblib.load(os.path.join(MODELS_PATH, name))


try:
    scaler_X = _load_pickle("scaler_X.pkl")
    scaler_y = _load_pickle("scaler_y.pkl")
    le_sede = _load_pickle("label_encoder_sede.pkl")
    le_periodo = _load_pickle("label_encoder_periodo.pkl")
    print("Scalers y encoders cargados correctamente")
except Exception as e:
    print(f"Error cargando scalers: {e}")
    scaler_X = scaler_y = le_sede = le_periodo = None


lstm_model = None


def build_lstm_architecture():
    import tensorflow as tf
    from tensorflow.keras.layers import BatchNormalization, Dense, Dropout, Input, LSTM
    from tensorflow.keras.models import Sequential

    return Sequential(
        [
            Input(shape=(24, 14)),
            LSTM(128, return_sequences=True, name="lstm"),
            BatchNormalization(name="batch_normalization"),
            Dropout(0.3, name="dropout"),
            LSTM(64, return_sequences=True, name="lstm_1"),
            BatchNormalization(name="batch_normalization_1"),
            Dropout(0.3, name="dropout_1"),
            LSTM(32, return_sequences=False, name="lstm_2"),
            Dropout(0.2, name="dropout_2"),
            Dense(32, activation="relu", name="dense"),
            Dense(16, activation="relu", name="dense_1"),
            Dense(1, activation="linear", name="dense_2"),
        ]
    )


def load_keras3_weights(model, weights_path):
    import h5py

    with h5py.File(weights_path, "r") as f:
        for layer in model.layers:
            layer_path = f"layers/{layer.name}"
            if layer_path not in f:
                continue
            layer_group = f[layer_path]
            if "lstm" in layer.name and "cell" in layer_group:
                cell_vars = layer_group["cell/vars"]
                weights = [np.array(cell_vars[str(i)]) for i in range(len(cell_vars))]
            elif "vars" in layer_group:
                vars_group = layer_group["vars"]
                weights = [np.array(vars_group[str(i)]) for i in range(len(vars_group))]
            else:
                weights = []
            if weights:
                layer.set_weights(weights)
                print(f"  Cargados pesos para {layer.name}")


def get_lstm_model():
    global lstm_model
    if lstm_model is not None:
        return lstm_model
    try:
        import tensorflow as tf

        weights_path = os.path.join(MODELS_PATH, "lstm_weights.h5")
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Archivo de pesos no encontrado: {weights_path}")
        print("Cargando modelo LSTM con pesos pre-extraidos...")
        lstm_model = build_lstm_architecture()
        load_keras3_weights(lstm_model, weights_path)
        lstm_model.compile(optimizer="adam", loss="mse", metrics=["mae"])
        print("Modelo LSTM reconstruido con pesos cargados correctamente")
    except Exception as e:
        print(f"Error cargando modelo LSTM: {e}")
        import traceback

        traceback.print_exc()
    return lstm_model


try:
    df_consumos = pd.read_csv(os.path.join(DATA_PATH, "consumos_uptc.csv"))
    df_consumos["timestamp"] = pd.to_datetime(df_consumos["timestamp"])
    print(f"Datos cargados: {len(df_consumos):,} registros")
except Exception as e:
    print(f"Error cargando datos: {e}")
    df_consumos = pd.DataFrame()


class PredictionRequest(BaseModel):
    sede: str
    fecha: str
    hora: int = 12


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class RecommendationRequest(BaseModel):
    sede: str
    sector: Optional[str] = None


class ExplainRequest(BaseModel):
    sede: str
    fecha: str
    hora: int = 12


@app.get("/")
def root():
    return {
        "service": "UPTC Energy AI API",
        "version": "1.0.0",
        "endpoints": ["/predict", "/chat", "/stats", "/recommendations", "/anomalies", "/explain", "/model-info", "/health"],
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": get_lstm_model() is not None,
        "data_loaded": len(df_consumos) > 0,
        "ollama_url": OLLAMA_URL,
    }


@app.get("/stats")
def get_stats():
    if df_consumos.empty:
        raise HTTPException(status_code=500, detail="Datos no disponibles")
    stats = {
        "total_registros": len(df_consumos),
        "periodo": {
            "inicio": df_consumos["timestamp"].min().isoformat(),
            "fin": df_consumos["timestamp"].max().isoformat(),
        },
        "sedes": df_consumos["sede"].unique().tolist(),
        "consumo_total_kwh": float(df_consumos["energia_total_kwh"].sum()),
        "consumo_promedio_kwh": float(df_consumos["energia_total_kwh"].mean()),
        "por_sede": {},
    }
    for sede in df_consumos["sede"].unique():
        sede_data = df_consumos[df_consumos["sede"] == sede]
        stats["por_sede"][sede] = {
            "total_kwh": float(sede_data["energia_total_kwh"].sum()),
            "promedio_kwh": float(sede_data["energia_total_kwh"].mean()),
            "registros": len(sede_data),
        }
    return stats


@app.get("/stats/{sede}")
def get_stats_sede(sede: str):
    if df_consumos.empty:
        raise HTTPException(status_code=500, detail="Datos no disponibles")
    sede_data = df_consumos[df_consumos["sede"] == sede]
    if sede_data.empty:
        raise HTTPException(status_code=404, detail=f"Sede '{sede}' no encontrada")
    sectores = [
        "energia_comedor_kwh",
        "energia_salones_kwh",
        "energia_laboratorios_kwh",
        "energia_auditorios_kwh",
        "energia_oficinas_kwh",
    ]
    consumo_sector = {}
    for sector in sectores:
        nombre = sector.replace("energia_", "").replace("_kwh", "").title()
        consumo_sector[nombre] = float(sede_data[sector].sum())
    return {
        "sede": sede,
        "total_kwh": float(sede_data["energia_total_kwh"].sum()),
        "promedio_hora_kwh": float(sede_data["energia_total_kwh"].mean()),
        "consumo_por_sector": consumo_sector,
        "pico_hora": int(sede_data.groupby("hora")["energia_total_kwh"].mean().idxmax()),
        "registros": len(sede_data),
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    model = get_lstm_model()
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")
    if scaler_X is None or scaler_y is None:
        raise HTTPException(status_code=500, detail="Scalers no disponibles")
    try:
        fecha = datetime.strptime(request.fecha, "%Y-%m-%d")
        hora = request.hora
        dia_semana = fecha.weekday()
        mes = fecha.month
        hora_sin = np.sin(2 * np.pi * hora / 24)
        hora_cos = np.cos(2 * np.pi * hora / 24)
        dia_sin = np.sin(2 * np.pi * dia_semana / 7)
        dia_cos = np.cos(2 * np.pi * dia_semana / 7)
        mes_sin = np.sin(2 * np.pi * mes / 12)
        mes_cos = np.cos(2 * np.pi * mes / 12)
        sede_encoded = le_sede.transform([request.sede])[0]
        periodo_encoded = 0
        temp_exterior = 15.0
        ocupacion = 50.0
        es_fin_semana = 1 if dia_semana >= 5 else 0
        es_festivo = 0
        es_parciales = 0
        es_finales = 0
        features = np.array(
            [
                hora_sin,
                hora_cos,
                dia_sin,
                dia_cos,
                mes_sin,
                mes_cos,
                temp_exterior,
                ocupacion,
                sede_encoded,
                periodo_encoded,
                es_fin_semana,
                es_festivo,
                es_parciales,
                es_finales,
            ]
        )
        features_scaled = scaler_X.transform(features.reshape(1, -1))
        sequence = np.tile(features_scaled, (24, 1)).reshape(1, 24, -1)
        pred_scaled = model.predict(sequence, verbose=0)
        pred = scaler_y.inverse_transform(pred_scaled)[0][0]
        return {
            "sede": request.sede,
            "fecha": request.fecha,
            "hora": request.hora,
            "prediccion_kwh": float(max(0, pred)),
            "confianza": 0.90,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    stats = {}
    if not df_consumos.empty:
        stats = {
            "total_registros": len(df_consumos),
            "sedes": df_consumos["sede"].unique().tolist(),
            "consumo_total_kwh": float(df_consumos["energia_total_kwh"].sum()),
            "consumo_promedio_kwh": float(df_consumos["energia_total_kwh"].mean()),
        }
        for sede in stats["sedes"]:
            sede_data = df_consumos[df_consumos["sede"] == sede]
            stats[f"{sede}_promedio"] = float(sede_data["energia_total_kwh"].mean())

    system_prompt = f"""Eres un asistente experto en eficiencia energetica y sostenibilidad para la UPTC (Universidad Pedagogica y Tecnologica de Colombia).

DATOS DEL SISTEMA DE MONITOREO:
- Registros historicos: {stats.get('total_registros', 275387):,} mediciones horarias
- Periodo: 2018-2025
- Sedes monitoreadas: Tunja, Duitama, Sogamoso, Chiquinquira
- Sectores: Comedores, Salones, Laboratorios, Auditorios, Oficinas
- Consumo total historico: {stats.get('consumo_total_kwh', 1398753):,.0f} kWh
- Promedio por hora: {stats.get('consumo_promedio_kwh', 5.08):.2f} kWh

CONSUMO PROMEDIO POR SEDE (kWh/hora):
- Tunja: ~3.2 kWh (sede principal, 18,000 estudiantes)
- Duitama: ~7.1 kWh (sede tecnologica, 5,500 estudiantes)
- Sogamoso: ~7.3 kWh (sede minera con laboratorios especializados, 6,000 estudiantes)
- Chiquinquira: ~2.5 kWh (sede mas pequena, 2,000 estudiantes)

TU ROL:
- Responde en espanol de forma clara, concisa y util
- Proporciona datos especificos cuando sea relevante
- Sugiere acciones concretas de ahorro energetico
- Explica patrones de consumo cuando te pregunten
- Si no tienes informacion especifica, indicalo honestamente"""

    user_message = request.message
    if request.context:
        user_message = f"Contexto: {request.context}\n\nPregunta: {request.message}"

    for model in ["qwen2.5:7b", "llama3.2", "qwen2.5:3b"]:
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": f"{system_prompt}\n\nUsuario: {user_message}\n\nAsistente:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 800,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                    },
                },
                timeout=120,
            )
            if response.status_code == 200:
                result = response.json()
                return {"response": result.get("response", "").strip(), "model": model}
        except Exception:
            continue

    return {
        "response": "El servicio de chat no esta disponible. Verifica que Ollama este corriendo con un modelo instalado.",
        "error": "no_model_available",
    }


@app.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    if df_consumos.empty:
        raise HTTPException(status_code=500, detail="Datos no disponibles")
    sede_data = df_consumos[df_consumos["sede"] == request.sede]
    if sede_data.empty:
        raise HTTPException(status_code=404, detail=f"Sede '{request.sede}' no encontrada")

    recommendations = []
    consumo_hora = sede_data.groupby("hora")["energia_total_kwh"].mean()
    hora_pico = consumo_hora.idxmax()
    hora_valle = consumo_hora.idxmin()
    recommendations.append(
        {
            "tipo": "horario",
            "titulo": "Optimizacion de horarios",
            "descripcion": f"El pico de consumo es a las {hora_pico}:00. Considere redistribuir cargas a horas valle ({hora_valle}:00).",
            "ahorro_estimado_pct": 10,
        }
    )

    consumo_fds = sede_data[sede_data["es_fin_semana"] == True]["energia_total_kwh"].mean()
    consumo_semana = sede_data[sede_data["es_fin_semana"] == False][
        "energia_total_kwh"
    ].mean()
    if consumo_fds > consumo_semana * 0.3:
        recommendations.append(
            {
                "tipo": "fin_semana",
                "titulo": "Reduccion en fines de semana",
                "descripcion": f"El consumo en fin de semana es {consumo_fds:.1f} kWh/h (vs {consumo_semana:.1f} en semana). Verifique equipos encendidos innecesariamente.",
                "ahorro_estimado_pct": 15,
            }
        )

    sectores = {
        "Comedor": "energia_comedor_kwh",
        "Salones": "energia_salones_kwh",
        "Laboratorios": "energia_laboratorios_kwh",
        "Auditorios": "energia_auditorios_kwh",
        "Oficinas": "energia_oficinas_kwh",
    }
    for nombre, col in sectores.items():
        consumo_sector = sede_data[col].mean()
        if consumo_sector > sede_data["energia_total_kwh"].mean() * 0.25:
            recommendations.append(
                {
                    "tipo": "sector",
                    "titulo": f"Alto consumo en {nombre}",
                    "descripcion": f"{nombre} representa un alto porcentaje del consumo. Revisar equipos de climatizacion e iluminacion.",
                    "ahorro_estimado_pct": 8,
                }
            )

    return {
        "sede": request.sede,
        "recomendaciones": recommendations,
        "total_ahorro_estimado_pct": sum(r["ahorro_estimado_pct"] for r in recommendations),
    }


@app.get("/anomalies/{sede}")
def get_anomalies(sede: str, limit: int = 10):
    if df_consumos.empty:
        raise HTTPException(status_code=500, detail="Datos no disponibles")
    sede_data = df_consumos[df_consumos["sede"] == sede].copy()
    if sede_data.empty:
        raise HTTPException(status_code=404, detail=f"Sede '{sede}' no encontrada")

    mean = sede_data["energia_total_kwh"].mean()
    std = sede_data["energia_total_kwh"].std()
    sede_data["z_score"] = (sede_data["energia_total_kwh"] - mean) / std
    anomalies = sede_data[sede_data["z_score"].abs() > 2].head(limit)

    result = []
    for _, row in anomalies.iterrows():
        result.append(
            {
                "timestamp": row["timestamp"].isoformat(),
                "consumo_kwh": float(row["energia_total_kwh"]),
                "z_score": float(row["z_score"]),
                "tipo": "PICO" if row["z_score"] > 0 else "BAJO",
                "severidad": "alta" if abs(row["z_score"]) > 3 else "media",
            }
        )

    return {
        "sede": sede,
        "anomalias": result,
        "umbral_z": 2.0,
        "media_kwh": float(mean),
        "std_kwh": float(std),
    }


@app.post("/explain")
def explain_prediction(request: ExplainRequest):
    """
    Endpoint de Explicabilidad (XAI) - Explica las predicciones del modelo
    Implementa conceptos de SHAP/LIME para transparencia del modelo
    """
    model = get_lstm_model()
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")

    try:
        fecha = datetime.strptime(request.fecha, "%Y-%m-%d")
        hora = request.hora
        dia_semana = fecha.weekday()
        mes = fecha.month

        # Calcular features
        hora_sin = np.sin(2 * np.pi * hora / 24)
        hora_cos = np.cos(2 * np.pi * hora / 24)
        dia_sin = np.sin(2 * np.pi * dia_semana / 7)
        dia_cos = np.cos(2 * np.pi * dia_semana / 7)
        mes_sin = np.sin(2 * np.pi * mes / 12)
        mes_cos = np.cos(2 * np.pi * mes / 12)
        sede_encoded = le_sede.transform([request.sede])[0]
        periodo_encoded = 0
        temp_exterior = 15.0
        ocupacion = 50.0
        es_fin_semana = 1 if dia_semana >= 5 else 0
        es_festivo = 0
        es_parciales = 0
        es_finales = 0

        features = np.array([
            hora_sin, hora_cos, dia_sin, dia_cos, mes_sin, mes_cos,
            temp_exterior, ocupacion, sede_encoded, periodo_encoded,
            es_fin_semana, es_festivo, es_parciales, es_finales
        ])

        # Nombres de features para explicabilidad
        feature_names = [
            "Hora (sin)", "Hora (cos)", "Dia semana (sin)", "Dia semana (cos)",
            "Mes (sin)", "Mes (cos)", "Temperatura", "Ocupacion",
            "Sede", "Periodo academico", "Fin de semana", "Festivo",
            "Semana parciales", "Semana finales"
        ]

        # Obtener prediccion base
        features_scaled = scaler_X.transform(features.reshape(1, -1))
        sequence = np.tile(features_scaled, (24, 1)).reshape(1, 24, -1)
        pred_scaled = model.predict(sequence, verbose=0)
        pred_base = float(scaler_y.inverse_transform(pred_scaled)[0][0])

        # Calcular importancia de features usando perturbacion (similar a SHAP)
        feature_importance = []
        for i in range(len(features)):
            # Perturbar cada feature y medir impacto
            features_perturbed = features.copy()
            features_perturbed[i] = 0  # Setear a cero para ver impacto

            features_perturbed_scaled = scaler_X.transform(features_perturbed.reshape(1, -1))
            sequence_perturbed = np.tile(features_perturbed_scaled, (24, 1)).reshape(1, 24, -1)
            pred_perturbed = model.predict(sequence_perturbed, verbose=0)
            pred_perturbed_val = float(scaler_y.inverse_transform(pred_perturbed)[0][0])

            impact = pred_base - pred_perturbed_val
            feature_importance.append({
                "feature": feature_names[i],
                "valor_actual": float(features[i]),
                "impacto_kwh": round(impact, 4),
                "impacto_porcentual": round((impact / pred_base) * 100, 2) if pred_base != 0 else 0,
                "direccion": "aumenta" if impact > 0 else "disminuye" if impact < 0 else "neutral"
            })

        # Ordenar por impacto absoluto
        feature_importance.sort(key=lambda x: abs(x["impacto_kwh"]), reverse=True)

        # Analisis de datos historicos para contexto
        sede_data = df_consumos[df_consumos["sede"] == request.sede]
        media_historica = float(sede_data["energia_total_kwh"].mean())
        std_historica = float(sede_data["energia_total_kwh"].std())

        # Calcular confianza basada en variabilidad historica
        z_score_pred = (pred_base - media_historica) / std_historica if std_historica > 0 else 0
        confianza = max(0.5, min(0.98, 1 - abs(z_score_pred) * 0.1))

        # Analizar factores contextuales
        factores_contextuales = []

        if es_fin_semana:
            consumo_fds = sede_data[sede_data["es_fin_semana"] == 1]["energia_total_kwh"].mean()
            consumo_lab = sede_data[sede_data["es_fin_semana"] == 0]["energia_total_kwh"].mean()
            diff_pct = ((consumo_fds / consumo_lab) - 1) * 100 if consumo_lab > 0 else 0
            factores_contextuales.append({
                "factor": "Fin de semana",
                "impacto": f"{diff_pct:+.1f}% vs dias laborales",
                "explicacion": "El consumo en fines de semana suele ser menor por menor actividad academica"
            })

        # Analizar hora
        consumo_por_hora = sede_data.groupby("hora")["energia_total_kwh"].mean()
        hora_max = consumo_por_hora.idxmax()
        hora_min = consumo_por_hora.idxmin()
        if hora == hora_max:
            factores_contextuales.append({
                "factor": "Hora pico",
                "impacto": f"Las {hora}:00 es la hora de mayor consumo",
                "explicacion": "Concentracion de actividades academicas y uso de equipos"
            })
        elif hora == hora_min:
            factores_contextuales.append({
                "factor": "Hora valle",
                "impacto": f"Las {hora}:00 es la hora de menor consumo",
                "explicacion": "Baja actividad, ideal para mantenimiento"
            })

        # Analizar mes/estacionalidad
        consumo_por_mes = sede_data.groupby(sede_data["timestamp"].dt.month)["energia_total_kwh"].mean()
        if mes in [1, 6, 7, 12]:  # Meses de vacaciones tipicos
            factores_contextuales.append({
                "factor": "Periodo de vacaciones",
                "impacto": "Consumo reducido esperado",
                "explicacion": "Los meses de vacaciones tienen menor ocupacion universitaria"
            })

        # Generar explicacion en lenguaje natural
        top_features = feature_importance[:3]
        explicacion_natural = f"La prediccion de {pred_base:.2f} kWh para {request.sede} el {request.fecha} a las {hora}:00 "
        explicacion_natural += "esta principalmente influenciada por: "
        explicacion_natural += ", ".join([
            f"{f['feature']} ({f['direccion']} consumo en {abs(f['impacto_porcentual']):.1f}%)"
            for f in top_features if f['impacto_porcentual'] != 0
        ])

        # Calcular nivel de certeza del modelo
        if abs(z_score_pred) < 1:
            nivel_certeza = "ALTO"
            certeza_explicacion = "La prediccion esta dentro del rango normal historico"
        elif abs(z_score_pred) < 2:
            nivel_certeza = "MEDIO"
            certeza_explicacion = "La prediccion esta ligeramente fuera del rango tipico"
        else:
            nivel_certeza = "BAJO"
            certeza_explicacion = "La prediccion esta significativamente fuera del patron historico"

        # Alertas y recomendaciones basadas en la prediccion
        alertas = []
        if pred_base > media_historica + 2 * std_historica:
            alertas.append({
                "tipo": "ALERTA_CONSUMO_ALTO",
                "mensaje": f"Consumo predicho ({pred_base:.2f} kWh) significativamente mayor al promedio ({media_historica:.2f} kWh)",
                "razon": "El modelo detecta condiciones que historicamente generan alto consumo",
                "recomendacion": "Verificar programacion de equipos y considerar redistribuir cargas"
            })
        elif pred_base < media_historica - 2 * std_historica:
            alertas.append({
                "tipo": "ALERTA_CONSUMO_BAJO",
                "mensaje": f"Consumo predicho ({pred_base:.2f} kWh) significativamente menor al promedio",
                "razon": "Puede indicar baja ocupacion o equipos apagados",
                "recomendacion": "Verificar que no haya interrupciones de servicio planificadas"
            })

        return {
            "prediccion": {
                "valor_kwh": round(pred_base, 2),
                "sede": request.sede,
                "fecha": request.fecha,
                "hora": request.hora,
                "confianza": round(confianza, 2)
            },
            "explicabilidad": {
                "metodo": "Perturbation-based Feature Importance (similar a SHAP)",
                "feature_importance": feature_importance,
                "top_3_factores": top_features,
                "explicacion_natural": explicacion_natural
            },
            "contexto_historico": {
                "media_sede_kwh": round(media_historica, 2),
                "std_sede_kwh": round(std_historica, 2),
                "z_score_prediccion": round(z_score_pred, 2),
                "factores_contextuales": factores_contextuales
            },
            "confianza_modelo": {
                "nivel": nivel_certeza,
                "valor_numerico": round(confianza, 2),
                "explicacion": certeza_explicacion
            },
            "alertas": alertas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-info")
def get_model_info():
    """Retorna informacion sobre el modelo para explicabilidad"""
    model = get_lstm_model()

    feature_names = [
        "Hora (componente seno)", "Hora (componente coseno)",
        "Dia de semana (seno)", "Dia de semana (coseno)",
        "Mes (seno)", "Mes (coseno)",
        "Temperatura exterior", "Ocupacion estimada",
        "Sede (codificada)", "Periodo academico",
        "Es fin de semana", "Es festivo",
        "Es semana de parciales", "Es semana de finales"
    ]

    return {
        "nombre": "UPTC Energy LSTM",
        "version": "1.0.0",
        "arquitectura": {
            "tipo": "LSTM (Long Short-Term Memory)",
            "capas": [
                {"nombre": "LSTM 1", "unidades": 128, "dropout": 0.3},
                {"nombre": "LSTM 2", "unidades": 64, "dropout": 0.3},
                {"nombre": "LSTM 3", "unidades": 32, "dropout": 0.2},
                {"nombre": "Dense 1", "unidades": 32, "activacion": "relu"},
                {"nombre": "Dense 2", "unidades": 16, "activacion": "relu"},
                {"nombre": "Salida", "unidades": 1, "activacion": "linear"}
            ],
            "secuencia_entrada": 24,
            "features": 14
        },
        "features": feature_names,
        "metricas_entrenamiento": {
            "mae": 0.734,
            "rmse": 1.630,
            "r2": 0.901,
            "train_samples": 192754,
            "val_samples": 41304,
            "test_samples": 41305
        },
        "interpretacion": {
            "mae_explicacion": "Error absoluto medio de 0.734 kWh - predicciones cercanas al valor real",
            "r2_explicacion": "R² de 0.901 indica que el modelo explica el 90.1% de la variabilidad",
            "uso_recomendado": "Predicciones a corto plazo (1-7 dias) para planificacion energetica"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
