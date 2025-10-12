# 🚀 Guide de Démarrage Rapide

Guide visuel pour démarrer avec le connecteur Dremio OpenMetadata en 5 minutes.

---

## Prérequis

✅ Python 3.8+  
✅ Dremio installé et accessible (localhost:9047 ou URL distante)  
✅ OpenMetadata installé et accessible (localhost:8585 ou URL distante)  
✅ Token JWT OpenMetadata

---

## Étape 1 : Installation (2 min)

### Windows (PowerShell)

```powershell
# Cloner le projet
git clone https://github.com/Monsau/dremio_connector.git
cd dremio_connector

# Créer environnement virtuel
python -m venv venv_dremio
.\venv_dremio\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt

# Installer le package
pip install -e .
```

### Linux/Mac (Bash)

```bash
# Cloner le projet
git clone https://github.com/Monsau/dremio_connector.git
cd dremio_connector

# Créer environnement virtuel
python3 -m venv venv_dremio
source venv_dremio/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Installer le package
pip install -e .
```

---

## Étape 2 : Obtenir le Token JWT (1 min)

1. Ouvrir OpenMetadata : http://localhost:8585
2. Cliquer sur **Settings** (⚙️) en haut à droite
3. Aller dans **Bots** → **ingestion-bot**
4. Cliquer sur **Revoke & Generate New Token**
5. **Copier le token** (il commence par `eyJ...`)

![JWT Token Screenshot](https://via.placeholder.com/800x200?text=OpenMetadata+JWT+Token+Generation)

---

## Étape 3 : Créer le Service OpenMetadata (30 sec)

### Option A : Utiliser un service existant

Si vous avez déjà un service (ex: `dremio_dbt_service`), passez à l'étape 4.

### Option B : Créer un nouveau service

```bash
python examples/create_service.py
```

Modifier le fichier si nécessaire :
```python
config = {
    "openmetadata_url": "http://localhost:8585/api",
    "jwt_token": "VOTRE_TOKEN_JWT_ICI",
    "service_name": "dremio_service"
}
```

---

## Étape 4 : Configurer la Synchronisation (1 min)

Éditer `examples/full_sync_example.py` :

```python
config = {
    # Configuration Dremio
    "dremio_url": "http://localhost:9047",  # ⬅️ Votre URL Dremio
    "dremio_user": "admin",                 # ⬅️ Votre utilisateur
    "dremio_password": "admin123",          # ⬅️ Votre mot de passe
    
    # Configuration OpenMetadata
    "openmetadata_url": "http://localhost:8585/api",
    "jwt_token": "VOTRE_TOKEN_JWT_ICI",     # ⬅️ Token obtenu à l'étape 2
    "service_name": "dremio_service"        # ⬅️ Nom du service (étape 3)
}
```

---

## Étape 5 : Lancer la Synchronisation (30 sec)

```bash
python examples/full_sync_example.py
```

### Sortie Attendue

```
================================================================================
🚀 SYNCHRONISATION AUTOMATIQUE DREMIO → OPENMETADATA
================================================================================

Configuration:
  • Dremio:        http://localhost:9047
  • OpenMetadata:  http://localhost:8585/api
  • Service:       dremio_service
  • User:          admin

✅ Authentification Dremio réussie
🔍 Démarrage auto-discovery Dremio...
📦 10 items racine trouvés

✓ [HOME   ] @admin
✓ [SPACE  ] Analytics
✓ [DATASET] Analytics.Vue_Clients_Complets
✓ [SPACE  ] Reports
✓ [SPACE  ] DataLake
✓ [DATASET] DataLake.Dashboard_Geographique
✓ [SOURCE ] PostgreSQL_Business
✓ [FOLDER ] PostgreSQL_Business.public
✓ [DATASET] PostgreSQL_Business.public.clients
✓ [DATASET] PostgreSQL_Business.public.commandes
...

✅ Découverte terminée: 36 ressources
📊 Répartition: {'home': 1, 'space': 7, 'dataset': 20, 'folder': 6, 'source': 2}

✅ Database: dremio_service.Analytics
✅ Schema: dremio_service.Analytics.default
✅ Table: dremio_service.Analytics.default.Vue_Clients_Complets (5 colonnes)
...

================================================================================
📊 STATISTIQUES DE SYNCHRONISATION
================================================================================
Ressources découvertes:     36
Databases créées/màj:       9
Schemas créés/màj:          15
Tables créées/màj:          20
Erreurs:                    0
Durée:                      12.34s
================================================================================

✅ SYNCHRONISATION TERMINÉE

📊 Résultats:
   • Ressources découvertes:  36
   • Databases créées/màj:    9
   • Schemas créés/màj:       15
   • Tables créées/màj:       20
   • Erreurs:                 0
   • Durée:                   12.34s

🎉 Vos ressources Dremio sont maintenant disponibles dans OpenMetadata!
   Visitez: http://localhost:8585 → Services → dremio_service
```

---

## Étape 6 : Vérifier dans OpenMetadata (1 min)

1. Ouvrir http://localhost:8585
2. Cliquer sur **Explore** → **Databases**
3. Chercher votre service : `dremio_service`
4. Explorer vos databases, schemas et tables

Vous devriez voir :
```
dremio_service/
├── Analytics/
│   └── default/
│       └── Vue_Clients_Complets
├── PostgreSQL_Business/
│   └── public/
│       ├── clients
│       ├── commandes
│       └── produits
└── staging/
    └── staging/
        ├── stg_customers
        └── stg_orders
```

---

## 🎉 Félicitations !

Vous avez synchronisé avec succès vos métadonnées Dremio dans OpenMetadata !

### Prochaines Étapes

1. **Explorer les tables** : Cliquez sur une table pour voir les colonnes, types, descriptions
2. **Vérifier le lineage** : Si vous utilisez dbt, le lineage devrait être visible
3. **Ajouter des descriptions** : Enrichissez vos métadonnées dans OpenMetadata
4. **Automatiser** : Configurez un cron/scheduler pour synchroniser régulièrement

---

## 🔄 Exécutions Suivantes

La synchronisation est **idempotente** - vous pouvez la relancer sans problème :

```bash
# Re-synchroniser (met à jour les changements)
python examples/full_sync_example.py
```

Les ressources existantes seront mises à jour, les nouvelles seront créées.

---

## 🆘 Besoin d'Aide ?

### Erreurs Courantes

#### ❌ `Échec authentification Dremio: 401`
**Solution** : Vérifiez username/password dans la config

#### ❌ `Échec database Analytics: 404`
**Solution** : Le service n'existe pas. Lancez `python examples/create_service.py`

#### ⚠️ `Timeout pour minio-storage/analytics`
**Normal** : Dossiers MinIO vides, le connecteur continue

#### ❌ `ModuleNotFoundError: No module named 'dremio_connector'`
**Solution** : Réinstallez : `pip install -e .`

### Documentation Complète

- [README.md](../README.md) - Documentation principale
- [ENRICHMENT_PLAN.md](ENRICHMENT_PLAN.md) - Feuille de route
- [Examples](../examples/) - Exemples additionnels

---

## 💡 Utilisation Programmatique

Au lieu d'utiliser l'exemple, vous pouvez intégrer directement :

```python
from dremio_connector import sync_dremio_to_openmetadata

# Synchronisation en une ligne
stats = sync_dremio_to_openmetadata(
    dremio_url="http://localhost:9047",
    dremio_user="admin",
    dremio_password="admin123",
    openmetadata_url="http://localhost:8585/api",
    jwt_token="eyJ...",
    service_name="dremio_service"
)

print(f"✅ {stats['tables_created']} tables créées !")
```

---

**Temps total : 5 minutes** ⏱️  
**Ressources découvertes : 36** 📊  
**Taux de succès : 100%** ✅

🎉 **Profitez de vos métadonnées Dremio dans OpenMetadata !**
