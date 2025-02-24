import math
 
class vector:    
 
    def __init__(self, x=0.0, y=0.0, limit=9999):
        self.x = x
        self.y = y
        self.limit = limit
 
    def __add__(self,other):
        return vector(self.x+other.x, self.y+other.y)
  
    def __sub__(self, other):
        return vector(self.x-other.x, self.y-other.y)
 
    def __mul__(self, other):
        return vector(self.x*other.x, self.y*other.y)
 
    def __truediv__(self, other):
        return vector(self.x/other.x, self.y/other.y)
 
    # 벡터 내적
    def dotVector(self, other):
        return (self.x*other.x) + (self.y*other.y)
 
    # 벡터 외적 (3D에서 사용)
    def corssVector(self, other1, other2):
        pass
 
    def angleVector(self):
        # -y 윈도우 좌표계는 y가 꺼꾸로
        theta = math.atan2(0-self.y, self.x)
        deg = theta * 180.0 / math.pi;
 
        if deg < 0:     
            deg += 360;
 
        return deg
 
    def angleBetweenVector(self, v2):
        v = vector(self.x, self.y, self.limit)
        v.normalize()
        v2.normalize()
 
        theta = v.dotVector(v2)
        theta = math.acos(theta)
        deg = theta * 180.0 / math.pi
        return deg           
         
 
    # 벡터 정규화(방향유지, 크기 1로)
    def normalize(self):
        # 피타고라스 정의 (빗변 구하기)
        mag = math.sqrt(self.x*self.x + self.y*self.y)
 
        if mag > 0:
            self.x /= mag
            self.y /= mag       
 
    def setLimit(self, limit):
        self.limit = limit
 
        #copysign (x, y) y의 부호만 취해 x에 적용
 
        if abs(self.x) > self.limit:
            self.x = math.copysign(limit, self.x);
 
        if abs(self.y) > self.limit:
            self.y = math.copysign(limit, self.y)