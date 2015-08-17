-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

drop table players cascade;
drop table matches cascade;

create table players (
	id SERIAL PRIMARY KEY,
	name VARCHAR(128) NOT NULL UNIQUE
	);
	
create table matches (
	player int REFERENCES players(id) ON DELETE CASCADE,
	rival int REFERENCES players(id) ON DELETE CASCADE,
	score smallint,
	PRIMARY KEY (player, rival)
	);

-- just for fun, not used in python code
create view scoretable
as 
SELECT players.id, players.name, SUM(matches.score) as total,
	sum(CASE WHEN matches.score != 0 THEN 1 END) AS mw
	FROM players
	left outer JOIN matches ON players.id=matches.player
	GROUP BY players.id
	ORDER BY total DESC;
