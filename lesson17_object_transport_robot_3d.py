"""틈새 공부 Python 교실 ⑰: 물건을 옮기는 3D 휴머노이드.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly streamlit-mic-recorder
실행: python -m streamlit run lesson17_object_transport_robot_3d.py

처음에는 로봇이 상자를 발견하고, 잡고, 운반하고, 내려놓는 과정이
동영상처럼 자동으로 진행됩니다. 화면을 멈추면 버튼이나 한국어 음성으로
각 작업을 직접 명령할 수 있습니다.
"""

from math import cos, pi, radians, sin, sqrt

import lesson16_robot_simulator_3d as robot_parts


PICKUP_POINT = (-3.0, -1.65)
DROP_POINT = (3.1, -1.65)
PICKUP_STANCE = (-3.0, -0.82, -90)
DROP_STANCE = (3.1, -0.82, -90)
FIELD_LIMIT = 4.65
MOVE_DISTANCE = 0.52
TURN_ANGLE = 45

# x, y, 방향, 단계 제목, 쉬운 설명, 작업 상태
AUTO_SCENES = (
    (-4.1, 1.55, -45, "작업 시작", "휴머노이드가 옮길 상자와 초록색 도착 구역을 확인합니다.", "search"),
    (-3.65, 0.65, -65, "상자 찾기", "가슴 센서가 파란 상자의 위치와 거리를 측정합니다.", "search"),
    (-3.0, -0.25, -90, "상자에 접근", "부딪히지 않도록 상자 앞까지 천천히 걸어갑니다.", "approach"),
    (-3.0, -0.82, -90, "두 손 뻗기", "두 손을 상자 양옆으로 뻗고 잡을 준비를 합니다.", "reach"),
    (-3.0, -0.82, -90, "상자 들어 올리기", "두 손으로 상자를 잡아 몸 가까이 들어 올립니다.", "carry"),
    (-2.2, -0.82, 0, "몸 돌리기", "상자를 놓치지 않도록 몸과 발을 이동 방향으로 돌립니다.", "carry"),
    (-0.7, -0.82, 0, "균형 잡고 운반", "상자를 몸 가까이 잡고 작은 걸음으로 이동합니다.", "transport"),
    (1.0, -0.82, 0, "목표로 이동", "센서로 앞길을 확인하며 초록색 구역으로 갑니다.", "transport"),
    (2.45, -0.82, 0, "도착 구역 접근", "목표 가까이에서 속도를 줄이고 멈출 준비를 합니다.", "transport"),
    (3.1, -0.82, -90, "내려놓을 방향 맞추기", "초록색 구역을 바라보도록 몸을 돌립니다.", "carry"),
    (3.1, -0.82, -90, "상자 천천히 내리기", "허리를 갑자기 굽히지 않고 두 손으로 상자를 내립니다.", "lower"),
    (3.1, -0.82, -90, "운반 성공!", "상자를 목표 구역에 내려놓고 두 손을 놓았습니다.", "done"),
)


def rotate_point(local_x, local_y, center_x, center_y, heading):
    """로봇을 기준으로 한 좌표를 진행 방향에 맞게 회전합니다."""
    angle = radians(heading)
    return (
        center_x + local_x * cos(angle) - local_y * sin(angle),
        center_y + local_x * sin(angle) + local_y * cos(angle),
    )


def add_zone(figure, center, radius, color, label):
    """상자를 놓는 원형 구역을 바닥에 표시합니다."""
    import plotly.graph_objects as go

    center_x, center_y = center
    angles = [2 * pi * index / 48 for index in range(49)]
    figure.add_trace(go.Scatter3d(
        x=[center_x + radius * cos(angle) for angle in angles],
        y=[center_y + radius * sin(angle) for angle in angles],
        z=[0.035] * len(angles),
        mode="lines",
        line=dict(color=color, width=10),
        hoverinfo="skip",
        showlegend=False,
    ))
    figure.add_trace(go.Scatter3d(
        x=[center_x], y=[center_y], z=[0.075],
        mode="text", text=[f"<b>{label}</b>"],
        textfont=dict(size=15, color=color),
        hoverinfo="skip", showlegend=False,
    ))


def hand_positions(x, y, heading, arm_pose):
    """팔 동작에 따라 두 손의 3D 위치를 계산합니다."""
    if arm_pose == "reach":
        hand_local_x, hand_local_y, hand_z = 0.66, 0.38, 0.61
    elif arm_pose == "lower":
        hand_local_x, hand_local_y, hand_z = 0.64, 0.37, 0.62
    elif arm_pose == "carry":
        hand_local_x, hand_local_y, hand_z = 0.58, 0.38, 1.08
    else:
        hand_local_x, hand_local_y, hand_z = 0.02, 0.57, 0.92

    positions = []
    for side in (-1, 1):
        hand_x, hand_y = rotate_point(
            hand_local_x, side * hand_local_y, x, y, heading
        )
        positions.append((hand_x, hand_y, hand_z))
    return positions


def add_transport_robot(figure, x, y, heading, arm_pose="idle"):
    """상자를 잡는 팔 동작이 가능한 가벼운 3D 휴머노이드를 그립니다."""
    import plotly.graph_objects as go

    # 몸통·허리·머리·얼굴
    robot_parts.add_box(
        figure, (x, y, 1.33), (0.50, 0.82, 0.70),
        "#2563EB", heading=heading, name="몸통",
    )
    robot_parts.add_box(
        figure, (x, y, 0.93), (0.46, 0.62, 0.24),
        "#1D4ED8", heading=heading, name="허리",
    )
    robot_parts.add_box(
        figure, (x, y, 1.70), (0.24, 0.28, 0.22),
        "#64748B", heading=heading, name="목",
    )
    robot_parts.add_sphere(
        figure, (x, y, 2.02), 0.35, "#DCEEFF", name="머리"
    )
    face_x, face_y = rotate_point(0.31, 0, x, y, heading)
    robot_parts.add_box(
        figure, (face_x, face_y, 2.02), (0.055, 0.42, 0.18),
        "#172554", heading=heading, name="얼굴 화면",
    )

    # 눈과 가슴 센서
    eye_x = []
    eye_y = []
    for side in (-1, 1):
        point_x, point_y = rotate_point(0.345, side * 0.13, x, y, heading)
        eye_x.append(point_x)
        eye_y.append(point_y)
    sensor_x, sensor_y = rotate_point(0.30, 0, x, y, heading)
    figure.add_trace(go.Scatter3d(
        x=eye_x + [sensor_x],
        y=eye_y + [sensor_y],
        z=[2.04, 2.04, 1.36],
        mode="markers",
        marker=dict(size=[6, 6, 10], color=["#67E8F9", "#67E8F9", "#22D3EE"]),
        hoverinfo="skip", showlegend=False,
    ))

    # 다리와 발
    for side in (-1, 1):
        leg_x, leg_y = rotate_point(0, side * 0.22, x, y, heading)
        foot_x, foot_y = rotate_point(0.15, side * 0.22, x, y, heading)
        robot_parts.add_box(
            figure, (leg_x, leg_y, 0.56), (0.27, 0.29, 0.68),
            "#3B82F6", heading=heading, name="다리",
        )
        robot_parts.add_box(
            figure, (foot_x, foot_y, 0.15), (0.56, 0.32, 0.22),
            "#172554", heading=heading, name="발",
        )

    # 어깨에서 손까지 이어지는 두 팔
    hands = hand_positions(x, y, heading, arm_pose)
    for side, hand in zip((-1, 1), hands):
        shoulder_x, shoulder_y = rotate_point(0, side * 0.52, x, y, heading)
        elbow_local_x = 0.35 if arm_pose in ("reach", "lower", "carry") else 0.0
        elbow_local_y = side * (0.48 if arm_pose in ("reach", "lower", "carry") else 0.57)
        elbow_z = 1.29 if arm_pose == "carry" else 1.18
        elbow_x, elbow_y = rotate_point(elbow_local_x, elbow_local_y, x, y, heading)
        figure.add_trace(go.Scatter3d(
            x=[shoulder_x, elbow_x, hand[0]],
            y=[shoulder_y, elbow_y, hand[1]],
            z=[1.55, elbow_z, hand[2]],
            mode="lines+markers",
            line=dict(color="#60A5FA", width=18),
            marker=dict(size=[8, 7, 8], color="#DCEEFF"),
            hoverinfo="skip", showlegend=False,
        ))

    figure.add_trace(go.Scatter3d(
        x=[x], y=[y], z=[2.52], mode="text",
        text=["<b>운반 로봇</b>"],
        textfont=dict(size=15, color="#0F172A"),
        hoverinfo="skip", showlegend=False,
    ))


def carried_box_center(x, y, heading, stage):
    """상자를 들고 있을 때 손 사이의 상자 중심을 반환합니다."""
    if stage == "lower":
        local_x, box_z = 0.72, 0.43
    else:
        local_x, box_z = 0.72, 1.02
    box_x, box_y = rotate_point(local_x, 0, x, y, heading)
    return box_x, box_y, box_z


def box_center_for_stage(x, y, heading, stage):
    """작업 단계에 맞는 상자 위치를 계산합니다."""
    if stage in ("carry", "transport", "lower"):
        return carried_box_center(x, y, heading, stage)
    if stage == "done":
        return DROP_POINT[0], DROP_POINT[1], 0.36
    return PICKUP_POINT[0], PICKUP_POINT[1], 0.36


def make_figure(x, y, heading, stage, trail, height=390):
    """현재 운반 작업을 한 화면에 보여 주는 3D 그림을 만듭니다."""
    import plotly.graph_objects as go

    figure = go.Figure()
    robot_parts.add_floor(figure)
    add_zone(figure, PICKUP_POINT, 0.62, "#2563EB", "상자 위치")
    add_zone(figure, DROP_POINT, 0.72, "#16A34A", "도착 구역")

    if trail:
        figure.add_trace(go.Scatter3d(
            x=[point[0] for point in trail],
            y=[point[1] for point in trail],
            z=[0.07] * len(trail),
            mode="lines+markers",
            line=dict(color="#7C3AED", width=7),
            marker=dict(size=4, color="#6D28D9"),
            hoverinfo="skip", showlegend=False,
        ))

    arm_pose = "idle"
    if stage == "reach":
        arm_pose = "reach"
    elif stage in ("carry", "transport"):
        arm_pose = "carry"
    elif stage == "lower":
        arm_pose = "lower"
    add_transport_robot(figure, x, y, heading, arm_pose)

    box_x, box_y, box_z = box_center_for_stage(x, y, heading, stage)
    box_color = "#22C55E" if stage == "done" else "#F59E0B"
    robot_parts.add_box(
        figure, (box_x, box_y, box_z), (0.68, 0.68, 0.68),
        box_color, opacity=0.98, heading=heading if stage in ("carry", "transport", "lower") else 0,
        name="운반 상자",
    )
    figure.add_trace(go.Scatter3d(
        x=[box_x], y=[box_y], z=[box_z + 0.46], mode="text",
        text=["<b>상자</b>"], textfont=dict(size=14, color="#78350F"),
        hoverinfo="skip", showlegend=False,
    ))

    figure.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=4, b=0),
        showlegend=False,
        scene=dict(
            camera=dict(
                eye=dict(x=1.30, y=1.60, z=1.42),
                projection=dict(type="orthographic"),
            ),
            aspectmode="manual",
            aspectratio=dict(x=1.30, y=1.0, z=0.58),
            xaxis=dict(range=[-5.1, 5.1], visible=False),
            yaxis=dict(range=[-4.1, 4.1], visible=False),
            zaxis=dict(range=[0, 2.85], visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        uirevision="transport-camera",
    )
    return figure


def stage_status(stage):
    """학생이 바로 이해할 수 있는 상자 상태를 반환합니다."""
    if stage in ("carry", "transport", "lower"):
        return "📦 상자 상태: 두 손으로 잡고 운반 중"
    if stage == "done":
        return "✅ 상자 상태: 도착 구역에 안전하게 내려놓음"
    return "🔎 상자 상태: 바닥에 있음"


def initialize_state(st):
    """운반 로봇의 세션 상태를 준비합니다."""
    defaults = {
        "transport_auto_index": 0,
        "transport_x": AUTO_SCENES[0][0],
        "transport_y": AUTO_SCENES[0][1],
        "transport_heading": AUTO_SCENES[0][2],
        "transport_stage": AUTO_SCENES[0][5],
        "transport_trail": [(AUTO_SCENES[0][0], AUTO_SCENES[0][1])],
        "transport_message": "자동 운반 작업을 시작합니다.",
        "transport_last_voice": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_transport(state):
    """로봇과 상자를 작업 시작 위치로 되돌립니다."""
    state["transport_auto_index"] = 0
    state["transport_x"] = AUTO_SCENES[0][0]
    state["transport_y"] = AUTO_SCENES[0][1]
    state["transport_heading"] = AUTO_SCENES[0][2]
    state["transport_stage"] = "search"
    state["transport_trail"] = [(AUTO_SCENES[0][0], AUTO_SCENES[0][1])]
    state["transport_message"] = "로봇과 상자를 처음 위치로 되돌렸습니다."


def distance(point_a, point_b):
    return sqrt((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2)


def walk_transport_robot(state, step_distance):
    """현재 바라보는 방향으로 한 걸음 이동합니다."""
    heading = int(state["transport_heading"])
    angle = radians(heading)
    next_x = float(state["transport_x"]) + step_distance * cos(angle)
    next_y = float(state["transport_y"]) + step_distance * sin(angle)

    if abs(next_x) > FIELD_LIMIT or abs(next_y) > FIELD_LIMIT - 0.7:
        state["transport_message"] = "운동장 밖으로 나갈 수 없어 멈췄습니다."
        return False

    stage = state["transport_stage"]
    carrying = stage in ("carry", "transport", "lower")
    if not carrying and stage != "done" and distance((next_x, next_y), PICKUP_POINT) < 0.72:
        state["transport_message"] = "상자와 부딪히기 전에 멈췄습니다. 이제 ‘물건 집기’를 눌러 보세요."
        return False

    state["transport_x"] = next_x
    state["transport_y"] = next_y
    state["transport_trail"].append((next_x, next_y))
    if carrying:
        state["transport_stage"] = "transport"
        state["transport_message"] = "상자를 몸 가까이 잡고 한 걸음 이동했습니다."
    else:
        state["transport_message"] = "바라보는 방향으로 한 걸음 이동했습니다."
    return True


def turn_transport_robot(state, turn_angle):
    """제자리에서 왼쪽 또는 오른쪽으로 방향을 바꿉니다."""
    state["transport_heading"] = (int(state["transport_heading"]) + turn_angle) % 360
    direction = "왼쪽" if turn_angle > 0 else "오른쪽"
    state["transport_message"] = f"제자리에서 {direction}으로 {abs(turn_angle)}° 방향을 바꿨습니다."


def perform_transport_action(state, action, spoken_text=None):
    """버튼 또는 음성으로 요청한 운반 동작을 안전한 순서로 실행합니다."""
    prefix = f'🎤 “{spoken_text}” → ' if spoken_text else ""
    stage = state["transport_stage"]

    if action == "reset":
        reset_transport(state)
        if spoken_text:
            state["transport_message"] = prefix + "처음 위치로 돌아왔습니다."
        return True
    if action == "stop":
        state["transport_message"] = prefix + "그 자리에서 작업을 멈췄습니다."
        return True
    if action == "approach":
        state["transport_x"], state["transport_y"], state["transport_heading"] = PICKUP_STANCE
        state["transport_stage"] = "approach"
        state["transport_trail"].append(PICKUP_STANCE[:2])
        state["transport_message"] = prefix + "상자 앞까지 안전하게 이동했습니다."
        return True
    if action == "grab":
        robot_point = (state["transport_x"], state["transport_y"])
        if distance(robot_point, PICKUP_POINT) > 1.18:
            state["transport_message"] = prefix + "먼저 ‘상자로 가’를 명령해 주세요."
            return False
        state["transport_stage"] = "carry"
        state["transport_message"] = prefix + "두 손으로 상자를 잡아 들어 올렸습니다."
        return True
    if action == "transport":
        if stage not in ("carry", "transport"):
            state["transport_message"] = prefix + "먼저 상자를 잡아야 합니다."
            return False
        state["transport_x"], state["transport_y"], state["transport_heading"] = DROP_STANCE
        state["transport_stage"] = "transport"
        state["transport_trail"].append(DROP_STANCE[:2])
        state["transport_message"] = prefix + "상자를 들고 도착 구역까지 이동했습니다."
        return True
    if action == "drop":
        robot_point = (state["transport_x"], state["transport_y"])
        if stage not in ("carry", "transport", "lower"):
            state["transport_message"] = prefix + "현재 들고 있는 상자가 없습니다."
            return False
        if distance(robot_point, DROP_POINT) > 1.18:
            state["transport_message"] = prefix + "먼저 ‘목표로 옮겨’를 명령해 주세요."
            return False
        state["transport_stage"] = "done"
        state["transport_message"] = prefix + "상자를 목표 구역에 안전하게 내려놓았습니다."
        return True
    return False


def interpret_voice_command(spoken_text):
    """한국어 문장에서 물건 운반 명령을 찾습니다."""
    normalized = str(spoken_text).lower().replace(" ", "")
    command_words = (
        ("reset", ("처음으로", "처음", "리셋", "원위치")),
        ("stop", ("멈춰", "정지", "스톱")),
        ("drop", ("내려놓", "놓아", "내려")),
        ("grab", ("잡아", "잡기", "들어", "집어")),
        ("transport", ("목표로", "운반", "옮겨", "도착")),
        ("approach", ("상자로", "상자에", "물건으로", "물건에", "가까이")),
    )
    for command, words in command_words:
        if any(word in normalized for word in words):
            return command
    return None


def execute_voice_command(state, spoken_text):
    """음성 명령을 한 번 실행하고 인식 결과를 남깁니다."""
    heard = str(spoken_text).strip()
    state["transport_last_voice"] = heard
    command = interpret_voice_command(heard)
    if command is None:
        state["transport_message"] = (
            f'🎤 “{heard}”을 이해하지 못했습니다. '
            '상자로 가·잡아·목표로 옮겨·내려놓아·멈춰·처음으로 중 하나를 말해 주세요.'
        )
        return None
    perform_transport_action(state, command, spoken_text=heard)
    return command


def main():
    import streamlit as st

    try:
        from streamlit_mic_recorder import speech_to_text
    except ImportError:
        speech_to_text = None

    st.set_page_config(
        page_title="틈새 공부 · 물건 옮기는 3D 로봇",
        page_icon="📦",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    initialize_state(st)

    st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], #MainMenu, footer {display:none !important;}
    .block-container {max-width:440px; padding:0.16rem 0.34rem 0.40rem !important;}
    [data-testid="stVerticalBlock"] {gap:0.27rem !important;}
    [data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] > div {height:390px !important;}
    .transport-brand {color:#172554; font-size:1.14rem; font-weight:800; text-align:center; line-height:1.18;}
    .transport-topic {color:#7C3AED; font-size:0.86rem; font-weight:750; text-align:center;}
    .transport-step {color:#172554; font-size:0.96rem; font-weight:800; text-align:center; line-height:1.22;}
    .transport-note {background:#E8F2FF; color:#174A7C; border-radius:0.60rem; padding:0.44rem 0.56rem;
                     font-size:0.82rem; font-weight:650; line-height:1.38;}
    .transport-status {background:#E7F8EE; color:#166534; border-radius:0.60rem; padding:0.43rem 0.54rem;
                       font-size:0.82rem; font-weight:750; text-align:center;}
    .voice-help {background:#FFF7D6; color:#713F12; border-radius:0.56rem; padding:0.36rem 0.48rem;
                 font-size:0.77rem; font-weight:700; text-align:center; line-height:1.30;}
    div[data-testid="stButton"] button {min-height:2.42rem !important; padding:0.18rem !important;
                                        font-size:0.84rem !important; font-weight:700 !important;}
    @media (max-width:640px) {
        .block-container {padding:0.12rem 0.24rem 0.30rem !important;}
        [data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] > div {height:365px !important;}
        .transport-brand {font-size:1.06rem;}
        .transport-note, .transport-status {font-size:0.79rem;}
    }
</style>
<div class="transport-brand">📦 틈새 공부 Python 로봇 교실</div>
<div class="transport-topic">3D 휴머노이드 · 물건을 안전하게 옮겨요!</div>
""", unsafe_allow_html=True)

    paused = st.toggle(
        "⏸ 자동 운반 멈춤 · 버튼/음성 명령",
        value=False,
        key="transport_paused",
    )
    supports_auto = hasattr(st, "fragment")
    if not supports_auto:
        st.warning("자동 재생에는 Streamlit 1.37 이상이 필요합니다.")
    interval = "2.5s" if supports_auto and not paused else None
    decorator = st.fragment(run_every=interval) if supports_auto else (lambda function: function)

    @decorator
    def show_transport():
        if not paused:
            index = int(st.session_state.transport_auto_index)
            scene = AUTO_SCENES[index]
            st.session_state.transport_x = scene[0]
            st.session_state.transport_y = scene[1]
            st.session_state.transport_heading = scene[2]
            st.session_state.transport_stage = scene[5]
            st.session_state.transport_message = scene[4]
            st.session_state.transport_trail = [
                (item[0], item[1]) for item in AUTO_SCENES[:index + 1]
            ]
            title = scene[3]
        else:
            index = int(st.session_state.transport_auto_index)
            title = "직접 운반 명령"

        st.progress(index / (len(AUTO_SCENES) - 1))
        mode = "직접 조종 중" if paused else "자동 시범 중"
        st.markdown(
            f'<div class="transport-step">{mode}　·　{title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="transport-note">{st.session_state.transport_message}</div>',
            unsafe_allow_html=True,
        )

        if paused:
            st.markdown(
                '<div class="voice-help">🎙️ “상자로 가 → 잡아 → 목표로 옮겨 → 내려놓아” 순서로 말해 보세요.</div>',
                unsafe_allow_html=True,
            )
            if speech_to_text is None:
                st.warning("음성 명령을 사용하려면 streamlit-mic-recorder가 필요합니다.")
            else:
                voice_text = speech_to_text(
                    language="ko",
                    start_prompt="🎙️ 음성 명령 시작",
                    stop_prompt="✅ 명령 보내기",
                    just_once=True,
                    use_container_width=True,
                    key="transport_voice_command",
                )
                if voice_text:
                    execute_voice_command(st.session_state, voice_text)
                if st.session_state.transport_last_voice:
                    st.caption(f'🎤 인식된 말: “{st.session_state.transport_last_voice}”')

        figure = make_figure(
            float(st.session_state.transport_x),
            float(st.session_state.transport_y),
            int(st.session_state.transport_heading),
            st.session_state.transport_stage,
            st.session_state.transport_trail,
            height=390,
        )
        st.plotly_chart(
            figure,
            width="stretch",
            key="transport_scene",
            config={"displayModeBar":False, "scrollZoom":True, "responsive":True},
        )
        st.markdown(
            f'<div class="transport-status">{stage_status(st.session_state.transport_stage)}</div>',
            unsafe_allow_html=True,
        )

        # 3D 화면 아래에 휴대폰용 작은 조종 버튼을 모아 둡니다.
        if paused:
            left, forward, right = st.columns(3)
            left.button(
                "↶ 왼쪽", width="stretch", key="transport_left",
                on_click=turn_transport_robot,
                args=(st.session_state, TURN_ANGLE),
            )
            forward.button(
                "▲ 전진", width="stretch", key="transport_forward",
                on_click=walk_transport_robot,
                args=(st.session_state, MOVE_DISTANCE),
            )
            right.button(
                "오른쪽 ↷", width="stretch", key="transport_right",
                on_click=turn_transport_robot,
                args=(st.session_state, -TURN_ANGLE),
            )

            backward, stop, reset = st.columns(3)
            backward.button(
                "▼ 후진", width="stretch", key="transport_backward",
                on_click=walk_transport_robot,
                args=(st.session_state, -MOVE_DISTANCE),
            )
            stop.button(
                "■ 멈춤", width="stretch", key="stop_transport",
                on_click=perform_transport_action,
                args=(st.session_state, "stop"),
            )
            reset.button(
                "↺ 처음", width="stretch", key="reset_transport",
                on_click=perform_transport_action,
                args=(st.session_state, "reset"),
            )

            go_box, grab, carry, drop = st.columns(4)
            go_box.button(
                "📍 상자로", width="stretch", key="go_to_box",
                on_click=perform_transport_action,
                args=(st.session_state, "approach"),
            )
            grab.button(
                "📦 집기", width="stretch", key="grab_box",
                on_click=perform_transport_action,
                args=(st.session_state, "grab"),
            )
            carry.button(
                "🚚 목표로", width="stretch", key="carry_box",
                on_click=perform_transport_action,
                args=(st.session_state, "transport"),
            )
            drop.button(
                "⬇ 놓기", width="stretch", key="drop_box",
                on_click=perform_transport_action,
                args=(st.session_state, "drop"),
            )

        if supports_auto and not paused:
            st.session_state.transport_auto_index = (
                0 if index == len(AUTO_SCENES) - 1 else index + 1
            )

    show_transport()

    with st.expander("🧠 물건을 옮기는 로봇의 생각 순서"):
        st.markdown("""
1. **감지:** 카메라와 거리 센서로 상자와 목표 위치를 찾습니다.
2. **접근:** 상자와 부딪히지 않도록 가까이 이동합니다.
3. **잡기:** 두 손을 상자 양옆에 맞추고 단단히 잡습니다.
4. **운반:** 상자를 몸 가까이 두고 균형을 잡으며 이동합니다.
5. **내려놓기:** 목표 구역에서 상자를 천천히 내려놓습니다.

Python은 `감지 → 판단 → 동작 → 확인` 순서를 반복합니다.
""")

    with st.expander("🎙️ 휴대폰 음성 명령"):
        st.markdown("""
- `상자로 가` → 상자 앞으로 이동
- `잡아` → 두 손으로 상자 들기
- `목표로 옮겨` → 도착 구역으로 운반
- `내려놓아` → 목표 구역에 상자 놓기
- `멈춰`, `처음으로` → 작업 정지 또는 초기화

카카오톡 안에서 마이크가 열리지 않으면 **다른 브라우저로 열기**를 선택해 Chrome에서 실행하세요.
""")


if __name__ == "__main__":
    main()
