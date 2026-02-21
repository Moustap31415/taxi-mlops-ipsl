# Data Documentation & Lineage
**Étudiant** : Mouhamadou Moustapha Sow  
**Cours** : Data Engineering, AI Engineering and MLOps  
**Institution** : Institut Polytechnique de Saint Louis (IPSL)  
**Date** : 21 Février 2026  

---

## 1. Data Lineage
```
taxi_mlops_prod.mouhamadou_moustapha_sow.yellowdata (Source)
        │
        │ Ingestion (Auto Loader / Unity Catalog)
        ▼
bronze_taxi_trips
        │
        │ Nettoyage + Feature Engineering
        │ - Filtrage des valeurs invalides
        │ - Calcul trip_duration_minutes, speed_mph
        │ - Extraction pickup_hour, pickup_day_of_week
        │ - Catégorisation time_of_day
        │ - is_rush_hour, trip_category, is_weekend
        ▼
silver_taxi_features
        │
        ├─────────────────────────────────────────┐
        │                                         │
        │ Agrégations                             │ Préparation ML
        ▼                                         ▼
┌───────────────────────┐              ml_training_data
│ gold_hourly_location_ │                    │
│ metrics               │                    ├──────────────┐
├───────────────────────┤                    ▼              ▼
│ gold_daily_time_      │         ml_model_training    ml_predictions
│ patterns              │                    │
├───────────────────────┤                    ▼
│ gold_location_pair_   │         ml_model_registry
│ metrics               │
└───────────────────────┘
```

---

## 2. Data Dictionary

### Table : bronze_taxi_trips
**Description** : Données brutes des courses de taxi NYC  
**Type** : Streaming Table  
**Source** : taxi_mlops_prod.mouhamadou_moustapha_sow.yellowdata

| Colonne | Type | Description |
|---------|------|-------------|
| `tpep_pickup_datetime` | timestamp | Date et heure de prise en charge |
| `tpep_dropoff_datetime` | timestamp | Date et heure de dépose |
| `trip_distance` | double | Distance du trajet en miles |
| `fare_amount` | double | Montant du tarif de base en $ |
| `pickup_zip` | int | Code postal de prise en charge |
| `dropoff_zip` | int | Code postal de dépose |

---

### Table : silver_taxi_features
**Description** : Données nettoyées avec features ML  
**Type** : Streaming Table  
**Source** : bronze_taxi_trips

| Colonne | Type | Description | Origine |
|---------|------|-------------|---------|
| `tpep_pickup_datetime` | timestamp | Date et heure de prise en charge | Bronze |
| `tpep_dropoff_datetime` | timestamp | Date et heure de dépose | Bronze |
| `trip_distance` | double | Distance en miles | Bronze |
| `fare_amount` | double | Montant tarif en $ | Bronze |
| `pickup_zip` | int | Code postal pickup | Bronze |
| `dropoff_zip` | int | Code postal dropoff | Bronze |
| `trip_duration_minutes` | double | Durée du trajet en minutes | Calculé |
| `speed_mph` | double | Vitesse moyenne en mph | Calculé |
| `pickup_hour` | int | Heure de prise en charge (0-23) | Calculé |
| `pickup_day_of_week` | int | Jour de la semaine (1-7) | Calculé |
| `pickup_date` | date | Date de prise en charge | Calculé |
| `time_of_day` | string | Période (morning/afternoon/evening/night) | Calculé |
| `is_rush_hour` | boolean | Indicateur heure de pointe | Calculé ⭐ |
| `trip_category` | string | Catégorie distance (short/medium/long) | Calculé ⭐ |
| `is_weekend` | boolean | Indicateur weekend | Calculé ⭐ |

⭐ Nouvelles features ajoutées par Mouhamadou Moustapha Sow

---

### Table : gold_hourly_location_metrics
**Description** : Métriques horaires par zone de pickup  
**Type** : Materialized View  
**Source** : silver_taxi_features  
**Partition** : pickup_date

| Colonne | Type | Description |
|---------|------|-------------|
| `pickup_date` | date | Date de prise en charge |
| `pickup_hour` | int | Heure de prise en charge |
| `pickup_zip` | int | Zone de pickup |
| `trip_count` | long | Nombre de courses |
| `avg_trip_distance` | double | Distance moyenne |
| `avg_trip_duration` | double | Durée moyenne en minutes |
| `avg_fare_amount` | double | Tarif moyen en $ |
| `avg_speed_mph` | double | Vitesse moyenne en mph |
| `total_revenue` | double | Revenu total en $ |

---

### Table : gold_daily_time_patterns
**Description** : Patterns journaliers par période  
**Type** : Materialized View  
**Source** : silver_taxi_features  
**Partition** : pickup_date

| Colonne | Type | Description |
|---------|------|-------------|
| `pickup_date` | date | Date |
| `pickup_day_of_week` | int | Jour de la semaine |
| `time_of_day` | string | Période de la journée |
| `trip_count` | long | Nombre de courses |
| `avg_trip_distance` | double | Distance moyenne |
| `avg_trip_duration` | double | Durée moyenne |
| `avg_fare_amount` | double | Tarif moyen |
| `avg_speed_mph` | double | Vitesse moyenne |
| `total_revenue` | double | Revenu total |
| `rush_hour_trips` | long | Courses en heure de pointe |
| `weekend_trips` | long | Courses le weekend |

---

### Table : gold_location_pair_metrics
**Description** : Métriques par paire origine-destination  
**Type** : Materialized View  
**Source** : silver_taxi_features  
**Partition** : pickup_date

| Colonne | Type | Description |
|---------|------|-------------|
| `pickup_date` | date | Date |
| `pickup_zip` | int | Zone de départ |
| `dropoff_zip` | int | Zone d'arrivée |
| `route_trip_count` | long | Nombre de courses sur la route |
| `avg_route_distance` | double | Distance moyenne de la route |
| `avg_route_duration` | double | Durée moyenne de la route |
| `avg_route_fare` | double | Tarif moyen de la route |
| `avg_route_speed` | double | Vitesse moyenne sur la route |
| `min_route_duration` | double | Durée minimale |
| `max_route_duration` | double | Durée maximale |

---

### Table : ml_training_data
**Description** : Dataset d'entraînement ML avec split 80/20  
**Type** : Materialized View  
**Source** : silver_taxi_features

| Colonne | Type | Description |
|---------|------|-------------|
| `target_total_amount` | double | Variable cible (fare_amount) |
| `trip_distance` | double | Distance en miles |
| `trip_duration_minutes` | double | Durée en minutes |
| `speed_mph` | double | Vitesse en mph |
| `pickup_hour` | int | Heure de pickup |
| `pickup_day_of_week` | int | Jour de la semaine |
| `time_of_day` | string | Période de la journée |
| `is_rush_hour` | boolean | Heure de pointe |
| `is_weekend` | boolean | Weekend |
| `trip_category` | string | Catégorie de distance |
| `pickup_zip` | int | Zone de pickup |
| `dropoff_zip` | int | Zone de dropoff |
| `pickup_date` | date | Date |
| `is_training` | boolean | True=train (80%), False=test (20%) |

---

### Table : ml_model_training
**Description** : Métriques d'évaluation du modèle  
**Type** : Materialized View  
**Source** : ml_training_data

| Colonne | Type | Description |
|---------|------|-------------|
| `model_type` | string | Type de modèle |
| `rmse` | double | Root Mean Square Error |
| `mae` | double | Mean Absolute Error |
| `correlation` | double | Corrélation prédictions/réalité |
| `training_timestamp` | timestamp | Date d'entraînement |

---

### Table : ml_model_registry
**Description** : Registre des métadonnées du modèle  
**Type** : Materialized View  
**Source** : ml_model_training

| Colonne | Type | Description |
|---------|------|-------------|
| `model_name` | string | Nom du modèle |
| `model_version` | string | Version du modèle |
| `model_type` | string | Type de modèle |
| `model_status` | string | Statut (active/archived) |
| `catalog` | string | Catalog Unity |
| `schema` | string | Schema Unity |
| `rmse` | double | RMSE |
| `mae` | double | MAE |
| `correlation` | double | Corrélation |
| `description` | string | Description du modèle |
| `training_timestamp` | timestamp | Date d'entraînement |
| `registered_at` | timestamp | Date d'enregistrement |

---

### Table : ml_predictions
**Description** : 1000 prédictions avec analyse des erreurs  
**Type** : Materialized View  
**Source** : ml_training_data

| Colonne | Type | Description |
|---------|------|-------------|
| `trip_distance` | double | Distance en miles |
| `trip_duration_minutes` | double | Durée en minutes |
| `speed_mph` | double | Vitesse en mph |
| `pickup_hour` | int | Heure de pickup |
| `pickup_day_of_week` | int | Jour de la semaine |
| `time_of_day` | string | Période |
| `is_rush_hour` | boolean | Heure de pointe |
| `is_weekend` | boolean | Weekend |
| `trip_category` | string | Catégorie distance |
| `pickup_zip` | int | Zone pickup |
| `dropoff_zip` | int | Zone dropoff |
| `actual_total_amount` | double | Montant réel en $ |
| `predicted_total_amount` | double | Montant prédit en $ |
| `prediction_error` | double | Erreur de prédiction |
| `absolute_error` | double | Erreur absolue |
| `error_percentage` | double | Pourcentage d'erreur |

---

## 3. Règles de qualité des données

| Table | Règle | Expression | Action |
|-------|-------|-----------|--------|
| Silver | valid_trip_distance | trip_distance > 0 AND < 100 | Drop |
| Silver | valid_fare | fare_amount > 0 AND < 500 | Drop |
| Silver | valid_timestamps | pickup < dropoff | Drop |
| Silver | valid_trip_duration | duration > 0 AND < 180 | Drop |
| Silver | reasonable_total | fare_amount > 0 AND < 1000 | Warn |

---

## 4. Statistiques des tables

| Table | Type | Enregistrements approximatifs |
|-------|------|------------------------------|
| bronze_taxi_trips | Streaming | Toutes les données yellowdata |
| silver_taxi_features | Streaming | ~95% du bronze (après filtrage) |
| gold_hourly_location_metrics | Materialized View | Agrégations horaires |
| gold_daily_time_patterns | Materialized View | Agrégations journalières |
| gold_location_pair_metrics | Materialized View | Routes avec ≥ 5 courses |
| ml_training_data | Materialized View | 80% train / 20% test |
| ml_model_training | Materialized View | 1 ligne (métriques) |
| ml_model_registry | Materialized View | 1 ligne (métadonnées) |
| ml_predictions | Materialized View | 1000 lignes |