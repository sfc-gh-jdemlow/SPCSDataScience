USE ROLE ACCOUNTADMIN;

CREATE SECURITY INTEGRATION IF NOT EXISTS snowservices_ingress_oauth
  TYPE=oauth
  OAUTH_CLIENT=snowservices_ingress
  ENABLED=true;


CREATE OR REPLACE NETWORK RULE ALLOW_ALL_RULE
  TYPE = 'HOST_PORT'
  MODE = 'EGRESS'
  VALUE_LIST= ('0.0.0.0:443', '0.0.0.0:80');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ALLOW_ALL_EAI
  ALLOWED_NETWORK_RULES = (ALLOW_ALL_RULE)
  ENABLED = true;

GRANT USAGE ON INTEGRATION ALLOW_ALL_EAI TO ROLE CONTAINER_USER_ROLE;

CREATE COMPUTE POOL IF NOT EXISTS CONTAINER_DEMO_POOL
  MIN_NODES = 1
  MAX_NODES = 2
  INSTANCE_FAMILY = CPU_X64_XS; -- standard_1 has been deprecated
 
-- ALTER COMPUTE POOL CONTAINER_DEMO_POOL SET MAX_NODES = 2;
-- CREATE COMPUTE POOL IF NOT EXISTS CONTAINER_DEMO_POOL
--   MIN_NODES = 1
--   MAX_NODES = 10
--   INSTANCE_FAMILY = CPU_X64_L;
-- ALTER COMPUTE POOL CONTAINER_DEMO_POOL SUSPEND;
-- ALTER COMPUTE POOL CONTAINER_DEMO_POOL STOP ALL;
-- DROP COMPUTE POOL CONTAINER_DEMO_POOL;
-- ALTER COMPUTE POOL CONTAINER_DEMO_POOL SET INSTANCE_FAMILY = CPU_X64_L;

GRANT USAGE ON COMPUTE POOL CONTAINER_DEMO_POOL TO ROLE CONTAINER_USER_ROLE;

USE ROLE CONTAINER_USER_ROLE;
CREATE SERVICE CONTAINER_DEMO_DB.PUBLIC.MODELING_SNOWPARK_SERVICE
in compute pool CONTAINER_DEMO_POOL
from @SPECS
specification_file='modeling.yaml'
external_access_integrations = (ALLOW_ALL_EAI)
MIN_INSTANCES=1
MAX_INSTANCES=1;

USE ROLE ACCOUNTADMIN;
GRANT USAGE ON SERVICE CONTAINER_DEMO_DB.PUBLIC.MODELING_SNOWPARK_SERVICE TO ROLE CONTAINER_USER_ROLE;

CREATE OR REPLACE USER RANDOMEMPLOYEE
IDENTIFIED BY 'Snowflake2024'
DEFAULT_ROLE = 'CONTAINER_USER_ROLE'
DEFAULT_WAREHOUSE = 'CONTAINER_DEMO_WH';

GRANT ROLE CONTAINER_USER_ROLE to USER RANDOMEMPLOYEE;
GRANT USAGE ON WAREHOUSE CONTAINER_DEMO_WH TO ROLE CONTAINER_USER_ROLE;
GRANT USAGE ON SERVICE CONTAINER_DEMO_DB.PUBLIC.modeling_SNOWPARK_SERVICE TO ROLE CONTAINER_USER_ROLE;
