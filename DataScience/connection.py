# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_Connection.ipynb.

# %% auto 0
__all__ = ['load_credentials', 'write_to_json', 'create_snowflake_session', 'get_connection_params', 'execute_sql_file']

# %% ../nbs/00_Connection.ipynb 3
import os
import json
import warnings
import logging

from snowflake.snowpark import Session

logging.getLogger('snowflake.snowpark').setLevel(logging.WARNING)

# %% ../nbs/00_Connection.ipynb 4
def load_credentials(file_path: str) -> dict:
    """
    Load credentials from a specified JSON file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Credentials file not found at {file_path}")

    with open(file_path) as f:
        data = json.load(f)

    required_keys = ["username", "password", "account"]
    if not all(key in data for key in required_keys):
        raise KeyError(f"Missing required credentials in {file_path}")

    return data


# %% ../nbs/00_Connection.ipynb 5
def write_to_json(username, password, account, file_name):
    data = {
        "username": username,
        "password": password,
        "account": account
    }
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file)


# %% ../nbs/00_Connection.ipynb 6
def create_snowflake_session(creds: dict = None, creds_file_path: str = None, **kwargs) -> Session:
    """
    Create a Snowflake session using Snowpark with given credentials.

    This function attempts to create a session using credentials passed directly,
    loaded from a specified file, or provided as keyword arguments. It prioritizes
    direct credentials, then credentials file, and finally environment variables
    and keyword arguments for any missing values.

    Parameters:
    - creds: A dictionary containing Snowflake connection parameters. Optional.
    - creds_file_path: A path to a file from which to load credentials. Optional.
    - **kwargs: Additional keyword arguments to override or specify connection parameters.

    Returns:
    - A Snowpark Session object if successful, None otherwise.
    """

    if os.path.isfile("/snowflake/session/token"):
        session_config = {
            'host': os.getenv('SNOWFLAKE_HOST'),
            'port': os.getenv('SNOWFLAKE_PORT'),
            'protocol': "https",
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'authenticator': "oauth",
            'token': open('/snowflake/session/token', 'r').read(),
            'warehouse': kwargs.get("warehouse") or os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': kwargs.get("database") or os.getenv('SNOWFLAKE_DATABASE'),
            'schema': kwargs.get("schema") or os.getenv('SNOWFLAKE_SCHEMA'),
            'client_session_keep_alive': True
        }

    elif creds_file_path is not None:
        creds = load_credentials(creds_file_path)

    else:
        creds = creds or {}
        session_config = {
            'account': creds.get("account") or os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': creds.get("username") or os.getenv('SNOWFLAKE_USER'),
            'password': creds.get("password") or os.getenv('SNOWFLAKE_PASSWORD'),
            'role': kwargs.get("role") or os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
            'warehouse': kwargs.get("warehouse") or os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': kwargs.get("database") or os.getenv('SNOWFLAKE_DATABASE'),
            'schema': kwargs.get("schema") or os.getenv('SNOWFLAKE_SCHEMA'),
            'client_session_keep_alive': True
        }
        # Check for missing or empty session configurations
        for key in ['account', 'user', 'password', 'role', 'warehouse', 'database', 'schema']:
            if key not in session_config or not session_config[key]:
                warnings.warn(f"Missing or empty session configuration for '{key}'.")

        # Update session_config with any additional kwargs
        session_config.update(kwargs)

    try:
        session = Session.builder.configs(session_config).create()
        logging.info("Snowpark session successfully created.")
        return session
    except Exception as e:
        logging.info(f"Error creating Snowpark session: {e}")
        return None

# %% ../nbs/00_Connection.ipynb 7
def get_connection_params(session):
    """Useful in session utility to retrieve common connection parameters"""
    conn = session.connection
    params = {
        "user": conn.user,
        "role": conn.role,
        "warehouse": conn.warehouse,
        "database": conn.database,
        "schema": conn.schema,
    }
    return params


# %% ../nbs/00_Connection.ipynb 8
def execute_sql_file(session: Session, file_path: str):
    """
    Execute multiple SQL commands from a file using a Snowpark session.

    Args:
    session (Session): A Snowpark Session object.
    file_path (str): Path to the SQL file containing the commands.

    Raises:
    FileNotFoundError: If the SQL file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SQL file not found at {file_path}")

    with open(file_path, 'r') as file:
        sql_content = file.read()

    sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]

    for command in sql_commands:
        try:
            if command:
                logging.info(f"Executing command:\n{command}")
                session.sql(command).collect()
                logging.info("Successfully executed")
        except Exception as e:
            logging.info(f"Error executing command: {command}\nError: {e}")
    
