# AGRI-CI Persisted Idempotency — v0.23

For sensitive mutations, the client sends `Idempotency-Key`.

The server:
1. hashes the normalized request payload;
2. locks/looks up `(user_id, endpoint, key)`;
3. rejects reuse with a different payload;
4. returns the persisted completed response on an exact replay;
5. otherwise executes the business mutation;
6. stores response status/body in the same database transaction;
7. commits mutation + replay record atomically.

Failed requests roll back the database session, including an unfinished idempotency row.

Covered code paths now include aggregation, commitment accept/decline, firm order,
collection, quality grading, lot creation, transport creation/departure, delivery,
direct payment creation and settlement preparation.

PostgreSQL runtime replay tests remain required before the commercial gate is green.
