import cv2
import math
import argparse


# variables
ix = -1
iy = -1
x1 = -1
y1 = -1
x2 = -1
y2 = -1
radius = -1
xm = -1
drawing = False
twisting = False
deform = False
rightElipse = False
numofrows = 0
numofcols = 0
imgName = ""

def makebiLinear(i,x,xround):
    ctl = img[i, xround]
    ctr = img[i, min(xround + 1, numofcols -1)]
    w = x - xround
    ct = (1 - w) * ctl + w * ctr
    return ct

def makeQubic( originalX, i , img):
    # assume originalX = j + xnew || j - xnew
    normalX = int(originalX)
    colorAcc = 0
    for k in range(-1, 3):  # y
        for l in range(-1, 3):  # x
            dx = abs(originalX - (normalX + l))
            cax = 0
            if dx <= 1:
                cax = 1.5 * (dx ** 3) - 2.5 * (dx ** 2) + 1
            elif dx <= 2:
                cax = -0.5 * (dx ** 3) + 2.5 * (dx ** 2) - 4 * dx + 2
            dy = abs(k)

            cay = 0
            if dy <= 1:
                cay = 1.5 * (dy ** 3) - 2.5 * (dy ** 2) + 1
            elif dy <= 2:
                cay = -0.5 * (dy ** 3) + 2.5 * (dy ** 2) - 4 * dy + 2

            colorAcc += img[min(max(0, (i + k)), numofrows-1), min(max(0, (normalX + l)), numofcols-1)] * cax * cay
    return colorAcc


def draw_reactangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, img, x1, y1, x2, y2, twisting, deform, radius, xm, rightElipse, numofrows, numofcols ,imgName

    x = min(max(0, x), numofcols)
    y = min(max(0, y), numofrows)

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y


    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            if not twisting:
                img2 = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
                cv2.rectangle(img2, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=4)
                cv2.ellipse(img2, (round((ix + x) / 2), (round((iy + y) / 2))), ((round(abs(y - iy) / 2)), 0), 270, 0, 180,
                            (255, 0, 0), 2)
                img = img2
            else:
                img2 = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
                cv2.rectangle(img2, pt1=(x1, y1), pt2=(x2, y2), color=(0, 255, 255), thickness=4)
                if x >= (round((x1 + x2) / 2)):
                    radius = round(min(abs(x - xm), abs(x2 - xm)))
                    cv2.ellipse(img2, (round((x1 + x2) / 2), (round((y1 + y2) / 2))),
                                ((round((y2 - y1) / 2)), radius), 270, 0, 180,
                                (255, 0, 0), 2)
                    rightElipse = True
                else:
                    radius = round(min(abs(x - xm), abs(x2 - xm)))
                    cv2.ellipse(img2, (round((x1 + x2) / 2), (round((y1 + y2) / 2))),
                                ((round((y2 - y1) / 2)), radius), 90, 0,
                                180,
                                (255, 0, 0), 2)
                    rightElipse = False
                img = img2
                deform = True



    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if not twisting:
            img2 = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
            cv2.rectangle(img2, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=4)
            cv2.ellipse(img2, (round((ix + x) / 2), (round((iy + y) / 2))), ((round(abs(y - iy) / 2)), 0), 270, 0, 180,
                        (255, 0, 0), 2)
            x1 = min(ix, x)
            y1 = min(iy, y)
            x2 = max(ix, x)
            y2 = max(iy, y)

            xm = round((x1 + x2) / 2)
            img = img2
            twisting = True

        if deform:

            img = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
            img_output1 = img.copy()
            img_output2 = img.copy()
            img_output3 = img.copy()

            highradius = (y2 - y1) / 2
            for i in range(y1, y2):
                for j in range(x1, x2):
                    ym = round((y2 + y1) / 2)
                    newy = (ym - y1) - abs(i - ym)
                    xofelipse = xm - int(radius * math.sin(2 * 3.14 * newy / (2 * 2 * highradius)))
                    if (j == x1):
                        newradius = 0
                    elif (j <= xofelipse):
                        newradius = ((j - x1) / (xofelipse - x1)) * radius
                    else:
                        newradius = (1 - ((j - xofelipse) / (x2 - xofelipse))) * radius

                    ym = round((y2 + y1) / 2)
                    newy = (ym - y1) - abs(i - ym)
                    xnew = newradius * math.sin(2 * 3.14 * newy / (2 * 2 * highradius))

                    if rightElipse:
                        j = x2 - j + x1 -1

                        # Nearest neighbor:
                        img_output1[i, j] = img[i, j - int(xnew)]

                        # Biliniear:
                        img_output2[i, j] = makebiLinear(i, (j - xnew), (int(j - xnew)))

                        # Qubic:
                        img_output3[i, j] = makeQubic(j - xnew, i, img)
                    else:
                        # Nearest neighbor:
                        img_output1[i, j] = img[i, j + int(xnew)]

                        # Biliniear:
                        img_output2[i, j] = makebiLinear(i, (j + xnew), (int(j + xnew)))

                        # Qubic:
                        img_output3[i, j] = makeQubic(j + xnew, i, img)

            cv2.imshow('nearest neighbor', img_output1)
            cv2.imshow('bilinear', img_output2)
            cv2.imshow('Qubic', img_output3)

def get_distance(src, target):
    d = abs(src - target)

    if d < 1:
        return 1.5 * (d**3) - 2.5 * (d**2) + 1
    if d < 2:
        return -0.5 * (d**3) + 2.5 * (d**2) - 4*d +2
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("imgName", help = "Prints the supplied argument.")

    args = parser.parse_args()
    imgName = args.imgName

    img = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
    numofrows, numofcols = img.shape

    cv2.namedWindow(winname="Work Space")
    cv2.setMouseCallback("Work Space", draw_reactangle_with_drag)

    while True:
        cv2.imshow("Work Space", img)
        if cv2.waitKey(10) == 113:
            break

    cv2.destroyAllWindows()

