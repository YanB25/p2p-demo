example = "d8:announce39:http://torrent.ubuntu.com:6969/announce13:announce-listll39:http://torrent.ubuntu.com:6969/announceel44:http://ipv6.torrent.ubuntu.com:6969/announceee7:comment29:Ubuntu CD releases.ubuntu.com13:creation datei1461232732e4:infod6:lengthi1485881344e4:name30:ubuntu-16.04-desktop-amd64.iso12:piece lengthi524288e6:pieces"
def itemType(s):
    if s[0] == 'd':
        return "dict"
    elif s[0] == 'i':
        return "int"
    elif s[0] == 'l':
        return "list"
    elif s[0] >= '0' or s[0] <= '9':
        return "str"
    else:
        raise Exception("unknow item type {}".format(s[0]))

def parceItem(s):
    print(s)
    itemtype = itemType(s)
    if itemtype == "int":
        end = s.find("e")        
        num = int(s[1:end])
        print("i {}, index {}, {}".format(str(num), str(end+1), s[end-1:end+2]))
        return num, itemtype, end+1
    elif itemtype == "str":
        end = s.find(":")
        num = int(s[0:end])
        val = s[end+1:end+1 + num]
        print("str {}, index {}, {}".format(val, str(end+1), s[end-1:end+2]))
        return val, itemtype, end+1 + num
    elif itemtype == "dict":
        dic, ni = parceDic(s[1:])
        print(dic, "index {}, {}".format(str(ni), s[ni-1:ni+2]))
        return dic, itemtype, ni+1
    elif itemtype == "list":
        ls, ni = parceList(s[1:])
        print(ls, "index {}, {}".format(str(ni), s[ni-1:ni+2]))
        return ls, itemtype, ni+1
    else:
        raise Exception("not premitive type {}".format(s[0]))

def parceList(s):
    print(s)
    ret = []
    index = 0
    while s[index] != 'e':
        val, _, ni = parceItem(s[index:])
        ret.append(val)
        index += ni
        print(ret, "index {}, {}".format(index, s[index-1:index+2]))
    return ret, index+1

def parceDic(s):
    print(s)
    ret = {}
    index = 0
    while s[index] != 'e':
        # key
        key, _, ni = parceItem(s[index:])
        index += ni 

        # value
        val, valtype, ni = parceItem(s[index:])
        index += ni

        print('add {}:{}, index {}, {}'.format(key, val, index, s[index-1:index+2]))
        ret[key] = val
        print(ret)
    return ret, index+1

def parce(s):
    tp = itemType(s)
    if tp == 'dict':
        dic, _ = parceDic(s[1:])
        return dic
    elif tp == 'list':
        ls, _ = parceList(s[1:])
        return ls