import dis


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for i in clsdict:
            try:
                ret = dis.get_instructions(clsdict[i])
            except TypeError:
                pass
            else:
                for j in ret:
                    if j.opname == 'LOAD_GLOBAL':
                        if j.argval not in methods:
                            methods.append(j.argval)
        for i in ['accept', 'listen', 'socket']:
            if i in methods:
                raise TypeError('В классе использован запрещённый метод')
        if 'get_data' in methods or 'post_data' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)


class ServerVerifier(type):
    def __init__(cls, clsname, parents, clsdict):
        methods = []
        for i in clsdict:
            try:
                ret = dis.get_instructions(clsdict[i])
            except TypeError:
                pass
            else:
                for j in ret:
                    if j.opname == 'LOAD_GLOBAL':
                        if j.argval not in methods:
                            methods.append(j.argval)
        if 'connect' in methods:
            raise TypeError('В классе использован запрещённый метод')
        if 'AF_INET' in methods and 'SOCK_STREAM' in methods:
            pass
        else:
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(clsname, parents, clsdict)