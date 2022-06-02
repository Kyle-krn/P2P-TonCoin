-- upgrade --
CREATE TABLE IF NOT EXISTS "order_proof" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "file_path" VARCHAR(255) NOT NULL,
    "order_id" UUID NOT NULL REFERENCES "order" ("uuid") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "order_proof";
