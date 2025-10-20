# 🏷️ Guide de Classification Automatique - Dremio Connector

## Vue d'ensemble

Le Dremio Connector intègre maintenant la **Classification Automatique** qui détecte automatiquement les colonnes contenant des données sensibles (PII, informations financières, credentials) et leur applique des tags appropriés.

## 🎯 Fonctionnalités

### Tags de Classification Créés

#### PII (Personally Identifiable Information)
- **PII.Email** - Adresses email
- **PII.Phone** - Numéros de téléphone
- **PII.Name** - Noms de personnes
- **PII.Address** - Adresses physiques
- **PII.ID** - Numéros d'identification (SSN, passeport, permis)

#### Sensitive
- **Sensitive.Credential** - Mots de passe, tokens, secrets

#### Financial
- **Financial.CreditCard** - Numéros de carte de crédit
- **Financial.BankAccount** - Numéros de compte bancaire (IBAN, SWIFT)

### Patterns de Détection

Le système détecte automatiquement les colonnes sensibles basé sur les **noms de colonnes** :

| Tag | Patterns détectés |
|-----|------------------|
| PII.Email | email, mail, e_mail, courriel |
| PII.Phone | phone, tel, telephone, mobile, cell |
| PII.Name | name, nom, prenom, firstname, lastname, fullname |
| PII.Address | address, adresse, street, city, ville, zip, postal, country, pays |
| PII.ID | ssn, social_security, passport, license, licence |
| Sensitive.Credential | password, passwd, pwd, token, secret, key, credential |
| Financial.CreditCard | credit_card, creditcard, cc_number, card_number, carte_credit |
| Financial.BankAccount | account, iban, swift, routing, bank_account, compte_bancaire |

## 🚀 Activation de la Classification

### Via l'Interface OpenMetadata

1. **Ouvrir OpenMetadata UI**
   ```
   http://localhost:8585
   ```

2. **Naviguer vers le service Dremio**
   - Cliquez sur **Settings** (⚙️)
   - Sélectionnez **Databases**
   - Cliquez sur **dremio-prod**

3. **Configurer l'agent Metadata**
   - Allez dans l'onglet **Agents**
   - Cliquez sur **Edit** (✏️) sur l'agent Metadata
   - Cochez ☑️ **Enable Auto Classification**
   - Sélectionnez les classifications à appliquer :
     - ☑️ PII
     - ☑️ Sensitive
     - ☑️ Financial

4. **Sauvegarder et lancer l'ingestion**
   - Cliquez sur **Save**
   - Cliquez sur **Run** pour lancer l'ingestion avec classification

### Via Configuration YAML

```yaml
source:
  type: Custom
  serviceName: dremio-prod
  sourceConfig:
    config:
      type: DatabaseMetadata
      # Enable auto classification
      enableAutoClassification: true
      # Classifications to apply
      classificationFilterPattern:
        includes:
          - PII
          - Sensitive
          - Financial
```

## 📊 Vérification des Résultats

### 1. Voir les Tags sur les Colonnes

1. **Naviguer vers une table**
   - Allez dans **Databases** > **dremio-prod**
   - Sélectionnez un source (ex: staging)
   - Sélectionnez un schema (ex: staging)
   - Cliquez sur une table (ex: stg_minio_customers)

2. **Voir les tags appliqués**
   - Dans la section **Schema**, chaque colonne affiche ses tags
   - Les tags automatiques sont marqués avec 🤖 (Automated)
   - Les tags suggérés sont en état "Suggested"

### 2. Exemple de Résultat

Pour la table `staging.staging.stg_minio_customers` :

| Colonne | Type | Tags Appliqués |
|---------|------|----------------|
| customer_id | INTEGER | - |
| customer_name | VARCHAR | 🏷️ PII.Name |
| email | VARCHAR | 🏷️ PII.Email |
| phone | VARCHAR | 🏷️ PII.Phone |
| address | VARCHAR | 🏷️ PII.Address |
| city | VARCHAR | 🏷️ PII.Address |
| country | VARCHAR | 🏷️ PII.Address |
| created_at | TIMESTAMP | - |

### 3. Filtrer par Classification

Dans l'interface OpenMetadata :
- Utilisez le filtre **Tags** pour afficher toutes les colonnes avec un tag spécifique
- Exemple : Filtrer par "PII" pour voir toutes les données personnelles

## 🔍 Méthodes Implémentées

### `yield_tag()`
Crée les tags de classification dans OpenMetadata :
- Définit les 8 catégories de tags (PII, Sensitive, Financial)
- Appelée automatiquement au début de l'ingestion
- Les tags sont réutilisables sur plusieurs tables

### `get_column_tag_labels(table_name, column)`
Classifie chaque colonne individuellement :
- Analyse le nom de la colonne
- Compare avec les patterns de détection
- Retourne les tags appropriés
- État : "Suggested" (l'utilisateur peut approuver/rejeter)

## ⚙️ Code Implémenté

### Structure du Code

```python
# Dans dremio_source.py

def yield_tag(self, *args, **kwargs) -> Iterable[Either[CreateTagRequest]]:
    """Crée les tags de classification PII/Sensitive/Financial"""
    # Définit 8 tags de classification
    # Yield CreateTagRequest pour chaque tag
    
def get_column_tag_labels(
    self,
    table_name: str,
    column: Dict[str, Any]
) -> Optional[List[TagLabel]]:
    """Applique les tags aux colonnes basé sur patterns"""
    # Analyse column_name.lower()
    # Détecte les patterns (email, phone, name, etc.)
    # Retourne List[TagLabel] ou None
```

### Tags Retournés

```python
TagLabel(
    tagFQN=FullyQualifiedEntityName("PII.Email"),
    source=TagSource.Classification,  # Indique que c'est une classification auto
    labelType=LabelType.Automated,    # Tag appliqué automatiquement
    state="Suggested"                  # Nécessite validation utilisateur
)
```

## 🎯 Prochaines Étapes

### 1. Test Immédiat
```bash
# Redéployer le code avec classification
docker exec -u root openmetadata_ingestion rm -rf /opt/airflow/dremio_connector
docker cp c:\projets\dremio\dremio_connector openmetadata_ingestion:/opt/airflow/
docker exec -u root openmetadata_ingestion find /opt/airflow -name "*.pyc" -delete
```

### 2. Activer dans l'UI
- Cocher "Enable Auto Classification"
- Lancer l'ingestion
- Vérifier les tags appliqués

### 3. Valider les Classifications
- Approuver les tags corrects
- Rejeter les faux positifs
- Ajouter des tags manuels si nécessaire

### 4. Créer des Policies
Basé sur les tags, créer des politiques :
- Masquage des données PII
- Accès restreint aux colonnes Sensitive
- Audit des accès aux données Financial

## ⚠️ Considérations Importantes

### 1. Validation Humaine
- Les tags sont en état "Suggested" par défaut
- Un Data Steward doit valider les classifications
- Évite les faux positifs

### 2. Patterns Personnalisables
Pour ajouter des patterns personnalisés, modifier `get_column_tag_labels()` :
```python
# Exemple : Ajouter détection pour un pattern spécifique
if 'customer_id' in column_name or 'client_id' in column_name:
    tags.append(TagLabel(
        tagFQN=FullyQualifiedEntityName("Business.CustomerID"),
        source=TagSource.Classification,
        labelType=LabelType.Automated,
        state="Suggested"
    ))
```

### 3. Performance
- Classification basée uniquement sur les noms de colonnes (pas de scan de données)
- Très rapide, pas d'impact performance
- Pour classification basée sur contenu → utiliser Data Quality Tests

### 4. Conformité
- Utile pour RGPD/GDPR compliance
- Identification automatique des données personnelles
- Base pour mise en place de Data Masking

## 🛡️ Sécurité et Conformité

### RGPD/GDPR
- Identification automatique des données à caractère personnel
- Facilite les audits de conformité
- Base pour les rapports DPIA (Data Protection Impact Assessment)

### Data Masking
Les tags peuvent déclencher automatiquement :
- Masquage des emails (john.doe@example.com → j***@e***.com)
- Hachage des numéros de téléphone
- Redaction des credentials

### Audit Trails
- Toutes les classifications sont tracées
- Qui a créé le tag, quand, pourquoi
- Historique des validations/rejets

## 📈 Monitoring

### Logs à Surveiller
```bash
# Voir les logs de classification
docker logs openmetadata_ingestion | grep "🏷️"

# Exemples de logs :
# 🏷️  Creating classification tags for auto-tagging
#   ✅ Created tag: PII.Email
#   ✅ stg_minio_customers.email: Applied 1 classification tags
#   🏷️  stg_minio_customers.phone: Detected PHONE
```

### Métriques Importantes
- Nombre de colonnes classifiées
- Nombre de colonnes PII découvertes
- Taux de validation des tags suggérés
- Colonnes non classifiées (potentiellement sensibles)

## 🔗 Ressources

- **OpenMetadata Classification**: https://docs.open-metadata.org/connectors/ingestion/workflows/data-quality/auto-classification
- **PII Detection Best Practices**: https://docs.open-metadata.org/connectors/ingestion/workflows/data-quality
- **RGPD Compliance**: https://www.cnil.fr/

---

✅ **Classification implémentée et prête à tester !**

🎯 **Action immédiate** : Redéployer le code et activer "Enable Auto Classification" dans l'UI OpenMetadata.
