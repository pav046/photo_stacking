import cv2
import numpy as np
import os
import shutil

class PhotoStacking:


    def __init__(self, pictures, name_of_session, a='auto'):
        self.img_list = [cv2.imread(i) for i in pictures]
        self.name_of_session = name_of_session
        self.grey_list = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in
                     self.img_list]
        self.sharp_list = [self.compute_gradients(i) for i in self.grey_list]
        if a == 'auto':
            self.a = self.auto_area()
        else:
            self.a = a
        self.colors()


    def compute_gradients(self, image):
        grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0)
        grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1)
        gradient_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
        return gradient_magnitude


    def main(self):
        a = self.a
        h, w = self.grey_list[0].shape[0], self.grey_list[0].shape[1]
        self.result_img = np.zeros_like(self.img_list[0], dtype=np.float32)
        self.result_sharpness = np.array([[0 for _ in range(w)] for _ in range(h)])
        self.color_image = np.zeros_like(self.img_list[0], dtype=np.float32)

        for i in range(0, h, a):
            for j in range(0, w, a):
                mean_gradient = max(map(lambda x: (np.mean(self.sharp_list[x][i:i + a, j:j + a]), x), range(len(self.sharp_list))), key=lambda y: y[0])
                self.result_img[i:i + a, j:j + a] = self.img_list[mean_gradient[1]][i:i + a, j:j + a]
                self.result_sharpness[i:i + a, j:j + a] = self.sharp_list[mean_gradient[1]][i:i + a, j:j + a]
                self.insert(i, i+a, j, j+a, self.colors_list[mean_gradient[1]])

        blurred = cv2.GaussianBlur(self.result_img, (0, 0), 2)
        details = cv2.subtract(self.result_img, blurred)
        self.result_img = cv2.add(self.result_img, details)

        if os.path.exists(self.name_of_session):
            shutil.rmtree(self.name_of_session)
        os.makedirs(self.name_of_session)
        for i in range(len(self.img_list)):
            os.makedirs(f"{self.name_of_session}/{i+1}")
            cv2.imwrite(f"{self.name_of_session}/{i+1}/colored.jpg", self.img_list[i])
            cv2.imwrite(f"{self.name_of_session}/{i + 1}/grey.jpg", self.grey_list[i])
            cv2.imwrite(f"{self.name_of_session}/{i + 1}/sharp.jpg", self.sharp_list[i])

        cv2.imwrite(f"{self.name_of_session}/result.jpg", self.result_img)
        cv2.imwrite(f"{self.name_of_session}/result_sharpness.jpg", self.result_sharpness)
        cv2.imwrite(f"{self.name_of_session}/result_color.jpg", self.color_image)


    def insert(self, i0, i1, j0, j1, c):
        for i in range(i0, i1):
            for j in range(j0, j1):
                try:
                    self.color_image[i][j] = np.array(c)
                except IndexError:
                    pass


    def auto_area(self):
        tmp = [2, 3, 5, 7, 9, 10]
        h, w = self.grey_list[0].shape[0], self.grey_list[0].shape[1]
        s = (0, 0)
        for area in tmp:
            c = 0
            for i in range(0, h, area):
                for j in range(0, w, area):
                    mean_gradient = max(map(lambda x: (np.mean(self.sharp_list[x][i:i + area, j:j + area]), x), range(len(self.sharp_list))), key=lambda y: y[0])
                    c += mean_gradient[0]
            if c >= s[0]:
                s = (c, area)
        return s[1]


    def colors(self):
        a = [[5, 5, 250]]
        b = [[5, 250, 250]]
        c = [[5, 250, 5]]
        d = [[250, 250, 5]]
        e = [[250, 5, 5]]
        f = [[250, 5, 250]]
        my_list = [a, b, c, d, e, f]
        l = len(self.img_list)
        mod = l % 6
        d = l // 6
        if l <= 6:
            self.colors_list = [my_list[i][0] for i in range(6)]
        else:
            for i in range(len(my_list)):
                if i + 1 <= mod:
                    self.h(d + 1, my_list[i], my_list[i + 1])
                else:
                    if i != 5:
                        self.h(d, my_list[i], my_list[i + 1])
                    else:
                        self.h(d, my_list[i], my_list[-1])

            self.colors_list = []
            for i in my_list:
                for j in i:
                    self.colors_list.append(j)


    def h(self, n, list1, list2):
        step = 245 // n
        ind = 0
        for i in range(3):
            if list1[0][i] != list2[0][i]:
                ind = i
                break

        if list1[0][ind] < list2[0][ind]:
            for j in range(n - 1):
                list1.append(list(list1[0]))
                list1[-1][ind] = list1[-1][ind] + step * (j + 1)
        else:
            for j in range(n - 1):
                list1.append(list(list1[0]))
                list1[-1][ind] = list1[-1][ind] - step * (j + 1)





if __name__ == "__main__":
    # pictures = ["photo\DSC_0094.jpg", "photo\DSC_0095.jpg", "photo\DSC_0096.jpg", "photo\DSC_0097.jpg", "photo\DSC_0098.jpg", "photo\DSC_0099.jpg", "photo\DSC_0100.jpg",
    #            "photo\DSC_0101.jpg", "photo\DSC_0102.jpg", "photo\DSC_0103.jpg"]
    # pictures = ["fff1.jpg", "fff2.jpg", "fff3.jpg", "fff4.jpg", "fff5.jpg",
    #             "fff6.jpg", "fff7.jpg"]
    # pictures = ["f1.jpg", "f2.jpg"]
    pictures = ['a1.png', 'a2.png', 'a3.png']
    butterfly = PhotoStacking(pictures, "shapes", 10)
    butterfly.main()