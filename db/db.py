import psycopg2


class DB:
    def __init__(self, dbname, user, password, host):
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, sslmode='disable')
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True
    
    def create_post(self, id_post, text, photo_ids):
        # Преобразование списка ID фото в строку
        with self.connection:
            self.cursor.execute('INSERT INTO public.post (id_post, text, photo_ids) VALUES (%s, %s, %s)', (id_post, text, photo_ids))
    
    
    def get_all_posts(self):
        # Выполнение запроса для получения всех постов
        self.cursor.execute('SELECT id, text, photo_ids FROM public.post')
        
        # Извлечение всех строк из результата запроса
        posts = self.cursor.fetchall()
        
        # Формирование списка словарей с постами
        all_posts = [
            {
                'id': post[0],
                'text': post[1],
                'photo_ids': post[2]
            }
            for post in posts
        ]
        
        return all_posts