# AGRI-CI — Journal du Commercial Pilot Release 1.0

Ce journal donne un résumé lisible des étapes importantes. L'historique Git reste la source détaillée des changements de code.

## Phase A — Cœur transactionnel

Construction du parcours producteur/acheteur/opérations : récolte future, offre, demande, agrégation, engagement, commande, collecte, qualité, lots, transport, livraison et règlement.

## Phase B — Durcissement

Renforcement des contrôles nécessaires au pilote : autorisations, idempotence, intégrité transactionnelle, PostgreSQL/Alembic, concurrence, erreurs HTTP standardisées, audit/outbox, paiements incrémentaux et ledger.

## Phase C — Preuves CI/E2E

Ajout et stabilisation des preuves automatisées : backend, PostgreSQL, migrations, concurrence, scénario `AGRI-CI-001`, build Web pilote et contrôles runtime/commerciaux.

## Phase D — Gel du périmètre Release 1.0

Définition explicite des fonctions nécessaires au premier pilote et exclusion des extensions non bloquantes afin de ne pas retarder la preuve terrain.

## Phase E — Préparation opérationnelle

Ajout du runbook terrain, de la fiche de contrôle de première commande, des responsabilités, des contrôles quotidiens et des critères d'arrêt.

## Phase F — Protection paiement de production

Le webhook/mécanisme générique de paiement de test a été explicitement protégé contre une utilisation comme mécanisme de production non certifié. Le fournisseur réel doit disposer de son intégration et de ses preuves propres.

## Phase G — Documentation durable

Le dépôt contient désormais :

- un historique maître ;
- un guide utilisateur français Release 1.0 ;
- un index documentaire ;
- un tracker séparé des blocages externes de go-live.

Cette organisation évite que l'état du projet dépende d'un historique de conversation ChatGPT.

## Statut actuel

Le statut logiciel et le statut externe doivent rester distincts. La réussite technique du Release 1.0 ne prouve pas que l'infrastructure de production, le fournisseur de paiement, les validations juridiques ou les partenaires réels sont déjà prêts.