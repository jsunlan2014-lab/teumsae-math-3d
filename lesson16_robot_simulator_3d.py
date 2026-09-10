"""틈새 공부 Python 교실 ⑯: 가상 3D 로봇 조종 시뮬레이터.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson16_robot_simulator_3d.py

처음에는 로봇이 자동으로 장애물을 피해 목표 지점까지 이동합니다.
화면을 멈추면 전진·후진·좌회전·우회전 버튼으로 직접 조종할 수 있습니다.
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
    (-3.3, -2.0, 0, "앞으로 이동", "두 바퀴를 같은 방향으로 돌리면 앞으로 갑니다."),
    (-2.6, -2.0, 0, "앞으로 이동", "로봇은 앞쪽 센서로 길을 계속 확인합니다."),
    (-2.0, -2.0, 0, "장애물 발견!", "센서가 앞의 상자를 발견했습니다. 먼저 멈춥니다."),
    (-2.0, -2.0, 90, "왼쪽으로 회전", "왼쪽 바퀴는 천천히, 오른쪽 바퀴는 빠르게 돌려 방향을 바꿉니다."),
    (-2.0, -1.1, 90, "장애물 옆으로 이동", "상자와 안전한 거리를 두고 옆길로 이동합니다."),
    (-2.0, -0.35, 0, "오른쪽으로 회전", "장애물의 위쪽 길을 따라가도록 다시 방향을 바꿉니다."),
    (-0.9, -0.35, 0, "장애물 우회", "장애물과 부딪히지 않고 옆을 지나갑니다."),
    (0.9, -0.35, 0, "장애물 통과", "센서로 거리를 확인하며 장애물을 완전히 통과합니다."),
    (1.8, -0.35, -90, "오른쪽으로 회전", "목표 지점이 있는 아래쪽으로 방향을 바꿉니다."),
    (1.8, -1.15, -90, "목표 쪽으로 이동", "이제 목표가 있는 줄로 내려갑니다."),
    (1.8, -2.0, 0, "왼쪽으로 회전", "목표를 정면으로 바라보도록 마지막으로 회전합니다."),
    (2.6, -2.0, 0, "목표 접근", "장애물을 지나 목표에 가까워졌습니다."),
    (3.55, -2.0, 0, "목표 도착!", "센서와 바퀴를 함께 사용해 안전하게 도착했습니다."),
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
    for value in grid:
        figure.add_trace(go.Scatter3d(
            x=[value, value], y=[-4, 4], z=[0.012, 0.012],
            mode="lines", line=dict(color="#C7D7EE", width=2), hoverinfo="skip",
        ))
        if value <= 4:
            figure.add_trace(go.Scatter3d(
                x=[-5, 5], y=[value, value], z=[0.012, 0.012],
                mode="lines", line=dict(color="#C7D7EE", width=2), hoverinfo="skip",
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
    """몸체·운전석·바퀴·센서로 이루어진 로봇을 그립니다."""
    import plotly.graph_objects as go

    add_box(figure, (x, y, 0.42), (1.18, 0.82, 0.38), "#2563EB", heading=heading, name="로봇 몸체")
    add_box(figure, (x, y, 0.72), (0.56, 0.58, 0.28), "#93C5FD", heading=heading, name="로봇 제어 장치")

    for local_x in (-0.38, 0.38):
        for local_y in (-0.50, 0.50):
            wheel_x, wheel_y = rotate_xy(local_x, local_y, x, y, heading)
            add_box(
                figure,
                (wheel_x, wheel_y, 0.28),
                (0.34, 0.20, 0.34),
                "#172033",
                heading=heading,
                name="바퀴",
            )

    # 로봇의 앞쪽 방향 화살표
    angle = radians(heading)
    start_x, start_y = rotate_xy(0.48, 0, x, y, heading)
    end_x, end_y = rotate_xy(1.42, 0, x, y, heading)
    beam_color = "#DC2626" if sensor_alert else "#0EA5E9"
    figure.add_trace(go.Scatter3d(
        x=[start_x, end_x], y=[start_y, end_y], z=[0.72, 0.72],
        mode="lines",
        line=dict(color=beam_color, width=9, dash="dot"),
        hovertemplate=("장애물 감지!" if sensor_alert else "앞쪽 거리 센서") + "<extra></extra>",
    ))
    figure.add_trace(go.Cone(
        x=[end_x], y=[end_y], z=[0.72],
        u=[0.34 * cos(angle)], v=[0.34 * sin(angle)], w=[0],
        anchor="tip", sizemode="absolute", sizeref=0.26,
        colorscale=[[0, beam_color], [1, beam_color]],
        showscale=False, hoverinfo="skip",
    ))

    # 카메라 방향과 무관하게 로봇 위치를 찾기 쉬운 큰 이름표
    figure.add_trace(go.Scatter3d(
        x=[x], y=[y], z=[1.27],
        mode="markers+text",
        marker=dict(size=24, color="#FFFFFF", line=dict(color="#1E3A8A", width=5)),
        text=["<b>ROBOT</b>"], textposition="middle center",
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
            aspectratio=dict(x=1.28, y=1.0, z=0.44),
            xaxis=dict(range=[-5.1, 5.1], visible=False),
            yaxis=dict(range=[-4.1, 4.1], visible=False),
            zaxis=dict(range=[0, 2.6], visible=False),
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
<div class="robot-topic">가상 3D 로봇 · 장애물을 피해 목표까지!</div>
""", unsafe_allow_html=True)

    paused = st.toggle("⏸ 자동 주행 멈춤 · 직접 조종", value=False, key="robot_paused")
    supports_auto = hasattr(st, "fragment")
    if not supports_auto:
        st.warning("자동 주행에는 Streamlit 1.37 이상이 필요합니다.")
    interval = "1.25s" if supports_auto and not paused else None
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
            st.session_state.robot_message = pose[5]
        else:
            index = int(st.session_state.robot_auto_index)
            pose = AUTO_ROUTE[index]

        progress_value = index / (len(AUTO_ROUTE) - 1)
        st.progress(progress_value)
        mode_text = "직접 조종 중" if paused else "자동 주행 중"
        title = "직접 조종" if paused else pose[4]
        st.markdown(
            f'<div class="robot-step">{mode_text}　·　{title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="robot-note">{st.session_state.robot_message}</div>',
            unsafe_allow_html=True,
        )

        if paused:
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
- **전진:** 왼쪽 바퀴와 오른쪽 바퀴를 같은 방향으로 돌립니다.
- **회전:** 두 바퀴의 속도나 방향을 다르게 만듭니다.
- **센서:** 로봇 앞의 물체까지 거리를 확인합니다.
- **판단:** 장애물이 가까우면 멈추고 안전한 방향으로 회전합니다.
- **Python:** `감지 → 판단 → 움직임`의 순서를 반복하도록 명령합니다.
""")


if __name__ == "__main__":
    main()
