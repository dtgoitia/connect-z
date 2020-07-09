FILE_NAME=game_for_profilling

good:
	python connectz.py profilling/30

stress:
	time python connectz.py profilling/million

test:
	python test_connectz.py

profile:
	python profile_game.py
