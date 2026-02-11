--======================
--APP: sales
--======================

--- Migration: 0001_initial ---

BEGIN;
--
-- Create model Customer
--
CREATE TABLE "sales_customer" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL UNIQUE, "phone" varchar(20) NOT NULL, "created_at" datetime NOT NULL);
--
-- Create model Product
--
CREATE TABLE "sales_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "price" decimal NOT NULL, "category" varchar(100) NOT NULL, "in_stock" integer unsigned NOT NULL CHECK ("in_stock" >= 0));
--
-- Create model Sale
--
CREATE TABLE "sales_sale" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "total_price" decimal NOT NULL, "sale_date" datetime NOT NULL, "customer_id" bigint NOT NULL REFERENCES "sales_customer" ("id") DEFERRABLE INITIALLY DEFERRED, "product_id" bigint NOT NULL REFERENCES "sales_product" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "sales_sale_customer_id_2d66a408" ON "sales_sale" ("customer_id");
CREATE INDEX "sales_sale_product_id_e01466c2" ON "sales_sale" ("product_id");
COMMIT;



======================
APP: analytics
======================

--- Migration: 0001_initial ---

BEGIN;
--
-- Create model DashboardFilter
--
CREATE TABLE "analytics_dashboardfilter" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "created_at" datetime NOT NULL, "active" bool NOT NULL);
--
-- Create model SalesMetric
--
CREATE TABLE "analytics_salesmetric" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "revenue" decimal NOT NULL, "profit" decimal NOT NULL, "created_at" datetime NOT NULL, "sale_id" bigint NOT NULL UNIQUE REFERENCES "sales_sale" ("id") DEFERRABLE INITIALLY DEFERRED);
COMMIT;



======================
APP: dashboard
======================

--- Migration: 0001_initial ---

BEGIN;
--
-- Create model GraphConfig
--
CREATE TABLE "dashboard_graphconfig" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "chart_type" varchar(50) NOT NULL, "created_at" datetime NOT NULL);
CREATE TABLE "dashboard_graphconfig_sales" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "graphconfig_id" bigint NOT NULL REFERENCES "dashboard_graphconfig" ("id") DEFERRABLE INITIALLY DEFERRED, "sale_id" bigint NOT NULL REFERENCES "sales_sale" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "dashboard_graphconfig_sales_graphconfig_id_sale_id_90185205_uniq" ON "dashboard_graphconfig_sales" ("graphconfig_id", "sale_id");
CREATE INDEX "dashboard_graphconfig_sales_graphconfig_id_0ce3834d" ON "dashboard_graphconfig_sales" ("graphconfig_id");
CREATE INDEX "dashboard_graphconfig_sales_sale_id_3bf0bb5f" ON "dashboard_graphconfig_sales" ("sale_id");
COMMIT;



======================
APP: reports
======================

--- Migration: 0001_initial ---

BEGIN;
--
-- Create model Report
--
CREATE TABLE "reports_report" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "generated_at" datetime NOT NULL, "file" varchar(100) NOT NULL);
CREATE TABLE "reports_report_sales" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "report_id" bigint NOT NULL REFERENCES "reports_report" ("id") DEFERRABLE INITIALLY DEFERRED, "sale_id" bigint NOT NULL REFERENCES "sales_sale" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "reports_report_sales_report_id_sale_id_849fe2c9_uniq" ON "reports_report_sales" ("report_id", "sale_id");
CREATE INDEX "reports_report_sales_report_id_94ce6399" ON "reports_report_sales" ("report_id");
CREATE INDEX "reports_report_sales_sale_id_ac25502d" ON "reports_report_sales" ("sale_id");
COMMIT;



======================
APP: users
======================

--- Migration: 0001_initial ---

BEGIN;
--
-- Create model RevUser
--
CREATE TABLE "users_revuser" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "phone" varchar(20) NOT NULL, "role" varchar(50) NOT NULL);
CREATE TABLE "users_revuser_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "revuser_id" bigint NOT NULL REFERENCES "users_revuser" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "users_revuser_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "revuser_id" bigint NOT NULL REFERENCES "users_revuser" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "users_revuser_groups_revuser_id_group_id_abbb9adc_uniq" ON "users_revuser_groups" ("revuser_id", "group_id");
CREATE INDEX "users_revuser_groups_revuser_id_96ac8f78" ON "users_revuser_groups" ("revuser_id");
CREATE INDEX "users_revuser_groups_group_id_35712688" ON "users_revuser_groups" ("group_id");
CREATE UNIQUE INDEX "users_revuser_user_permissions_revuser_id_permission_id_21e7b551_uniq" ON "users_revuser_user_permissions" ("revuser_id", "permission_id");
CREATE INDEX "users_revuser_user_permissions_revuser_id_15af38a9" ON "users_revuser_user_permissions" ("revuser_id");
CREATE INDEX "users_revuser_user_permissions_permission_id_874d7e85" ON "users_revuser_user_permissions" ("permission_id");
COMMIT;



