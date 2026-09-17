# AGRI-CI — Règles de maintenance documentaire

1. `PROJECT_STATUS.md` doit refléter le statut synthétique actuel.
2. `HISTORIQUE_MAITRE_AGRI_CI.md` doit être mis à jour lorsqu'une décision majeure de périmètre ou de release change.
3. `CHANGELOG_PILOT_1_0.md` résume les phases importantes ; Git reste la source détaillée des commits.
4. `GUIDE_UTILISATEUR_COMMERCIAL_PILOT_1_0_FR.md` doit rester aligné sur l'interface réellement utilisée.
5. Les captures d'écran doivent provenir de l'environnement déployé correspondant au guide ; ne pas utiliser de maquettes comme preuve d'écran réel.
6. `EXTERNAL_GO_LIVE_BLOCKERS.md` ne doit être coché qu'avec preuve réelle.
7. Une CI verte ne suffit jamais à déclarer les dépendances externes terminées.
8. Les fonctions hors Release 1.0 ne doivent pas être ajoutées au guide du pilote avant leur inclusion explicite dans un futur périmètre.