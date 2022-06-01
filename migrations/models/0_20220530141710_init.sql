-- upgrade --
CREATE TABLE IF NOT EXISTS "currency" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "exchange_rate" DECIMAL(1000,2) NOT NULL,
    "is_active" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "currency" IS 'валюта платежа';
CREATE TABLE IF NOT EXISTS "lang" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "target_table" VARCHAR(255),
    "target_id" UUID,
    "rus" TEXT NOT NULL,
    "eng" TEXT NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "lang" IS 'таблица с переводами всех названий и сообщений бота';
CREATE TABLE IF NOT EXISTS "staff" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "login" VARCHAR(255) NOT NULL,
    "password" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "staff" IS 'данные о администраторах системы';
CREATE TABLE IF NOT EXISTS "user" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "telegram_id" BIGINT NOT NULL UNIQUE,
    "tg_username" VARCHAR(255),
    "wallet" VARCHAR(255),
    "balance" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "frozen_balance" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "lang" VARCHAR(30),
    "referal_user_id" UUID REFERENCES "user" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "user" IS 'данные о пользователях';
CREATE TABLE IF NOT EXISTS "order" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "state" VARCHAR(255) NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "origin_amount" DOUBLE PRECISION NOT NULL,
    "margin" INT NOT NULL,
    "final_price" DECIMAL(1000,2) NOT NULL,
    "commission" DOUBLE PRECISION NOT NULL,
    "min_buy_sum" DOUBLE PRECISION NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "currency_id" UUID NOT NULL REFERENCES "currency" ("uuid") ON DELETE CASCADE,
    "customer_id" UUID REFERENCES "user" ("uuid") ON DELETE CASCADE,
    "parent_id" UUID REFERENCES "order" ("uuid") ON DELETE SET NULL,
    "seller_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "order" IS 'заказ на покупку-продажу Toncoin';
CREATE TABLE IF NOT EXISTS "order_amount_change" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "old_amount" DOUBLE PRECISION NOT NULL,
    "new_amount" DOUBLE PRECISION NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "order_id" UUID NOT NULL REFERENCES "order" ("uuid") ON DELETE CASCADE,
    "staff_id" UUID REFERENCES "staff" ("uuid") ON DELETE CASCADE,
    "target_order_id" UUID NOT NULL REFERENCES "order" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "order_amount_change" IS 'модель изменения продаваемого количества Toncoin в заказе Order';
CREATE TABLE IF NOT EXISTS "order_state_change" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "old_state" VARCHAR(255) NOT NULL,
    "new_state" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "order_id" UUID NOT NULL REFERENCES "order" ("uuid") ON DELETE CASCADE,
    "staff_id" UUID REFERENCES "staff" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "order_state_change" IS 'модель изменения статуса заказ Order';
CREATE TABLE IF NOT EXISTS "payment_operation" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "recipient_data" TEXT NOT NULL,
    "state" VARCHAR(255) NOT NULL,
    "check" VARCHAR(255),
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "order_id" UUID NOT NULL REFERENCES "order" ("uuid") ON DELETE CASCADE,
    "recipient_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE,
    "sender_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "payment_operation" IS 'операция перечисления средств от покупателя продавцу';
CREATE TABLE IF NOT EXISTS "user_balance_change" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "type" VARCHAR(255) NOT NULL,
    "amount" DOUBLE PRECISION,
    "hash" VARCHAR(255),
    "wallet" VARCHAR(255),
    "code" VARCHAR(255),
    "state" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "user_balance_change" IS 'данные пополнениях и списаниях баланса в Toncoin пользователя';
CREATE TABLE IF NOT EXISTS "user_payment_account_type" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "serial_int" INT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "data" JSONB NOT NULL,
    "is_active" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "currency_id" UUID NOT NULL REFERENCES "currency" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "user_payment_account_type" IS 'способ оплаты, на который можно отправлять фиат при покупке Toncoin';
CREATE TABLE IF NOT EXISTS "user_payment_account" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "serial_int" INT NOT NULL,
    "data" JSONB NOT NULL,
    "is_active" BOOL NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "type_id" UUID NOT NULL REFERENCES "user_payment_account_type" ("uuid") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "user_payment_account" IS 'данные о счете пользователя, на который можно отправлять фиат при покупке Toncoin';
CREATE TABLE IF NOT EXISTS "order_user_payment_account" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "is_active" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" UUID NOT NULL REFERENCES "user_payment_account" ("uuid") ON DELETE CASCADE,
    "order_id" UUID NOT NULL REFERENCES "order" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "order_user_payment_account" IS 'модель изменения статуса заказ Order';
CREATE TABLE IF NOT EXISTS "user_referal_bonus" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "state" VARCHAR(255) NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL  DEFAULT 1,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "invited_user_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
COMMENT ON TABLE "user_referal_bonus" IS 'данные о вознаграждениях пользователям за регистрацию по их приглашениям';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
