# TicketFlow

**Système de gestion de tickets de support client multi-tenant** — API REST construite avec Django 5.x et Django REST Framework.

TicketFlow permet à plusieurs organisations d'utiliser une seule instance pour gérer leurs tickets de support. Chaque organisation dispose de son espace isolé avec ses propres agents, clients et tickets — le tout exposé via une API REST propre, documentée en OpenAPI, et prête à être consommée par n'importe quel frontend.

---

## Le problème

Les PME et startups ont besoin de centraliser les demandes de support de leurs utilisateurs, mais les solutions existantes (Zendesk à $19-115/agent/mois, Freshdesk à $15-79/agent/mois) sont trop coûteuses ou trop complexes. Il n'existe pas de solution open-source légère, multi-tenant, et exposant une API REST propre pour s'intégrer à n'importe quel frontend ou outil tiers.

| Critère | Zendesk | Freshdesk | TicketFlow |
|---------|---------|-----------|------------|
| Modèle | SaaS propriétaire | SaaS propriétaire | Open-source, self-hosted |
| Multi-tenant | Oui (SaaS natif) | Oui (SaaS natif) | Oui (shared DB, schema isolation) |
| API REST | Oui | Oui | Oui — API-first |
| Prix | $19-115/agent/mois | $15-79/agent/mois | Gratuit |
| Personnalisation | Limitée | Limitée | Totale (code source) |

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Langage | Python 3.12+ |
| Framework | Django 5.x + DRF 3.15+ |
| Auth | Simple JWT (access + refresh + rotation + blacklist) |
| Docs API | drf-spectacular (OpenAPI 3.0, Swagger UI, Redoc) |
| Filtrage | django-filter |
| Base de données | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Tâches async | Celery 5.x |
| Containerisation | Docker + docker-compose |
| CI | GitHub Actions (ruff + pytest + check --deploy) |
| Tests | pytest + pytest-django + Factory Boy |
| Linting | ruff |

## Architecture

```
Client HTTP → DRF View → Serializer → Service Layer → ORM (Models) → PostgreSQL
```

Le projet suit le pattern **Service Layer** : les views sont thin (validation + routing), les models sont thin (schéma + managers), et toute la logique métier (transitions de statut, génération de numéros, notifications) vit dans la couche service.

L'isolation multi-tenant utilise la stratégie **Shared Database, Shared Schema** : toutes les organisations partagent les mêmes tables, et chaque QuerySet est filtré par `organization_id`.

### Structure du projet

```
ticketflow/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # CustomUser (email-based), JWT auth
│   ├── organizations/     # Organization, Membership, invitations
│   └── tickets/           # Ticket, Comment, TicketHistory, state machine
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── .github/workflows/ci.yml
```

### Rôles et permissions

Chaque utilisateur est rattaché à une organisation via la table `Membership` avec l'un des 3 rôles :

| Rôle | Périmètre |
|------|-----------|
| **ADMIN** | Gère l'organisation, les membres, voit tous les tickets et stats |
| **AGENT** | Traite les tickets, change les statuts, peut être assigné |
| **CLIENT** | Soumet des tickets, ne voit que les siens, commente |

Un utilisateur peut appartenir à plusieurs organisations avec des rôles différents.

### Workflow des tickets

```
NEW → OPEN → PENDING → RESOLVED → CLOSED
         ↑       ↓
         └───────┘
```

Les transitions sont contrôlées par une machine à états (`state_machine.py`). Toute transition invalide est rejetée par l'API avec un message explicite.

## Installation

### Prérequis

- Docker & docker-compose
- Git

### Lancement

```bash
# Cloner le repo
git clone https://github.com/<votre-username>/ticketflow.git
cd ticketflow

# Copier la config environnement
cp .env.example .env

# Lancer les services (web + PostgreSQL + Redis)
docker-compose up -d --build

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Charger les données de démo
docker-compose exec web python manage.py seed

# L'API est accessible sur http://localhost:8000/api/v1/
```

### Données de démo

La commande `manage.py seed` crée 2 organisations avec des tickets, agents et clients pré-configurés pour tester immédiatement l'API.

## Endpoints API

Tous les endpoints sont préfixés par `/api/v1/`. La documentation interactive est accessible sur :

- **Swagger UI** : `http://localhost:8000/api/docs/`
- **Redoc** : `http://localhost:8000/api/redoc/`


## Documentation technique

La conception complète du projet est documentée dans 3 fichiers :

| Document | Contenu |
|----------|---------|
| [Cahier des Charges](./docs/ticketflow-cdc.html) | Contexte, objectifs, user stories, MoSCoW, workflow, stack, chronogramme (Gantt) |
| [Analyse UML](./docs/ticketflow-uml.html) | Cas d'utilisation, classes, séquences (9 diagrammes), activités (9 diagrammes) |
| [MCD / MLD](./docs/ticketflow-mcd.html) | Modèle conceptuel, modèle logique, dictionnaire de données, contraintes d'intégrité |


## Licence

MIT
