SELECT a.name
    FROM movies m
    JOIN movie_actors ma
        ON ma.movie_id = m.id
    JOIN actors a
        ON ma.actor_id = a.id
    WHERE m.director LIKE '%Lerdam%';

