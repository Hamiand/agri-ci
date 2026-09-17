# AGRI-CI — Checklist d’activation DigitalOcean

[English version](DIGITALOCEAN_ACTIVATION_CHECKLIST_EN.md)

Cette checklist commence uniquement lorsque le propriétaire du projet décide d’autoriser la création de ressources DigitalOcean. Elle ne contient aucun secret.

## Avant de cliquer sur « Create Resources »

- [ ] La révision Git exacte à déployer est identifiée.
- [ ] GitHub Actions est vert sur cette révision, y compris les images Docker de production.
- [ ] Le coût affiché par DigitalOcean a été relu et accepté par le propriétaire du projet.
- [ ] PostgreSQL managé est prévu comme base de données de production.
- [ ] Un service Redis/Valkey compatible est prévu si requis par le runtime.
- [ ] L’API, le Web, le worker transactionnel et le job Alembic PRE_DEPLOY sont configurés.
- [ ] Aucun mot de passe, token ou secret réel n’est enregistré dans GitHub.

## Variables API / worker

Configurer comme variables d’exécution dans DigitalOcean :

- `APP_ENV=production`
- `APP_DEBUG=false`
- `DATABASE_URL` = connexion PostgreSQL managée (préférer la connexion privée quand elle est disponible)
- `REDIS_URL` = connexion Redis/Valkey
- `JWT_SECRET` = secret aléatoire fort, stocké comme secret chiffré
- `JWT_ALGORITHM=HS256`
- `JWT_ACCESS_TOKEN_MINUTES=30`
- `JWT_REFRESH_TOKEN_DAYS=30`
- `CORS_ORIGINS=https://www.agri-ci.com`
- `PAYMENT_WEBHOOK_SECRET` = uniquement la valeur de production correspondant au prestataire de paiement retenu

Le worker utilise la même configuration PostgreSQL que l’API. Il n’a aucune route HTTP publique.

## Variable Web

Au moment de construire le Web :

- `NEXT_PUBLIC_API_BASE_URL=https://api.agri-ci.com`

Cette valeur n’est pas un secret.

## Migration

Créer un job `PRE_DEPLOY` :

```sh
alembic upgrade head
```

Le job doit utiliser la même base PostgreSQL que l’API. Si la migration échoue, le déploiement doit être considéré comme échoué.

## Contrôles après le premier déploiement

- [ ] `/health` répond HTTP 200.
- [ ] `/ready` confirme l’accès à PostgreSQL.
- [ ] `/commercial-readiness` passe avec la configuration de production prévue.
- [ ] Le Web charge correctement et appelle l’API en HTTPS.
- [ ] CORS n’autorise que les origines prévues et jamais `*` en production.
- [ ] Le webhook générique/de test de paiement reste bloqué en production.
- [ ] Le worker démarre sans exposition publique.
- [ ] Les logs ne révèlent aucun secret.

## Domaine et HTTPS

Ne modifier les DNS qu’après validation des URL temporaires DigitalOcean.

Cible prévue :

- `www.agri-ci.com` → Web AGRI-CI
- `api.agri-ci.com` → API AGRI-CI

Vérifier ensuite le certificat TLS/HTTPS avant tout trafic pilote.

## Données et reprise

Avant une transaction commerciale réelle :

- [ ] sauvegarde PostgreSQL automatique confirmée ;
- [ ] durée de conservation documentée ;
- [ ] restauration réellement testée ;
- [ ] procédure d’incident documentée ;
- [ ] responsables du pilote identifiés.

## Paiement et terrain

Le déploiement technique ne lève pas les blocages externes suivants :

- prestataire de paiement agréé sélectionné et certifié ;
- validation juridique/confidentialité ;
- agriculteurs/coopérative et acheteur réels ;
- point de collecte et transporteur ;
- répétition terrain contrôlée ;
- première transaction à faible volume et rapprochement final.

## Point d’arrêt utilisateur

La préparation du dépôt peut être faite sans dépense. La première intervention obligatoire du propriétaire intervient au moment d’autoriser le compte DigitalOcean, de confirmer le coût affiché et de créer les ressources payantes. Aucun achat ne doit être effectué automatiquement.
