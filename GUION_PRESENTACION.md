# GUION DE PRESENTACION
## UPTC Energy AI - Sistema Inteligente de Gestion Energetica
### IAMinds Hackathon 2026 - Indra Group

---

## ESTRUCTURA DE LA PRESENTACION (10-15 minutos)

---

## 1. INTRODUCCION (1-2 minutos)

### Saludo
> "Buenos dias/tardes, mi nombre es [TU NOMBRE] y vengo a presentarles **UPTC Energy AI**, un sistema inteligente de gestion energetica desarrollado para la Universidad Pedagogica y Tecnologica de Colombia."

### El Problema
> "Las universidades publicas colombianas enfrentan un desafio critico: **el consumo energetico representa hasta el 30% de sus costos operativos**, y en muchos casos, este consumo no esta optimizado."

> "La UPTC, con mas de **31,500 estudiantes** distribuidos en 4 sedes, consume millones de kilovatios-hora al ano. Sin herramientas inteligentes, es imposible identificar patrones de desperdicio, predecir demanda y tomar decisiones informadas."

### La Solucion
> "UPTC Energy AI es una plataforma de inteligencia artificial que transforma datos energeticos en **decisiones accionables**, permitiendo:
> - Predecir el consumo con **90% de precision**
> - Detectar anomalias automaticamente
> - Generar recomendaciones de ahorro personalizadas
> - Y lo mas importante: **explicar** cada decision de la IA"

---

## 2. DATOS Y CONTEXTO (1-2 minutos)

### Los Datos
> "Nuestro sistema fue entrenado con datos **reales** de la UPTC:"

| Metrica | Valor |
|---------|-------|
| Registros historicos | **275,387** mediciones |
| Periodo | 2018 - 2025 (7 anos) |
| Sedes monitoreadas | 4 (Tunja, Duitama, Sogamoso, Chiquinquira) |
| Sectores | Comedores, Salones, Laboratorios, Auditorios, Oficinas |
| Frecuencia | Medicion **cada hora** |

### Sedes UPTC
> "Cada sede tiene caracteristicas unicas:"

| Sede | Estudiantes | Consumo Promedio | Caracteristica |
|------|-------------|------------------|----------------|
| Tunja | 18,000 | 3.2 kWh/h | Sede principal |
| Duitama | 5,500 | 7.1 kWh/h | Sede tecnologica |
| Sogamoso | 6,000 | 7.3 kWh/h | Laboratorios especializados |
| Chiquinquira | 2,000 | 2.5 kWh/h | Sede mas eficiente |

---

## 3. ARQUITECTURA TECNICA (2-3 minutos)

### Stack Tecnologico
> "UPTC Energy AI utiliza tecnologias de vanguardia:"

**Backend:**
- FastAPI (API REST de alto rendimiento)
- TensorFlow 2.18 (modelo de deep learning)
- scikit-learn (preprocesamiento y anomalias)

**Frontend:**
- Streamlit (dashboard interactivo)
- Plotly (visualizaciones dinamicas)

**Inteligencia Artificial:**
- Modelo LSTM para prediccion
- Ollama + Qwen2.5:7b para chat conversacional
- Explicabilidad tipo SHAP/LIME

**Infraestructura:**
- Docker y Docker Compose
- Soporte GPU NVIDIA para aceleracion

### Modelo LSTM
> "El corazon del sistema es un modelo de **redes neuronales recurrentes LSTM**:"

```
Arquitectura:
- Entrada: 24 horas de historial (secuencia temporal)
- LSTM 1: 128 unidades + BatchNorm + Dropout 30%
- LSTM 2: 64 unidades + BatchNorm + Dropout 30%
- LSTM 3: 32 unidades + Dropout 20%
- Dense: 32 -> 16 -> 1 (prediccion)

Features (14 variables):
- Temporales: hora, dia, mes (codificacion ciclica)
- Climaticas: temperatura exterior
- Ocupacion: porcentaje estimado
- Contexto: sede, periodo academico, festivos, parciales
```

### Metricas del Modelo
> "Los resultados de entrenamiento demuestran alta precision:"

| Metrica | Valor | Interpretacion |
|---------|-------|----------------|
| **R²** | 0.901 | Explica el 90% de la variabilidad |
| **MAE** | 0.73 kWh | Error promedio menor a 1 kWh |
| **RMSE** | 1.63 kWh | Desviacion controlada |

---

## 4. DEMO EN VIVO (3-4 minutos)

### 4.1 Dashboard Principal
> "Comenzamos con el dashboard general..."

**Mostrar:**
- KPIs principales (registros, consumo total, promedio)
- Metricas de eficiencia por sede
- **Impacto ambiental**: reduccion de CO2 proyectada
- **Ahorro economico**: millones de pesos anuales
- Graficos de consumo por hora y por sede

**Punto clave:**
> "Con una optimizacion del 15%, la UPTC podria ahorrar **[X] toneladas de CO2** y **[X] millones de pesos** anualmente."

### 4.2 Predicciones
> "El modulo de predicciones permite proyectar el consumo futuro..."

**Mostrar:**
- Seleccionar multiples sedes
- Elegir rango de fechas
- Generar predicciones
- Grafico de prediccion por hora

**Punto clave:**
> "Esto permite a la universidad planificar mantenimiento, redistribuir cargas y negociar mejores tarifas con el operador electrico."

### 4.3 Deteccion de Anomalias
> "El sistema detecta automaticamente consumos anormales..."

**Mostrar:**
- Seleccionar una sede
- Ver anomalias detectadas (picos y bajos)
- Z-score y severidad

**Punto clave:**
> "Detectar un equipo danado o dejado encendido puede prevenir miles de pesos en desperdicios."

### 4.4 Recomendaciones
> "Basado en el analisis, el sistema genera recomendaciones personalizadas..."

**Mostrar:**
- Recomendaciones con porcentaje de ahorro
- Impacto en CO2 y dinero por recomendacion
- Equivalencias ambientales (arboles, km en auto)

### 4.5 IA Explicable (XAI)
> "Este es nuestro diferenciador: **transparencia total** en las decisiones de la IA..."

**Mostrar:**
- Explicar una prediccion especifica
- Importancia de cada variable
- Top 3 factores que influyen
- Nivel de confianza del modelo

**Punto clave:**
> "No es una caja negra. El usuario puede entender **por que** el modelo predice un valor especifico. Esto cumple con estandares de IA responsable y genera confianza."

### 4.6 Chat con IA
> "Finalmente, un asistente conversacional para consultas en lenguaje natural..."

**Mostrar:**
- Preguntar: "Como puedo reducir el consumo en Sogamoso?"
- Preguntar: "Cual es el horario de mayor consumo en Tunja?"

**Punto clave:**
> "El personal no tecnico puede obtener insights sin conocer SQL ni estadistica."

---

## 5. IMPACTO Y VALOR (1-2 minutos)

### Impacto Cuantificable

| Aspecto | Impacto Estimado |
|---------|------------------|
| **Ahorro energetico** | 15-20% reduccion |
| **Ahorro economico** | $50-100M COP/ano |
| **Reduccion CO2** | 10-20 toneladas/ano |
| **Deteccion anomalias** | Prevencion de desperdicios |
| **Planificacion** | Mejor negociacion de tarifas |

### Valor Diferencial

1. **Datos reales**: Entrenado con 7 anos de datos de la UPTC
2. **Explicabilidad**: No es una caja negra, cada prediccion es transparente
3. **Escalabilidad**: Docker permite desplegar en cualquier universidad
4. **Chat IA**: Democratiza el acceso a los datos
5. **Codigo abierto**: Replicable y mejorable

---

## 6. ESCALABILIDAD Y FUTURO (1 minuto)

### Proximos Pasos
> "UPTC Energy AI puede evolucionar hacia:"

1. **Integracion IoT**: Sensores en tiempo real
2. **Alertas automaticas**: Notificaciones por anomalias
3. **Optimizacion automatica**: Control de HVAC con IA
4. **Expansion**: Otras universidades publicas colombianas
5. **API publica**: Integracion con sistemas existentes

### Escalabilidad
> "Gracias a Docker, el sistema puede desplegarse en minutos en cualquier infraestructura. Una universidad solo necesita sus datos historicos para tener su propia instancia."

---

## 7. CIERRE (30 segundos)

### Resumen
> "UPTC Energy AI demuestra que la inteligencia artificial puede generar **impacto real** en la sostenibilidad universitaria. Con predicciones precisas, deteccion de anomalias, recomendaciones accionables y total transparencia, estamos transformando la gestion energetica."

### Llamado a la accion
> "Invitamos a Indra y al ecosistema IAMinds a considerar este proyecto como una solucion escalable para el sector educativo colombiano."

### Agradecimiento
> "Gracias por su atencion. Estoy disponible para preguntas."

---

## PREGUNTAS FRECUENTES (PREPARATE)

### Tecnicas
**P: ¿Por que LSTM y no otro modelo?**
> R: "LSTM es ideal para series temporales porque tiene 'memoria' de patrones pasados. Probamos tambien Random Forest y XGBoost, pero LSTM capturo mejor la estacionalidad."

**P: ¿Como manejan la explicabilidad?**
> R: "Usamos perturbacion de features similar a SHAP. Modificamos cada variable y medimos su impacto en la prediccion, generando explicaciones comprensibles."

**P: ¿Que tan rapido responde el chat?**
> R: "Con GPU, Qwen2.5:7b responde en 5-10 segundos. Sin GPU, puede tomar 30-60 segundos."

### Negocio
**P: ¿Cual es el costo de implementacion?**
> R: "El software es codigo abierto. Solo se requiere infraestructura (servidor con 8GB RAM, GPU opcional) y los datos historicos de consumo."

**P: ¿Funciona con datos de otras universidades?**
> R: "Si. El modelo puede reentrenarse con nuevos datos. La arquitectura es generica."

**P: ¿Como se integra con sistemas existentes?**
> R: "La API REST permite integracion con cualquier sistema. Endpoints documentados en /docs."

---

## TIPS PARA LA PRESENTACION

1. **Practica el demo** - Asegurate que Docker este corriendo antes
2. **Ten datos listos** - Pre-genera algunas predicciones para no esperar
3. **Mira al publico** - No leas, usa el guion como referencia
4. **Enfatiza el impacto** - Los numeros de ahorro son tu argumento mas fuerte
5. **Explica la explicabilidad** - Es tu diferenciador, dedicale tiempo
6. **Controla el tiempo** - 10-15 minutos maximo
7. **Prepara backup** - Ten capturas de pantalla por si falla el demo

---

## COMANDOS UTILES DURANTE EL DEMO

```bash
# Verificar que todo esta corriendo
docker-compose ps

# Si algo falla, reiniciar
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# URLs
# Dashboard: http://localhost:8501
# API Docs:  http://localhost:8080/docs
```

---

**Mucha suerte en tu presentacion!**
