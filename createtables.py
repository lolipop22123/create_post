import psycopg2


class DB:
    def __init__(self, dbname, user, password, host):
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, sslmode='disable')
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True

    def create(self):
        with self.connection:
            # self.cursor.execute('''CREATE TABLE public.post
            #     (
            #         id serial NOT NULL,
            #         id_post bigint,
            #         text character varying,
            #         photo_ids TEXT[] NOT NULL,
            #         PRIMARY KEY (id)
            #     );''')
            
            self.cursor.execute('''CREATE TABLE public.channel_posting
                (
                    id serial NOT NULL,
                    name character varying,
                    id_channel bigint,
                    PRIMARY KEY (id)
                );''')
            

DB('botpost', 'postgres', '1111', 'localhost').create()