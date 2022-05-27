-- upgrade --
CREATE UNIQUE INDEX "uid_user_telegra_66ffbd" ON "user" ("telegram_id");
-- downgrade --
DROP INDEX "idx_user_telegra_66ffbd";
