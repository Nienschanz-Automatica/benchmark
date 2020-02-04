import cv2


transparent = 0.3
colors = {"road": (0, 255, 0),
          "curb": (255, 0, 0),
          "mark": (0, 0, 255)}
confidence_thresh = 0.45

def visualize(img, data):
    road, curb, mark = prepare_net_output(data)
    overlay = img.copy()
    overlay = draw_data(overlay, road, colors["road"])
    overlay = draw_data(overlay, curb, colors["curb"])
    overlay = draw_data(overlay, mark, colors["mark"])
    alpha = transparent
    beta = 1 - transparent
    cv2.addWeighted(overlay, alpha, img, beta, 1, img)  # for transparent drawing
    return img


def prepare_net_output(net_output):
    net_output = net_output[0]
    road = net_output[1]
    curb = net_output[2]
    mark = net_output[3]
    return road, curb, mark


def draw_data(img, confidence_data, color):
    confidence_data = confidence_data
    confidence_data[confidence_data > confidence_thresh] = 1
    confidence_data[confidence_data <= confidence_thresh] = 0
    orig_h, orig_w, _ = img.shape
    dst_data = cv2.resize(confidence_data, (orig_w, orig_h))
    img[dst_data == 1] = color
    return img