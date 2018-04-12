class State():
    """ 状态基类 """
    def __init__(self, states : str):
        self.states = states
    
    def __str__(self):
        return self.states
    
    def _to_state(self, states : str):
        self.states = states

    def _is_state(self, states):
        if self.states == states:
            return True
        return False

class State01(State):
    """ 基于状态积累，实现01状态 """
    def __init__(self, states : str):
        super().__init__(states)

    def to_00(self):
        self._to_state('00')
    
    def is_00(self):
        return self._is_state('00')

    def to_01(self):
        self._to_state('01')
    
    def is_01(self):
        return self._is_state('01')

    def to_10(self):
        self._to_state('10')
    
    def is_10(self):
        return self._is_state('10')

    def to_11(self):
        self._to_state('11')
    
    def is_11(self):
        return self._is_state('11')

class recvFileState(State01):
    """ 
    接受文件的状态机的状态
    (peer_choke, my_interested)
     """
    def __init__(self, states : str):
        super().__init__(states)

class sendFileState(State01):
    """
    发送文件的状态机的状态
    (my_choke, peer_interested)
    """
    def __init__(self, states : str):
        super().__init__(states)

if __name__ == '__main__':
    a = sendFileState('10')
    print(a)

    a.to_01()
    print('a.to_01() : ', a)
    print('a.is_01() ? ', a.is_01())

    a.to_10()
    print('a.to_10() : ', a)
    print('a.is_10() ? ', a.is_10())

    a.to_00()
    print('a.to_00() : ', a)
    print('a.is_00() ? ', a.is_00())

    a.to_11()
    print('a.to_11() : ', a)
    print('a.is_11() ? ', a.is_11())

