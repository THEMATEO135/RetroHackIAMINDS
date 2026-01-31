# UPTC Energy AI

Sistema Inteligente de Gestion Energetica para la Universidad Pedagogica y Tecnologica de Colombia (UPTC).

**IAMinds 2026 Hackathon - Indra Group**

## Caracteristicas

- **Prediccion de Consumo**: Modelo LSTM entrenado con datos reales (R2 = 0.90)
- **Deteccion de Anomalias**: Identificacion automatica de patrones inusuales
- **Recomendaciones**: Sugerencias personalizadas de ahorro energetico
- **Chat IA**: Asistente conversacional con Ollama + Qwen2.5:7b
- **Dashboard**: Visualizacion interactiva con Streamlit

## Deploy Rapido (Docker)

### Requisitos
- Docker y Docker Compose
- 8GB RAM minimo
- GPU NVIDIA (opcional, mejora rendimiento del chat)

### Iniciar el sistema

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/uptc-energy-ai.git
cd uptc-energy-ai

# Iniciar todos los servicios
docker-compose up -d

# Ver logs (opcional)
docker-compose logs -f
```

> **Nota**: En el primer inicio, Ollama descargara automaticamente el modelo Qwen2.5:7b (~4.7GB). Esto puede tomar varios minutos dependiendo de tu conexion.

### URLs de acceso

| Servicio | URL | Descripcion |
|----------|-----|-------------|
| **Dashboard** | http://localhost:8501 | Interfaz principal Streamlit |
| **API** | http://localhost:8080 | Backend FastAPI |
| **Ollama** | http://localhost:11434 | Servidor LLM |

## Endpoints API

```
GET  /health              - Estado del servicio
GET  /stats               - Estadisticas generales
GET  /stats/{sede}        - Estadisticas por sede
POST /predict             - Prediccion de consumo
POST /chat                - Chat con IA
POST /recommendations     - Recomendaciones de ahorro
GET  /anomalies/{sede}    - Anomalias detectadas
```

### Ejemplo de prediccion

```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"sede": "Tunja", "fecha": "2025-03-15", "hora": 12}'
```

### Ejemplo de chat

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Como puedo reducir el consumo en la sede Sogamoso?"}'
```

## Estructura del Proyecto

```
uptc-energy-ai/
├── api/                    # Backend FastAPI
│   └── main.py
├── app/                    # Frontend Streamlit
│   └── streamlit_app.py
├── consumos_uptc_hackday/  # Datos reales UPTC (~275k registros)
├── fase1_modelado_predictivo/
│   └── models/             # Modelo LSTM y scalers
├── docker-compose.yml      # Orquestacion de servicios
├── Dockerfile              # Imagen de la aplicacion
└── requirements.txt        # Dependencias Python
```

## Sedes UPTC

| Sede | Estudiantes | Consumo Promedio |
|------|-------------|------------------|
| Tunja | ~18,000 | 3.2 kWh/hora |
| Duitama | ~5,500 | 7.1 kWh/hora |
| Sogamoso | ~6,000 | 7.3 kWh/hora |
| Chiquinquira | ~2,000 | 2.5 kWh/hora |

## Modelo LSTM

- **Arquitectura**: 3 capas LSTM (128→64→32 unidades)
- **Features**: 14 variables (temporales, climaticas, ocupacion)
- **Secuencia**: 24 horas de historia
- **Metricas**: MAE=0.73 kWh, RMSE=1.63 kWh, R2=0.90

## Comandos utiles

```bash
# Ver estado de los contenedores
docker-compose ps

# Reiniciar un servicio
docker-compose restart api

# Ver logs de un servicio
docker-compose logs -f api

# Detener todo
docker-compose down

# Reconstruir (despues de cambios)
docker-compose build --no-cache
docker-compose up -d
```

## Tecnologias

- **Backend**: FastAPI, TensorFlow 2.18, scikit-learn
- **Frontend**: Streamlit, Plotly
- **LLM**: Ollama + Qwen2.5:7b (4.7GB, mejor que Llama3.2)
- **Contenedores**: Docker, Docker Compose
- **GPU**: Soporte NVIDIA para Ollama

## Troubleshooting

### El chat es lento
- Verifica que Ollama tenga acceso a la GPU: `docker logs uptc-ollama`
- El modelo Qwen2.5:7b requiere ~5GB de VRAM

### Error "Modelo no disponible"
- Verifica que los archivos de modelos existan en `fase1_modelado_predictivo/models/`
- Reinicia la API: `docker-compose restart api`

### Ollama no descarga el modelo
- Ejecuta manualmente: `docker exec -it uptc-ollama ollama pull qwen2.5:7b`

## Licencia

MIT License - IAMinds 2026

---

Desarrollado para el Hackathon IAMinds 2026 - Indra Group
