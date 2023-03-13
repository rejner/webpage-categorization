
import os
import psycopg2

conn = psycopg2.connect(
        host="host.docker.internal",
        database="webcat_db",
        user='postgres',
        password='postgres',
        port=5432)

# Open a cursor to perform database operations
cur = conn.cursor()

# get all from table templates
cur.execute('SELECT * FROM templates;')
template_id = cur.fetchone()[0]

# now get all element ids from element_template table where template_id = template_id
cur.execute('SELECT element_id FROM element_template WHERE template_id = %s;', (template_id,))
element_ids = cur.fetchall()
elements_ids = tuple([el[0] for el in element_ids])

# now get all records from elements with returned ids
cur.execute('SELECT * FROM elements WHERE id IN %s;', (elements_ids,))
elements = cur.fetchall()






cur.close()
conn.close()