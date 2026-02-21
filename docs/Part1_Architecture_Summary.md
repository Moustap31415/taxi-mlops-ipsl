# Résumé de l'Architecture Pipeline MLOps
**Étudiant** : Mouhamadou Moustapha Sow  
**Cours** : Data Engineering, AI Engineering and MLOps  
**Institution** : Institut Polytechnique de Saint Louis (IPSL)  
**Date** : 21 Février 2026  

---

## 1. Vue d'ensemble

Ce projet implémente un pipeline MLOps complet basé sur l'architecture Medallion 
(Bronze, Silver, Gold) en utilisant Databricks Delta Live Tables (DLT). 
L'objectif est de prédire le montant des courses de taxi à New York (NYC) 
à partir des données historiques de la NYC Taxi & Limousine Commission.

Le pipeline est déployé sur :
- **Plateforme** : Databricks (AWS)
- **Catalog** : taxi_mlops_prod
- **Schema** : mouhamadou_moustapha_sow
- **Compute** : Serverless

---

## 2. Architecture Medallion

### Couche Bronze — Ingestion des données brutes
La couche Bronze constitue le point d'entrée des données. Elle ingère les données 
brutes directement depuis la table Unity Catalog `yellowdata` sans transformation. 
Cette couche conserve les données dans leur format original pour garantir la 
traçabilité et permettre la reprise en cas d'erreur.

**Table** : `bronze_taxi_trips`  
**Type** : Streaming Table  
**Source** : `taxi_mlops_prod.mouhamadou_moustapha_sow.yellowdata`  
**Colonnes** : tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, 
fare_amount, pickup_zip, dropoff_zip

### Couche Silver — Nettoyage et Feature Engineering
La couche Silver applique des règles de qualité sur les données brutes et crée 
des features ML. Les enregistrements invalides sont supprimés grâce aux 
expectations DLT. Cette couche transforme les données brutes en données 
exploitables pour les modèles ML.

**Table** : `silver_taxi_features`  
**Type** : Streaming Table  
**Règles de qualité** :
- trip_distance entre 0 et 100 miles
- fare_amount entre 0 et 500$
- trip_duration_minutes entre 0 et 180 minutes
- pickup_datetime < dropoff_datetime

**Features créées** :
- `trip_duration_minutes` : durée du trajet en minutes
- `speed_mph` : vitesse moyenne en mph
- `pickup_hour` : heure de prise en charge
- `pickup_day_of_week` : jour de la semaine
- `time_of_day` : catégorie (morning/afternoon/evening/night)
- `is_rush_hour` : indicateur heure de pointe *(nouvelle feature)*
- `trip_category` : catégorie de distance (short/medium/long) *(nouvelle feature)*
- `is_weekend` : indicateur weekend *(nouvelle feature)*

### Couche Gold — Agrégations analytiques
La couche Gold produit trois vues matérialisées agrégées, optimisées pour 
l'analyse et l'alimentation des modèles ML.

**Tables** :
- `gold_hourly_location_metrics` : métriques horaires par zone de pickup
- `gold_daily_time_patterns` : patterns journaliers par période de la journée
- `gold_location_pair_metrics` : métriques par paire origine-destination

Toutes les tables Gold sont partitionnées par `pickup_date` pour optimiser 
les performances de requête.

### Couche ML — Entraînement et Inférence
La couche ML implémente le pipeline complet d'apprentissage automatique.

**Tables** :
- `ml_training_data` : données d'entraînement avec split 80/20
- `ml_model_training` : métriques d'évaluation (RMSE, MAE, corrélation)
- `ml_model_registry` : registre des métadonnées du modèle
- `ml_predictions` : 1000 prédictions avec analyse des erreurs

---

## 3. Flux de données
```
yellowdata (Unity Catalog)
        │
        ▼
bronze_taxi_trips (Raw)
        │
        ▼
silver_taxi_features (Cleaned + Features)
        │
        ├──────────────────────────┐
        ▼                          ▼
Gold Tables (3)              ml_training_data
                                   │
                             ┌─────┴─────┐
                             ▼           ▼
                    ml_model_training  ml_predictions
                             │
                             ▼
                    ml_model_registry
```

---

## 4. CI/CD

Le pipeline est automatisé via GitHub Actions avec deux jobs principaux :
- **Validate Pipeline Syntax** : vérifie la syntaxe Python à chaque push
- **Trigger Pipeline** : déclenche le pipeline Databricks automatiquement

**Repository** : https://github.com/Moustap31415/taxi-mlops-ipsl  
**Pipeline ID** : fd42f730-389c-4775-a742-bbaab69fbb5a

---

## 5. Problèmes rencontrés et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Volume not found | Chemin Auto Loader incorrect | Lecture directe depuis Unity Catalog table |
| Colonnes manquantes | Table yellowdata simplifiée | Adaptation du code aux colonnes disponibles |
| Tokens désactivés | Restriction admin IPSL | Validation syntaxique uniquement en CI/CD |
| PERMISSION_DENIED | Schema partagé `default` | Utilisation du schema personnel |