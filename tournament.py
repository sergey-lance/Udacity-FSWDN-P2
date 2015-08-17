#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


TIE_SCORE, WIN_SCORE = 1,3  #hardcoded scores for win and tie, loss score assumed to be 0

# We decorate all functions to not to duplicate code for common steps
def db(f):
    def wrap(*args, **kwargs):
		conn = connect()
		f.func_globals['cur'] = conn.cursor()
		res = f(*args, **kwargs)
		conn.commit()
		conn.close()
		return res
		
    return wrap


def connect():
	"""Connect to the PostgreSQL database.  Returns a database connection."""
	return psycopg2.connect("dbname=tournament")
	
@db
def deleteMatches():
	"""Remove all the match records from the database."""
	cur.execute('''DELETE FROM matches;''')

@db
def deletePlayers():
	"""Remove all the player records from the database."""
	cur.execute('''DELETE FROM players;''')

@db
def countPlayers():
	"""Returns the number of players currently registered."""
	cur.execute('''select count(id) as cnt from players;''')
	cnt = cur.fetchone()[0]
	return cnt

@db
def registerPlayer(name):
	"""Adds a player to the tournament database.
  
	The database assigns a unique serial id number for the player.  (This
	should be handled by your SQL database schema, not in your Python code.)
  
	Args:
	  name: the player's full name (need not be unique).
	"""
	cur.execute('''INSERT INTO players(name) VALUES(%s);''', (name,) )

@db
def playerStandings():
	"""Returns a list of the players and their win records, sorted by wins.

	The first entry in the list should be the player in first place, or a player
	tied for first place if there is currently a tie.

	Returns:
	  A list of tuples, each of which contains (id, name, wins, matches):
		id: the player's unique id (assigned by the database)
		name: the player's full name (as registered)
		wins: the number of matches the player has won
		matches: the number of matches the player has played
	"""
	cur.execute(
			# COALESCE because tournament_test #6 distinguishes between None and 0.
			# We are not using nested selects here because they are not cool =)
			'''
			SELECT players.id, players.name,
				COALESCE( sum(CASE WHEN matches.score = %(winscore)s THEN 1 END),0) AS wins,
				COUNT(matches.player) AS total
			FROM players
			LEFT OUTER JOIN matches ON players.id = matches.player
			GROUP BY players.id
			ORDER BY players.name;
			''',
			{'winscore':WIN_SCORE}
		)
	res = cur.fetchall()
	return res
	
# I don't like this API since it allows to report the mathch
#  even if was not appointed before with swiss-system.
# But API assumed by tournament_test doesn't allow to make swissPairings stateful.

@db
def reportMatch(winner, loser):
	"""Records the outcome of a single match between two players.

	Args:
	  winner:  the id number of the player who won
	  loser:  the id number of the player who lost
	"""
	cur.execute('''
			INSERT INTO matches(player,rival,score)
			VALUES 
			(%(winner)s, %(loser)s, %(winscore)s),
			(%(loser)s, %(winner)s, 0);
			''',
			{'winner':winner, 'loser':loser, 'winscore':WIN_SCORE}
		)
	
@db
# A separate function for ties since it's not a good practice to change the main API for a minor feature.
def reportTie(player1, player2):
	"""Records the tie between two players.

	Args:
		the id numbers of the players
	"""
	cur.execute(''' INSERT INTO matches(player,rival,score)
				VALUES 
				(%(player1)s, %(player2)s, %(tiescore)s),
				(%(player2)s, %(player1)s, %(tiescore)s);
				''',
				{'player1':player1, 'player2':player2, 'tiescore':TIE_SCORE}
			)

@db 
def swissPairings():
	"""Returns a list of pairs of players for the next round of a match.
  
	Assuming that there are an even number of players registered, each player
	appears exactly once in the pairings.  Each player is paired with another
	player with an equal or nearly-equal win record, that is, a player adjacent
	to him or her in the standings.
  
	Returns:
	  A list of tuples, each of which contains (id1, name1, id2, name2)
		id1: the first player's unique id
		name1: the first player's name
		id2: the second player's unique id
		name2: the second player's name
		
	  Prevents duplicate matches.
	  Will return (id1, name1, None, None) for the player if all the combinations in the
	  rest part of the scoretable was played before already.
	"""
	#~ # A simple version, order by total score.
	#~ cur.execute(''' 
			#~ SELECT players.id, players.name
			#~ FROM players
			#~ LEFT OUTER JOIN matches ON players.id=matches.player
			#~ GROUP BY players.id
			#~ ORDER BY SUM(matches.score) DESC;
			#~ ''')
			
	# A sophisticated version: order by total score, then by Opponent's Matches Win.
	cur.execute(''' 	
			SELECT players.id, players.name
			FROM players
			LEFT OUTER JOIN matches ON matches.player = players.id
			LEFT OUTER JOIN
				(	SELECT id,
						name,
						sum(CASE WHEN matches.score = %(winscore)s THEN 1 END) AS mw
					FROM players
					JOIN matches ON id=matches.player
					GROUP BY id) AS opponents
				ON matches.rival = opponents.id
			GROUP BY players.id, players.name
			ORDER BY
				SUM(matches.score) DESC NULLS LAST,
				SUM(opponents.mw) DESC NULLS LAST;
			''',
			{'winscore': WIN_SCORE}
			)
	
	players_ordered = cur.fetchall()
	
	# Prevent duplicate matches
	cur.execute('''SELECT player,rival FROM matches;''')
	played_combinations = cur.fetchall()
	ret = []
	
	while len(players_ordered):
		player1 = players_ordered.pop(0)
		player2 = (None,None)
		for idx, p in enumerate(players_ordered):
			if (player1[0], p) not in played_combinations:
				player2 = players_ordered.pop(idx)
				break
		ret.append((player1[0], player1[1], player2[0], player2[1]))
	
	return ret
