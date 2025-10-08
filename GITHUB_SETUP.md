# Instructions pour pousser vers GitHub

## 1. Créer le dépôt GitHub
1. Allez sur https://github.com
2. Cliquez sur "New repository"
3. Nommez le dépôt (ex: `dremio-openmetadata-connector`)
4. Ajoutez une description : "Connecteur d'ingestion des métadonnées Dremio vers OpenMetadata"
5. Gardez le dépôt PUBLIC ou PRIVATE selon vos besoins
6. NE PAS initialiser avec README, .gitignore ou licence (nous avons déjà tout)
7. Cliquez "Create repository"

## 2. Lier le dépôt local au dépôt GitHub
Une fois le dépôt créé, utilisez les commandes fournies par GitHub :

```bash
# Ajouter l'origine GitHub (remplacez USERNAME et REPO-NAME)
git remote add origin https://github.com/USERNAME/REPO-NAME.git

# Pousser vers GitHub
git branch -M main
git push -u origin main
```

## 3. Structure du projet sur GitHub
```
dremio-openmetadata-connector/
├── .gitignore                    # Exclusions globales
├── README.md                     # Documentation principale  
├── ingestion/                    # Module d'ingestion principal
│   ├── dremio_ingestion_clean.py # Script d'ingestion optimisé
│   ├── README_CLEAN.md          # Documentation détaillée
│   ├── requirements.txt         # Dépendances Python
│   ├── .env.template           # Template de configuration
│   ├── setup_ingestion.py      # Script de setup
│   └── src/                    # Code source
│       ├── client/             # Clients API
│       └── utils/              # Utilitaires
├── env/                        # Environnement Docker
│   ├── docker-compose-auto.yml # Configuration Docker
│   └── README.md              # Documentation Docker
└── initEnv/                   # Scripts d'initialisation
    ├── *.py                   # Scripts Python
    └── README_*.md           # Documentations
```

## 4. Après la publication
- Mettez à jour le README principal avec les liens GitHub
- Ajoutez des badges de statut si nécessaire
- Configurez les issues/discussions GitHub si souhaité