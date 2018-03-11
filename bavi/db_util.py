def create_audit_trigger(c, table_name, pk):
    insert_trigger = '''
            CREATE TRIGGER IF NOT EXISTS {table_name}_insert_aud
            AFTER INSERT ON {table_name} FOR EACH ROW
            BEGIN
                UPDATE {table_name}
                   SET created_at = DATETIME(),
                       updated_at = DATETIME()
                 WHERE {pk} = NEW.{pk};
            END;
    '''.format(table_name=table_name, pk=pk)

    c.execute(insert_trigger)

    update_trigger = '''
            CREATE TRIGGER IF NOT EXISTS {table_name}_update_aud
            AFTER UPDATE ON {table_name} FOR EACH ROW
            BEGIN
                UPDATE {table_name}
                   SET updated_at = DATETIME()
                 WHERE {pk} = NEW.{pk};
            END;
    '''.format(table_name=table_name, pk=pk)

    c.execute(update_trigger)
