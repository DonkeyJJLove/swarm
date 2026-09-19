-- Test-runtime bootstrap only. This does not define an authoritative production schema.
CREATE TABLE drone_data (
    drone_id TEXT NOT NULL,
    position JSONB NOT NULL,
    battery_level INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
