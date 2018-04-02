from bittorrentParcer import *
dic2 = "d2:ybd3:wyfi123eee"
ls = "l2:ybi234ee"
# print(parce(dic2))
# print(parce(ls))
comps = [
    "d",
        "2:yb",
        "i789e",
        "3:wyf",
        "l",
            "i123e",
            "3:abc",
        "e",
        "4:mydi",
        "d",
            "3:age",
            "i18e",
        "e",
    "e"
]
compls = "".join(comps)
# print(compls)
print(parce(compls))