-- Actors who Jørgen Lerdam has deal with
SELECT a.name
    FROM movies m
    JOIN movie_actors ma
        ON ma.movie_id = m.id
    JOIN actors a
        ON ma.actor_id = a.id
    WHERE m.director LIKE '%Lerdam%';


-- Writers who have took part in most films
SELECT writer, MAX(amount) as movies_amount
    FROM (
        SELECT w.name as writer, count(m.id) as amount
            FROM writers w
            JOIN movies m
            ON w.id = m.writer
            WHERE w.name != 'N/A'
            GROUP BY w.name
    )
