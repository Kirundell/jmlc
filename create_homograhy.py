import numpy as np
import cv2 as cv

def resize_image(img, max_width=800, max_height=600):
    """
    Функция для изменения размера изображения с сохранением пропорций
    """
    height, width = img.shape[:2]
    scale_width = max_width / width
    scale_height = max_height / height
    scale = min(scale_width, scale_height)

    if scale >= 1:
        return img.copy()

    new_width = int(width * scale)
    new_height = int(height * scale)
    resized = cv.resize(img, (new_width, new_height), interpolation=cv.INTER_AREA)
    return resized

drawing = False
src_x, src_y = -1, -1
dst_x, dst_y = -1, -1

src_list = []
dst_list = []
H = None 

def select_points_src(event, x, y, flags, param):
    global src_x, src_y, drawing
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        src_x, src_y = x, y
        cv.circle(src_copy, (x, y), 5, (0, 0, 255), -1)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False

def select_points_dst(event, x, y, flags, param):
    global dst_x, dst_y, drawing
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        dst_x, dst_y = x, y
        cv.circle(dst_copy, (x, y), 5, (0, 0, 255), -1)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False

def get_plan_view(src, dst):
    if len(src_list) >= 4 and len(dst_list) >= 4:
        src_pts = np.array(src_list).reshape(-1, 1, 2)
        dst_pts = np.array(dst_list).reshape(-1, 1, 2)
        H, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
        print("H (homography matrix):")
        print(H)
        plan_view = cv.warpPerspective(src, H, (dst.shape[1], dst.shape[0]))
        return plan_view
    else:
        print("Необходимо как минимум 4 точки для вычисления гомографии.")
        return dst.copy()

def merge_views(src, dst):
    plan_view = get_plan_view(src, dst)
    merged = plan_view.copy()
    for i in range(dst.shape[0]):
        for j in range(dst.shape[1]):
            if np.all(merged[i, j] == 0):
                merged[i, j] = dst[i, j]
    return merged

# Загрузка изображений
src = cv.imread(r'C:\Users\Kirill\Desktop\img.png', cv.IMREAD_COLOR)
if src is None:
    raise FileNotFoundError("Не удалось загрузить исходное изображение.")
# src = resize_image(src)
src_copy = src.copy()
cv.namedWindow('src', cv.WINDOW_NORMAL)
cv.moveWindow("src", 1280, 800)
cv.setMouseCallback('src', select_points_src)

dst = cv.imread(r'C:\Users\Kirill\Desktop\map.png', cv.IMREAD_COLOR)
if dst is None:
    raise FileNotFoundError("Не удалось загрузить изображение карты.")
# dst = resize_image(dst)
dst_copy = dst.copy()
cv.namedWindow('dst', cv.WINDOW_NORMAL)
cv.moveWindow("dst", 800, 600)
cv.setMouseCallback('dst', select_points_dst)

while True:
    cv.imshow('src', src_copy)
    cv.imshow('dst', dst_copy)
    key = cv.waitKey(1) & 0xFF

    if key == ord('s'):
        print('save points')
        cv.circle(src_copy, (src_x, src_y), 5, (0, 255, 0), -1)
        cv.circle(dst_copy, (dst_x, dst_y), 5, (0, 255, 0), -1)
        src_list.append([src_x, src_y])
        dst_list.append([dst_x, dst_y])
        print("src points:", src_list)
        print("dst points:", dst_list)

    elif key == ord('h'):
        print('create plan view')
        plan_view = get_plan_view(src, dst)
        cv.imshow("plan view", plan_view)

    elif key == ord('m'):
        print('merge views')
        merged = merge_views(src, dst)
        cv.imshow("merge", merged)

    elif key == 27:
        print("Выход из программы")
        break

cv.destroyAllWindows()

if H is not None:
    print("Сохранённая матрица гомографии H:")
    print(H)
