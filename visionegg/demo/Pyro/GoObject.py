class GoObject:
    def set_go_func(self,go_func):
        self.go_func = go_func

    def go(self):
        self.go_func()
