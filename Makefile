FILE_NAME=game_for_profilling

good:
	python connectz.py profilling/30

stress:
	python create_game.py 700 700
	time python connectz.py profilling/700
	# time python connectz.py profilling/million

test:
	python test_connectz.py

profile:
	python profile_game.py
