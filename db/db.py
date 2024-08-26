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
        self.cursor.execute('SELECT id, id_post, text, photo_ids FROM public.post')
        
        # Извлечение всех строк из результата запроса
        posts = self.cursor.fetchall()
        
        # Формирование списка словарей с постами
        all_posts = [
            {
                'id': post[0],
                'id_post': post[1],
                'text': post[2],
                'photo_ids': post[3]
            }
            for post in posts
        ]
        
        return all_posts

    def get_post_by_id(self, id_post):        
        id_post = int(id_post)
        # Выполнение запроса для получения поста по ID
        self.cursor.execute('SELECT id, text, photo_ids FROM public.post WHERE id_post = %s', (id_post,))
        
        # Извлечение результата запроса
        post = self.cursor.fetchone()
        
        # Если пост найден, формируем словарь с данными
        if post:
            post_info = {
                'id': post[0],
                'text': post[1],
                'photo_ids': post[2]
            }
            return post_info
        else:
            # Если поста с таким ID не существует, возвращаем None
            return None

        
    
    def delete_post_by_id(self, id_post):
        with self.connection:
            # Выполнение запроса на удаление поста по ID
            self.cursor.execute('DELETE FROM public.post WHERE id_post = %s', (id_post,))
            
            # Фиксация изменений в базе данных
            self.connection.commit()


    # работа с каналами
    def add_channel_posting(self, name, id_channel):
        with self.connection:
            # Выполнение запроса на вставку данных в таблицу
            self.cursor.execute(
                '''
                INSERT INTO public.channel_posting (name, id_channel)
                VALUES (%s, %s)
                RETURNING id;
                ''',
                (name, id_channel)
            )
            
            # Фиксация изменений в базе данных
            self.connection.commit()
        
    def get_all_channel_postings(self):
        with self.connection:
            # Выполнение запроса на получение всех данных из таблицы
            self.cursor.execute(
                '''
                SELECT * FROM public.channel_posting;
                '''
            )
            
            # Извлечение всех данных
            results = self.cursor.fetchall()
            
            # Фиксация изменений в базе данных
            self.connection.commit()
            
            # Возвращаем все записи
            return results
    
    
    def delete_channel_posting(self, id_channel):
        with self.connection:
            # Выполнение запроса на удаление записи из таблицы по ID
            self.cursor.execute(
                '''
                DELETE FROM public.channel_posting
                WHERE id_channel = %s;
                ''',
                (id_channel,)
            )
            
            # Фиксация изменений в базе данных
            self.connection.commit()

            
    def add_plan_posting(self, id_post, time, channel_post, day_post):
        self.cursor.execute('''
            INSERT INTO public.planPosting (id_post, time, channel_post, day_post)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        ''', (id_post, time, channel_post, day_post))
        
        self.connection.commit()  # Сохранение изменений
    
    
    def get_all_plan_postings(self):
        self.cursor.execute('''
            SELECT * FROM public.planPosting;
        ''')
        
        # Получаем все записи
        records = self.cursor.fetchall()
        return records
    
    
    def delete_plan_posting(self, id_post):
        self.cursor.execute('''
            DELETE FROM public.planPosting WHERE id_post = %s;
        ''', (id_post,))
        
        self.connection.commit()  # Сохранение изменений
    
    
    def get_post_text(self, id_post):
        self.cursor.execute('''
            SELECT text 
            FROM public.post 
            WHERE id_post = %s;
        ''', (id_post,))
        
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None  # Если текст не найден
        
    
    def add_reposting(self, name, id_copy, id_posting):
        self.cursor.execute('''
            INSERT INTO public.reposting (name, id_copy, id_posting)
            VALUES (%s, %s, %s)
            RETURNING id;
        ''', (name, id_copy, id_posting))
        
        self.connection.commit()  # Сохранение изменений
    
    def get_all_repostings(self):
        self.cursor.execute('''
            SELECT * FROM public.reposting;
        ''')
        
        # Получаем все строки из результата запроса
        repostings = self.cursor.fetchall()
        
        return repostings

    
    # Отправленные посты
    def add_sent_post(self, post_id, chat_id):
        with self.connection:
            self.cursor.execute(
                '''
                INSERT INTO public.sent_posts (post_id, chat_id, send_date)
                VALUES (%s, %s, CURRENT_DATE)
                RETURNING id;
                ''',
                (post_id, chat_id)
            )
            self.connection.commit()
    
    def is_post_sent_today(self, post_id, chat_id):
        with self.connection:
            self.cursor.execute(
                '''
                SELECT id FROM public.sent_posts
                WHERE post_id = %s AND chat_id = %s AND send_date = CURRENT_DATE;
                ''',
                (post_id, chat_id)
            )
            result = self.cursor.fetchone()
            return result is not None

    
    def clear_sent_posts(self):
        with self.connection:
            self.cursor.execute(
                '''
                DELETE FROM public.sent_posts;
                '''
            )
            self.connection.commit()


    