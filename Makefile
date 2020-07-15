STRESS_AMOUNT=1000

good:
	python connectz.py profilling/30

stress:
	python create_game.py ${STRESS_AMOUNT} ${STRESS_AMOUNT}
	time python connectz.py profilling/${STRESS_AMOUNT}

test:
	python test_connectz.py

profile:
	python profile_game.py