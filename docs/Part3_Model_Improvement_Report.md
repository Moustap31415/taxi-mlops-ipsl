# Rapport d'Amélioration du Modèle ML
**Étudiant** : Mouhamadou Moustapha Sow  
**Cours** : Data Engineering, AI Engineering and MLOps  
**Institution** : Institut Polytechnique de Saint Louis (IPSL)  
**Date** : 21 Février 2026  

---

## 1. Modèle Original (V1)

### Formule
```
predicted_fare = 3.0 (base)
               + trip_distance × 2.5
               + trip_duration_minutes × 0.5
               + 2.0 si time_evening
               + 3.0 si time_night
               + 5.0 si is_airport_pickup
               + 5.0 si is_airport_dropoff
               + passenger_count × 0.5
```

### Limitations identifiées
- Ne prend pas en compte les heures de pointe
- Pas de différenciation selon la distance du trajet
- Colonnes `is_airport_pickup`, `passenger_count` non disponibles dans le dataset

---

## 2. Modèle Amélioré (V2)

### Formule
```
predicted_fare = 3.0 (base)
               + trip_distance × 2.5
               + trip_duration_minutes × 0.5
               + 2.0 si time_evening
               + 3.0 si time_night
               + 2.0 si is_rush_hour        ← NOUVEAU
               + 1.5 si trip_category = "long"  ← NOUVEAU
```

### Améliorations apportées

**Amélioration 1 : Rush Hour Surcharge (+2.0$)**
- Ajout d'une majoration de 2.0$ pour les courses pendant les heures de pointe
- Justification : Les embouteillages augmentent la durée et le coût réel
- Impact : Meilleure prédiction pour ~30% des courses (heures de pointe)

**Amélioration 2 : Long Trip Adjustment (+1.5$)**
- Ajout d'une majoration de 1.5$ pour les trajets longs (> 10 miles)
- Justification : Les longs trajets ont des coûts additionnels (péages, etc.)
- Impact : Meilleure prédiction pour les trajets vers les aéroports

---

## 3. Comparaison des performances

### Requêtes SQL de comparaison
```sql
-- Voir les métriques du modèle V2
SELECT 
  model_type,
  ROUND(rmse, 2) as rmse,
  ROUND(mae, 2) as mae,
  ROUND(correlation, 4) as correlation,
  training_timestamp
FROM taxi_mlops_prod.mouhamadou_moustapha_sow.ml_model_training;

-- Analyser la distribution des erreurs de prédiction
SELECT 
  ROUND(AVG(absolute_error), 2) as avg_error,
  ROUND(MAX(absolute_error), 2) as max_error,
  ROUND(MIN(absolute_error), 2) as min_error,
  ROUND(PERCENTILE(absolute_error, 0.50), 2) as median_error,
  ROUND(PERCENTILE(absolute_error, 0.95), 2) as p95_error,
  ROUND(AVG(error_percentage), 2) as avg_error_pct
FROM taxi_mlops_prod.mouhamadou_moustapha_sow.ml_predictions;

-- Analyser les erreurs par catégorie de trajet
SELECT 
  trip_category,
  COUNT(*) as nb_predictions,
  ROUND(AVG(absolute_error), 2) as avg_error,
  ROUND(AVG(error_percentage), 2) as avg_error_pct
FROM taxi_mlops_prod.mouhamadou_moustapha_sow.ml_predictions
GROUP BY trip_category
ORDER BY avg_error DESC;

-- Analyser les erreurs par heure de pointe
SELECT 
  is_rush_hour,
  COUNT(*) as nb_predictions,
  ROUND(AVG(absolute_error), 2) as avg_error,
  ROUND(AVG(error_percentage), 2) as avg_error_pct
FROM taxi_mlops_prod.mouhamadou_moustapha_sow.ml_predictions
GROUP BY is_rush_hour;

-- Comparer modèle V1 vs V2 (simulation V1 sans nouvelles features)
SELECT
  'V1 (sans rush_hour, sans trip_category)' as model_version,
  ROUND(SQRT(AVG(POW(
    (3.0 + trip_distance * 2.5 + trip_duration_minutes * 0.5) - actual_total_amount
  , 2))), 2) as rmse_simule,
  ROUND(AVG(ABS(
    (3.0 + trip_distance * 2.5 + trip_duration_minutes * 0.5) - actual_total_amount
  )), 2) as mae_simule
FROM taxi_mlops_prod.mouhamadou_moustapha_sow.ml_predictions
UNION ALL
SELECT
  'V2 (avec rush_hour et trip_category)' as model_version,
  ROUND(SQRT(AVG(POW(predicted_total_amount - actual_total_amount, 2))), 2) as rmse,
  ROUND(AVG(ABS(predicted_total_amount - actual_total_amount)), 2) as mae
FROM taxi_mlops_prod.mouhamadou_moustapha_sow.ml_predictions;
```

---

## 4. Analyse des cas de mauvaise prédiction

### Cas où le modèle sous-estime
- Courses très longues avec beaucoup d'arrêts (embouteillages)
- Courses nocturnes avec suppléments non capturés
- Trajets avec péages non inclus dans les données

### Cas où le modèle sur-estime
- Courses courtes avec vitesse élevée (peu de trafic)
- Trajets rapides hors heures de pointe

---

## 5. Recommandations pour améliorations futures

1. **Ajouter les données météo** : La pluie augmente significativement 
   la demande et les durées de trajet à NYC

2. **Intégrer is_weekend dans la formule** : Les courses du weekend 
   ont des patterns différents (sorties nocturnes, moins de rush hour)

3. **Features d'interaction** : Combiner distance × time_of_day pour 
   capturer les effets non-linéaires

4. **Modèle plus sophistiqué** : Remplacer la régression linéaire par 
   un Random Forest ou XGBoost pour capturer les non-linéarités

5. **Données historiques** : Ajouter la popularité historique des routes 
   comme feature pour améliorer les prédictions