import re

dicti = {"a": 1, "b": 2, "c": 3, "d": 4}

pizza_name = "hawaian_fg_m"
pizza_name = re.sub("_[a-z][a-z]$", "", pizza_name)
print(pizza_name)
# letras = ["a", "b", "c", "d", "e"]
# for letra in letras:
#     if letra not in dicti:
#         dicti[letra] = 5
# print(dicti)
# dicti["a"] += 1
# print(dicti)