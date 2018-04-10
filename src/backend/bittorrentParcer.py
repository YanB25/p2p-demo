example = "d8:announce39:http://torrent.ubuntu.com:6969/announce13:announce-listll39:http://torrent.ubuntu.com:6969/announceel44:http://ipv6.torrent.ubuntu.com:6969/announceee7:comment29:Ubuntu CD releases.ubuntu.com13:creation datei1461232732e4:infod6:lengthi1485881344e4:name30:ubuntu-16.04-desktop-amd64.iso12:piece lengthi524288e6:pieces"
DEBUG = 0
def debug_print(*args, **kw):
    if DEBUG:
        print(*args, **kw)

def itemType(s):
    if s[0] == b'd'[0]:
        return "dict"
    elif s[0] == b'i'[0]:
        return "int"
    elif s[0] == b'l'[0]:
        return "list"
    elif s[0] >= b'0'[0] or s[0] <= b'9'[0]:
        return "str"
    else:
        raise Exception("unknow item type {}".format(s[0]))

def parceItem(s):
    debug_print(s, "in parce Item")
    itemtype = itemType(s)
    if itemtype == "int":
        end = s.find(b"e")        
        num = int(s[1:end])
        debug_print("i {}, index {}, {}".format(str(num), str(end+1), s[end-1:end+2]))
        return num, itemtype, end+1
    elif itemtype == "str":
        end = s.find(b":")
        num = int(s[0:end])
        # val = s[end+1:end+1 + num].decode("utf-8")
        val = s[end+1:end+1 + num]
        debug_print("str {}, index {}, {}".format(val, str(end+1), s[end-1:end+2]))
        return val, itemtype, end+1 + num 
    elif itemtype == "dict":
        dic, ni = parceDic(s[1:])
        debug_print(dic, "index {}, {}".format(str(ni), s[ni-1:ni+2]))
        return dic, itemtype, ni+1
    elif itemtype == "list":
        ls, ni = parceList(s[1:])
        debug_print(ls, "index {}, {}".format(str(ni), s[ni-1:ni+2]))
        return ls, itemtype, ni+1
    else:
        raise Exception("not premitive type {}".format(s[0]))

def parceList(s):
    debug_print(s, " in parce List")
    ret = []
    index = 0
    while s[index] != b'e'[0]:
        val, _, ni = parceItem(s[index:])
        ret.append(val)
        index += ni
        debug_print(ret, "index {}, {}".format(index, s[index-1:index+2]))
    debug_print('leave parce List')
    return ret, index+1

def parceDic(s):
    debug_print(s, "in parce dict")
    ret = {}
    index = 0
    while s[index] != b'e'[0]:
        # key
        key, _, ni = parceItem(s[index:])
        index += ni 
        debug_print('key {},{}'.format(str(index), s[index-1:index+2] ))

        # value
        val, valtype, ni = parceItem(s[index:])
        index += ni

        debug_print('add {}:{}, index {}, {}'.format(key, val, index, s[index-1:index+2]))
        ret[key] = val
        debug_print(ret)
    return ret, index+1

def parce(s):
    tp = itemType(s)
    debug_print(tp)
    if tp == 'dict':
        dic, _ = parceDic(s[1:])
        return dic
    elif tp == 'list':
        ls, _ = parceList(s[1:])
        return ls

if __name__ == "__main__":
    with open("../../example.torrent", 'rb') as f:
        b = f.read()
        # print(parce(b))
        p = parce(b)
        print()
        print()
        for key in p:
            if key != b'info':
                print('{} : {}'.format(key, p[key]))
        dic = p[b'info']
        print()
        for key in dic:
            if key != b'pieces':
                print('{} : {}'.format(key, dic[key]))