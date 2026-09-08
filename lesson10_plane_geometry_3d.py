"""틈새 공부 3D 수학 교실 ①: 다각형의 내각·외각·부채꼴.

각 개념을 3단계로 자동 재생하고, 도형 위의 각도와 계산 과정을
같은 순서로 보여 주는 수업용 시뮬레이션입니다.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson10_plane_geometry_3d.py
"""

import math


def regular_polygon(n, radius=4.0, start_angle=math.pi / 2):
    """반시계 방향의 정n각형 꼭짓점을 만듭니다."""
    if not isinstance(n, int) or not 3 <= n <= 12:
        raise ValueError("변의 수 n은 3부터 12까지의 정수여야 합니다.")
    return [
        (radius * math.cos(start_angle + 2 * math.pi * k / n),
         radius * math.sin(start_angle + 2 * math.pi * k / n))
        for k in range(n)
    ]


def interior_sum(n):
    if not isinstance(n, int) or n < 3:
        raise ValueError("다각형은 변이 3개 이상이어야 합니다.")
    return (n - 2) * 180


def regular_interior_angle(n):
    return interior_sum(n) / n


def exterior_sum(n):
    if not isinstance(n, int) or n < 3:
        raise ValueError("다각형은 변이 3개 이상이어야 합니다.")
    return 360


def regular_exterior_angle(n):
    return exterior_sum(n) / n


def sector_values(radius, angle_degrees):
    """부채꼴의 호의 길이와 넓이를 반환합니다."""
    radius, angle_degrees = float(radius), float(angle_degrees)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("반지름은 0보다 커야 합니다.")
    if not math.isfinite(angle_degrees) or not 0 < angle_degrees <= 360:
        raise ValueError("중심각은 0도보다 크고 360도 이하여야 합니다.")
    fraction = angle_degrees / 360
    return {
        "fraction": fraction,
        "arc_length": 2 * math.pi * radius * fraction,
        "area": math.pi * radius**2 * fraction,
    }


def thin_prism_mesh(points, thickness=0.18):
    """볼록다각형을 얇은 3D 수학판으로 만듭니다."""
    count = len(points)
    if count < 3:
        raise ValueError("꼭짓점이 3개 이상 필요합니다.")
    z0, z1 = -thickness / 2, thickness / 2
    x = [p[0] for p in points] * 2
    y = [p[1] for p in points] * 2
    z = [z0] * count + [z1] * count
    i, j, k = [], [], []
    # 아래·위 면: 첫 꼭짓점에서 삼각형 n-2개로 나눕니다.
    for index in range(1, count - 1):
        i.extend([0, count])
        j.extend([index + 1, count + index])
        k.extend([index, count + index + 1])
    # 옆면: 사각형 하나를 삼각형 두 개로 나눕니다.
    for index in range(count):
        following = (index + 1) % count
        i.extend([index, index])
        j.extend([following, count + following])
        k.extend([count + following, count + index])
    return {"x": x, "y": y, "z": z, "i": i, "j": j, "k": k}


def sector_mesh(radius, angle_degrees, thickness=0.18, samples=72):
    """부채꼴을 삼각형 면으로 정확히 나눈 얇은 3D 모형입니다."""
    sector_values(radius, angle_degrees)  # 입력 검증
    steps = max(8, round(samples * angle_degrees / 360))
    angles = [math.radians(angle_degrees) * index / steps for index in range(steps + 1)]
    ring = [(radius * math.cos(angle), radius * math.sin(angle)) for angle in angles]
    points = [(0.0, 0.0), *ring]
    count = len(points)
    z0, z1 = -thickness / 2, thickness / 2
    x = [p[0] for p in points] * 2
    y = [p[1] for p in points] * 2
    z = [z0] * count + [z1] * count
    i, j, k = [], [], []
    # 중심과 호의 이웃한 점을 연결한 부채꼴 면
    for index in range(1, count - 1):
        i.extend([0, count])
        j.extend([index + 1, count + index])
        k.extend([index, count + index + 1])
    # 경계의 얇은 옆면
    boundary = list(range(count))
    for first, second in zip(boundary, boundary[1:] + boundary[:1]):
        i.extend([first, first])
        j.extend([second, count + second])
        k.extend([count + second, count + first])
    return {"x": x, "y": y, "z": z, "i": i, "j": j, "k": k,
            "ring": ring, "top_z": z1}


def angle_arc(vertex, ray_a, ray_b, radius, z, choose_larger=False, samples=30):
    """두 방향 사이의 작은 각 또는 큰 각을 나타내는 원호 좌표입니다."""
    angle_a = math.atan2(ray_a[1], ray_a[0])
    angle_b = math.atan2(ray_b[1], ray_b[0])
    delta = (angle_b - angle_a + math.pi) % (2 * math.pi) - math.pi
    if choose_larger:
        delta = delta - 2 * math.pi if delta > 0 else delta + 2 * math.pi
    angles = [angle_a + delta * index / samples for index in range(samples + 1)]
    return ([vertex[0] + radius * math.cos(angle) for angle in angles],
            [vertex[1] + radius * math.sin(angle) for angle in angles],
            [z] * len(angles))


def base_figure(title, top_view=False):
    import plotly.graph_objects as go

    figure = go.Figure()
    eye = dict(x=0.01, y=0.01, z=2.55) if top_view else dict(x=1.25, y=1.25, z=1.15)
    figure.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        margin=dict(l=0, r=0, t=55, b=0), height=560,
        showlegend=False,
        scene=dict(
            camera=dict(eye=eye), aspectmode="data",
            xaxis=dict(title="x", showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(title="y", showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(title="", showgrid=False, zeroline=False, showticklabels=False,
                       range=[-1.2, 1.2]),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def add_polygon_board(figure, points):
    import plotly.graph_objects as go

    mesh = thin_prism_mesh(points)
    figure.add_trace(go.Mesh3d(
        **mesh, color="#4F86F7", opacity=0.30, flatshading=True,
        hoverinfo="skip", name="다각형 수학판",
    ))
    closed = points + [points[0]]
    figure.add_trace(go.Scatter3d(
        x=[p[0] for p in closed], y=[p[1] for p in closed], z=[0.1] * len(closed),
        mode="lines", line=dict(color="#2357C6", width=7), hoverinfo="skip",
    ))
    labels = [chr(65 + index) for index in range(len(points))]
    figure.add_trace(go.Scatter3d(
        x=[p[0] for p in points], y=[p[1] for p in points], z=[0.18] * len(points),
        mode="markers+text", marker=dict(size=5, color="#174092"), text=labels,
        textposition="top center", hovertemplate="꼭짓점 %{text}<extra></extra>",
    ))


def polygon_figure(n, lesson, step, top_view=False):
    """내각 또는 외각 학습용 3D 그림입니다."""
    import plotly.graph_objects as go

    points = regular_polygon(n)
    title = f"정{n}각형의 {'내각' if lesson == 'interior' else '외각'}"
    figure = base_figure(title, top_view)
    add_polygon_board(figure, points)
    z = 0.14

    if lesson == "interior":
        if step >= 1:
            # 모든 꼭짓점의 안쪽에 내각 호와 각도값을 표시합니다.
            angle_value = regular_interior_angle(n)
            label_factor = 0.70 if n <= 6 else 0.77
            for index, vertex in enumerate(points):
                previous = points[(index - 1) % n]
                following = points[(index + 1) % n]
                ray_a = (previous[0] - vertex[0], previous[1] - vertex[1])
                ray_b = (following[0] - vertex[0], following[1] - vertex[1])
                arc = angle_arc(vertex, ray_a, ray_b, 0.68, 0.2)
                figure.add_trace(go.Scatter3d(
                    x=arc[0], y=arc[1], z=arc[2], mode="lines",
                    line=dict(color="#F59E0B", width=8), hoverinfo="skip",
                ))
            figure.add_trace(go.Scatter3d(
                x=[point[0] * label_factor for point in points],
                y=[point[1] * label_factor for point in points],
                z=[0.27] * n, mode="text",
                text=[f"{angle_value:g}°"] * n,
                textfont=dict(size=17, color="#9A3412"),
                hovertemplate="정다각형의 한 내각: %{text}<extra></extra>",
            ))
        if step >= 2:
            # A에서 이웃하지 않은 꼭짓점으로 그린 대각선: 정확히 n-3개
            for index in range(2, n - 1):
                figure.add_trace(go.Scatter3d(
                    x=[points[0][0], points[index][0]],
                    y=[points[0][1], points[index][1]], z=[z, z], mode="lines",
                    line=dict(color="#E34A33", width=4, dash="dash"), hoverinfo="skip",
                ))
            figure.add_trace(go.Scatter3d(
                x=[0], y=[0], z=[0.34], mode="text",
                text=[f"삼각형 {n - 2}개"],
                textfont=dict(size=17, color="#B91C1C"), hoverinfo="skip",
            ))
    else:
        if step >= 1:
            # 1단계는 A의 외각만, 2단계부터는 모든 외각을 보여 줍니다.
            shown_indices = range(1) if step == 1 else range(n)
            label_x, label_y = [], []
            for index in shown_indices:
                vertex = points[index]
                previous = points[(index - 1) % n]
                following = points[(index + 1) % n]
                incoming = (vertex[0] - previous[0], vertex[1] - previous[1])
                length = math.hypot(*incoming)
                unit = (incoming[0] / length, incoming[1] / length)
                extension = (vertex[0] + 1.15 * unit[0], vertex[1] + 1.15 * unit[1])
                figure.add_trace(go.Scatter3d(
                    x=[vertex[0], extension[0]], y=[vertex[1], extension[1]], z=[z, z],
                    mode="lines", line=dict(color="#7C3AED", width=4, dash="dash"),
                    hoverinfo="skip",
                ))
                outgoing = (following[0] - vertex[0], following[1] - vertex[1])
                arc = angle_arc(vertex, incoming, outgoing, 0.55, 0.2)
                figure.add_trace(go.Scatter3d(
                    x=arc[0], y=arc[1], z=arc[2], mode="lines",
                    line=dict(color="#F59E0B", width=7), hoverinfo="skip",
                ))
                label_x.append(vertex[0] * 1.18)
                label_y.append(vertex[1] * 1.18)
            figure.add_trace(go.Scatter3d(
                x=label_x, y=label_y, z=[0.27] * len(label_x), mode="text",
                text=[f"{regular_exterior_angle(n):g}°"] * len(label_x),
                textfont=dict(size=17, color="#6D28D9"),
                hovertemplate="정다각형의 한 외각: %{text}<extra></extra>",
            ))
    return figure


def sector_figure(radius, angle_degrees, top_view=False, step=3):
    import plotly.graph_objects as go

    figure = base_figure(f"반지름 {radius:g}, 중심각 {angle_degrees}°인 부채꼴", top_view)
    mesh = sector_mesh(radius, angle_degrees)
    figure.add_trace(go.Mesh3d(
        x=mesh["x"], y=mesh["y"], z=mesh["z"],
        i=mesh["i"], j=mesh["j"], k=mesh["k"],
        color="#39A96B", opacity=0.42 if step >= 3 else 0.14,
        flatshading=True, hoverinfo="skip",
    ))
    ring, z = mesh["ring"], mesh["top_z"] + 0.03
    if step >= 2:
        figure.add_trace(go.Scatter3d(
            x=[p[0] for p in ring], y=[p[1] for p in ring], z=[z] * len(ring),
            mode="lines", line=dict(color="#18794E", width=9),
            hovertemplate="호<extra></extra>",
        ))
    start, finish = ring[0], ring[-1]
    figure.add_trace(go.Scatter3d(
        x=[start[0], 0, finish[0]], y=[start[1], 0, finish[1]], z=[z, z, z],
        mode="lines", line=dict(color="#12613E", width=6), hoverinfo="skip",
    ))
    arc = [(0.75 * math.cos(math.radians(angle_degrees) * index / 30),
            0.75 * math.sin(math.radians(angle_degrees) * index / 30)) for index in range(31)]
    figure.add_trace(go.Scatter3d(
        x=[p[0] for p in arc], y=[p[1] for p in arc], z=[z + 0.05] * len(arc),
        mode="lines", line=dict(color="#F59E0B", width=8), hoverinfo="skip",
    ))
    figure.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[z + 0.08], mode="markers+text",
        marker=dict(size=6, color="#B45309"), text=[f"  {angle_degrees}°"],
        textposition="top center", hoverinfo="skip",
    ))
    label_angle = math.radians(angle_degrees) / 2
    label_x = radius * 0.56 * math.cos(label_angle)
    label_y = radius * 0.56 * math.sin(label_angle)
    if step >= 2:
        values = sector_values(radius, angle_degrees)
        figure.add_trace(go.Scatter3d(
            x=[radius * 1.08 * math.cos(label_angle)],
            y=[radius * 1.08 * math.sin(label_angle)], z=[z + 0.10], mode="text",
            text=[f"호 ≈ {values['arc_length']:.2f}"],
            textfont=dict(size=16, color="#166534"), hoverinfo="skip",
        ))
    if step >= 3:
        values = sector_values(radius, angle_degrees)
        figure.add_trace(go.Scatter3d(
            x=[label_x], y=[label_y], z=[z + 0.13], mode="text",
            text=[f"넓이 ≈ {values['area']:.2f}"],
            textfont=dict(size=17, color="#14532D"), hoverinfo="skip",
        ))
    return figure


def lesson_step_content(lesson, step, n=5, radius=4.0, angle=90):
    """자동 재생 화면에 표시할 현재 단계의 제목·설명·수식을 만듭니다."""
    if step not in (1, 2, 3):
        raise ValueError("설명 단계는 1, 2, 3 중 하나여야 합니다.")

    if lesson == "interior":
        angle_value = regular_interior_angle(n)
        contents = {
            1: (
                "① 다각형 안쪽의 각을 찾아요",
                f"서로 이웃한 두 변이 도형 안쪽에서 만드는 각이 내각입니다. "
                f"정{n}각형에서는 모든 내각이 같아서 각각 {angle_value:g}°입니다.",
                "",
            ),
            2: (
                "② 한 꼭짓점에서 대각선을 그어요",
                f"A에서 이웃하지 않은 꼭짓점으로 대각선 {n - 3}개를 그으면 "
                f"정{n}각형이 삼각형 {n - 2}개로 나뉩니다.",
                rf"{n}-2={n - 2}\;\text{{개의 삼각형}}",
            ),
            3: (
                "③ 삼각형의 각을 모두 더해요",
                f"삼각형 하나의 내각의 합은 180°이므로 내각의 합은 "
                f"{interior_sum(n)}°입니다. 정{n}각형의 한 내각은 이를 {n}으로 나눕니다.",
                rf"({n}-2)\times180^\circ={interior_sum(n)}^\circ,\quad "
                rf"{interior_sum(n)}^\circ\div {n}={angle_value:g}^\circ",
            ),
        }
    elif lesson == "exterior":
        angle_value = regular_exterior_angle(n)
        contents = {
            1: (
                "① 한 변을 바깥으로 연장해요",
                f"연장한 변과 이웃한 변 사이의 바깥쪽 각이 외각입니다. "
                f"정{n}각형의 한 외각은 {angle_value:g}°입니다.",
                rf"180^\circ-{regular_interior_angle(n):g}^\circ={angle_value:g}^\circ",
            ),
            2: (
                "② 같은 방향으로 한 외각씩 돌아요",
                "각 꼭짓점에서 같은 방향의 외각을 하나씩 따라가면 출발 방향으로 되돌아옵니다. "
                "즉, 정확히 한 바퀴를 돕니다.",
                r"\text{한 바퀴}=360^\circ",
            ),
            3: (
                "③ 외각의 합은 언제나 360°예요",
                f"모든 외각의 합은 360°입니다. 정{n}각형은 외각의 크기도 모두 같으므로 "
                f"360°를 {n}으로 나누면 {angle_value:g}°입니다.",
                rf"360^\circ\div {n}={angle_value:g}^\circ",
            ),
        }
    elif lesson == "sector":
        values = sector_values(radius, angle)
        contents = {
            1: (
                "① 두 반지름이 중심각을 만들어요",
                f"부채꼴은 두 반지름과 그 사이의 호로 둘러싸인 도형입니다. "
                f"현재 중심각은 {angle}°입니다.",
                rf"\frac{{{angle}^\circ}}{{360^\circ}}\;\text{{만큼의 원}}",
            ),
            2: (
                "② 호의 길이를 구해요",
                "호의 길이는 전체 원주에서 중심각이 차지하는 비율만큼입니다.",
                rf"2\pi\times {radius:g}\times\frac{{{angle}}}{{360}}"
                rf"\approx {values['arc_length']:.2f}",
            ),
            3: (
                "③ 부채꼴의 넓이를 구해요",
                "부채꼴의 넓이도 전체 원의 넓이에서 중심각이 차지하는 비율만큼입니다.",
                rf"\pi\times {radius:g}^2\times\frac{{{angle}}}{{360}}"
                rf"\approx {values['area']:.2f}",
            ),
        }
    else:
        raise ValueError("lesson은 interior, exterior, sector 중 하나여야 합니다.")

    title, explanation, formula = contents[step]
    return {"title": title, "explanation": explanation, "formula": formula}


def show_current_step(st, lesson, step, n=5, radius=4.0, angle=90):
    """현재 자동 설명 단계만 크게 보여 줍니다."""
    content = lesson_step_content(lesson, step, n, radius, angle)
    st.progress(step / 3)
    st.markdown(f"### {content['title']}")
    st.info(content["explanation"])
    if content["formula"]:
        st.latex(content["formula"])


def show_formula_steps(st, lesson, n=None, radius=None, angle=None, step=3):
    """그림과 같은 순서로 계산 과정을 보여줍니다."""
    if lesson == "interior":
        if step >= 1:
            st.write("**① 한 꼭짓점의 내각**은 다각형 안쪽에서 두 변이 만드는 각입니다.")
        if step >= 2:
            st.write(f"**② 한 꼭짓점에서 대각선 {n - 3}개**를 그으면 삼각형이 {n - 2}개 생깁니다.")
        if step >= 3:
            st.latex(rf"({n}-2)\times180^\circ={interior_sum(n)}^\circ")
            st.write(f"따라서 정{n}각형의 한 내각은 "
                     rf"${interior_sum(n)}^\circ \div {n}={regular_interior_angle(n):g}^\circ$입니다.")
    elif lesson == "exterior":
        if step >= 1:
            st.write("**① 외각**은 한 변을 연장했을 때 이웃한 변과 이루는 바깥쪽 각입니다.")
        if step >= 2:
            st.write("**② 각 꼭짓점에서 같은 방향으로 한 외각씩** 더하면 정확히 한 바퀴 돕니다.")
        if step >= 3:
            st.latex(r"\text{외각의 합}=360^\circ")
            st.write(f"정{n}각형의 한 외각은 "
                     rf"$360^\circ \div {n}={regular_exterior_angle(n):g}^\circ$입니다.")
    else:
        values = sector_values(radius, angle)
        if step >= 1:
            st.write(f"**① 중심각 {angle}°**는 원 한 바퀴 360°의 "
                     f"$\frac{{{angle}}}{{360}}$입니다.")
        if step >= 2:
            st.write("**② 호의 길이**는 원주의 같은 비율입니다.")
            st.latex(rf"2\pi\times {radius:g}\times\frac{{{angle}}}{{360}}"
                     rf"\approx {values['arc_length']:.2f}")
        if step >= 3:
            st.write("**③ 부채꼴의 넓이**는 원 넓이의 같은 비율입니다.")
            st.latex(rf"\pi\times {radius:g}^2\times\frac{{{angle}}}{{360}}"
                     rf"\approx {values['area']:.2f}")


def main():
    import streamlit as st

    st.set_page_config(page_title="틈새 공부 3D 수학 교실", page_icon="📐", layout="wide")
    st.title("📐 틈새 공부 3D 수학 교실")
    st.subheader("① 다각형의 내각·외각·부채꼴")
    st.caption(
        "자동 설명이 1→2→3단계로 반복됩니다. 그림을 마우스 또는 손가락으로 돌려보세요. "
        "계산값의 단위는 도(°)와 길이 단위입니다."
    )

    lesson_label = st.radio(
        "학습할 개념", ["다각형의 내각", "다각형의 외각", "부채꼴"],
        horizontal=True,
    )

    lesson_code = {
        "다각형의 내각": "interior",
        "다각형의 외각": "exterior",
        "부채꼴": "sector",
    }[lesson_label]

    if "auto_step" not in st.session_state:
        st.session_state.auto_step = 1
    if st.session_state.get("last_lesson") != lesson_code:
        st.session_state.auto_step = 1
        st.session_state.last_lesson = lesson_code

    control1, control2, control3, control4 = st.columns([1.1, 1.2, 1.4, 1.8])
    with control1:
        auto_play = st.toggle("▶ 자동 설명 재생", value=True)
    with control2:
        speed = st.slider("단계 전환(초)", 1.5, 6.0, 3.0, 0.5,
                          disabled=not auto_play)
    with control3:
        top_view = st.checkbox(
            "위에서 정확히 보기", value=False,
            help="각의 모양을 정면에서 봅니다. 그래도 그림을 다시 돌릴 수 있습니다.",
        )
    with control4:
        manual_step = st.slider(
            "직접 선택할 설명 단계", 1, 3, 1,
            disabled=auto_play,
            help="자동 재생을 끄면 원하는 단계를 직접 선택할 수 있습니다.",
        )

    supports_auto_play = hasattr(st, "fragment")
    effective_auto_play = auto_play and supports_auto_play
    if auto_play and not supports_auto_play:
        st.warning(
            "자동 재생에는 Streamlit 1.37 이상이 필요합니다. 터미널에서 "
            "`python -m pip install --upgrade streamlit`을 실행해 주세요."
        )

    run_interval = f"{speed}s" if effective_auto_play else None
    player_decorator = (
        st.fragment(run_every=run_interval)
        if supports_auto_play
        else (lambda function: function)
    )

    @player_decorator
    def show_simulation():
        step = st.session_state.auto_step if effective_auto_play else manual_step
        st.markdown(
            f"**현재 {step}단계** · "
            + (f"{speed:g}초마다 자동 전환 중" if effective_auto_play else "직접 탐색 중")
        )

        left, right = st.columns([1, 2], gap="large")
        with left:
            if lesson_code == "sector":
                radius = st.slider("반지름 r", 1.0, 10.0, 4.0, 0.5, key="sector_radius")
                angle = st.slider("중심각 θ", 10, 350, 90, 5, key="sector_angle")
                values = sector_values(radius, angle)
                metric1, metric2 = st.columns(2)
                metric1.metric("호의 길이", f"{values['arc_length']:.2f}")
                metric2.metric("부채꼴의 넓이", f"{values['area']:.2f}")
                show_current_step(st, "sector", step, radius=radius, angle=angle)
            else:
                n = st.slider(
                    "다각형의 변의 수 n", 3, 12, 5, key="polygon_sides",
                    help="처음에는 오각형(n=5)으로 관찰해 보세요.",
                )
                if lesson_code == "interior":
                    metric1, metric2 = st.columns(2)
                    metric1.metric("내각의 합", f"{interior_sum(n)}°")
                    metric2.metric(f"정{n}각형의 한 내각", f"{regular_interior_angle(n):g}°")
                    show_current_step(st, "interior", step, n=n)
                else:
                    metric1, metric2 = st.columns(2)
                    metric1.metric("외각의 합", "360°")
                    metric2.metric(f"정{n}각형의 한 외각", f"{regular_exterior_angle(n):g}°")
                    show_current_step(st, "exterior", step, n=n)

        with right:
            if lesson_code == "sector":
                figure = sector_figure(radius, angle, top_view, step)
            elif lesson_code == "interior":
                figure = polygon_figure(n, "interior", step, top_view)
            else:
                figure = polygon_figure(n, "exterior", step, top_view)
            st.plotly_chart(figure, width="stretch", config={"displaylogo": False})
            if lesson_code == "interior" and n == 5:
                st.success("오각형 안쪽의 주황색 호와 **108°** 표시를 확인하세요.")
            st.caption(
                "파란색/초록색 면은 얇은 3D 수학판입니다. 회전 때문에 각이 달라 보일 수 있지만 "
                "계산된 각도는 변하지 않습니다."
            )

        # 화면을 그린 뒤 다음 자동 실행에서 사용할 단계를 준비합니다.
        if effective_auto_play:
            st.session_state.auto_step = 1 if step == 3 else step + 1

    show_simulation()

    with st.expander("꼭 기억할 것"):
        st.markdown("""
- 다각형의 내각의 합: $$(n-2)\\times180^\\circ$$
- 다각형의 외각의 합: $$360^\\circ$$  
  단, 각 꼭짓점에서 **같은 방향으로 한 외각씩** 선택합니다.
- 정다각형의 한 내각: $$\\frac{(n-2)\\times180^\\circ}{n}$$
- 정다각형의 한 외각: $$\\frac{360^\\circ}{n}$$
- 호의 길이: $$2\\pi r\\times\\frac{\\theta}{360^\\circ}$$
- 부채꼴의 넓이: $$\\pi r^2\\times\\frac{\\theta}{360^\\circ}$$

‘한 내각’과 ‘한 외각’을 변의 수로 나누는 공식은 **정다각형일 때만** 사용할 수 있습니다.
""")


if __name__ == "__main__":
    main()
