def select_schema(table_name: str) -> str:
    if table_name[:3] == "stg": select_schema = "main_staging"
    elif table_name[:3] == "int": select_schema = "main_intermediate"
    elif table_name[:3] == "mrt": select_schema = "main_marts"
    elif table_name[:3] == "jpn": select_schema = "main_japanese"
    else : select_schema = "main"
    return select_schema
