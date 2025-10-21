def log_violation_to_file(text):
    with open("data/violations.log", "a") as f:
        f.write(text + "\n")
