import mysql.connector

from app.config import settings


class DatabaseConnection:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=settings.MYSQL_INITDB_HOST,
            user=settings.MYSQL_INITDB_ROOT_USERNAME,
            password=settings.MYSQL_INITDB_ROOT_PASSWORD,
            database=settings.MYSQL_INITDB_DATABASE
        )

    def close(self):
        if self.connection.is_connected():
            self.connection.close()

    def save_data_to_database(self, table_name, column_names, data):
        global cursor
        placeholders = ", ".join(["%s"] * len(column_names))
        columns = ", ".join(column_names)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            return cursor.lastrowid
        except mysql.connector.Error as error:
            print("Fehler beim Einfügen des Datensatzes:", error)
            return None
        finally:
            cursor.close()

    def find_record_by_id(self, table_name, id_column, id_value, columns):
        query = f"SELECT {', '.join(columns)} FROM {table_name} WHERE {id_column} = %s"
        values = (id_value,)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)

            result = cursor.fetchone()
            cursor.close()

            if result:
                record = {}
                for idx, column_name in enumerate(columns):
                    record[column_name] = result[idx]
                return record
            else:
                return None
        except mysql.connector.Error as error:
            print(f"Fehler beim Abrufen des Datensatzes aus der Tabelle '{table_name}' mit ID '{id_value}': {error}")
            return None
