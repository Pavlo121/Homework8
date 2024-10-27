import sqlite3 as db

# Встановлення з'єднання з базою даних "kinobaza.db"
with db.connect("kinobaza.db") as con:
    cur = con.cursor()

    # Створення таблиці для фільмів
    cur.execute("""CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,   -- Унікальний ідентифікатор фільму
        title TEXT,               -- Назва фільму
        release_year INTEGER,     -- Рік випуску фільму
        genre TEXT                -- Жанр фільму
        )""")

    # Створення таблиці для акторів
    cur.execute("""CREATE TABLE IF NOT EXISTS actors (
        id INTEGER PRIMARY KEY,   -- Унікальний ідентифікатор актора
        name TEXT,                -- Ім'я актора
        birth_year INTEGER        -- Рік народження актора
    )""")

    # Створення таблиці для зв'язку фільмів та акторів
    cur.execute("""CREATE TABLE IF NOT EXISTS movie_cast (
        movie_id INTEGER,         -- Ідентифікатор фільму
        actor_id INTEGER,         -- Ідентифікатор актора
        PRIMARY KEY (movie_id, actor_id), -- Первинний ключ, що складається з movie_id та actor_id
        FOREIGN KEY(movie_id) REFERENCES movies(id), -- Зовнішній ключ для movie_id
        FOREIGN KEY(actor_id) REFERENCES actors(id)  -- Зовнішній ключ для actor_id
    )""")
    print("Таблиці створено успішно.")


def add_movie():
    """Додає новий фільм до бази даних разом з акторами."""
    title = input("Введіть назву фільму: ")
    release_year = int(input("Введіть рік випуску: "))
    genre = input("Введіть жанр: ")

    # Додавання фільму до таблиці movies
    cur.execute("INSERT INTO movies (title, release_year, genre) VALUES (?, ?, ?)", (title, release_year, genre))
    movie_id = cur.lastrowid  # Отримуємо ID нового фільму
    con.commit()

    print("Додайте акторів для фільму:")
    while True:
        actor_name = input("Введіть ім'я актора (або залиште порожнім для виходу): ")
        if not actor_name:
            break
        # Перевірка, чи існує актор
        cur.execute("SELECT id FROM actors WHERE name = ?", (actor_name,))
        actor = cur.fetchone()
        if actor:
            actor_id = actor[0]  # Отримуємо ID існуючого актора
        else:
            birth_year = int(input("Введіть рік народження актора: "))
            # Додавання нового актора до таблиці actors
            cur.execute("INSERT INTO actors (name, birth_year) VALUES (?, ?)", (actor_name, birth_year))
            actor_id = cur.lastrowid  # Отримуємо ID нового актора
            con.commit()
        # Додаємо зв'язок між фільмом та актором у таблицю movie_cast
        cur.execute("INSERT INTO movie_cast (movie_id, actor_id) VALUES (?, ?)", (movie_id, actor_id))
        con.commit()
    print("Фільм успішно додано.")


def add_actor():
    """Додає нового актора до бази даних."""
    name = input("Введіть ім'я актора: ")
    birth_year = int(input("Введіть рік народження: "))
    # Додавання актора до таблиці actors
    cur.execute("INSERT INTO actors (name, birth_year) VALUES (?, ?)", (name, birth_year))
    con.commit()
    print("Актор успішно доданий.")


def show_movies_with_actors():
    """Показує всі фільми разом з акторами, що в них знімалися."""
    cur.execute('''SELECT movies.title, GROUP_CONCAT(actors.name, ', ') AS actor_names
                      FROM movies
                      JOIN movie_cast ON movies.id = movie_cast.movie_id
                      JOIN actors ON movie_cast.actor_id = actors.id
                      GROUP BY movies.title''')
    movies = cur.fetchall()
    for movie in movies:
        print(f"Фільм: {movie[0]}, Актори: {movie[1]}")


def show_unique_genres():
    """Виводить унікальні жанри фільмів."""
    cur.execute("SELECT DISTINCT genre FROM movies")
    genres = cur.fetchall()
    for genre in genres:
        print(genre[0])


def count_movies_by_genre():
    """Показує кількість фільмів у кожному жанрі."""
    cur.execute("SELECT genre, COUNT(*) FROM movies GROUP BY genre")
    genres = cur.fetchall()
    for genre, count in genres:
        print(f"{genre}: {count}")


def average_birth_year_by_genre():
    """Виводить середній рік народження акторів у фільмах певного жанру."""
    genre = input("Введіть жанр: ")
    cur.execute('''SELECT AVG(actors.birth_year)
                      FROM actors
                      JOIN movie_cast ON actors.id = movie_cast.actor_id
                      JOIN movies ON movie_cast.movie_id = movies.id
                      WHERE movies.genre = ?''', (genre,))
    avg_birth_year = cur.fetchone()[0]
    print(f"Середній рік народження акторів у жанрі '{genre}': {avg_birth_year:.2f}")


def search_movies_by_keyword():
    """Шукає фільми за ключовим словом у назві."""
    keyword = input("Введіть ключове слово для пошуку: ")
    cur.execute("SELECT title, release_year FROM movies WHERE title LIKE ?", ('%' + keyword + '%',))
    movies = cur.fetchall()
    for movie in movies:
        print(f"{movie[0]} ({movie[1]})")


def show_movies_with_pagination():
    """Показує фільми з пагінацією."""
    page = int(input("Введіть номер сторінки: "))
    page_size = 10  # Кількість фільмів на сторінці
    offset = (page - 1) * page_size
    cur.execute("SELECT title FROM movies LIMIT ? OFFSET ?", (page_size, offset))
    movies = cur.fetchall()
    for movie in movies:
        print(movie[0])


def show_all_actors_and_movies():
    """Виводить імена всіх акторів та назви всіх фільмів."""
    cur.execute("SELECT name FROM actors UNION SELECT title FROM movies")
    items = cur.fetchall()
    for item in items:
        print(item[0])


def show_movie_age():
    """Виводить вік фільму на основі року випуску."""
    cur.execute("SELECT title, (strftime('%Y', 'now') - release_year) AS age FROM movies")
    movies = cur.fetchall()
    for movie in movies:
        print(f"Фільм: {movie[0]}, Вік: {movie[1]} років")


def menu():
    """Основне меню програми."""
    while True:
        print("\nМеню:")
        print("1. Додати фільм")
        print("2. Додати актора")
        print("3. Показати всі фільми з акторами")
        print("4. Показати унікальні жанри")
        print("5. Показати кількість фільмів за жанром")
        print("6. Показати середній рік народження акторів у фільмах певного жанру")
        print("7. Пошук фільму за назвою")
        print("8. Показати фільми (з пагінацією)")
        print("9. Показати імена всіх акторів та назви всіх фільмів")
        print("0. Вихід")

        choice = input("Виберіть дію: ")
        if choice == '1':
            add_movie()
        elif choice == '2':
            add_actor()
        elif choice == '3':
            show_movies_with_actors()
        elif choice == '4':
            show_unique_genres()
        elif choice == '5':
            count_movies_by_genre()
        elif choice == '6':
            average_birth_year_by_genre()
        elif choice == '7':
            search_movies_by_keyword()
        elif choice == '8':
            show_movies_with_pagination()
        elif choice == '9':
            show_all_actors_and_movies()
        elif choice == '0':
            break
        else:
            print("Неправильний вибір. Спробуйте ще раз.")


# Запуск програми
menu()

# Закриття з'єднання з базою даних
con.close()
