# Documentation des Features - Feature Engineering
**Étudiant** : Mouhamadou Moustapha Sow  
**Cours** : Data Engineering, AI Engineering and MLOps  
**Institution** : Institut Polytechnique de Saint Louis (IPSL)  
**Date** : 21 Février 2026  

---

## 1. Features existantes

| Feature | Description | Calcul |
|---------|-------------|--------|
| `trip_duration_minutes` | Durée du trajet en minutes | (dropoff - pickup) / 60 |
| `speed_mph` | Vitesse moyenne en mph | (distance / duration) * 60 |
| `pickup_hour` | Heure de prise en charge (0-23) | HOUR(tpep_pickup_datetime) |
| `pickup_day_of_week` | Jour de la semaine (1-7) | DAYOFWEEK(tpep_pickup_datetime) |
| `pickup_date` | Date de prise en charge | TO_DATE(tpep_pickup_datetime) |
| `time_of_day` | Période de la journée | morning/afternoon/evening/night |

---

## 2. Nouvelles Features ajoutées

### Feature 1 : `is_rush_hour`

**Description** : Indicateur booléen signalant si la course a eu lieu 
pendant les heures de pointe.

**Calcul** :
```python
is_rush_hour = True si pickup_hour entre 7h-9h OU entre 17h-19h
             = False sinon
```

**Justification business** : Les heures de pointe à New York correspondent 
aux trajets domicile-travail le matin (7h-9h) et travail-domicile le soir 
(17h-19h). Durant ces périodes, la demande de taxis augmente fortement, 
ce qui se traduit par des durées de trajet plus longues à cause des 
embouteillages, et potentiellement des tarifs plus élevés. Cette feature 
permet au modèle de capturer cet effet sur le montant final de la course.

**Règle de qualité** : Aucune — valeur booléenne calculée, toujours valide.

**Impact attendu sur le modèle** : +2.0$ sur le montant prédit.

---

### Feature 2 : `trip_category`

**Description** : Catégorie de distance du trajet (short, medium, long).

**Calcul** :
```python
trip_category = "short"  si trip_distance < 2 miles
              = "medium" si trip_distance entre 2 et 10 miles
              = "long"   si trip_distance >= 10 miles
```

**Justification business** : Les courses de taxi à New York suivent des 
patterns de tarification différents selon la distance. Les courts trajets 
(< 2 miles) sont souvent des déplacements intra-Manhattan avec un tarif 
minimum. Les trajets moyens (2-10 miles) représentent la majorité des 
courses. Les longs trajets (> 10 miles) incluent souvent des trajets vers 
les aéroports avec des suppléments. Cette segmentation aide le modèle à 
mieux différencier les structures tarifaires.

**Règle de qualité** : Dépend de `valid_trip_distance` (0 < distance < 100).

**Impact attendu sur le modèle** : +1.5$ supplémentaire pour les trajets "long".

---

### Feature 3 : `is_weekend`

**Description** : Indicateur booléen signalant si la course a eu lieu 
un weekend (samedi ou dimanche).

**Calcul** :
```python
is_weekend = True si pickup_day_of_week IN (1, 7)  # 1=Dimanche, 7=Samedi
           = False sinon
```

**Justification business** : Les patterns de déplacement à New York sont 
très différents entre la semaine et le weekend. Le weekend, on observe 
davantage de trajets de loisirs (restaurants, sorties nocturnes) avec des 
distances et durées différentes, moins d'embouteillages aux heures habituelles 
mais plus de trafic le soir. Cette feature permet au modèle de capturer 
ces différences de comportement.

**Règle de qualité** : Aucune — valeur booléenne calculée, toujours valide.

**Impact attendu sur le modèle** : Feature utilisée pour l'analyse, 
pas encore intégrée dans la formule de prédiction (amélioration future).

---

## 3. Résumé des règles de qualité

| Règle | Expression | Action |
|-------|-----------|--------|
| `valid_trip_distance` | trip_distance > 0 AND < 100 | Drop |
| `valid_fare` | fare_amount > 0 AND < 500 | Drop |
| `valid_timestamps` | pickup < dropoff | Drop |
| `valid_trip_duration` | duration > 0 AND < 180 min | Drop |
| `reasonable_total` | fare_amount > 0 AND < 1000 | Warn |

---

## 4. Impact sur le modèle ML

L'intégration des nouvelles features dans la formule de prédiction :
```
predicted_fare = 3.0 (base)
               + trip_distance × 2.5
               + trip_duration_minutes × 0.5
               + 2.0 si time_evening
               + 3.0 si time_night
               + 2.0 si is_rush_hour      ← NOUVELLE FEATURE
               + 1.5 si trip_category = "long"  ← NOUVELLE FEATURE
```