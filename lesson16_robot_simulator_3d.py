"""틈새 공부 Python 교실 ⑯: 가상 3D 로봇 조종 시뮬레이터.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly streamlit-mic-recorder
실행: python -m streamlit run lesson16_robot_simulator_3d.py

처음에는 로봇이 자동으로 장애물을 피해 목표 지점까지 이동합니다.
화면을 멈추면 버튼 또는 휴대폰 음성 명령으로 직접 조종할 수 있습니다.
"""

from math import cos, pi, radians, sin, sqrt


FIELD_LIMIT = 4.6
OBSTACLE = (0.0, -2.0, 1.35, 1.35)
TARGET = (3.55, -2.0)
MOVE_DISTANCE = 0.55
TURN_ANGLE = 45

# x, y, 진행 방향(도), 장면 제목, 초등학생도 이해하기 쉬운 설명
AUTO_ROUTE = (
    (-4.0, -2.0, 0, "출발 준비", "파란 로봇이 목표를 향해 출발할 준비를 합니다."),
    (-3.3, -2.0, 0, "앞으로 이동", "오른발과 왼발을 번갈아 내디디며 앞으로 걷습니다."),
    (-2.6, -2.0, 0, "앞으로 이동", "로봇은 앞쪽 센서로 길을 계속 확인합니다."),
    (-2.0, -2.0, 0, "장애물 발견!", "센서가 앞의 상자를 발견했습니다. 먼저 멈춥니다."),
    (-2.0, -2.0, 90, "왼쪽으로 회전", "몸과 발끝을 왼쪽으로 돌려 진행 방향을 바꿉니다."),
    (-2.0, -1.1, 90, "장애물 옆으로 이동", "상자와 안전한 거리를 두고 옆길로 이동합니다."),
    (-2.0, -0.35, 0, "오른쪽으로 회전", "장애물의 위쪽 길을 따라가도록 다시 방향을 바꿉니다."),
    (-0.9, -0.35, 0, "장애물 우회", "장애물과 부딪히지 않고 옆을 지나갑니다."),
    (0.9, -0.35, 0, "장애물 통과", "센서로 거리를 확인하며 장애물을 완전히 통과합니다."),
    (1.8, -0.35, -90, "오른쪽으로 회전", "목표 지점이 있는 아래쪽으로 방향을 바꿉니다."),
    (1.8, -1.15, -90, "목표 쪽으로 이동", "이제 목표가 있는 줄로 내려갑니다."),
    (1.8, -2.0, 0, "왼쪽으로 회전", "목표를 정면으로 바라보도록 마지막으로 회전합니다."),
    (2.6, -2.0, 0, "목표 접근", "장애물을 지나 목표에 가까워졌습니다."),
    (3.55, -2.0, 0, "목표 도착!", "가슴 센서와 두 다리를 사용해 안전하게 도착했습니다."),
)


def rotate_xy(local_x, local_y, center_x, center_y, heading):
    """로봇의 진행 방향에 맞추어 평면 좌표를 회전합니다."""
    angle = radians(heading)
    return (
        center_x + local_x * cos(angle) - local_y * sin(angle),
        center_y + local_x * sin(angle) + local_y * cos(angle),
    )


def add_box(figure, center, size, color, opacity=1.0, heading=0, name=""):
    """회전할 수 있는 직육면체를 3D 장면에 추가합니다."""
    import plotly.graph_objects as go

    center_x, center_y, center_z = center
    size_x, size_y, size_z = size
    vertices = []
    for local_z in (-size_z / 2, size_z / 2):
        for local_y in (-size_y / 2, size_y / 2):
            for local_x in (-size_x / 2, size_x / 2):
                world_x, world_y = rotate_xy(
                    local_x, local_y, center_x, center_y, heading
                )
                vertices.append((world_x, world_y, center_z + local_z))

    x, y, z = zip(*vertices)
    # 꼭짓점 순서: 아래/위 각각 (왼쪽뒤, 오른쪽뒤, 왼쪽앞, 오른쪽앞)
    triangles = (
        (0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5),
        (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6),
        (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3),
    )
    i, j, k = zip(*triangles)
    figure.add_trace(go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=opacity,
        flatshading=True,
        lighting=dict(ambient=0.62, diffuse=0.85, specular=0.26),
        lightposition=dict(x=5, y=4, z=9),
        hovertemplate=f"{name}<extra></extra>" if name else None,
        name=name,
        showlegend=False,
    ))


def add_sphere(figure, center, radius, color, opacity=1.0, name=""):
    """가벼운 저면수 메시로 둥근 부품을 추가해 화면 깜박임을 줄입니다."""
    import plotly.graph_objects as go

    center_x, center_y, center_z = center
    latitude_steps = 7
    longitude_steps = 12
    x_values = []
    y_values = []
    z_values = []
    for latitude_index in range(latitude_steps + 1):
        latitude = pi * latitude_index / latitude_steps
        for longitude_index in range(longitude_steps):
            longitude = 2 * pi * longitude_index / longitude_steps
            x_values.append(center_x + radius * sin(latitude) * cos(longitude))
            y_values.append(center_y + radius * sin(latitude) * sin(longitude))
            z_values.append(center_z + radius * cos(latitude))

    triangle_i = []
    triangle_j = []
    triangle_k = []
    for latitude_index in range(latitude_steps):
        for longitude_index in range(longitude_steps):
            next_longitude = (longitude_index + 1) % longitude_steps
            lower_left = latitude_index * longitude_steps + longitude_index
            lower_right = latitude_index * longitude_steps + next_longitude
            upper_left = (latitude_index + 1) * longitude_steps + longitude_index
            upper_right = (latitude_index + 1) * longitude_steps + next_longitude
            triangle_i.extend((lower_left, lower_left))
            triangle_j.extend((upper_left, upper_right))
            triangle_k.extend((upper_right, lower_right))

    figure.add_trace(go.Mesh3d(
        x=x_values,
        y=y_values,
        z=z_values,
        i=triangle_i,
        j=triangle_j,
        k=triangle_k,
        color=color,
        opacity=opacity,
        flatshading=False,
        lighting=dict(ambient=0.64, diffuse=0.88, specular=0.38),
        lightposition=dict(x=5, y=4, z=9),
        hovertemplate=f"{name}<extra></extra>" if name else None,
        name=name,
        showlegend=False,
    ))


def add_floor(figure):
    """바닥과 격자선을 그립니다."""
    import plotly.graph_objects as go

    grid = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    figure.add_trace(go.Surface(
        x=[[-5, 5], [-5, 5]],
        y=[[-4, -4], [4, 4]],
        z=[[0, 0], [0, 0]],
        surfacecolor=[[0, 0], [0, 0]],
        colorscale=[[0, "#EAF2FF"], [1, "#EAF2FF"]],
        opacity=0.82,
        cmin=0,
        cmax=1,
        showscale=False,
        hoverinfo="skip",
    ))
    # 격자 18개를 한 개의 선 묶음으로 합쳐 WebGL 다시 그리기를 줄입니다.
    grid_x = []
    grid_y = []
    grid_z = []
    for value in grid:
        grid_x.extend((value, value, None, -5, 5, None))
        grid_y.extend((-4, 4, None, value, value, None))
        grid_z.extend((0.012, 0.012, None, 0.012, 0.012, None))
    figure.add_trace(go.Scatter3d(
        x=grid_x,
        y=grid_y,
        z=grid_z,
        mode="lines",
        line=dict(color="#C7D7EE", width=2),
        hoverinfo="skip",
        showlegend=False,
    ))


def add_target(figure):
    """목표 지점을 원과 깃발로 표시합니다."""
    import plotly.graph_objects as go

    target_x, target_y = TARGET
    angles = [2 * pi * index / 48 for index in range(49)]
    figure.add_trace(go.Scatter3d(
        x=[target_x + 0.58 * cos(angle) for angle in angles],
        y=[target_y + 0.58 * sin(angle) for angle in angles],
        z=[0.045] * len(angles),
        mode="lines",
        line=dict(color="#16A34A", width=10),
        hovertemplate="목표 지점<extra></extra>",
    ))
    figure.add_trace(go.Scatter3d(
        x=[target_x], y=[target_y], z=[0.11],
        mode="markers+text",
        marker=dict(size=15, color="#FACC15", line=dict(color="#166534", width=4)),
        text=["<b>목표</b>"],
        textposition="top center",
        textfont=dict(size=17, color="#14532D"),
        hoverinfo="skip",
    ))


def add_robot(figure, x, y, heading, sensor_alert=False):
    """머리·몸통·팔·다리·가슴 센서가 있는 휴머노이드를 그립니다."""
    import plotly.graph_objects as go

    # 몸통과 허리
    add_box(
        figure, (x, y, 1.34), (0.48, 0.80, 0.70),
        "#2563EB", heading=heading, name="휴머노이드 몸통",
    )
    chest_x, chest_y = rotate_xy(0.265, 0, x, y, heading)
    add_box(
        figure, (chest_x, chest_y, 1.36), (0.07, 0.48, 0.42),
        "#93C5FD", heading=heading, name="가슴 제어판",
    )
    add_box(
        figure, (x, y, 0.93), (0.44, 0.62, 0.24),
        "#1D4ED8", heading=heading, name="허리",
    )

    # 머리와 얼굴. 앞쪽(+x)에 검은 얼굴판과 두 눈을 붙입니다.
    neck_x, neck_y = rotate_xy(0, 0, x, y, heading)
    add_box(
        figure, (neck_x, neck_y, 1.70), (0.24, 0.28, 0.22),
        "#64748B", heading=heading, name="목",
    )
    add_sphere(figure, (x, y, 2.02), 0.35, "#DCEEFF", name="휴머노이드 머리")
    face_x, face_y = rotate_xy(0.31, 0, x, y, heading)
    add_box(
        figure, (face_x, face_y, 2.02), (0.055, 0.42, 0.18),
        "#172554", heading=heading, name="얼굴 화면",
    )
    for eye_side in (-0.13, 0.13):
        eye_x, eye_y = rotate_xy(0.345, eye_side, x, y, heading)
        add_sphere(
            figure, (eye_x, eye_y, 2.04), 0.058,
            "#67E8F9", name="빛나는 눈",
        )

    # 두 팔과 손
    for side in (-1, 1):
        shoulder_x, shoulder_y = rotate_xy(0, side * 0.52, x, y, heading)
        arm_x, arm_y = rotate_xy(0, side * 0.57, x, y, heading)
        add_sphere(
            figure, (shoulder_x, shoulder_y, 1.55), 0.15,
            "#60A5FA", name="어깨 관절",
        )
        add_box(
            figure, (arm_x, arm_y, 1.25), (0.23, 0.23, 0.62),
            "#60A5FA", heading=heading, name="팔",
        )
        add_sphere(
            figure, (arm_x, arm_y, 0.91), 0.13,
            "#DCEEFF", name="손",
        )

    # 두 다리와 앞으로 조금 나온 발
    for side in (-1, 1):
        leg_x, leg_y = rotate_xy(0, side * 0.22, x, y, heading)
        foot_x, foot_y = rotate_xy(0.15, side * 0.22, x, y, heading)
        add_box(
            figure, (leg_x, leg_y, 0.56), (0.27, 0.29, 0.68),
            "#3B82F6", heading=heading, name="다리",
        )
        add_box(
            figure, (foot_x, foot_y, 0.15), (0.56, 0.32, 0.22),
            "#172554", heading=heading, name="발",
        )

    # 가슴 센서와 로봇의 진행 방향을 알려 주는 감지 빛
    sensor_x, sensor_y = rotate_xy(0.32, 0, x, y, heading)
    beam_color = "#EF4444" if sensor_alert else "#06B6D4"
    add_sphere(
        figure, (sensor_x, sensor_y, 1.39), 0.115,
        beam_color, name="가슴 거리 센서",
    )
    angle = radians(heading)
    start_x, start_y = rotate_xy(0.42, 0, x, y, heading)
    end_x, end_y = rotate_xy(1.52, 0, x, y, heading)
    figure.add_trace(go.Scatter3d(
        x=[start_x, end_x], y=[start_y, end_y], z=[1.39, 1.39],
        mode="lines",
        line=dict(color=beam_color, width=9, dash="dot"),
        hovertemplate=("장애물 감지!" if sensor_alert else "가슴 거리 센서") + "<extra></extra>",
    ))
    figure.add_trace(go.Cone(
        x=[end_x], y=[end_y], z=[1.39],
        u=[0.34 * cos(angle)], v=[0.34 * sin(angle)], w=[0],
        anchor="tip", sizemode="absolute", sizeref=0.26,
        colorscale=[[0, beam_color], [1, beam_color]],
        showscale=False, hoverinfo="skip",
    ))

    # 카메라 방향과 무관하게 로봇의 위치를 찾기 쉬운 이름표
    figure.add_trace(go.Scatter3d(
        x=[x], y=[y], z=[2.52],
        mode="text",
        text=["<b>휴머노이드</b>"], textposition="middle center",
        textfont=dict(size=15, color="#0F172A"), hoverinfo="skip",
    ))


def point_hits_obstacle(x, y, margin=0.62):
    """로봇 중심이 장애물의 안전 영역 안에 들어가는지 확인합니다."""
    obstacle_x, obstacle_y, width, depth = OBSTACLE
    return (
        abs(x - obstacle_x) <= width / 2 + margin
        and abs(y - obstacle_y) <= depth / 2 + margin
    )


def move_pose(x, y, heading, distance):
    """현재 방향으로 지정된 거리만큼 이동한 새 위치를 계산합니다."""
    angle = radians(heading)
    return x + distance * cos(angle), y + distance * sin(angle)


def safe_move(x, y, heading, distance):
    """경계와 장애물을 통과하지 않는 이동 결과를 반환합니다."""
    next_x, next_y = move_pose(x, y, heading, distance)
    if abs(next_x) > FIELD_LIMIT or abs(next_y) > FIELD_LIMIT - 0.8:
        return x, y, "운동장 밖으로 나갈 수 없어 멈췄습니다."
    if point_hits_obstacle(next_x, next_y):
        return x, y, "장애물을 발견하여 안전하게 멈췄습니다."
    return next_x, next_y, "안전하게 이동했습니다."


def interpret_voice_command(spoken_text):
    """한국어 음성 문장에서 로봇이 실행할 한 가지 명령을 찾습니다."""
    normalized = str(spoken_text).lower().replace(" ", "")
    command_words = (
        ("reset", ("처음으로", "처음", "리셋", "원위치", "출발점")),
        ("stop", ("멈춰", "멈춤", "정지", "스톱")),
        ("backward", ("뒤로", "후진", "뒤")),
        ("left", ("왼쪽", "좌회전")),
        ("right", ("오른쪽", "우회전")),
        ("forward", ("앞으로", "전진", "앞")),
    )
    for command, words in command_words:
        if any(word in normalized for word in words):
            return command
    return None


def execute_voice_command(state, spoken_text):
    """인식한 음성 명령을 세션 상태에 한 번 적용합니다."""
    command = interpret_voice_command(spoken_text)
    heard = str(spoken_text).strip()
    state["robot_last_voice"] = heard

    if command is None:
        state["robot_message"] = (
            f'🎤 “{heard}”을 이해하지 못했습니다. '
            '앞으로·뒤로·왼쪽·오른쪽·멈춰·처음으로 중 하나를 말해 주세요.'
        )
        return None

    if command == "reset":
        state["robot_auto_index"] = 0
        state["robot_x"] = AUTO_ROUTE[0][0]
        state["robot_y"] = AUTO_ROUTE[0][1]
        state["robot_heading"] = AUTO_ROUTE[0][2]
        state["robot_trail"] = [(AUTO_ROUTE[0][0], AUTO_ROUTE[0][1])]
        result = "출발점으로 돌아왔습니다."
    elif command == "stop":
        result = "그 자리에서 안전하게 멈췄습니다."
    elif command == "left":
        state["robot_heading"] = (int(state["robot_heading"]) + TURN_ANGLE) % 360
        result = "왼쪽으로 45° 회전했습니다."
    elif command == "right":
        state["robot_heading"] = (int(state["robot_heading"]) - TURN_ANGLE) % 360
        result = "오른쪽으로 45° 회전했습니다."
    else:
        distance = MOVE_DISTANCE if command == "forward" else -MOVE_DISTANCE
        new_x, new_y, result = safe_move(
            float(state["robot_x"]),
            float(state["robot_y"]),
            int(state["robot_heading"]),
            distance,
        )
        state["robot_x"] = new_x
        state["robot_y"] = new_y
        state["robot_trail"].append((new_x, new_y))

    state["robot_message"] = f'🎤 “{heard}” → {result}'
    return command


def make_figure(x, y, heading, trail, planned_route=True, sensor_alert=False, height=410):
    """현재 로봇 상태를 보여 주는 Plotly 3D 그림을 만듭니다."""
    import plotly.graph_objects as go

    figure = go.Figure()
    add_floor(figure)

    if planned_route:
        figure.add_trace(go.Scatter3d(
            x=[pose[0] for pose in AUTO_ROUTE],
            y=[pose[1] for pose in AUTO_ROUTE],
            z=[0.055] * len(AUTO_ROUTE),
            mode="lines",
            line=dict(color="#94A3B8", width=5, dash="dash"),
            hovertemplate="자동 주행 예정 경로<extra></extra>",
        ))

    if trail:
        figure.add_trace(go.Scatter3d(
            x=[point[0] for point in trail],
            y=[point[1] for point in trail],
            z=[0.085] * len(trail),
            mode="lines+markers",
            line=dict(color="#2563EB", width=8),
            marker=dict(size=4, color="#1D4ED8"),
            hovertemplate="지나온 길<extra></extra>",
        ))

    obstacle_x, obstacle_y, width, depth = OBSTACLE
    add_box(
        figure,
        (obstacle_x, obstacle_y, 0.70),
        (width, depth, 1.40),
        "#F97316",
        opacity=0.96,
        name="장애물",
    )
    figure.add_trace(go.Scatter3d(
        x=[obstacle_x], y=[obstacle_y], z=[1.58],
        mode="text", text=["<b>장애물</b>"],
        textfont=dict(size=17, color="#7C2D12"), hoverinfo="skip",
    ))
    add_target(figure)
    add_robot(figure, x, y, heading, sensor_alert=sensor_alert)

    figure.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        showlegend=False,
        scene=dict(
            camera=dict(
                eye=dict(x=1.28, y=1.62, z=1.46),
                projection=dict(type="orthographic"),
            ),
            aspectmode="manual",
            aspectratio=dict(x=1.28, y=1.0, z=0.58),
            xaxis=dict(range=[-5.1, 5.1], visible=False),
            yaxis=dict(range=[-4.1, 4.1], visible=False),
            zaxis=dict(range=[0, 2.85], visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#172554"),
        uirevision="robot-camera",
    )
    figure.add_annotation(
        x=0.01, y=0.99, xref="paper", yref="paper",
        text=f"<b>위치 ({x:.1f}, {y:.1f})　방향 {heading % 360}°</b>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(size=14, color="#0F172A"),
        bgcolor="rgba(255,255,255,0.94)", bordercolor="#93C5FD",
        borderwidth=2, borderpad=5,
    )
    return figure


def initialize_state(st):
    """Streamlit 세션의 로봇 상태를 처음 한 번만 준비합니다."""
    if "robot_auto_index" not in st.session_state:
        st.session_state.robot_auto_index = 0
    if "robot_x" not in st.session_state:
        st.session_state.robot_x = AUTO_ROUTE[0][0]
        st.session_state.robot_y = AUTO_ROUTE[0][1]
        st.session_state.robot_heading = AUTO_ROUTE[0][2]
        st.session_state.robot_trail = [(AUTO_ROUTE[0][0], AUTO_ROUTE[0][1])]
        st.session_state.robot_message = "자동 주행을 시작합니다."
        st.session_state.robot_last_voice = ""


def reset_robot(st):
    """로봇을 출발점으로 되돌립니다."""
    st.session_state.robot_auto_index = 0
    st.session_state.robot_x = AUTO_ROUTE[0][0]
    st.session_state.robot_y = AUTO_ROUTE[0][1]
    st.session_state.robot_heading = AUTO_ROUTE[0][2]
    st.session_state.robot_trail = [(AUTO_ROUTE[0][0], AUTO_ROUTE[0][1])]
    st.session_state.robot_message = "출발점으로 돌아왔습니다."


def main():
    import streamlit as st

    try:
        from streamlit_mic_recorder import speech_to_text
    except ImportError:
        speech_to_text = None

    st.set_page_config(
        page_title="틈새 공부 · 가상 3D 로봇",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    initialize_state(st)

    st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], #MainMenu, footer {display: none !important;}
    .block-container {max-width: 440px; padding: 0.20rem 0.38rem 0.45rem !important;}
    [data-testid="stVerticalBlock"] {gap: 0.30rem !important;}
    [data-testid="stPlotlyChart"] {height: 410px !important; overflow: hidden;}
    [data-testid="stPlotlyChart"] > div {height: 410px !important;}
    [data-testid="stProgressBar"], [data-testid="stToggle"] {margin: 0 !important;}
    .robot-brand {color:#172554; font-size:1.20rem; font-weight:800; text-align:center; line-height:1.18;}
    .robot-topic {color:#1D4ED8; font-size:0.91rem; font-weight:750; text-align:center; margin-bottom:0.04rem;}
    .robot-step {color:#172554; font-size:0.98rem; font-weight:800; text-align:center; line-height:1.22;}
    .robot-note {background:#E8F2FF; color:#174A7C; border-radius:0.62rem; padding:0.48rem 0.60rem;
                 font-size:0.84rem; font-weight:650; line-height:1.40;}
    .robot-status {background:#E7F8EE; color:#166534; border-radius:0.62rem; padding:0.46rem 0.58rem;
                   font-size:0.84rem; font-weight:750; text-align:center; line-height:1.35;}
    .voice-help {background:#FFF7D6; color:#713F12; border-radius:0.58rem; padding:0.38rem 0.52rem;
                 font-size:0.78rem; font-weight:700; text-align:center; line-height:1.32;}
    div[data-testid="stButton"] button {min-height:2.45rem !important; padding:0.20rem !important;
                                        font-size:0.90rem !important; font-weight:700 !important;}
    @media (max-width: 640px) {
        .block-container {padding:0.16rem 0.28rem 0.35rem !important;}
        [data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] > div {height:390px !important;}
        .robot-brand {font-size:1.12rem;}
        .robot-topic {font-size:0.85rem;}
        .robot-note, .robot-status {font-size:0.81rem;}
    }
</style>
<div class="robot-brand">🤖 틈새 공부 Python 로봇 교실</div>
<div class="robot-topic">가상 3D 휴머노이드 · 장애물을 피해 목표까지!</div>
""", unsafe_allow_html=True)

    paused = st.toggle("⏸ 자동 주행 멈춤 · 버튼/음성 조종", value=False, key="robot_paused")
    supports_auto = hasattr(st, "fragment")
    if not supports_auto:
        st.warning("자동 주행에는 Streamlit 1.37 이상이 필요합니다.")
    # 휴머노이드 장면을 완전히 그린 뒤 다음 장면으로 넘어가도록 여유를 둡니다.
    interval = "2.4s" if supports_auto and not paused else None
    decorator = st.fragment(run_every=interval) if supports_auto else (lambda function: function)

    @decorator
    def show_robot():
        if not paused:
            index = int(st.session_state.robot_auto_index)
            pose = AUTO_ROUTE[index]
            st.session_state.robot_x = pose[0]
            st.session_state.robot_y = pose[1]
            st.session_state.robot_heading = pose[2]
            st.session_state.robot_trail = [(item[0], item[1]) for item in AUTO_ROUTE[:index + 1]]
            st.session_state.robot_message = pose[4]
        else:
            index = int(st.session_state.robot_auto_index)
            pose = AUTO_ROUTE[index]

        progress_value = index / (len(AUTO_ROUTE) - 1)
        st.progress(progress_value)
        mode_text = "직접 조종 중" if paused else "자동 주행 중"
        title = "직접 조종" if paused else pose[3]
        st.markdown(
            f'<div class="robot-step">{mode_text}　·　{title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="robot-note">{st.session_state.robot_message}</div>',
            unsafe_allow_html=True,
        )

        if paused:
            st.markdown(
                '<div class="voice-help">🎙️ 마이크를 누르고 “앞으로·뒤로·왼쪽·오른쪽·멈춰·처음으로”라고 말해 보세요.</div>',
                unsafe_allow_html=True,
            )
            if speech_to_text is None:
                st.warning("음성 조종 준비가 필요합니다: streamlit-mic-recorder를 설치해 주세요.")
            else:
                voice_text = speech_to_text(
                    language="ko",
                    start_prompt="🎙️ 음성 명령 시작",
                    stop_prompt="✅ 명령 보내기",
                    just_once=True,
                    use_container_width=True,
                    key="robot_voice_command",
                )
                if voice_text:
                    execute_voice_command(st.session_state, voice_text)
                if st.session_state.get("robot_last_voice"):
                    st.caption(f'🎤 인식된 말: “{st.session_state.robot_last_voice}”')

            left, forward, right = st.columns(3)
            if left.button("↶ 좌회전", width="stretch", key="robot_left"):
                st.session_state.robot_heading = (st.session_state.robot_heading + TURN_ANGLE) % 360
                st.session_state.robot_message = "제자리에서 왼쪽으로 45° 회전했습니다."
            if forward.button("▲ 전진", width="stretch", key="robot_forward"):
                new_x, new_y, message = safe_move(
                    st.session_state.robot_x,
                    st.session_state.robot_y,
                    st.session_state.robot_heading,
                    MOVE_DISTANCE,
                )
                st.session_state.robot_x, st.session_state.robot_y = new_x, new_y
                st.session_state.robot_message = message
                st.session_state.robot_trail.append((new_x, new_y))
            if right.button("우회전 ↷", width="stretch", key="robot_right"):
                st.session_state.robot_heading = (st.session_state.robot_heading - TURN_ANGLE) % 360
                st.session_state.robot_message = "제자리에서 오른쪽으로 45° 회전했습니다."

            back, stop, reset = st.columns(3)
            if back.button("▼ 후진", width="stretch", key="robot_back"):
                new_x, new_y, message = safe_move(
                    st.session_state.robot_x,
                    st.session_state.robot_y,
                    st.session_state.robot_heading,
                    -MOVE_DISTANCE,
                )
                st.session_state.robot_x, st.session_state.robot_y = new_x, new_y
                st.session_state.robot_message = message
                st.session_state.robot_trail.append((new_x, new_y))
            if stop.button("■ 정지", width="stretch", key="robot_stop"):
                st.session_state.robot_message = "모터를 멈췄습니다."
            if reset.button("↺ 처음", width="stretch", key="robot_reset"):
                reset_robot(st)

        robot_x = float(st.session_state.robot_x)
        robot_y = float(st.session_state.robot_y)
        robot_heading = int(st.session_state.robot_heading)
        obstacle_distance = sqrt((robot_x - OBSTACLE[0]) ** 2 + (robot_y - OBSTACLE[1]) ** 2)
        sensor_alert = obstacle_distance < 2.35
        figure = make_figure(
            robot_x,
            robot_y,
            robot_heading,
            st.session_state.robot_trail,
            planned_route=not paused,
            sensor_alert=sensor_alert,
            height=410,
        )
        st.plotly_chart(
            figure,
            width="stretch",
            key="robot_scene",
            config={"displayModeBar": False, "scrollZoom": True, "responsive": True},
        )

        if sensor_alert:
            status = "🚨 센서: 가까운 장애물을 감지했습니다."
        elif sqrt((robot_x - TARGET[0]) ** 2 + (robot_y - TARGET[1]) ** 2) < 0.72:
            status = "🎉 목표 도착! 로봇을 안전하게 정지합니다."
        else:
            status = "🟢 센서: 앞쪽 이동 공간을 확인하고 있습니다."
        st.markdown(f'<div class="robot-status">{status}</div>', unsafe_allow_html=True)

        if supports_auto and not paused:
            st.session_state.robot_auto_index = 0 if index == len(AUTO_ROUTE) - 1 else index + 1

    show_robot()

    with st.expander("🧠 로봇이 움직이는 원리"):
        st.markdown("""
- **전진:** 왼발과 오른발을 번갈아 내디디며 몸의 균형을 잡습니다.
- **회전:** 몸과 발끝을 움직일 방향으로 돌립니다.
- **센서:** 가슴의 거리 센서가 앞에 있는 물체까지의 거리를 확인합니다.
- **균형:** 두 팔을 움직여 넘어지지 않도록 중심을 잡습니다.
- **판단:** 장애물이 가까우면 멈추고 안전한 방향으로 회전합니다.
- **Python:** `감지 → 판단 → 움직임`의 순서를 반복하도록 명령합니다.
""")

    with st.expander("🎙️ 휴대폰 음성 조종 방법"):
        st.markdown("""
1. **자동 주행 멈춤 · 버튼/음성 조종**을 켭니다.
2. **음성 명령 시작**을 누르고 마이크 사용을 허용합니다.
3. `앞으로`, `뒤로`, `왼쪽`, `오른쪽`, `멈춰`, `처음으로` 중 하나를 말합니다.
4. **명령 보내기**를 누르면 인식된 말과 실행 결과가 표시됩니다.

카카오톡 안에서 마이크가 열리지 않으면 오른쪽 위 메뉴에서 **다른 브라우저로 열기**를 선택해 Chrome에서 실행하세요.
""")


if __name__ == "__main__":
    main()
