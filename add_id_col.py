import sqlite3

def add_primary_key_to_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a new table with a primary key
    cursor.execute(f'''CREATE TABLE {table_name}_temp (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT, company_name TEXT, location TEXT, salary TEXT, short_description TEXT, date_posted TEXT, long_description TEXT, date_time_loaded TEXT, full_description_html_path TEXT, search_term TEXT, search_location TEXT)''')

    # Copy data from the old table to the new table
    cursor.execute(f'''INSERT INTO {table_name}_temp (title, link, company_name, location, salary, short_description, date_posted, long_description, date_time_loaded, full_description_html_path, search_term, search_location) SELECT * FROM {table_name}''')

    # Drop the old table
    cursor.execute(f'''DROP TABLE {table_name}''')

    # Rename the new table to the old table name
    cursor.execute(f'''ALTER TABLE {table_name}_temp RENAME TO {table_name}''')

    conn.commit()
    conn.close()

# Usage
add_primary_key_to_table('Job_Data/jobs.db', 'jobs')
