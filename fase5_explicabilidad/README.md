# Fase 5 - Explicabilidad y Etica (XAI)

## Objetivo
Garantizar que las decisiones del modelo sean transparentes y auditables mediante tecnicas de IA explicable.

## Estructura
```
fase5_explicabilidad/
|-- src/
|   |-- explainability.py  # Implementacion SHAP/LIME
|-- reports/               # Reportes generados
```

## Tecnicas Implementadas

### SHAP (SHapley Additive exPlanations)
- Basado en teoria de juegos cooperativos
- Calcula contribucion de cada feature a la prediccion
- Visualizaciones: summary plot, waterfall, force plot

### LIME (Local Interpretable Model-agnostic Explanations)
- Explicaciones locales para instancias individuales
- Genera modelo interpretable alrededor de la prediccion
- Muestra reglas simples que aproximan el modelo

## Outputs Generados

### 1. Importancia Global de Features
```
Top Features por Importancia SHAP:
1. hora: 0.2341
2. ocupacion_estimada: 0.1892
3. temperatura_exterior: 0.1456
4. dia_semana: 0.1234
5. sector_Comedores: 0.0987
```

### 2. Explicacion Individual
```
El consumo predicho es 45.3 kWh.
El valor base esperado es 32.1 kWh.
El consumo es MAYOR al esperado debido a:
  - hora (aumenta 8.2 kWh)
  - ocupacion_estimada (aumenta 3.5 kWh)
  - sector_Laboratorios (aumenta 2.1 kWh)
```

### 3. Nivel de Confianza
- Prediccion promedio
- Desviacion estandar
- Coeficiente de variacion

## Visualizaciones

### SHAP Summary Plot
![SHAP Summary](reports/shap_summary.png)

Muestra importancia y direccion del impacto de cada feature.

### SHAP Waterfall
![SHAP Waterfall](reports/shap_waterfall_1.png)

Descompone una prediccion individual en contribuciones.

## Uso

```bash
python src/explainability.py
```

## Metricas de Impacto

| Metrica | Descripcion |
|---------|-------------|
| Reduccion kWh | Ahorro energetico estimado |
| Reduccion CO2 | Huella de carbono evitada |
| Ahorro COP | Impacto economico proyectado |

## Panel de IA Explicable

El dashboard incluye panel que muestra:
- Variables que mas influyeron en la prediccion
- Por que se genero una alerta o recomendacion
- Nivel de confianza del modelo

## Consideraciones Eticas

1. **Transparencia**: Todas las predicciones son explicables
2. **Auditabilidad**: Logs de decisiones del modelo
3. **Sesgo**: Monitoreo de equidad entre sedes/sectores
4. **Privacidad**: No se procesan datos personales
