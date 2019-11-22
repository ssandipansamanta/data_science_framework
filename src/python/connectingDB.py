import sqlalchemy as db_engine
import json
import pandas as pd
import gc
import logging as lg

def connect_db(db_credential_path: str, db_credential_file_name: str):
    db_credentials = json.loads(pd.read_json(db_credential_path + db_credential_file_name +'.json').to_json())
    engine = db_engine.create_engine(db_credentials["DBCredentials"]['0']['DBType'] + '://' +
                                     db_credentials["DBCredentials"]['0']['USERID'] + ':' +
                                     db_credentials["DBCredentials"]['0']['PASSWORD'] + '@' +
                                     db_credentials["DBCredentials"]['0']['HOST'] + ':' +
                                     db_credentials["DBCredentials"]['0']['PORT'] + '/' +
                                     db_credentials["DBCredentials"]['0']['Database'], echo=False)

    return engine


def python_to_db(queries: str, pandas_to_table: bool, df_name: pd.DataFrame, schema_name: str, table_name: str, db_credential_path: str, db_credential_file_name: str):
    connection_session = connect_db(db_credential_path, db_credential_file_name)
    if not pandas_to_table:
        connection_session.execute(queries)
    else:
        df_name.to_sql(name=table_name, schema=schema_name, con=connection_session, if_exists='append', index=False, method='multi')
    connection_session.dispose(); gc.collect()
    return None


def reading_sql_query(code_path: str, file_name: str) -> str:
    fd = open(code_path + file_name + '.sql', 'r')
    query_template = fd.read()
    fd.close()
    __query = 'f"' + query_template + '"'
    return __query

def db_to_python(queries: str, db_credential_path: str, db_credential_file_name: str) -> pd.DataFrame:
    connection_session = connect_db(db_credential_path, db_credential_file_name);
    output_df = pd.read_sql_query(queries, con=connection_session)
    connection_session.dispose(); gc.collect();
    return output_df
