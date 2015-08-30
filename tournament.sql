-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE players CASCADE;
DROP TABLE matches CASCADE;

CREATE TABLE players ( id SERIAL PRIMARY KEY, name VARCHAR(128) NOT NULL UNIQUE );

CREATE TABLE matches (
      player INT REFERENCES players(id) ON DELETE CASCADE,
      rival INT REFERENCES players(id) ON DELETE CASCADE,
      score SMALLINT, PRIMARY KEY (player, rival) );


CREATE VIEW scoretable AS
SELECT players.id,
       players.name,
       SUM(matches.score) AS total,
       SUM(CASE WHEN matches.score != 0 THEN 1 END) AS mw
FROM players
LEFT OUTER JOIN matches ON players.id=matches.player
GROUP BY players.id
ORDER BY total DESC;
