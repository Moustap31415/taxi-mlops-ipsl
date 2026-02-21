# Documentation CI/CD - GitHub Actions
**Étudiant** : Mouhamadou Moustapha Sow  
**Cours** : Data Engineering, AI Engineering and MLOps  
**Institution** : Institut Polytechnique de Saint Louis (IPSL)  
**Date** : 21 Février 2026  

---

## 1. Architecture CI/CD
```
Code Push → GitHub Actions → Validate Syntax → Trigger Pipeline Databricks
```

**Repository** : https://github.com/Moustap31415/taxi-mlops-ipsl  
**Workflow** : `.github/workflows/databricks-pipeline.yml`  
**Pipeline ID** : fd42f730-389c-4775-a742-bbaab69fbb5a  
**Workspace** : https://dbc-7ca4beb1-ec32.cloud.databricks.com  

---

## 2. Secrets GitHub configurés

| Secret | Description | Statut |
|--------|-------------|--------|
| `DATABRICKS_PROD_HOST` | URL du workspace Databricks | ✅ Configuré |
| `DATABRICKS_PROD_TOKEN` | Token d'authentification | ✅ Configuré |
| `PIPELINE_ID` | ID du pipeline DLT | ✅ Configuré |

---

## 3. Jobs du workflow

### Job 1 : validate-pipeline ✅
**Déclencheur** : Chaque push sur les branches configurées  
**Durée** : ~36 secondes  
**Actions** :
- Checkout du code
- Installation de Python 3.10 et pyspark
- Validation syntaxique de tous les fichiers `.py`

### Job 2 : trigger-pipeline ✅
**Déclencheur** : Push sur main, develop ou feature/MouhamadouMoustaphaSow  
**Durée** : ~2 minutes 49 secondes  
**Actions** :
- Déclenchement automatique du pipeline Databricks
- Attente de la complétion
- Rapport du statut final

### Job 3 : dry-run-on-pr ⏭️
**Déclencheur** : Pull Request vers main uniquement  
**Actions** : Commentaire automatique sur la PR si validation réussie

---

## 4. Comment déclencher le pipeline

### Via GitHub Actions (automatique)
```bash
# Faire une modification dans transformations/
git add .
git commit -m "feat: ma modification"
git push origin feature/MouhamadouMoustaphaSow
# → GitHub Actions se déclenche automatiquement
```

### Via l'interface Databricks (manuel)
1. Aller dans Databricks → Workflows → Delta Live Tables
2. Sélectionner `Complete-MLOps-Pipeline-MouhamadouMoustaphaSow`
3. Cliquer **"Start"**
4. Surveiller la progression dans l'onglet Events

### Via le script trigger_pipeline.py (local)
```bash
export DATABRICKS_HOST="https://dbc-7ca4beb1-ec32.cloud.databricks.com"
export DATABRICKS_TOKEN="votre-token"
python cicd/trigger_pipeline.py --action start-and-wait
```

---

## 5. Surveiller l'exécution

### Sur GitHub Actions
1. Aller sur github.com → repo → onglet **Actions**
2. Cliquer sur le workflow run en cours
3. Voir les logs de chaque job en temps réel

### Sur Databricks
1. Aller dans Workflows → Delta Live Tables
2. Cliquer sur le pipeline
3. Consulter l'onglet **Events** pour le détail
4. Vérifier les tables dans **Catalog Explorer**

---

## 6. Branches et déclencheurs

| Branche | Push | Pull Request |
|---------|------|-------------|
| `main` | ✅ Validate + Trigger | ✅ Dry Run |
| `develop` | ✅ Validate + Trigger | — |
| `feature/MouhamadouMoustaphaSow` | ✅ Validate + Trigger | — |

---

## 7. Troubleshooting

| Problème | Cause | Solution |
|----------|-------|----------|
| Authentication failed | Token invalide ou expiré | Renouveler le token Databricks |
| Pipeline not found | PIPELINE_ID incorrect | Vérifier l'ID dans l'URL Databricks |
| Syntax validation failed | Erreur Python dans le code | Corriger l'erreur signalée dans les logs |
| 409 Conflict | Pipeline déjà en cours | Attendre la fin ou arrêter le pipeline |
| Timeout | Pipeline trop long | Augmenter le timeout dans trigger_pipeline.py |

---

## 8. Historique des exécutions

| Run | Commit | Validate | Trigger | Durée |
|-----|--------|----------|---------|-------|
| #17 | ci: test trigger pipeline | ✅ | ✅ | 2m 49s |
| #16 | ci: test trigger pipeline | ✅ | ❌ (409 Conflict) | 48s |
| #12 | fix: mise a jour Pipeline ID | ✅ | ❌ (token désactivé) | 49s |
| #9 | fix: correction ml_model_registry | ✅ | ❌ (token désactivé) | 49s |
| #8 | fix: suppression colonnes inexistantes | ✅ | ❌ (token désactivé) | 46s |
| #7 | fix: adaptation ml_training_data | ✅ | ❌ (token désactivé) | 49s |
| #6 | fix: adaptation gold layer | ✅ | ❌ (token désactivé) | 50s |
| #5 | fix: adaptation silver layer | ✅ | ❌ (token désactivé) | 44s |