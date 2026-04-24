"""Event-driven (Pub/Sub) protocol configuration using CloudEvents spec.

Supports async workflow triggers via message brokers (Kafka, NATS).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EventBroker(str, Enum):
    """Supported message broker backends."""

    KAFKA = "kafka"
    NATS = "nats"
    AWS_EVENTBRIDGE = "aws-eventbridge"
    REDIS_STREAMS = "redis-streams"


class EventBusConfig(BaseModel):
    """Configuration for event-driven async messaging.

    Template A (Centralized): Kafka / AWS EventBridge (persistent audit log).
    Template B (Distributed): NATS / JetStream (lightweight, edge-friendly).
    """

    spec: str = Field(default="cloudevents", description="Event specification standard")
    broker: EventBroker = Field(
        default=EventBroker.NATS,
        description="Message broker backend",
    )
    topics: list[str] = Field(
        default_factory=list,
        description="Pre-defined event topics/subjects",
    )
