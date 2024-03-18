import cv2
import numpy as np
from random import randint
import os

class SC():
    def __init__(self,f_name):
        print('Подсчёт ведется автоматически при создании объекта object = SC()\n для нарезки примените метод .chop()')
        self.path = str(f_name)+'.tif'
        self.ff_name = f_name
        self.img = cv2.imread(self.path) #img for searching
        self.orig = self.img

        # BGR --> Gray
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        #self.img = cv2.bitwise_not(self.img)  #that's for alternative imgs with reversed colors

        #Find value between white and black
        height,width,ch = self.orig.shape 
        S=[] #array for calculating value
        #picking random pixels for finding our value
        for j in range (1000):
            a = randint(0,width-1)
            b = randint(0,height-1)
            c = self.orig[b][a]
            d = c[0]
            S.append(d)            
       
        porog=0
        for i in range(1000):
            porog+=S[i]
        
        porog = porog//1000 #and that's our value
        print('porog = '+str(porog))

        #I had imgs with frame (that's a convention of shooting technology) and I needed to delete it. So now a bit code for deleting frame
        self.ramka = self.img.copy()
        _, self.ramka = cv2.threshold(self.ramka, porog, 255, cv2.THRESH_BINARY)
        self.ramka = cv2.bitwise_not(self.ramka) #reverse to make search simple

        contours,_ = cv2.findContours(self.ramka, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        largest_contour = max(contours,key=cv2.contourArea) #looking for frame
        xr, yr, wr, hr = cv2.boundingRect(largest_contour) #frame's coordinates 

        self.img = self.img[yr+5:yr+hr, xr+10:xr+wr-10]
        self.orig = self.orig[yr+5:yr+hr, xr+10:xr+wr-10]

        #And now we can go to binary img
        _, self.img = cv2.threshold(self.img, porog, 255, cv2.THRESH_BINARY)

        #an attempt to get rid of small noise (also due to the peculiarities of the shooting technology)
        self.img = cv2.medianBlur(self.img, 7)

        """imgshow = cv2.resize(self.img,(height//2,width//3))
        cv2.imshow('pikcha',imgshow)  #to look at result
        cv2.waitKey(0)"""

        #searching seeds
        contours, _ = cv2.findContours(self.img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.A = []
        arr = np.array(self.img)
        #saving coordinates of contours
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            rrr = arr[y:(y+h),x:(x+w)]
            wh = np.count_nonzero(rrr==255)  #another filter
            if wh < 1000:  #this filter had to be added manually due to large noise grains
                continue
            if w and h > 35:
                self.A.append([x,y,w,h])
                
        print('Количество найденных контуров '+str(len(self.A)))
    
    def chop(self,form):
        height,width,ch = self.orig.shape
        folder_name = 'file_'+str(self.ff_name)
        folder_path = str(folder_name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        for i in range(len(self.A)):
            d1y = self.A[i][1] - 20
            d1x = self.A[i][0] - 20
            dy = self.A[i][1] + self.A[i][3] + 20
            dx = self.A[i][0] + self.A[i][2] + 20
            
            if dy > height or dx > width or d1x < 0 or d1y < 0:   #error checking conditions
                continue
            
            result = self.orig[d1y:dy, d1x:dx]
            
            if result is None:
                print("Изображение пустое")
                continue
            
            #saving files
            name = 'pic_numero_'+str(self.ff_name)+'_'+str(i)+'.'+str(form)
            file_path = os.path.join(folder_path, name)
            cv2.imwrite(file_path, result)
        print('нарезка закончена')
pic = SC('1x')
pic.chop("bmp")
