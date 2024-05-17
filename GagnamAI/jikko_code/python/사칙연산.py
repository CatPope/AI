class Mod:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def add(self):
        c = self.a + self.b
        return c
    
    def sub(self):
        c = self.a - self.b
        return c
    
    def mul(self):
        c = self.a * self.b
        return c
    
    def div(self):
        c = self.a / self.b
        return  c
    
    
    
a, b = map(int, input().split())
obj = Mod(a, b)
print(obj.add())
print(obj.sub())
print(obj.mul())
print(obj.div())