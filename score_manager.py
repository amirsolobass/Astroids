import os

def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    return 0

def save_high_score(new_score):
    with open("highscore.txt", "w") as f:
        f.write(str(new_score))

# Initialize high score at the start of main()
high_score = load_high_score()