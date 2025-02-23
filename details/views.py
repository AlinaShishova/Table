from django.shortcuts import render
import oracledb

# Инициализация Oracle Instant Client
oracledb.init_oracle_client(lib_dir="C:\oracle\instantclient\instantclient_19_25") # проверить путь

# Настройки подключения к Oracle
ORACLE_USER = "AMR"
ORACLE_PASSWORD = "AMR"
ORACLE_DSN = "10.124.12.2:1521/db1p"

def execute_query(dm_index_where):
    connection = None
    cursor = None
    try:
        connection = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
        cursor = connection.cursor()
        query = """
        SELECT d.dm_index,
               d.dm_name as dse_name,
               d.dm_draft as dse_draft_number,
               a.da_num as count_in_assembling,
               a.cn_tech_marshrut as workshop_route,
               (SELECT c.short_name FROM dse_classes c WHERE c.ind = d.dm_class_id) as class_name
        FROM 
            dse_assembling a, 
            dse_main d
        WHERE 
            d.dm_index = a.dm_index_what
            AND a.dm_index_where = :dm_index_where
            AND d.dm_class_id IN (2456, 2454, 2797, 2896)
        ORDER BY 
            d.dm_class_id, 
            d.dm_draft, 
            d.dm_name
        """
        cursor.execute(query, dm_index_where=dm_index_where)
        results = cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return results

def index(request):
    # Получаем значение dm_index_where из GET-параметров (по умолчанию 19408746)
    dm_index_where = request.GET.get('dm_index_where', '19408746')
    try:
        dm_index_where = int(dm_index_where)
    except ValueError:
        dm_index_where = 19408746

    old_dm_index_where = dm_index_where
    results = execute_query(dm_index_where)
    context = {
        'results': results,
        'old_dm_index_where': old_dm_index_where,
    }
    return render(request, 'index.html', context)