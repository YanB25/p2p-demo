with open("example.torrent", "rb") as f:
    fileb = f.read()
    print(fileb.index(b'pieces'))
