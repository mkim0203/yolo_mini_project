from text_to_sql.llm_tools import get_database_schema, get_database_relationships, execute_readonly_sql

if __name__ == "__main__":
    print(get_database_schema.name)
    print(get_database_schema.description)
    result = get_database_schema.invoke({})

    print(result)

    print(get_database_relationships.name)
    print(get_database_relationships.description)
    result = get_database_relationships.invoke({})

    print(result)

    query = "SELECT * FROM warehouse_slot LIMIT 5"
    result = execute_readonly_sql.invoke({"sql_query": query})
    print(result)