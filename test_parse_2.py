import re
with open("graders.py", "r") as f:
    code = f.read()
code = code.replace("order_score = 0.0", "order_score = 0.01")
code = code.replace("order_score = 1.0", "order_score = 0.99")
code = code.replace("user_score = 0.0", "user_score = 0.01")
code = code.replace("user_score = 1.0", "user_score = 0.99")

with open("graders.py", "w") as f:
    f.write(code)
