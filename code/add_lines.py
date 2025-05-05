import cv2
import numpy as np

from sklearn.linear_model import RANSACRegressor, LinearRegression
import numpy as np


def draw_ransac_lines(image, centroids, color=(255, 255, 0)):
    if len(centroids) < 2:
        return image, False  # not enough points

    # Convert to numpy array
    points = np.array(centroids)
    X = points[:, 0].reshape(-1, 1)  # x values
    y = points[:, 1]  # y values

    # Fit first RANSAC model
    ransac = RANSACRegressor(LinearRegression(), residual_threshold=10, max_trials=100)
    ransac.fit(X, y)
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)

    # Draw first line
    x_range = np.linspace(0, image.shape[1], 2).reshape(-1, 1)
    y_pred = ransac.predict(x_range)
    pt1 = (int(x_range[0]), int(y_pred[0]))
    pt2 = (int(x_range[1]), int(y_pred[1]))
    cv2.line(image, pt1, pt2, color, 2)
    middle_slope = (y_pred[1] - y_pred[0]) / (x_range[1] - x_range[0])

    # If there are enough outliers, fit a second line
    intersection_detected = False
    if np.count_nonzero(outlier_mask) > 1:
        intersection_detected = True
        X_out = X[outlier_mask]
        y_out = y[outlier_mask]

        if len(X_out) >= 2:
            ransac2 = RANSACRegressor(
                LinearRegression(), residual_threshold=10, max_trials=100
            )
            ransac2.fit(X_out, y_out)

            y_pred2 = ransac2.predict(x_range)
            pt3 = (int(x_range[0]), int(y_pred2[0]))
            pt4 = (int(x_range[1]), int(y_pred2[1]))
            cv2.line(image, pt3, pt4, (150, 150, 0), 2)

    return image, intersection_detected


def process_image_with_steering_overlay(frame, from_file=False):
    intersection_detected = False
    avg_x, avg_y = -1, -1

    if from_file:
        frame = cv2.imread(frame)
    frame = cv2.resize(frame, (640, 480))  # Resize for consistency
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Yellow mask (your tuned values)
    # lower_yellow = np.array([18, 93, 132])
    # upper_yellow = np.array([26, 255, 255])
    lower_yellow = np.array([20, 74, 100])
    s_max = 82
    upper_yellow = np.array([34, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    if from_file:
        cv2.imshow("Yello Mask", mask)
        cv2.waitKey(0)

    # Morphological cleanup
    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    # Find contours in the mask
    contours, _ = cv2.findContours(
        mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Draw the mask and lines on a copy of the image
    annotated = frame.copy()

    if contours:
        centroids = []
        for cnt in contours:
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((cx, cy))
                # Draw each centroid
                cv2.circle(annotated, (cx, cy), 3, (0, 0, 255), -1)

        if centroids:
            # Average largest  centroids
            top_centroids = sorted(centroids, key=lambda pt: pt[1], reverse=True)[:3]
            # top_centroids = centroids
            avg_x = int(np.mean([pt[0] for pt in top_centroids]))
            avg_y = int(np.mean([pt[1] for pt in top_centroids]))

            # Draw average centroid
            cv2.circle(annotated, (avg_x, avg_y), 6, (255, 0, 0), -1)

            # Draw steering line
            height, width = frame.shape[:2]
            bottom_center = (width // 2, height - 1)
            cv2.line(annotated, bottom_center, (avg_x, avg_y), (0, 255, 0), 3)
            annotated, intersection_suggested = draw_ransac_lines(annotated, centroids)
            try:
                steering_slope = (avg_y - bottom_center[1]) / (avg_x - (bottom_center[0]+50))
            except ZeroDivisionError:
                steering_slope = 0

            # --- INTERSECTION DETECTION ---
        if (
            len(centroids) >= 5 or intersection_suggested
        ):  # enough lines to suggest complexity
            x_vals = [pt[0] for pt in centroids]
            # print("Intersection detected ", x_vals)
            spread = max(x_vals) - min(x_vals)

            if spread > frame.shape[1] * 0.5:  # half the frame width
            # if spread > 100:
                intersection_detected = True
            else:
                intersection_detected = False
        else:
            intersection_detected = False

        # Optional: Draw intersection notice
        if intersection_detected:
            cv2.putText(
                annotated,
                "INTERSECTION AHEAD",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3,
            )

    # Show results
    if from_file:
        cv2.imshow("Annotated Steering Overlay", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if contours:
        return annotated, (avg_x, avg_y), steering_slope, intersection_detected
    else:
        return annotated, (-1, -1), 0, intersection_detected


if __name__ == "__main__":
    ret = process_image_with_steering_overlay("data/road_19.jpg", True)
    print(ret[1])