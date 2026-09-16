from decimal import Decimal
import uuid

from app.payments.router import _attribute_delivery_sources


def test_partial_delivery_pays_only_delivered_fraction():
    """A 3,000 kg truck delivering 1,500 kg must expose only 1,500 kg to settlement.

    The four source quantities mirror the final AGRI-CI-001 allocation after Yao declines:
    Koffi 400, Awa 750, Mariam 600, Cooperative A 1,250 kg.
    """
    job_id=uuid.uuid4()
    farmers=[uuid.uuid4() for _ in range(4)]
    capacities={job_id:Decimal("3000")}
    delivered={job_id:Decimal("1500")}
    sources=[
        (job_id,farmers[0],Decimal("400")),
        (job_id,farmers[1],Decimal("750")),
        (job_id,farmers[2],Decimal("600")),
        (job_id,farmers[3],Decimal("1250")),
    ]

    attributed=_attribute_delivery_sources(capacities,delivered,sources)

    assert attributed=={
        farmers[0]:Decimal("200.000"),
        farmers[1]:Decimal("375.000"),
        farmers[2]:Decimal("300.000"),
        farmers[3]:Decimal("625.000"),
    }
    assert sum(attributed.values(),Decimal("0"))==Decimal("1500.000")
    assert sum(attributed.values(),Decimal("0"))*Decimal("760")==Decimal("1140000.000")
