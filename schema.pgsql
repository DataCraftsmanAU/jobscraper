CREATE SCHEMA jobscraper;

CREATE TABLE jobscraper.jobs(
"date" date,
"Work Type" text,
"Search Term" text,
"Job Title" text,
"Company Name" text,
"Location" text,
"Salary" text,
"Link" text,
"Salary Calculation" int,
"Date Removed" date)

ALTER TABLE ONLY jobscraper.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY ("Link");