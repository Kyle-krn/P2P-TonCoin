-- upgrade --
CREATE TABLE IF NOT EXISTS "currency_key" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "key" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
-- downgrade --
DROP TABLE IF EXISTS "currency_key";
