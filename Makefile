FILE_NAME=game_for_profilling

good:
	python connectz.py tests/good_file

test:
	python test_connectz.py

profile:
	python profile_game.py
