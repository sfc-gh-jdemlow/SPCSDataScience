USE ROLE ACCOUNTADMIN;
ALTER COMPUTE POOL CONTAINER_DEMO_POOL STOP ALL;
ALTER COMPUTE POOL CONTAINER_DEMO_POOL SUSPEND;
DROP SERVICE CONTAINER_DEMO_DB.PUBLIC.modeling_SNOWPARK_SERVICE;
DROP COMPUTE POOL CONTAINER_DEMO_POOL;
DROP DATABASE CONTAINER_DEMO_DB;
DROP WAREHOUSE CONTAINER_DEMO_WH;
DROP ROLE CONTAINER_USER_ROLE;
DROP USER RANDOMEMPLOYEE;
