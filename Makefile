FILE_NAME=game_for_profilling

good:
	python connectz.py good_file

bad:
	python connectz.py foo

test:
	python test_connectz.py

profile:
	python create_game.py $(FILE_NAME)
	python profile_game.py $(FILE_NAME)
