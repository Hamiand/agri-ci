import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

def utcnow(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__="users"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    phone: Mapped[str]=mapped_column(String(30),unique=True,index=True,nullable=False)
    password_hash: Mapped[str]=mapped_column(String(255),nullable=False)
    preferred_language: Mapped[str]=mapped_column(String(10),default="fr",nullable=False)
    status: Mapped[str]=mapped_column(String(20),default="ACTIVE",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Role(Base):
    __tablename__="roles"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    name: Mapped[str]=mapped_column(String(50),unique=True,nullable=False)

class UserRole(Base):
    __tablename__="user_roles"
    user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    role_id: Mapped[int]=mapped_column(ForeignKey("roles.id",ondelete="CASCADE"),primary_key=True)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),nullable=True)
    action: Mapped[str]=mapped_column(String(100),nullable=False)
    entity_type: Mapped[str]=mapped_column(String(100),nullable=False)
    entity_id: Mapped[str|None]=mapped_column(String(100),nullable=True)
    request_id: Mapped[str|None]=mapped_column(String(100),nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Farmer(Base):
    __tablename__="farmers"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),unique=True,nullable=False)
    farmer_ref: Mapped[str]=mapped_column(String(30),unique=True,nullable=False)
    display_name: Mapped[str]=mapped_column(String(150),nullable=False)
    status: Mapped[str]=mapped_column(String(20),default="VERIFIED",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Farm(Base):
    __tablename__="farms"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id",ondelete="CASCADE"),nullable=False)
    name: Mapped[str]=mapped_column(String(150),nullable=False)
    region: Mapped[str|None]=mapped_column(String(100))
    department: Mapped[str|None]=mapped_column(String(100))
    locality: Mapped[str|None]=mapped_column(String(150))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Plot(Base):
    __tablename__="plots"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farms.id",ondelete="CASCADE"),nullable=False)
    plot_ref: Mapped[str]=mapped_column(String(40),nullable=False)
    name: Mapped[str]=mapped_column(String(150),nullable=False)
    area_ha: Mapped[Decimal]=mapped_column(Numeric(12,3),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)
    farm: Mapped["Farm"]=relationship()

class Product(Base):
    __tablename__="products"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    code: Mapped[str]=mapped_column(String(20),unique=True,nullable=False)
    name_fr: Mapped[str]=mapped_column(String(100),nullable=False)
    name_en: Mapped[str]=mapped_column(String(100),nullable=False)
    default_unit: Mapped[str]=mapped_column(String(20),default="kg",nullable=False)
    active: Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)

class Harvest(Base):
    __tablename__="harvests"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    harvest_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id"),nullable=False)
    plot_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("plots.id"),nullable=False)
    product_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
    expected_start_date: Mapped[date]=mapped_column(Date,nullable=False)
    expected_end_date: Mapped[date]=mapped_column(Date,nullable=False)
    estimated_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="FORECAST",nullable=False)
    version: Mapped[int]=mapped_column(Integer,default=1,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class HarvestForecast(Base):
    __tablename__="harvest_forecasts"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    harvest_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("harvests.id",ondelete="CASCADE"),nullable=False)
    revision_no: Mapped[int]=mapped_column(Integer,nullable=False)
    estimated_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    expected_start_date: Mapped[date]=mapped_column(Date,nullable=False)
    expected_end_date: Mapped[date]=mapped_column(Date,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Offer(Base):
    __tablename__="offers"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    offer_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    harvest_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("harvests.id"),nullable=False)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id"),nullable=False)
    product_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
    quantity_total_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    quantity_available_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    quantity_proposed_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),default=0,nullable=False)
    quantity_reserved_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),default=0,nullable=False)
    quantity_sold_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),default=0,nullable=False)
    asking_price_xof_per_kg: Mapped[Decimal|None]=mapped_column(Numeric(14,2))
    quality_grade: Mapped[str|None]=mapped_column(String(20))
    status: Mapped[str]=mapped_column(String(30),default="DRAFT",nullable=False)
    version: Mapped[int]=mapped_column(Integer,default=1,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Text, UniqueConstraint

class Buyer(Base):
    __tablename__="buyers"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),unique=True,nullable=False)
    buyer_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    display_name: Mapped[str]=mapped_column(String(180),nullable=False)
    buyer_type: Mapped[str]=mapped_column(String(30),nullable=False)
    city: Mapped[str|None]=mapped_column(String(100))
    reliability_score: Mapped[Decimal]=mapped_column(Numeric(5,2),default=70,nullable=False)

class Demand(Base):
    __tablename__="demands"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    demand_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    buyer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("buyers.id"),nullable=False)
    product_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
    quantity_required_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    delivery_start_date: Mapped[date]=mapped_column(Date,nullable=False)
    delivery_end_date: Mapped[date]=mapped_column(Date,nullable=False)
    target_price_xof_per_kg: Mapped[Decimal|None]=mapped_column(Numeric(14,2))
    accepted_quality_grades: Mapped[list]=mapped_column(JSONB,default=list,nullable=False)
    delivery_city: Mapped[str]=mapped_column(String(120),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="PUBLISHED",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Match(Base):
    __tablename__="matches"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    demand_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("demands.id",ondelete="CASCADE"),nullable=False)
    offer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("offers.id",ondelete="CASCADE"),nullable=False)
    total_score: Mapped[Decimal]=mapped_column(Numeric(6,2),nullable=False)
    score_components: Mapped[dict]=mapped_column(JSONB,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Aggregation(Base):
    __tablename__="aggregations"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    aggregation_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    demand_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("demands.id"),nullable=False)
    target_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    proposed_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),default=0,nullable=False)
    accepted_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),default=0,nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="PROPOSING",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class AggregationMember(Base):
    __tablename__="aggregation_members"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    aggregation_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("aggregations.id",ondelete="CASCADE"),nullable=False)
    offer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("offers.id"),nullable=False)
    proposed_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    accepted_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),default=0,nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="PROPOSED",nullable=False)

class Commitment(Base):
    __tablename__="commitments"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    commitment_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    aggregation_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("aggregations.id"),nullable=False)
    aggregation_member_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("aggregation_members.id"),nullable=False)
    offer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("offers.id"),nullable=False)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id"),nullable=False)
    quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="PENDING",nullable=False)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    responded_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))

class Order(Base):
    __tablename__="orders"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    order_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    aggregation_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("aggregations.id"),unique=True,nullable=False)
    demand_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("demands.id"),nullable=False)
    buyer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("buyers.id"),nullable=False)
    product_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
    quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="CONFIRMED",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class OrderAllocation(Base):
    __tablename__="order_allocations"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    order_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("orders.id",ondelete="CASCADE"),nullable=False)
    offer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("offers.id"),nullable=False)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id"),nullable=False)
    quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="ALLOCATED",nullable=False)

class DomainEvent(Base):
    __tablename__="domain_events"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    event_type: Mapped[str]=mapped_column(String(100),nullable=False)
    aggregate_type: Mapped[str]=mapped_column(String(50),nullable=False)
    aggregate_id: Mapped[str]=mapped_column(String(100),nullable=False)
    payload: Mapped[dict]=mapped_column(JSONB,nullable=False)
    status: Mapped[str]=mapped_column(String(20),default="PENDING",nullable=False)
    attempts: Mapped[int]=mapped_column(Integer,default=0,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)
    published_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))

class CollectionEvent(Base):
    __tablename__="collection_events"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    collection_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    order_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("orders.id"),nullable=False)
    order_allocation_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("order_allocations.id"),nullable=False)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id"),nullable=False)
    announced_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    received_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    location_name: Mapped[str|None]=mapped_column(String(180))
    status: Mapped[str]=mapped_column(String(30),default="RECEIVED",nullable=False)
    collected_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class QualityCheck(Base):
    __tablename__="quality_checks"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    collection_event_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("collection_events.id",ondelete="CASCADE"),nullable=False)
    grade: Mapped[str]=mapped_column(String(10),nullable=False)
    quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    notes: Mapped[str|None]=mapped_column(Text)
    checked_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class Lot(Base):
    __tablename__="lots"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    lot_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    order_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("orders.id"),nullable=False)
    product_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("products.id"),nullable=False)
    grade: Mapped[str]=mapped_column(String(10),nullable=False)
    quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="READY",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class LotSource(Base):
    __tablename__="lot_sources"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("lots.id",ondelete="CASCADE"),nullable=False)
    quality_check_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("quality_checks.id"),nullable=False)
    quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)

class TransportJob(Base):
    __tablename__="transport_jobs"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    transport_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    order_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("orders.id"),nullable=False)
    transporter_user_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=True,index=True)
    origin: Mapped[str]=mapped_column(String(180),nullable=False)
    destination: Mapped[str]=mapped_column(String(180),nullable=False)
    vehicle_ref: Mapped[str|None]=mapped_column(String(100))
    driver_name: Mapped[str|None]=mapped_column(String(150))
    status: Mapped[str]=mapped_column(String(30),default="PLANNED",nullable=False)
    departed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    arrived_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class TransportJobLot(Base):
    __tablename__="transport_job_lots"
    transport_job_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("transport_jobs.id",ondelete="CASCADE"),primary_key=True)
    lot_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("lots.id"),primary_key=True)

class Delivery(Base):
    __tablename__="deliveries"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    delivery_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    order_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("orders.id"),nullable=False)
    transport_job_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("transport_jobs.id"),nullable=False)
    delivered_quantity_kg: Mapped[Decimal]=mapped_column(Numeric(14,3),nullable=False)
    received_by: Mapped[str]=mapped_column(String(150),nullable=False)
    status: Mapped[str]=mapped_column(String(30),default="DELIVERED",nullable=False)
    delivered_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class PaymentIntent(Base):
    __tablename__="payment_intents"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    payment_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    order_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("orders.id"),nullable=False)
    farmer_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("farmers.id"),nullable=False)
    gross_amount_xof: Mapped[Decimal]=mapped_column(Numeric(16,2),nullable=False)
    deductions_xof: Mapped[Decimal]=mapped_column(Numeric(16,2),default=0,nullable=False)
    net_amount_xof: Mapped[Decimal]=mapped_column(Numeric(16,2),nullable=False)
    currency: Mapped[str]=mapped_column(String(3),default="XOF",nullable=False)
    provider: Mapped[str]=mapped_column(String(50),nullable=False)
    provider_reference: Mapped[str|None]=mapped_column(String(120),unique=True)
    status: Mapped[str]=mapped_column(String(30),default="PENDING",nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class PaymentDeduction(Base):
    __tablename__="payment_deductions"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    payment_intent_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("payment_intents.id",ondelete="CASCADE"),nullable=False)
    deduction_type: Mapped[str]=mapped_column(String(40),nullable=False)
    description: Mapped[str]=mapped_column(String(200),nullable=False)
    amount_xof: Mapped[Decimal]=mapped_column(Numeric(16,2),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class LedgerEntry(Base):
    __tablename__="ledger_entries"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    entry_ref: Mapped[str]=mapped_column(String(40),unique=True,nullable=False)
    payment_intent_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("payment_intents.id"),nullable=False)
    entry_type: Mapped[str]=mapped_column(String(30),nullable=False)
    amount_xof: Mapped[Decimal]=mapped_column(Numeric(16,2),nullable=False)
    currency: Mapped[str]=mapped_column(String(3),default="XOF",nullable=False)
    description: Mapped[str]=mapped_column(String(240),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)

class IdempotencyKey(Base):
    __tablename__="idempotency_keys"
    __table_args__=(UniqueConstraint("user_id","endpoint","key",name="uq_idempotency_user_endpoint_key"),)
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    endpoint: Mapped[str]=mapped_column(String(200),nullable=False)
    key: Mapped[str]=mapped_column(String(120),nullable=False)
    request_hash: Mapped[str]=mapped_column(String(64),nullable=False)
    response_status: Mapped[int|None]=mapped_column(Integer)
    response_body: Mapped[dict|None]=mapped_column(JSONB)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)
