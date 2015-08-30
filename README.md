# Udacity-FSWDN-P2
Full Stack Web Developer Nanodegree. P2: Swiss-system tournament

The game tournament will use the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.


* tournament.py -- a swiss-system tournament implementation API;
* tournament_test.py -- an example of how to use this API;
* tournament.sql -- the database definitions for this project.

## Additional features implemented:
* Prevents rematches between players.
* Supports tie (draw) games.
* If the number of players is not even, a "bye" fantom player can be created.
* When two players have the same number of wins, they are ranked according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
* A decorator function was added to get rid of duplications in the code.

## Running
To run the application you need a python interpreter, python-psycopg2 library and a Postgres RDB installed. It guaranteed to work with python v2.7 and PostgreSQL v9.3.

How to run the application:

1. Create the tournament database if it doesn't exist.

        createdb tournament
        
2. Create required tables:

        psql tournament < tournament.sql 
        
3. Run the tournament test script to ensure that it functions properly.

        python tournament_test.py

## Copyright and license
You are free to use this code as an example, but do not forget about Udacity Honor Code.
