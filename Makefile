FILE_NAME=game_for_profilling

good:
	python connectz.py tests/good_file

test:
	python test_connectz.py

profile:
	python create_game.py $(FILE_NAME)_1
	python profile_game.py $(FILE_NAME)_1
	cp profilling/$(FILE_NAME)_1 profilling/$(FILE_NAME)_2
	python profile_game.py $(FILE_NAME)_2
	cp profilling/$(FILE_NAME)_1 profilling/$(FILE_NAME)_3
	python profile_game.py $(FILE_NAME)_3
	cp profilling/$(FILE_NAME)_1 profilling/$(FILE_NAME)_4
	python profile_game.py $(FILE_NAME)_4
