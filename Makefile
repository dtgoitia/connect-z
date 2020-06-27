FILE_NAME=game_for_profilling

good:
	python connectz.py tests/good_file

test:
	python test_connectz.py

profile:
	python create_game.py $(FILE_NAME)
	python profile_game.py $(FILE_NAME)
