# AGRI-CI — Historique maître
## Du MVP au Commercial Pilot Release 1.0

Ce document constitue le point de référence durable de l'évolution du projet AGRI-CI. Il complète l'historique Git et les documents techniques du dépôt.

## 1. Vision

AGRI-CI vise à mieux relier production agricole et demande réelle, tout en conservant la traçabilité des quantités, des responsabilités et du règlement au producteur.

Pour éviter qu'un projet trop large ne retarde la preuve de valeur, le périmètre a été recentré sur une transaction agricole complète et contrôlée.

## 2. Chaîne commerciale de référence

La chaîne retenue pour le premier pilote est :

**Producteur → récolte future → offre → demande acheteur → matching/agrégation → engagement → commande → collecte → qualité/lot → transport → livraison → préparation du règlement → prestataire de paiement agréé.**

Le scénario automatisé `AGRI-CI-001` constitue la preuve technique de référence du cœur de cette chaîne.

## 3. Construction du cœur métier

Le projet a progressivement couvert :

- déclaration de récolte future ;
- création d'offres producteur ;
- publication de demandes acheteur ;
- matching et agrégation ;
- engagements producteur ;
- création conditionnelle des commandes ;
- allocations de collecte ;
- enregistrement des quantités réellement collectées ;
- contrôle qualité et lots traçables ;
- transport ;
- livraison partielle ou complète ;
- préparation de règlement sur quantité effectivement livrée ;
- historique et comptabilisation des paiements.

## 4. Durcissement indispensable

Avant de considérer le cœur du MVP comme techniquement prêt pour un pilote, plusieurs mécanismes initialement partiels ont été traités comme obligatoires :

- RBAC et autorisation au niveau des objets/opérations sensibles ;
- idempotence systématique des mutations sensibles ;
- gestion des jetons et mécanismes d'authentification nécessaires au parcours ;
- enveloppes d'erreurs HTTP standardisées et request IDs ;
- PostgreSQL réel et chaîne de migrations Alembic ;
- intégrité transactionnelle ;
- protection contre les courses concurrentes et doubles allocations ;
- transactional outbox et traitement retry-safe ;
- événements/audit ;
- livraison et règlement incrémentaux ;
- sémantique de remplacement pour paiements échoués/remboursés ;
- preuve de ledger de paiement ;
- tests d'intégration PostgreSQL et tests E2E réels.

Ces protections ne doivent pas être affaiblies pour accélérer le pilote.

## 5. CI et preuves d'exécution

La barrière technique Release 1.0 exige sur la même révision de `main` :

- build de l'interface Web pilote ;
- compilation/import backend et tests non-intégration ;
- migration Alembic contre PostgreSQL ;
- tests PostgreSQL d'intégration et de concurrence ;
- scénario E2E authentifié HTTP/PostgreSQL `AGRI-CI-001` ;
- contrôle runtime/configuration commerciale RC1 ;
- absence de blocage logiciel essentiel dans le parcours producteur/acheteur/opérations.

Les preuves détaillées sont conservées dans les documents CI/E2E du dossier `docs/` et dans GitHub Actions.

## 6. Passage au Commercial Pilot Release 1.0

Le périmètre a ensuite été gelé pour empêcher l'ajout de fonctions optionnelles avant le pilote.

Sont explicitement hors Release 1.0 : IA/ML de prévision, Radar national, livestream commerce, USSD/SMS/voix, application Flutter native, déploiement national multi-régions, optimisation géospatiale avancée et scoring automatique de fiabilité des producteurs.

Ces fonctions pourront être réévaluées après la preuve terrain.

## 7. Préparation du pilote terrain

Une documentation opérationnelle a été ajoutée afin de transformer la réussite logicielle en opération contrôlée :

- `COMMERCIAL_PILOT_RELEASE_1_0.md` — définition de la barrière Release 1.0 ;
- `CONTROLLED_FIELD_PILOT_RUNBOOK.md` — procédure terrain ;
- `FIRST_PILOT_ORDER_CONTROL_SHEET.md` — contrôle de la première commande ;
- `GUIDE_UTILISATEUR_COMMERCIAL_PILOT_1_0_FR.md` — guide utilisateur français ;
- documents techniques de preuve sur HTTP, E2E, migrations, concurrence et idempotence.

## 8. Dernier durcissement avant gel technique

Les dernières interventions ont notamment porté sur les responsabilités du pilote, les contrôles quotidiens et la protection du webhook de paiement générique afin qu'il ne soit pas utilisé comme mécanisme de production non certifié.

Le principe est ferme : un mécanisme générique de test ne vaut pas intégration certifiée d'un prestataire de paiement réel.

## 9. Signification de « Release 1.0 ready »

Cela signifie que le cœur logiciel AGRI-CI et l'interface pilote ont satisfait la barrière technique définie pour être raccordés à un environnement contrôlé.

Cela ne signifie pas :

- lancement national ;
- infrastructure de production externe déjà vérifiée ;
- certification d'un prestataire de paiement déjà obtenue ;
- validation juridique déjà obtenue ;
- partenaires terrain déjà contractés ou effectivement embarqués ;
- traitement d'argent réel autorisé sans les contrôles externes.

## 10. Blocages externes de mise en service

Les éléments suivants restent séparés du statut logiciel et doivent être vérifiés dans le monde réel :

1. prestataire de paiement agréé : sélection, credentials, certification/sandbox, webhooks propres au fournisseur et rapprochement ;
2. infrastructure de production : HTTPS, secrets, PostgreSQL/Redis/storage, sauvegardes, test de restauration, monitoring et logs ;
3. partenaires du pilote : producteurs/cooperative, acheteur(s), point de collecte, transporteur et opérateurs autorisés ;
4. procédure terrain : petit volume initial, responsabilités nominatives, gestion des incidents/litiges et critères d'arrêt ;
5. juridique/confidentialité : conditions, données personnelles et conformité opérationnelle/paiement applicables.

Aucun de ces éléments ne doit être déclaré terminé sans preuve.

## 11. Principe du premier pilote

Commencer petit : un produit, une zone clairement délimitée, un petit groupe de producteurs, des acheteurs identifiés, un flux de collecte, un transport autorisé et un prestataire de paiement agréé.

Après chaque commande, rapprocher les quantités et l'argent. Tout écart critique inexpliqué arrête l'augmentation du volume.

## 12. Mesure de la valeur créée

Le pilote doit mesurer notamment les quantités annoncées, offertes, engagées, collectées, livrées et réglées ; le pourcentage vendu avant récolte ; le délai collecte-livraison ; le coût logistique par kg ; le délai de paiement ; les litiges ; et le montant net réellement reçu par chaque producteur.

La question centrale reste :

> **Qu'est-ce qui a réellement changé pour le producteur ?**

---

**Règle de conservation :** toute évolution majeure du périmètre, du statut de release ou des blocages externes doit être reflétée dans ce document afin que l'état du projet ne dépende jamais uniquement de l'historique d'une conversation.