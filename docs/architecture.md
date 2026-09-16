# Architecture AGRI-CI v0.1
Architecture initiale : client(s) → FastAPI → services métier → SQLAlchemy → PostgreSQL.
Redis est réservé aux fonctions de cache, limitation, files de travail et coordination lorsque nécessaires.
PostgreSQL reste la source de vérité transactionnelle.
