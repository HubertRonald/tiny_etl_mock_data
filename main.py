#!/usr/bin/python
import os
import json
import numpy as np
import pandas as pd


def get_element_list(lst, name):
    '''
    get unique element in list
    '''
    lst = list(set(lst))
    return [_ for _ in lst if name in _.lower()][0]


def read_tables():
    '''
    return dataframes and filenames input
    '''
    files_input = os.listdir('input')

    df = {'users': pd.DataFrame(), 'appointment': pd.DataFrame()}
    for df_name in df:
        file_input = get_element_list(files_input, df_name)
        df[df_name] = pd.read_csv(f'input/{file_input}')

    # print(df['appointment']['id_ein'])
    return df['users'], df['appointment'], files_input


def tiny_etl():
    '''
    return dataframes and filenames input
    cardinality one-to-many
    '''
    df_users, df_appointments, files_input = read_tables()
    df_users['id_ein'].replace('-','',regex=True, inplace=True)

    id_ein = df_users['id_ein'].unique().tolist()
    df_appointments['id_ein'] = np.random.choice(
        id_ein
        , size=len(df_appointments)
        , replace=True
    )

    """
    Bigquery data type Datetime
    Can change format time by in Bigquery is
    YYYY-MM-DD HH:MM:SS
    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#datetime_type
    https://stackoverflow.com/questions/59548775/bigquery-fails-on-parsing-dates-in-m-d-yyyy-format-from-csv-file
    
    df_appointments['appointment_date'] = pd.to_datetime(
        df_appointments['appointment_date']
        , format='%Y-%m-%d %H:%M:%S'
    ) \
    .dt.strftime('%d-%m-%Y %H:%M:%S')
    """

    # print(df_appointments['id_ein'])
    return df_users, df_appointments, files_input


def save_df(df, path):
    '''
    save dataframe to csv format
    '''
    df.to_csv(f'output/{path}', sep=';', index=False, encoding='utf-8')
    pass


def create_schema(columns, path):
    '''
    save schema like json
    JSON Schema Bigquery
    https://cloud.google.com/bigquery/docs/schemas?hl=es_419#specifying_a_json_schema_file
    '''
    data = []
    for column in columns:
        data.append({
            "description": column.replace('_',' ').title(),
            "name": column,
            "type": 'DATETIME' if 'date' in column else 'STRING',
            "mode": "REQUIRED"
        })

    path = path.lower().replace('.csv', '.json')

    with open(f'output/schemas/{path}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    pass


def main():
    '''
    run etl and save dataframe to csv format
    '''
    df_users, df_appointments, files_input = tiny_etl()

    # save mock data
    path_appointment = get_element_list(files_input, 'appointment')
    path_users = get_element_list(files_input, 'users')

    save_df(df_appointments, path_appointment)
    save_df(df_users, path_users)

    # create schema json
    create_schema(df_appointments.columns.to_list(), path_appointment)
    create_schema(df_users, path_users)
    
    pass


if __name__ == '__main__':
    main()