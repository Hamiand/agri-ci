# AGRI-CI — Guide utilisateur
## Commercial Pilot Release 1.0

**Version française — pilote commercial contrôlé**

Ce guide accompagne les utilisateurs du premier pilote commercial AGRI-CI. Il explique le parcours métier par rôle, depuis la récolte future jusqu'au règlement. Il complète le runbook opérationnel et ne remplace pas les contrôles de production, les procédures du prestataire de paiement ni les validations juridiques applicables.

---

## 1. À quoi sert AGRI-CI ?

AGRI-CI organise une transaction agricole traçable entre producteurs et acheteurs :

**Producteur → récolte future → offre → demande acheteur → rapprochement/agrégation → engagement → commande → collecte → qualité/lot → transport → livraison → règlement.**

Pour Release 1.0, l'objectif est volontairement limité : réussir un premier cycle commercial contrôlé avec un produit, une zone délimitée, des participants identifiés et de petits volumes.

AGRI-CI ne doit pas être utilisé comme preuve qu'un lancement national ou un traitement d'argent réel sans contrôles externes est déjà autorisé.

---

## 2. Les rôles

### Producteur
Le producteur déclare sa récolte future, crée une offre, consulte la demande disponible, accepte ou refuse les engagements proposés et suit ses paiements.

### Acheteur
L'acheteur publie ses besoins, suit l'agrégation des quantités et crée une commande ferme lorsque les conditions d'agrégation sont satisfaites.

### Agent de collecte / Opérations
L'agent autorisé enregistre la quantité réellement reçue et le point de collecte. Les opérations enregistrent ensuite la qualité, créent les lots et suivent leur progression.

### Transporteur
Le transporteur identifié prend en charge les lots qui lui sont affectés. Le départ et la livraison doivent être traçables.

### Responsable du pilote
Il supervise les comptes, les contrôles, les rapprochements, les incidents et les critères d'arrêt. Il ne doit pas contourner les règles de rôle ou modifier des données pour masquer un écart.

---

## 3. Avant de commencer

Chaque participant doit disposer de son propre compte et du rôle approprié. Aucun acteur anonyme ne doit enregistrer une collecte, un transport, une livraison ou un règlement.

Avant la première transaction réelle, le responsable du pilote doit vérifier les identités, le produit, les quantités prévues, la période de livraison, le lieu de collecte, les règles de qualité, le prix commercial, les déductions autorisées, les responsabilités de transport et les contacts chargés des litiges.

L'environnement technique doit également avoir passé les contrôles de production : HTTPS, secrets de production, PostgreSQL, sauvegarde et restauration testée, supervision, alertes et intégration vérifiée avec le prestataire de paiement agréé.

---

# PARTIE I — PRODUCTEUR

## 4. Se connecter

1. Ouvrir AGRI-CI à l'adresse fournie par le responsable du pilote.
2. S'authentifier avec son compte personnel.
3. Vérifier que l'espace affiché correspond au rôle **Producteur**.
4. Ne jamais partager ses identifiants avec un collecteur, un acheteur ou un autre producteur.

En cas d'accès à un espace qui ne correspond pas au rôle attendu, ne pas poursuivre la transaction et prévenir le responsable du pilote.

## 5. Déclarer une récolte future

Le producteur commence par déclarer ce qu'il prévoit réellement de récolter.

Renseigner les informations demandées sur la production : produit, quantité prévue et informations de récolte disponibles dans l'interface pilote.

La quantité déclarée doit rester réaliste. Une récolte future est une prévision, pas encore une vente.

Après validation, vérifier que la déclaration apparaît dans l'espace producteur.

## 6. Créer une offre

À partir d'une récolte déclarée, le producteur peut proposer une quantité à la vente.

La quantité offerte ne doit jamais dépasser la quantité encore disponible de la récolte correspondante.

Avant de confirmer, vérifier le produit et la quantité. L'offre devient ensuite disponible dans le parcours commercial AGRI-CI.

## 7. Consulter la demande des acheteurs

L'espace producteur permet de voir les demandes pertinentes disponibles dans le pilote.

Une demande acheteur indique un besoin commercial. Elle ne signifie pas automatiquement que toute la récolte du producteur est vendue.

AGRI-CI rapproche les offres et les demandes puis construit l'agrégation nécessaire.

## 8. Accepter ou refuser un engagement

Lorsqu'AGRI-CI propose un engagement, le producteur doit vérifier les informations avant d'accepter.

**Accepter** signifie que la quantité concernée entre dans le processus menant à la commande. **Refuser** signifie que le producteur ne s'engage pas sur cette proposition.

Ne jamais accepter une quantité que l'on sait ne pas pouvoir fournir.

## 9. Suivre la collecte

Lorsque la transaction avance, le producteur peut consulter les informations de collecte qui lui sont rendues visibles.

Au point de collecte, la quantité réellement reçue doit être enregistrée par un agent autorisé. Le producteur doit signaler immédiatement toute différence importante entre la quantité remise et celle enregistrée.

## 10. Suivre son règlement

Le producteur peut consulter l'historique réel des règlements enregistré dans AGRI-CI.

Le règlement ne doit porter que sur une quantité effectivement livrée et encore non réglée. Un paiement échoué ou remboursé ne doit pas être considéré comme définitivement réglé.

Le producteur doit pouvoir comprendre le montant brut, les déductions autorisées et le montant net qui lui revient.

---

# PARTIE II — ACHETEUR

## 11. Publier une demande

L'acheteur se connecte avec son compte et ouvre son espace Acheteur.

Il publie son besoin réel en renseignant les données demandées dans l'interface : produit, quantité et autres conditions disponibles dans Release 1.0.

Une demande ne doit pas être créée uniquement pour tester un environnement où les autres participants pensent effectuer une transaction réelle.

## 12. Suivre l'agrégation

AGRI-CI rapproche la demande avec les offres disponibles et les engagements des producteurs.

L'acheteur peut suivre l'agrégation et la reprendre lorsque le processus n'est pas encore terminé.

La présence de quelques offres ne suffit pas nécessairement à créer une commande ferme.

## 13. Créer la commande ferme

La commande ne peut être créée qu'une fois la barrière d'agrégation satisfaite.

Avant de poursuivre, l'acheteur doit vérifier la quantité engagée et les conditions commerciales convenues.

Après création, la commande devient la référence du parcours physique : collecte, qualité, lots, transport, livraison et règlement.

## 14. Suivre l'exécution

L'acheteur suit la progression de la commande à travers les étapes opérationnelles.

Il doit pouvoir rapprocher la quantité commandée avec les quantités collectées, qualifiées, transportées et livrées.

Une livraison partielle doit rester identifiable comme telle ; elle ne doit pas être artificiellement transformée en livraison complète.

---

# PARTIE III — COLLECTE, QUALITÉ ET LOTS

## 15. Enregistrer la collecte

Seul un agent autorisé enregistre la collecte.

Pour chaque réception :

1. identifier la commande/allocation concernée ;
2. identifier le producteur ;
3. enregistrer la quantité réellement reçue ;
4. enregistrer le véritable point de collecte ;
5. vérifier le résultat avant validation.

La quantité collectée ne doit jamais dépasser la quantité allouée au producteur.

En cas d'écart, conserver la donnée réelle et déclencher la procédure de vérification. Ne pas modifier artificiellement le poids pour faire correspondre les chiffres.

## 16. Contrôler la qualité

L'opérateur autorisé enregistre le résultat réel du contrôle qualité selon les règles convenues pour le pilote.

La quantité soumise au parcours qualité ne doit pas dépasser ce qui a effectivement été collecté.

Les désaccords de qualité doivent être documentés et traités selon la procédure d'escalade du pilote.

## 17. Créer les lots traçables

Après contrôle, AGRI-CI permet la constitution des lots.

Chaque lot doit rester relié aux données qui expliquent son origine : collecte et contrôle qualité correspondants.

La traçabilité ne doit pas être cassée pour simplifier une opération terrain.

---

# PARTIE IV — TRANSPORT ET LIVRAISON

## 18. Affecter le transport

L'opérateur affecte les lots à un transporteur identifié et autorisé.

Vérifier le transporteur, les lots concernés, l'origine et la destination avant de confirmer l'affectation.

## 19. Enregistrer le départ

Le départ du transport doit être enregistré lorsque la marchandise quitte réellement le point prévu.

Une opération ne doit pas être marquée comme partie uniquement pour faire progresser son statut dans l'application.

## 20. Confirmer la livraison

À destination, l'opérateur autorisé enregistre la quantité effectivement livrée et les informations du réceptionnaire prévues par le pilote.

AGRI-CI accepte le principe de livraison partielle : la quantité enregistrée doit donc correspondre à la réalité.

Une quantité non livrée ne doit jamais entrer dans le règlement comme si elle avait été reçue.

---

# PARTIE V — RÈGLEMENT ET RAPPROCHEMENT

## 21. Préparer le règlement

AGRI-CI prépare le règlement uniquement pour la quantité :

- effectivement livrée ;
- admissible au règlement ;
- qui n'a pas déjà été réglée.

Le prix et les déductions doivent correspondre aux conditions réellement autorisées.

## 22. Paiement par le prestataire agréé

AGRI-CI ne remplace pas un prestataire de paiement agréé.

Pour l'argent réel, le prestataire sélectionné doit être intégré avec ses mécanismes de production vérifiés, notamment l'authentification de ses notifications/webhooks et la protection contre les répétitions frauduleuses ou accidentelles.

L'interface ou le mécanisme générique utilisé pour les tests ne doit pas être considéré comme une certification de paiement de production.

## 23. Vérifier le paiement

Après retour du prestataire, AGRI-CI enregistre le résultat et les écritures de ledger correspondantes.

Le rapprochement doit confirmer :

- quantité réglée ;
- montant brut ;
- déductions autorisées ;
- montant net producteur ;
- référence du prestataire ;
- état réel du paiement.

Un paiement échoué ou remboursé ne compte pas comme quantité définitivement réglée.

---

# PARTIE VI — CONTRÔLE DE LA PREMIÈRE COMMANDE

## 24. Rapprochement obligatoire

Après chaque commande du pilote, vérifier :

| Élément | Contrôle attendu |
|---|---|
| Commandé | correspond aux allocations d'agrégation acceptées |
| Collecté | ne dépasse pas l'allocation producteur |
| Qualité | ne dépasse pas la quantité collectée |
| Lots | restent traçables aux contrôles qualité |
| Transporté | reste traçable aux lots affectés |
| Livré | correspond à la livraison réelle |
| Réglé | ne dépasse jamais le livré |
| Échec/remboursement | n'est pas compté comme définitivement réglé |
| Brut | quantité de règlement × prix convenu |
| Déductions | uniquement les coûts autorisés |
| Net producteur | brut moins déductions autorisées |
| Référence paiement | cohérente avec le résultat du prestataire |

Tout écart inexpliqué empêche d'augmenter le volume du pilote.

## 25. Quand arrêter temporairement les nouvelles transactions

Suspendre les nouvelles transactions commerciales si :

- une quantité est allouée ou réglée deux fois ;
- un utilisateur accède à une opération qu'il n'est pas autorisé à effectuer ;
- une quantité collectée, livrée ou réglée ne peut pas être rapprochée ;
- le résultat du prestataire de paiement ne peut pas être vérifié ;
- le ledger et le règlement du prestataire sont en désaccord ;
- les sauvegardes de la base de production ne sont pas disponibles ;
- une panne critique empêche une supervision fiable ;
- un litige sérieux ne peut pas être relié à des preuves enregistrées.

Préserver les enregistrements. Ne jamais supprimer ou réécrire les preuves pour faire disparaître une anomalie.

---

# PARTIE VII — RESPONSABLE DU PILOTE

## 26. Contrôle quotidien

Avant les opérations du jour : vérifier l'état des services, les alertes, la base de données, les événements de paiement attendus et les incidents ouverts.

Pendant les opérations : surveiller les écarts de quantité, les blocages de rôles, les doubles tentatives, les erreurs de paiement et les étapes qui nécessitent une intervention manuelle.

En fin de journée : rapprocher les commandes actives et conserver les références nécessaires à l'audit du pilote.

## 27. Agrandir progressivement le pilote

Ne pas augmenter simultanément toutes les dimensions.

Après plusieurs commandes correctement rapprochées, augmenter progressivement un élément : nombre de producteurs, nombre d'acheteurs, volume, point de collecte, transporteur, puis éventuellement produit ou région supplémentaire.

Un petit pilote réussi n'est pas une preuve de capacité nationale.

---

# PARTIE VIII — INDICATEURS

## 28. Ce qu'AGRI-CI doit mesurer pendant le pilote

Pour chaque cycle, conserver au minimum :

- quantité annoncée ;
- quantité offerte ;
- quantité engagée ;
- quantité collectée ;
- quantité livrée ;
- quantité réglée ;
- pourcentage vendu avant récolte ;
- délai collecte-livraison ;
- coût logistique par kg ;
- délai de paiement ;
- nombre de litiges et délai de résolution ;
- montant net reçu par chaque producteur ;
- écarts de quantité, qualité, identité ou paiement.

La question centrale du pilote est :

> **Qu'est-ce qui a réellement changé pour le producteur ?**

---

## 29. Ce que Release 1.0 ne prétend pas avoir terminé

Le logiciel peut franchir sa barrière technique sans que les conditions externes de mise en service soient remplies.

Avant un véritable pilote avec argent réel, il reste à vérifier concrètement :

1. le prestataire de paiement agréé et sa certification/intégration de production ;
2. l'infrastructure de production et ses procédures de sauvegarde/restauration/supervision ;
3. les producteurs/cooperative, acheteur(s), point de collecte, transporteur et opérateurs réellement engagés ;
4. la procédure terrain contrôlée et les responsabilités nominatives ;
5. les validations juridiques, confidentialité et conformité applicables.

Ces éléments ne doivent être déclarés terminés qu'après preuve réelle.

---

## 30. Résumé de la première transaction

**Producteur** : déclarer → offrir → examiner → s'engager → remettre la production → vérifier le paiement.

**Acheteur** : demander → suivre l'agrégation → commander → suivre la livraison.

**Opérations** : collecter → contrôler la qualité → créer les lots → affecter le transport → confirmer la livraison → préparer le règlement → rapprocher.

**AGRI-CI** : protéger les rôles et les quantités → conserver la traçabilité → empêcher les doubles opérations → enregistrer les événements → permettre le rapprochement.

---

**Document de référence : AGRI-CI Commercial Pilot Release 1.0**

Pour les opérations terrain détaillées, utiliser également `CONTROLLED_FIELD_PILOT_RUNBOOK.md` et `FIRST_PILOT_ORDER_CONTROL_SHEET.md`.