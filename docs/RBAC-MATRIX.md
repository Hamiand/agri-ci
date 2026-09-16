# AGRI-CI RBAC Matrix

| Area | Allowed roles |
|---|---|
| Farmer profile/harvest/offer | FARMER, COOPERATIVE_MANAGER, ADMIN |
| Buyer demand/order | BUYER, PRO_BUYER, ADMIN + object ownership |
| Commitment response | owning FARMER / cooperative + ADMIN |
| Collection/quality mutation | COLLECTION_AGENT, OPERATIONS_MANAGER, ADMIN |
| Lot/transport mutation | TRANSPORTER, OPERATIONS_MANAGER, ADMIN |
| Delivery confirmation | OPERATIONS_MANAGER, ADMIN |
| Settlement preparation | OPERATIONS_MANAGER, ADMIN |
| Provider success development seam | OPERATIONS_MANAGER, ADMIN |

Object-level authorization remains mandatory in addition to role authorization.
