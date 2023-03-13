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


cur.execute('DROP TABLE IF EXISTS element_template;')
cur.execute('DROP TABLE IF EXISTS templates;')
cur.execute('DROP TABLE IF EXISTS elements;')

# classes = array of strings
cur.execute('CREATE TABLE elements (id serial PRIMARY KEY,'
                                    'tag varchar (150) NOT NULL,'
                                    'classes varchar (150) [],'
                                    'id_attr varchar (150) NOT NULL,'
                                    'type integer NOT NULL);'
                                    )

cur.execute('CREATE TABLE templates (id serial PRIMARY KEY,'
                                    'creation_date date DEFAULT CURRENT_TIMESTAMP,'
                                    'origin_file varchar (150) NOT NULL);'
                                    )

cur.execute('CREATE TABLE element_template (id serial PRIMARY KEY,'
                                    'element_id integer NOT NULL,'
                                    'template_id integer NOT NULL,'
                                    'FOREIGN KEY (element_id) REFERENCES elements(id),'
                                    'FOREIGN KEY (template_id) REFERENCES templates(id));')
                                    

# Insert element into the table
cur.execute('INSERT INTO elements (tag, classes, id_attr, type)'
            'VALUES (%s, %s, %s, %s) RETURNING id;',
            ('div',
                ['post', 'post-wrapper'],
                'post-1',
                1
            )
            )
el1_id = cur.fetchone()[0]

cur.execute('INSERT INTO elements (tag, classes, id_attr, type)'
            'VALUES (%s, %s, %s, %s) RETURNING id;',
            ('div',
                ['post-header'],
                'post-header-1',
                1
            )
            )
el2_id = cur.fetchone()[0]

cur.execute('INSERT INTO templates (origin_file)'
            'VALUES (%s) RETURNING id;',
            ('test.html',)
            )

id_template = cur.fetchone()[0]

cur.execute('INSERT INTO element_template (element_id, template_id)'
            'VALUES (%s, %s)',
            (el1_id, id_template)
            )

cur.execute('INSERT INTO element_template (element_id, template_id)'
            'VALUES (%s, %s)',
            (el2_id, id_template)
            )
            
# Make the changes to the database persistent
conn.commit()


cur.close()
conn.close()