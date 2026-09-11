"""틈새 공부 AI 교실 ⑲: 휴대폰용 홈트레이닝 자세 분석기.

설치:
    python -m pip install -r requirements.txt

실행:
    python -m streamlit run lesson19_home_training_pose_analyzer.py

휴대폰 운동 영상을 올리면 MediaPipe Pose Landmarker가 33개 신체 지점을 찾아
스쿼트·런지·팔굽혀펴기·플랭크·점핑잭의 반복 횟수와 핵심 자세를 분석합니다.
이 결과는 운동 학습을 돕기 위한 참고 자료이며 의료 진단이 아닙니다.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import urlretrieve


MODEL_FILENAME = "pose_landmarker_lite.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
MAX_VIDEO_SECONDS = 45
MAX_UPLOAD_MB = 80
TARGET_ANALYSIS_FPS = 15

# MediaPipe Pose Landmarker의 주요 골격 연결
POSE_CONNECTIONS = (
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),
    (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),
)

KEY_LANDMARKS = (11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 31, 32)

EXERCISES = ("스쿼트", "런지", "팔굽혀펴기", "플랭크", "점핑잭")
EXERCISE_CODE = {
    "스쿼트": "SQUAT",
    "런지": "LUNGE",
    "팔굽혀펴기": "PUSH-UP",
    "플랭크": "PLANK",
    "점핑잭": "JUMPING JACK",
}
EXERCISE_FILE_CODE = {
    "스쿼트": "squat",
    "런지": "lunge",
    "팔굽혀펴기": "pushup",
    "플랭크": "plank",
    "점핑잭": "jumping_jack",
}
EXERCISE_GUIDE = {
    "스쿼트": "서 있는 자세 → 앉기 → 완전히 일어서기가 모두 나오게 촬영하세요.",
    "런지": "두 발을 앞뒤로 두고 내려갔다가 다시 일어서는 전신을 촬영하세요.",
    "팔굽혀펴기": "휴대폰을 옆에 두고 머리·어깨·골반·발목이 모두 나오게 촬영하세요.",
    "플랭크": "휴대폰을 옆에 두고 몸을 일직선으로 유지하는 모습을 촬영하세요.",
    "점핑잭": "팔을 머리 위로 올리고 두 발을 벌렸다 모으는 전신을 정면에서 촬영하세요.",
}


def angle_between(point_a, point_b, point_c):
    """B를 꼭짓점으로 하는 A-B-C 각도를 도 단위로 반환합니다."""
    vector_ba = (point_a[0] - point_b[0], point_a[1] - point_b[1])
    vector_bc = (point_c[0] - point_b[0], point_c[1] - point_b[1])
    length_ba = math.hypot(*vector_ba)
    length_bc = math.hypot(*vector_bc)
    if length_ba < 1e-9 or length_bc < 1e-9:
        return 180.0
    cosine = (
        vector_ba[0] * vector_bc[0] + vector_ba[1] * vector_bc[1]
    ) / (length_ba * length_bc)
    cosine = max(-1.0, min(1.0, cosine))
    return math.degrees(math.acos(cosine))


def midpoint(point_a, point_b):
    return (
        (point_a[0] + point_b[0]) / 2,
        (point_a[1] + point_b[1]) / 2,
    )


def landmark_point(landmark, width, height):
    return landmark.x * width, landmark.y * height


def frame_metrics(landmarks, width, height, camera_view, exercise="스쿼트"):
    """한 장면에서 선택한 운동의 핵심 관절 각도와 자세 문제를 계산합니다."""
    if not landmarks or len(landmarks) < 33:
        return None

    required_landmarks = {
        "스쿼트": (11, 12, 23, 24, 25, 26, 27, 28),
        "런지": (11, 12, 23, 24, 25, 26, 27, 28),
        "팔굽혀펴기": (11, 12, 13, 14, 15, 16, 23, 24, 27, 28),
        "플랭크": (11, 12, 23, 24, 27, 28),
        "점핑잭": (11, 12, 15, 16, 23, 24, 27, 28),
    }.get(exercise, KEY_LANDMARKS)
    visibility = [
        float(getattr(landmarks[index], "visibility", 1.0))
        for index in required_landmarks
    ]
    required_visible = max(5, math.ceil(len(required_landmarks) * 0.7))
    if sum(value >= 0.42 for value in visibility) < required_visible:
        return None

    points = {
        index: landmark_point(landmarks[index], width, height)
        for index in KEY_LANDMARKS
    }
    left_knee = angle_between(points[23], points[25], points[27])
    right_knee = angle_between(points[24], points[26], points[28])
    average_knee = (left_knee + right_knee) / 2
    knee_asymmetry = abs(left_knee - right_knee)

    left_elbow = angle_between(points[11], points[13], points[15])
    right_elbow = angle_between(points[12], points[14], points[16])
    average_elbow = (left_elbow + right_elbow) / 2
    elbow_asymmetry = abs(left_elbow - right_elbow)

    left_body_line = angle_between(points[11], points[23], points[27])
    right_body_line = angle_between(points[12], points[24], points[28])
    average_body_line = (left_body_line + right_body_line) / 2
    body_asymmetry = abs(left_body_line - right_body_line)

    left_arm_raise = angle_between(points[23], points[11], points[15])
    right_arm_raise = angle_between(points[24], points[12], points[16])
    average_arm_raise = (left_arm_raise + right_arm_raise) / 2
    arm_asymmetry = abs(left_arm_raise - right_arm_raise)

    shoulder_center = midpoint(points[11], points[12])
    hip_center = midpoint(points[23], points[24])
    horizontal_change = abs(shoulder_center[0] - hip_center[0])
    vertical_change = max(1.0, abs(shoulder_center[1] - hip_center[1]))
    trunk_lean = math.degrees(math.atan2(horizontal_change, vertical_change))

    ankle_spacing = abs(points[27][0] - points[28][0])
    knee_spacing = abs(points[25][0] - points[26][0])
    knee_spacing_ratio = knee_spacing / max(ankle_spacing, 1.0)
    shoulder_spacing = abs(points[11][0] - points[12][0])
    foot_spacing_ratio = ankle_spacing / max(shoulder_spacing, 1.0)
    knee_inward = (
        camera_view == "정면"
        and average_knee < 145
        and knee_spacing_ratio < 0.56
    )

    issues = []
    if exercise == "스쿼트":
        primary_left, primary_right = left_knee, right_knee
        primary_label = "무릎 각도"
        left_label, right_label = "왼쪽 무릎", "오른쪽 무릎"
        active = average_knee < 150
        if active and trunk_lean > 43:
            issues.append(("posture", "상체 기울기"))
        if active and knee_asymmetry > 22:
            issues.append(("balance", "좌우 무릎 균형"))
        if knee_inward:
            issues.append(("alignment", "무릎 정렬"))
    elif exercise == "런지":
        primary_left, primary_right = left_knee, right_knee
        primary_label = "무릎 각도"
        left_label, right_label = "왼쪽 무릎", "오른쪽 무릎"
        active = min(left_knee, right_knee) < 145
        if active and trunk_lean > 38:
            issues.append(("posture", "상체 기울기"))
        if active and knee_asymmetry < 12:
            issues.append(("alignment", "앞뒤 다리 구분"))
    elif exercise == "팔굽혀펴기":
        primary_left, primary_right = left_elbow, right_elbow
        primary_label = "팔꿈치 각도"
        left_label, right_label = "왼쪽 팔꿈치", "오른쪽 팔꿈치"
        active = average_elbow < 155
        if active and average_body_line < 155:
            issues.append(("posture", "몸통 일직선"))
        if active and elbow_asymmetry > 22:
            issues.append(("balance", "좌우 팔 균형"))
    elif exercise == "플랭크":
        primary_left, primary_right = left_body_line, right_body_line
        primary_label = "몸통 일직선 각도"
        left_label, right_label = "왼쪽 몸통", "오른쪽 몸통"
        active = True
        if average_body_line < 160:
            issues.append(("posture", "몸통 일직선"))
        if body_asymmetry > 18:
            issues.append(("balance", "좌우 몸통 균형"))
    else:  # 점핑잭
        primary_left, primary_right = left_arm_raise, right_arm_raise
        primary_label = "팔 올림 각도"
        left_label, right_label = "왼팔", "오른팔"
        active = True
        arms_open = average_arm_raise > 140
        feet_open = foot_spacing_ratio > 1.25
        arms_closed = average_arm_raise < 55
        feet_closed = foot_spacing_ratio < 1.05
        if arms_open != feet_open or arms_closed != feet_closed:
            issues.append(("alignment", "팔·다리 타이밍"))
        if arm_asymmetry > 25:
            issues.append(("balance", "좌우 팔 균형"))

    primary_average = (
        min(primary_left, primary_right)
        if exercise == "런지"
        else (primary_left + primary_right) / 2
    )
    issue_codes = {code for code, _ in issues}

    return {
        "left_knee": left_knee,
        "right_knee": right_knee,
        "average_knee": average_knee,
        "left_elbow": left_elbow,
        "right_elbow": right_elbow,
        "average_elbow": average_elbow,
        "left_body_line": left_body_line,
        "right_body_line": right_body_line,
        "average_body_line": average_body_line,
        "left_arm_raise": left_arm_raise,
        "right_arm_raise": right_arm_raise,
        "average_arm_raise": average_arm_raise,
        "primary_left": primary_left,
        "primary_right": primary_right,
        "primary_average": primary_average,
        "primary_label": primary_label,
        "left_label": left_label,
        "right_label": right_label,
        "trunk_lean": trunk_lean,
        "knee_spacing_ratio": knee_spacing_ratio,
        "foot_spacing_ratio": foot_spacing_ratio,
        "knee_inward": knee_inward,
        "active": active,
        "quality_good": not issue_codes,
        "open_position": (
            average_arm_raise > 140 and foot_spacing_ratio > 1.25
        ),
        "closed_position": (
            average_arm_raise < 55 and foot_spacing_ratio < 1.05
        ),
        "issues": issues,
    }


def ensure_pose_model():
    """모델을 같은 폴더 또는 임시 폴더에서 찾고, 없으면 한 번 다운로드합니다."""
    bundled_model = Path(__file__).with_name(MODEL_FILENAME)
    if bundled_model.exists() and bundled_model.stat().st_size > 1_000_000:
        return bundled_model

    cached_model = Path(tempfile.gettempdir()) / MODEL_FILENAME
    if cached_model.exists() and cached_model.stat().st_size > 1_000_000:
        return cached_model

    try:
        urlretrieve(MODEL_URL, cached_model)
    except Exception as error:
        raise RuntimeError(
            "자세 인식 모델을 자동으로 내려받지 못했습니다. 인터넷 연결을 확인한 뒤 "
            "다시 시도하거나 pose_landmarker_lite.task 파일을 프로그램과 같은 "
            "폴더에 넣어 주세요."
        ) from error
    return cached_model


def resize_for_analysis(frame, maximum_width=720):
    """긴 휴대폰 영상을 빠르게 처리할 수 있도록 큰 프레임만 줄입니다."""
    import cv2

    height, width = frame.shape[:2]
    if width <= maximum_width:
        return frame
    scale = maximum_width / width
    return cv2.resize(
        frame,
        (maximum_width, max(1, int(height * scale))),
        interpolation=cv2.INTER_AREA,
    )


def draw_pose(frame, landmarks, connections, color):
    """OpenCV 영상 위에 관절과 골격선을 표시합니다."""
    import cv2

    height, width = frame.shape[:2]
    for start, end in connections:
        first = landmarks[start]
        second = landmarks[end]
        if (
            float(getattr(first, "visibility", 1.0)) < 0.42
            or float(getattr(second, "visibility", 1.0)) < 0.42
        ):
            continue
        point_a = (int(first.x * width), int(first.y * height))
        point_b = (int(second.x * width), int(second.y * height))
        cv2.line(frame, point_a, point_b, color, 4, cv2.LINE_AA)

    for index in KEY_LANDMARKS:
        item = landmarks[index]
        if float(getattr(item, "visibility", 1.0)) < 0.42:
            continue
        center = (int(item.x * width), int(item.y * height))
        cv2.circle(frame, center, 7, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, center, 7, color, 3, cv2.LINE_AA)


def draw_frame_information(
    frame, exercise, rep_count, hold_seconds, metrics, issues
):
    """분석 영상 위에 숫자로 된 핵심 결과를 표시합니다."""
    import cv2

    height, width = frame.shape[:2]
    panel_height = min(104, max(78, int(height * 0.115)))
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, panel_height), (12, 25, 50), -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)

    scale = max(0.55, min(0.92, width / 760))
    count_text = (
        f"HOLD {hold_seconds:.1f}s"
        if exercise == "플랭크"
        else f"REPS {rep_count}"
    )
    cv2.putText(
        frame, f"{EXERCISE_CODE[exercise]}  {count_text}", (16, 34),
        cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 2, cv2.LINE_AA,
    )
    if metrics:
        metric_code = {
            "스쿼트": "KNEE", "런지": "KNEE", "팔굽혀펴기": "ELBOW",
            "플랭크": "BODY", "점핑잭": "ARM",
        }[exercise]
        cv2.putText(
            frame,
            f"{metric_code} {metrics['primary_average']:.0f} deg",
            (16, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale * 0.82,
            (147, 255, 236),
            2,
            cv2.LINE_AA,
        )
        status = "CHECK FORM" if issues else "GOOD TRACKING"
        status_color = (80, 100, 255) if issues else (90, 225, 120)
        cv2.putText(
            frame, status, (max(16, width - 230), 34),
            cv2.FONT_HERSHEY_SIMPLEX, scale * 0.76,
            status_color, 2, cv2.LINE_AA,
        )


def record_issue(issue_events, last_issue_time, code, label, timestamp):
    """같은 경고가 너무 촘촘하게 반복되지 않도록 대표 시간만 저장합니다."""
    previous = last_issue_time.get(code, -99.0)
    if timestamp - previous >= 2.0 and len(issue_events) < 15:
        issue_events.append({"time": timestamp, "code": code, "label": label})
        last_issue_time[code] = timestamp


def browser_friendly_video(raw_path, output_directory):
    """가능하면 분석 영상을 휴대폰 브라우저용 H.264 MP4로 변환합니다."""
    raw_bytes = Path(raw_path).read_bytes()
    try:
        import imageio_ffmpeg

        target_path = Path(output_directory) / "pose_analysis_h264.mp4"
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y", "-loglevel", "error",
            "-i", str(raw_path),
            "-an",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "25",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(target_path),
        ]
        subprocess.run(command, check=True, capture_output=True, timeout=180)
        if target_path.exists() and target_path.stat().st_size > 10_000:
            return target_path.read_bytes(), "video/mp4"
    except Exception:
        pass
    return raw_bytes, "video/mp4"


def build_feedback(result, camera_view):
    """분석 수치를 초보자도 이해하기 쉬운 한국어로 바꿉니다."""
    exercise = result["exercise"]
    feedback = []
    if result["detection_rate"] < 70:
        feedback.append(
            "전신 관절을 충분히 찾지 못했습니다. 머리부터 발끝까지 나오게 하고 "
            "카메라를 조금 더 멀리 두어 다시 촬영해 보세요."
        )

    if exercise == "플랭크":
        if result["hold_seconds"] < 3:
            feedback.append(
                "바른 플랭크 자세가 3초 이상 이어진 구간을 찾지 못했습니다. "
                "옆에서 전신이 보이게 촬영하고 어깨부터 발목까지 길게 펴 보세요."
            )
        if result["posture_issue_rate"] > 15:
            feedback.append(
                "일부 장면에서 골반이 올라가거나 처져 몸의 선이 꺾였습니다. "
                "배에 힘을 주고 어깨·골반·발목을 한 줄로 맞춰 보세요."
            )
    elif exercise == "스쿼트":
        if result["reps"] == 0:
            feedback.append(
                "완전한 반복 동작을 찾지 못했습니다. 서 있는 자세에서 시작해 "
                "앉았다가 다시 완전히 일어나는 장면까지 촬영해 주세요."
            )
        if result["primary_min"] > 120:
            feedback.append(
                "앉는 깊이가 비교적 얕게 나타났습니다. 통증이 없는 범위에서 "
                "엉덩이를 조금 더 낮춰 보세요."
            )
        if result["posture_issue_rate"] > 15:
            feedback.append(
                "일부 장면에서 상체가 많이 숙여졌습니다. 가슴을 편 상태로 "
                "엉덩이를 뒤로 보내는 느낌을 연습해 보세요."
            )
        if camera_view == "정면" and result["alignment_issue_rate"] > 10:
            feedback.append(
                "무릎 사이가 발목 사이보다 지나치게 좁아진 장면이 있습니다. "
                "무릎이 발끝 방향을 따라가도록 천천히 움직여 보세요."
            )
    elif exercise == "런지":
        if result["reps"] == 0:
            feedback.append(
                "내려갔다가 다시 일어나는 한 번의 런지를 찾지 못했습니다. "
                "두 발과 전신이 모두 보이도록 옆에서 촬영해 보세요."
            )
        if result["primary_min"] > 125:
            feedback.append(
                "앞쪽 무릎이 충분히 굽혀진 장면이 적습니다. 통증이 없는 "
                "범위에서 몸을 수직으로 조금 더 내려 보세요."
            )
        if result["posture_issue_rate"] > 15:
            feedback.append(
                "내려갈 때 상체가 앞으로 많이 기울었습니다. 가슴을 세우고 "
                "몸이 위아래로 움직이는 느낌을 연습해 보세요."
            )
    elif exercise == "팔굽혀펴기":
        if result["reps"] == 0:
            feedback.append(
                "팔을 굽혔다가 완전히 펴는 동작을 찾지 못했습니다. "
                "휴대폰을 옆에 두고 손목부터 발목까지 나오게 촬영해 주세요."
            )
        if result["primary_min"] > 115:
            feedback.append(
                "팔꿈치가 많이 굽혀진 구간이 짧습니다. 무릎을 바닥에 대는 "
                "쉬운 동작부터 통증 없는 범위에서 연습해 보세요."
            )
        if result["posture_issue_rate"] > 15:
            feedback.append(
                "몸통이 꺾인 장면이 있습니다. 배와 엉덩이에 힘을 주어 "
                "어깨부터 발목까지 길게 유지해 보세요."
            )
    else:  # 점핑잭
        if result["reps"] == 0:
            feedback.append(
                "팔과 다리를 벌렸다가 다시 모으는 한 번의 동작을 찾지 못했습니다. "
                "정면에서 머리 위와 두 발이 모두 나오게 촬영해 주세요."
            )
        if result["alignment_issue_rate"] > 15:
            feedback.append(
                "팔을 올리는 때와 다리를 벌리는 때가 어긋난 장면이 있습니다. "
                "처음에는 천천히 같은 박자로 움직여 보세요."
            )

    if result["balance_issue_rate"] > 15:
        feedback.append(
            "왼쪽과 오른쪽 움직임의 차이가 큰 장면이 있습니다. 속도를 줄이고 "
            "양쪽에 힘을 고르게 쓰는지 확인해 보세요."
        )
    if not feedback:
        feedback.append(
            "관절이 안정적으로 추적되었고 큰 자세 경고가 발견되지 않았습니다. "
            "같은 속도로 부드럽게 반복해 보세요."
        )
    return feedback


def _analyze_squat_video_legacy(
    video_bytes, filename, camera_view, progress_callback=None
):
    """업로드 영상 전체를 분석하고 결과와 관절 표시 영상을 반환합니다."""
    import cv2
    import mediapipe as mp

    model_path = ensure_pose_model()
    safe_suffix = Path(filename).suffix.lower()
    if safe_suffix not in (".mp4", ".mov", ".avi", ".m4v"):
        safe_suffix = ".mp4"

    with tempfile.TemporaryDirectory(prefix="home_pose_") as work_directory:
        input_path = Path(work_directory) / f"input{safe_suffix}"
        raw_output_path = Path(work_directory) / "squat_analysis_raw.mp4"
        input_path.write_bytes(video_bytes)

        capture = cv2.VideoCapture(str(input_path))
        if not capture.isOpened():
            raise ValueError(
                "영상을 열 수 없습니다. 휴대폰에서 MP4(H.264) 형식으로 다시 저장해 주세요."
            )

        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 1:
            fps = 30.0
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_step = max(1, int(round(fps / TARGET_ANALYSIS_FPS)))
        output_fps = max(5.0, fps / sample_step)
        frame_limit = min(
            total_frames if total_frames > 0 else int(fps * MAX_VIDEO_SECONDS),
            int(fps * MAX_VIDEO_SECONDS),
        )

        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.55,
            min_pose_presence_confidence=0.55,
            min_tracking_confidence=0.55,
            output_segmentation_masks=False,
        )

        writer = None
        processed_frames = 0
        detected_frames = 0
        active_frames = 0
        lean_issue_frames = 0
        balance_issue_frames = 0
        knee_issue_frames = 0
        frame_index = -1
        rep_count = 0
        correct_reps = 0
        phase = "up"
        active_rep = None
        time_values = []
        knee_values = []
        left_knee_values = []
        right_knee_values = []
        lean_values = []
        issue_events = []
        last_issue_time = {}
        lowest_pose_world = None
        lowest_pose_normalized = None
        minimum_knee_angle = 180.0

        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        with PoseLandmarker.create_from_options(options) as landmarker:
            while True:
                success, frame = capture.read()
                if not success:
                    break
                frame_index += 1
                if frame_index >= frame_limit:
                    break
                if frame_index % sample_step != 0:
                    continue

                frame = resize_for_analysis(frame)
                height, width = frame.shape[:2]
                if writer is None:
                    codec = cv2.VideoWriter_fourcc(*"mp4v")
                    writer = cv2.VideoWriter(
                        str(raw_output_path), codec, output_fps, (width, height)
                    )
                    if not writer.isOpened():
                        raise RuntimeError("분석 영상을 만들 수 없습니다.")

                timestamp = frame_index / fps
                timestamp_ms = int(round(timestamp * 1000))
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame,
                )
                pose_result = landmarker.detect_for_video(mp_image, timestamp_ms)
                processed_frames += 1

                landmarks = (
                    pose_result.pose_landmarks[0]
                    if pose_result.pose_landmarks
                    else None
                )
                world_landmarks = (
                    pose_result.pose_world_landmarks[0]
                    if pose_result.pose_world_landmarks
                    else None
                )
                metrics = frame_metrics(landmarks, width, height, camera_view)
                frame_issues = []

                if metrics is not None:
                    detected_frames += 1
                    average_knee = metrics["average_knee"]
                    time_values.append(timestamp)
                    knee_values.append(average_knee)
                    left_knee_values.append(metrics["left_knee"])
                    right_knee_values.append(metrics["right_knee"])
                    lean_values.append(metrics["trunk_lean"])

                    if average_knee < minimum_knee_angle:
                        minimum_knee_angle = average_knee
                        lowest_pose_normalized = [
                            (
                                float(item.x),
                                float(item.y),
                                float(item.z),
                                float(getattr(item, "visibility", 1.0)),
                            )
                            for item in landmarks
                        ]
                        if world_landmarks:
                            lowest_pose_world = [
                                (
                                    float(item.x),
                                    float(item.y),
                                    float(item.z),
                                    float(getattr(item, "visibility", 1.0)),
                                )
                                for item in world_landmarks
                            ]

                    if average_knee < 150:
                        active_frames += 1
                        if metrics["trunk_lean"] > 43:
                            lean_issue_frames += 1
                        if metrics["asymmetry"] > 22:
                            balance_issue_frames += 1
                        if metrics["knee_inward"]:
                            knee_issue_frames += 1

                    frame_issues = metrics["issues"]
                    for code, label in frame_issues:
                        record_issue(
                            issue_events, last_issue_time,
                            code, label, timestamp,
                        )

                    if phase == "up" and average_knee < 145:
                        phase = "down"
                        active_rep = {
                            "minimum": average_knee,
                            "maximum_lean": metrics["trunk_lean"],
                            "maximum_asymmetry": metrics["asymmetry"],
                            "knee_inward": metrics["knee_inward"],
                            "reached_depth": average_knee <= 110,
                        }
                    elif phase == "down" and active_rep is not None:
                        active_rep["minimum"] = min(
                            active_rep["minimum"], average_knee
                        )
                        active_rep["maximum_lean"] = max(
                            active_rep["maximum_lean"], metrics["trunk_lean"]
                        )
                        active_rep["maximum_asymmetry"] = max(
                            active_rep["maximum_asymmetry"], metrics["asymmetry"]
                        )
                        active_rep["knee_inward"] = (
                            active_rep["knee_inward"] or metrics["knee_inward"]
                        )
                        active_rep["reached_depth"] = (
                            active_rep["reached_depth"] or average_knee <= 110
                        )
                        if average_knee > 155:
                            rep_count += 1
                            good_rep = (
                                active_rep["reached_depth"]
                                and active_rep["maximum_lean"] <= 47
                                and active_rep["maximum_asymmetry"] <= 26
                                and not active_rep["knee_inward"]
                            )
                            if good_rep:
                                correct_reps += 1
                            phase = "up"
                            active_rep = None

                    skeleton_color = (
                        (55, 85, 245) if frame_issues else (65, 210, 115)
                    )
                    draw_pose(frame, landmarks, POSE_CONNECTIONS, skeleton_color)
                else:
                    skeleton_color = (120, 120, 120)

                draw_frame_information(
                    frame, rep_count, metrics, frame_issues
                )
                writer.write(frame)

                if progress_callback and processed_frames % 8 == 0:
                    denominator = max(1, math.ceil(frame_limit / sample_step))
                    progress_callback(min(0.98, processed_frames / denominator))

        capture.release()
        if writer is not None:
            writer.release()
        if processed_frames == 0 or writer is None:
            raise ValueError("분석할 수 있는 영상 장면이 없습니다.")
        if detected_frames < 5:
            raise ValueError(
                "사람의 전신 자세를 충분히 찾지 못했습니다. 밝은 장소에서 "
                "머리부터 발끝까지 나오도록 다시 촬영해 주세요."
            )

        active_denominator = max(1, active_frames)
        lean_issue_rate = 100 * lean_issue_frames / active_denominator
        balance_issue_rate = 100 * balance_issue_frames / active_denominator
        knee_issue_rate = 100 * knee_issue_frames / active_denominator
        detection_rate = 100 * detected_frames / max(1, processed_frames)
        minimum_knee_angle = (
            minimum_knee_angle if minimum_knee_angle < 180 else 180.0
        )

        depth_score = (
            100.0
            if minimum_knee_angle <= 110
            else max(35.0, 100.0 - (minimum_knee_angle - 110) * 2.0)
        )
        alignment_score = (
            100.0 if camera_view == "측면" else max(0.0, 100 - knee_issue_rate)
        )
        movement_score = round(max(
            0.0,
            min(
                100.0,
                depth_score * 0.35
                + max(0.0, 100 - lean_issue_rate) * 0.25
                + max(0.0, 100 - balance_issue_rate) * 0.25
                + alignment_score * 0.15,
            ),
        ))

        analyzed_video, video_mime = browser_friendly_video(
            raw_output_path, work_directory
        )
        result = {
            "reps": rep_count,
            "correct_reps": correct_reps,
            "score": movement_score,
            "minimum_knee_angle": round(minimum_knee_angle, 1),
            "detection_rate": round(detection_rate, 1),
            "lean_issue_rate": round(lean_issue_rate, 1),
            "balance_issue_rate": round(balance_issue_rate, 1),
            "knee_issue_rate": round(knee_issue_rate, 1),
            "time_values": time_values,
            "knee_values": knee_values,
            "left_knee_values": left_knee_values,
            "right_knee_values": right_knee_values,
            "lean_values": lean_values,
            "issue_events": issue_events,
            "lowest_pose_world": lowest_pose_world,
            "lowest_pose_normalized": lowest_pose_normalized,
            "video_bytes": analyzed_video,
            "video_mime": video_mime,
            "processed_seconds": round(min(frame_limit / fps, MAX_VIDEO_SECONDS), 1),
            "was_trimmed": total_frames > frame_limit > 0,
        }
        result["feedback"] = build_feedback(result, camera_view)
        if progress_callback:
            progress_callback(1.0)
        return result


def analyze_exercise_video(
    video_bytes, filename, camera_view, exercise, progress_callback=None
):
    """업로드 영상에서 선택 운동의 반복·유지 시간·자세를 분석합니다."""
    import cv2
    import mediapipe as mp

    model_path = ensure_pose_model()
    safe_suffix = Path(filename).suffix.lower()
    if safe_suffix not in (".mp4", ".mov", ".avi", ".m4v"):
        safe_suffix = ".mp4"

    movement_profiles = {
        "스쿼트": {"start": 145, "target": 110, "finish": 155},
        "런지": {"start": 135, "target": 110, "finish": 155},
        "팔굽혀펴기": {"start": 145, "target": 100, "finish": 155},
    }

    with tempfile.TemporaryDirectory(prefix="home_pose_") as work_directory:
        input_path = Path(work_directory) / f"input{safe_suffix}"
        raw_output_path = Path(work_directory) / "pose_analysis_raw.mp4"
        input_path.write_bytes(video_bytes)

        capture = cv2.VideoCapture(str(input_path))
        if not capture.isOpened():
            raise ValueError(
                "영상을 열 수 없습니다. 휴대폰에서 MP4(H.264) 형식으로 다시 저장해 주세요."
            )

        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 1:
            fps = 30.0
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_step = max(1, int(round(fps / TARGET_ANALYSIS_FPS)))
        output_fps = max(5.0, fps / sample_step)
        frame_limit = min(
            total_frames if total_frames > 0 else int(fps * MAX_VIDEO_SECONDS),
            int(fps * MAX_VIDEO_SECONDS),
        )

        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.55,
            min_pose_presence_confidence=0.55,
            min_tracking_confidence=0.55,
            output_segmentation_masks=False,
        )

        writer = None
        processed_frames = 0
        detected_frames = 0
        active_frames = 0
        posture_issue_frames = 0
        balance_issue_frames = 0
        alignment_issue_frames = 0
        frame_index = -1
        rep_count = 0
        correct_reps = 0
        phase = "closed" if exercise == "점핑잭" else "extended"
        active_rep = None
        current_good_hold = 0.0
        longest_good_hold = 0.0
        time_values = []
        primary_values = []
        primary_left_values = []
        primary_right_values = []
        issue_events = []
        last_issue_time = {}
        representative_pose_world = None
        representative_pose_normalized = None
        representative_value = None
        last_metrics = None
        last_timestamp = 0.0

        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        try:
            with PoseLandmarker.create_from_options(options) as landmarker:
                while True:
                    success, frame = capture.read()
                    if not success:
                        break
                    frame_index += 1
                    if frame_index >= frame_limit:
                        break
                    if frame_index % sample_step != 0:
                        continue

                    frame = resize_for_analysis(frame)
                    height, width = frame.shape[:2]
                    if writer is None:
                        codec = cv2.VideoWriter_fourcc(*"mp4v")
                        writer = cv2.VideoWriter(
                            str(raw_output_path), codec, output_fps, (width, height)
                        )
                        if not writer.isOpened():
                            raise RuntimeError("분석 영상을 만들 수 없습니다.")

                    timestamp = frame_index / fps
                    last_timestamp = timestamp
                    timestamp_ms = int(round(timestamp * 1000))
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB,
                        data=rgb_frame,
                    )
                    pose_result = landmarker.detect_for_video(
                        mp_image, timestamp_ms
                    )
                    processed_frames += 1

                    landmarks = (
                        pose_result.pose_landmarks[0]
                        if pose_result.pose_landmarks else None
                    )
                    world_landmarks = (
                        pose_result.pose_world_landmarks[0]
                        if pose_result.pose_world_landmarks else None
                    )
                    metrics = frame_metrics(
                        landmarks, width, height, camera_view, exercise
                    )
                    frame_issues = []

                    if metrics is not None:
                        last_metrics = metrics
                        detected_frames += 1
                        primary_value = metrics["primary_average"]
                        time_values.append(timestamp)
                        primary_values.append(primary_value)
                        primary_left_values.append(metrics["primary_left"])
                        primary_right_values.append(metrics["primary_right"])

                        choose_snapshot = representative_value is None
                        if exercise in ("점핑잭", "플랭크"):
                            choose_snapshot = (
                                choose_snapshot
                                or primary_value > representative_value
                            )
                        else:
                            choose_snapshot = (
                                choose_snapshot
                                or primary_value < representative_value
                            )
                        if choose_snapshot:
                            representative_value = primary_value
                            representative_pose_normalized = [
                                (
                                    float(item.x), float(item.y), float(item.z),
                                    float(getattr(item, "visibility", 1.0)),
                                )
                                for item in landmarks
                            ]
                            if world_landmarks:
                                representative_pose_world = [
                                    (
                                        float(item.x), float(item.y), float(item.z),
                                        float(getattr(item, "visibility", 1.0)),
                                    )
                                    for item in world_landmarks
                                ]

                        if metrics["active"]:
                            active_frames += 1
                            issue_codes = {
                                code for code, _ in metrics["issues"]
                            }
                            posture_issue_frames += int("posture" in issue_codes)
                            balance_issue_frames += int("balance" in issue_codes)
                            alignment_issue_frames += int("alignment" in issue_codes)

                        frame_issues = metrics["issues"]
                        for code, label in frame_issues:
                            record_issue(
                                issue_events, last_issue_time,
                                code, label, timestamp,
                            )

                        if exercise in movement_profiles:
                            profile = movement_profiles[exercise]
                            if (
                                phase == "extended"
                                and primary_value < profile["start"]
                            ):
                                phase = "flexed"
                                active_rep = {
                                    "reached_target": (
                                        primary_value <= profile["target"]
                                    ),
                                    "bad_frames": int(bool(frame_issues)),
                                    "frames": 1,
                                }
                            elif phase == "flexed" and active_rep is not None:
                                active_rep["reached_target"] = (
                                    active_rep["reached_target"]
                                    or primary_value <= profile["target"]
                                )
                                active_rep["bad_frames"] += int(bool(frame_issues))
                                active_rep["frames"] += 1
                                if primary_value > profile["finish"]:
                                    rep_count += 1
                                    bad_ratio = (
                                        active_rep["bad_frames"]
                                        / max(1, active_rep["frames"])
                                    )
                                    if (
                                        active_rep["reached_target"]
                                        and bad_ratio <= 0.25
                                    ):
                                        correct_reps += 1
                                    phase = "extended"
                                    active_rep = None
                        elif exercise == "점핑잭":
                            if phase == "closed" and metrics["open_position"]:
                                phase = "open"
                                active_rep = {
                                    "bad_frames": int(bool(frame_issues)),
                                    "frames": 1,
                                }
                            elif phase == "open" and active_rep is not None:
                                active_rep["bad_frames"] += int(bool(frame_issues))
                                active_rep["frames"] += 1
                                if metrics["closed_position"]:
                                    rep_count += 1
                                    bad_ratio = (
                                        active_rep["bad_frames"]
                                        / max(1, active_rep["frames"])
                                    )
                                    if bad_ratio <= 0.25:
                                        correct_reps += 1
                                    phase = "closed"
                                    active_rep = None
                        else:  # 플랭크
                            frame_seconds = sample_step / fps
                            if metrics["quality_good"]:
                                current_good_hold += frame_seconds
                                longest_good_hold = max(
                                    longest_good_hold, current_good_hold
                                )
                            else:
                                current_good_hold = 0.0

                        skeleton_color = (
                            (55, 85, 245) if frame_issues else (65, 210, 115)
                        )
                        draw_pose(
                            frame, landmarks, POSE_CONNECTIONS, skeleton_color
                        )

                    draw_frame_information(
                        frame, exercise, rep_count, longest_good_hold,
                        metrics, frame_issues,
                    )
                    writer.write(frame)

                    if progress_callback and processed_frames % 8 == 0:
                        denominator = max(
                            1, math.ceil(frame_limit / sample_step)
                        )
                        progress_callback(
                            min(0.98, processed_frames / denominator)
                        )
        finally:
            capture.release()
            if writer is not None:
                writer.release()

        if processed_frames == 0 or writer is None:
            raise ValueError("분석할 수 있는 영상 장면이 없습니다.")
        if detected_frames < 5 or last_metrics is None:
            raise ValueError(
                "사람의 전신 자세를 충분히 찾지 못했습니다. 밝은 장소에서 "
                "머리부터 발끝까지 나오도록 다시 촬영해 주세요."
            )

        active_denominator = max(1, active_frames)
        posture_issue_rate = 100 * posture_issue_frames / active_denominator
        balance_issue_rate = 100 * balance_issue_frames / active_denominator
        alignment_issue_rate = 100 * alignment_issue_frames / active_denominator
        detection_rate = 100 * detected_frames / max(1, processed_frames)
        primary_minimum = min(primary_values)
        primary_maximum = max(primary_values)

        if exercise in movement_profiles:
            target = movement_profiles[exercise]["target"]
            range_score = (
                100.0 if primary_minimum <= target
                else max(35.0, 100.0 - (primary_minimum - target) * 2.0)
            )
        elif exercise == "플랭크":
            range_score = min(100.0, longest_good_hold / 15.0 * 100)
        else:
            range_score = min(
                100.0, max(30.0, primary_maximum / 150.0 * 100)
            )

        movement_score = round(max(
            0.0,
            min(
                100.0,
                range_score * 0.40
                + max(0.0, 100 - posture_issue_rate) * 0.30
                + max(0.0, 100 - balance_issue_rate) * 0.20
                + max(0.0, 100 - alignment_issue_rate) * 0.10,
            ),
        ))

        analyzed_video, video_mime = browser_friendly_video(
            raw_output_path, work_directory
        )
        result = {
            "exercise": exercise,
            "reps": rep_count,
            "correct_reps": correct_reps,
            "hold_seconds": round(longest_good_hold, 1),
            "score": movement_score,
            "primary_min": round(primary_minimum, 1),
            "primary_max": round(primary_maximum, 1),
            "primary_label": last_metrics["primary_label"],
            "left_label": last_metrics["left_label"],
            "right_label": last_metrics["right_label"],
            "detection_rate": round(detection_rate, 1),
            "posture_issue_rate": round(posture_issue_rate, 1),
            "balance_issue_rate": round(balance_issue_rate, 1),
            "alignment_issue_rate": round(alignment_issue_rate, 1),
            "time_values": time_values,
            "primary_values": primary_values,
            "primary_left_values": primary_left_values,
            "primary_right_values": primary_right_values,
            "issue_events": issue_events,
            "representative_pose_world": representative_pose_world,
            "representative_pose_normalized": representative_pose_normalized,
            "video_bytes": analyzed_video,
            "video_mime": video_mime,
            "processed_seconds": round(
                min(last_timestamp, MAX_VIDEO_SECONDS), 1
            ),
            "was_trimmed": total_frames > frame_limit > 0,
        }
        result["feedback"] = build_feedback(result, camera_view)
        if progress_callback:
            progress_callback(1.0)
        return result


def make_angle_chart(result):
    """시간에 따른 선택 운동의 양쪽 핵심 각도를 표시합니다."""
    import plotly.graph_objects as go

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=result["time_values"],
        y=result["primary_left_values"],
        mode="lines",
        name=result["left_label"],
        line=dict(color="#2563EB", width=3),
    ))
    figure.add_trace(go.Scatter(
        x=result["time_values"],
        y=result["primary_right_values"],
        mode="lines",
        name=result["right_label"],
        line=dict(color="#F97316", width=3),
    ))
    threshold_lines = {
        "스쿼트": ((110, "#16A34A", "충분히 앉기 110°"),
                 (155, "#64748B", "완전히 서기 155°")),
        "런지": ((110, "#16A34A", "충분히 굽히기 110°"),
                (155, "#64748B", "다시 서기 155°")),
        "팔굽혀펴기": ((100, "#16A34A", "충분히 굽히기 100°"),
                    (155, "#64748B", "팔 펴기 155°")),
        "플랭크": ((160, "#16A34A", "몸 일직선 160°"),),
        "점핑잭": ((55, "#64748B", "팔 내림 55°"),
                  (140, "#16A34A", "팔 올림 140°")),
    }[result["exercise"]]
    for index, (value, color, label) in enumerate(threshold_lines):
        figure.add_hline(
            y=value,
            line_dash="dot",
            line_color=color,
            annotation_text=label,
            annotation_position="bottom right" if index == 0 else "top right",
        )
    figure.update_layout(
        height=292,
        margin=dict(l=42, r=10, t=12, b=40),
        xaxis_title="시간(초)",
        yaxis_title=f"{result['primary_label']}(°)",
        yaxis=dict(range=[0, 190]),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F8FAFC",
        font=dict(color="#172554", size=12),
    )
    return figure


def pose_points_for_chart(result):
    """월드 좌표를 우선 사용하고 없으면 영상 좌표로 3D 골격을 만듭니다."""
    if result["representative_pose_world"]:
        source = result["representative_pose_world"]
        return [
            (item[0], item[2], -item[1], item[3])
            for item in source
        ]
    source = result["representative_pose_normalized"]
    return [
        (item[0] - 0.5, item[2], 1.0 - item[1], item[3])
        for item in source
    ]


def make_pose_3d(result):
    """선택 운동의 대표 순간을 회전 가능한 3D 골격으로 보여 줍니다."""
    import plotly.graph_objects as go

    points = pose_points_for_chart(result)
    line_x, line_y, line_z = [], [], []
    for start, end in POSE_CONNECTIONS:
        line_x.extend((points[start][0], points[end][0], None))
        line_y.extend((points[start][1], points[end][1], None))
        line_z.extend((points[start][2], points[end][2], None))

    figure = go.Figure()
    figure.add_trace(go.Scatter3d(
        x=line_x, y=line_y, z=line_z,
        mode="lines",
        line=dict(color="#2563EB", width=9),
        hoverinfo="skip",
        showlegend=False,
    ))
    visible_indices = sorted(set(
        index for connection in POSE_CONNECTIONS for index in connection
    ))
    figure.add_trace(go.Scatter3d(
        x=[points[index][0] for index in visible_indices],
        y=[points[index][1] for index in visible_indices],
        z=[points[index][2] for index in visible_indices],
        mode="markers",
        marker=dict(
            size=6, color="#F97316",
            line=dict(color="#FFFFFF", width=2),
        ),
        hovertext=[
            f"신체 지점 {index}" for index in visible_indices
        ],
        hoverinfo="text",
        showlegend=False,
    ))

    label_indices = (11, 23, 25, 27)
    label_text = ("어깨", "골반", "무릎", "발목")
    figure.add_trace(go.Scatter3d(
        x=[points[index][0] for index in label_indices],
        y=[points[index][1] for index in label_indices],
        z=[points[index][2] for index in label_indices],
        mode="text",
        text=[f"<b>{text}</b>" for text in label_text],
        textposition="top center",
        textfont=dict(size=13, color="#172554"),
        hoverinfo="skip",
        showlegend=False,
    ))
    figure.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=4, b=0),
        scene=dict(
            aspectmode="data",
            camera=dict(eye=dict(x=1.35, y=1.65, z=1.15)),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        uirevision=f"{result['exercise']}-pose-camera",
    )
    return figure


def result_summary_html(result):
    if result["exercise"] == "플랭크":
        cards = (
            ("바른 자세 유지", f'{result["hold_seconds"]:.1f}초'),
            ("분석 시간", f'{result["processed_seconds"]:.0f}초'),
            ("연습 점수", f'{result["score"]}점'),
            ("최소 몸통각", f'{result["primary_min"]:.0f}°'),
        )
    else:
        value_label = (
            "최대 팔 올림" if result["exercise"] == "점핑잭"
            else f'최저 {result["primary_label"]}'
        )
        value = (
            result["primary_max"] if result["exercise"] == "점핑잭"
            else result["primary_min"]
        )
        cards = (
            ("전체 반복", f'{result["reps"]}회'),
            ("바른 반복", f'{result["correct_reps"]}회'),
            ("연습 점수", f'{result["score"]}점'),
            (value_label, f"{value:.0f}°"),
        )
    items = "".join(
        f'<div class="result-item"><span>{label}</span><strong>{value}</strong></div>'
        for label, value in cards
    )
    return f"""
<div class="result-grid">
  {items}
</div>
"""


def format_timestamp(seconds):
    minute = int(seconds // 60)
    second = int(seconds % 60)
    return f"{minute:02d}:{second:02d}"


def main():
    import streamlit as st

    st.set_page_config(
        page_title="틈새 공부 · AI 홈트레이닝 자세 분석",
        page_icon="🏠",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
<style>
  [data-testid="stHeader"], [data-testid="stToolbar"],
  [data-testid="stDecoration"], #MainMenu, footer {display:none !important;}
  .block-container {max-width:470px; padding:0.16rem 0.34rem 0.55rem !important;}
  [data-testid="stVerticalBlock"] {gap:0.36rem !important;}
  .pose-brand {color:#172554; font-size:1.12rem; font-weight:800;
               text-align:center; line-height:1.18;}
  .pose-topic {color:#2563EB; font-size:0.86rem; font-weight:750;
               text-align:center;}
  .guide {background:#E8F2FF; color:#174A7C; border-radius:0.62rem;
          padding:0.48rem 0.58rem; font-size:0.80rem; line-height:1.42;
          font-weight:650;}
  .privacy {background:#FFF7D6; color:#713F12; border-radius:0.60rem;
            padding:0.42rem 0.52rem; font-size:0.76rem; line-height:1.38;}
  .result-grid {display:grid; grid-template-columns:repeat(4, 1fr);
                gap:0.32rem; margin:0.14rem 0;}
  .result-item {background:#F1F5F9; border-radius:0.60rem;
                padding:0.44rem 0.18rem; text-align:center;}
  .result-item span {display:block; color:#475569; font-size:0.70rem;
                     font-weight:650;}
  .result-item strong {display:block; color:#172554; font-size:1.02rem;
                       margin-top:0.12rem;}
  .feedback {background:#E7F8EE; color:#166534; border-radius:0.60rem;
             padding:0.44rem 0.54rem; font-size:0.80rem; line-height:1.42;
             font-weight:650;}
  div[data-testid="stButton"] button,
  div[data-testid="stDownloadButton"] button {
      min-height:2.58rem !important; font-weight:750 !important;
      font-size:0.84rem !important;
  }
  @media (max-width:380px) {
    .block-container {padding:0.10rem 0.20rem 0.40rem !important;}
    .result-grid {grid-template-columns:repeat(2, 1fr);}
    .pose-brand {font-size:1.04rem;}
  }
</style>
<div class="pose-brand">🏠 틈새 공부 AI 홈트레이닝</div>
<div class="pose-topic">휴대폰 영상으로 다섯 가지 운동 자세를 분석해요</div>
""", unsafe_allow_html=True)

    st.markdown(
        '<div class="guide">① 운동을 고르세요.<br>'
        '② 전신이 보이는 45초 이하 영상을 올리세요.<br>'
        '③ AI가 반복 횟수·유지 시간·관절 각도를 알려 줍니다.</div>',
        unsafe_allow_html=True,
    )

    exercise = st.selectbox("분석할 운동", EXERCISES)
    st.caption(f"촬영 도움말 · {EXERCISE_GUIDE[exercise]}")
    camera_view = st.radio(
        "촬영 방향",
        ("측면", "정면"),
        horizontal=True,
        help="측면은 무릎 각도와 상체 기울기, 정면은 좌우 균형과 무릎 정렬 분석에 좋습니다.",
    )
    if exercise in ("팔굽혀펴기", "플랭크") and camera_view != "측면":
        st.info("이 운동은 몸의 일직선을 보기 쉬운 측면 촬영을 권장합니다.")
    elif exercise == "점핑잭" and camera_view != "정면":
        st.info("점핑잭은 팔과 다리의 좌우 움직임이 보이는 정면 촬영을 권장합니다.")
    uploaded_video = st.file_uploader(
        f"📹 {exercise} 영상 올리기",
        type=("mp4", "mov", "avi", "m4v"),
        help="MP4(H.264) 형식을 권장합니다.",
    )

    session_defaults = {
        "pose_analysis_result": None,
        "pose_upload_digest": "",
        "pose_analysis_view": "",
        "pose_analysis_exercise": "",
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if uploaded_video is not None:
        video_bytes = uploaded_video.getvalue()
        digest = hashlib.sha256(video_bytes).hexdigest()
        if (
            digest != st.session_state.pose_upload_digest
            or camera_view != st.session_state.pose_analysis_view
            or exercise != st.session_state.pose_analysis_exercise
        ):
            st.session_state.pose_analysis_result = None
            st.session_state.pose_upload_digest = digest
            st.session_state.pose_analysis_view = camera_view
            st.session_state.pose_analysis_exercise = exercise

        file_size_mb = len(video_bytes) / (1024 * 1024)
        st.caption(f"선택한 영상: {uploaded_video.name} · {file_size_mb:.1f} MB")
        st.video(video_bytes)

        python_supported = sys.version_info < (3, 13)
        if not python_supported:
            st.error(
                f"현재 Python {sys.version_info.major}.{sys.version_info.minor}에서는 "
                "MediaPipe 설치가 지원되지 않습니다. Python 3.12 환경에서 실행해 주세요."
            )
        if file_size_mb > MAX_UPLOAD_MB:
            st.error(f"영상은 {MAX_UPLOAD_MB}MB 이하로 줄여 주세요.")

        analyze_button = st.button(
            "🔍 AI 자세 분석 시작",
            type="primary",
            width="stretch",
            disabled=(not python_supported or file_size_mb > MAX_UPLOAD_MB),
        )
        if analyze_button:
            progress = st.progress(0)
            status = st.empty()
            status.info(
                f"AI가 {exercise} 영상에서 관절을 찾고 있습니다. 잠시 기다려 주세요."
            )

            def update_progress(value):
                progress.progress(float(max(0.0, min(1.0, value))))

            try:
                result = analyze_exercise_video(
                    video_bytes,
                    uploaded_video.name,
                    camera_view,
                    exercise,
                    progress_callback=update_progress,
                )
                st.session_state.pose_analysis_result = result
                status.success(f"{exercise} 자세 분석이 완료되었습니다.")
            except Exception as error:
                st.session_state.pose_analysis_result = None
                status.error(str(error))
                with st.expander("오류 상세 보기"):
                    st.exception(error)
            finally:
                progress.empty()
    else:
        st.info(f"휴대폰으로 촬영한 {exercise} 영상을 먼저 올려 주세요.")

    result = st.session_state.pose_analysis_result
    if result:
        st.markdown(f"#### 📊 {result['exercise']} 분석 결과")
        st.markdown(result_summary_html(result), unsafe_allow_html=True)
        st.caption(
            f"관절 인식률 {result['detection_rate']:.0f}% · "
            f"분석 구간 {result['processed_seconds']:.0f}초"
        )
        if result["was_trimmed"]:
            st.warning(
                f"휴대폰에서 빠르게 분석하기 위해 처음 {MAX_VIDEO_SECONDS}초만 분석했습니다."
            )

        for message in result["feedback"]:
            st.markdown(
                f'<div class="feedback">⭐ {message}</div>',
                unsafe_allow_html=True,
            )

        if result["issue_events"]:
            with st.expander("⏱ 자세를 다시 확인할 시간"):
                for event in result["issue_events"]:
                    st.write(
                        f"• {format_timestamp(event['time'])} · {event['label']} 확인"
                    )

        st.markdown("#### 🎬 관절 표시 분석 영상")
        st.video(result["video_bytes"], format=result["video_mime"])
        st.download_button(
            "⬇ 분석 영상 저장",
            data=result["video_bytes"],
            file_name=(
                f"{EXERCISE_FILE_CODE[result['exercise']]}_pose_analysis.mp4"
            ),
            mime=result["video_mime"],
            width="stretch",
        )

        with st.expander(
            f"📈 시간에 따른 {result['primary_label']}", expanded=True
        ):
            st.plotly_chart(
                make_angle_chart(result),
                width="stretch",
                config={"displayModeBar":False, "responsive":True},
            )

        with st.expander("🧍 대표 자세를 3D로 보기", expanded=True):
            st.plotly_chart(
                make_pose_3d(result),
                width="stretch",
                config={
                    "displayModeBar":False,
                    "scrollZoom":True,
                    "responsive":True,
                },
                key=f"{EXERCISE_FILE_CODE[result['exercise']]}_pose_3d",
            )
            st.caption("한 손가락으로 회전하고 두 손가락으로 확대·축소할 수 있습니다.")

    st.markdown(
        '<div class="privacy">🔒 개인정보 안내: 업로드한 영상은 분석을 위해 '
        'Streamlit 서버로 전송됩니다. 이 프로그램에는 영상을 영구 저장하는 '
        '기능이 없지만, 학생 영상은 반드시 사전 동의를 받고 얼굴과 이름이 '
        '드러나지 않게 촬영하세요.<br><br>⚠ 이 결과는 운동 학습용 참고 자료이며 '
        '의료 진단이나 치료 지침이 아닙니다. 통증이 있으면 운동을 중단하세요.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
