"""틈새 공부 3D 수학 교실 ③: 겉넓이와 부피.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson12_surface_volume_3d.py
"""

import math


SHAPE_LABELS = {
    "직육면체 기둥": "prism",
    "사각뿔": "pyramid",
    "원기둥": "cylinder",
    "원뿔": "cone",
    "구": "sphere",
}

STEP_TITLES = {
    1: "길이와 모양 찾기",
    2: "밑넓이부터 구하기",
    3: "겉넓이 만들기",
    4: "부피를 층층이 채우기",
    5: "공식 완성하기",
}


def format_number(value):
    """계산값을 학습 화면에 알맞게 표시합니다."""
    value = float(value)
    if math.isclose(value, round(value), abs_tol=1e-9):
        return f"{value:.0f}"
    return f"{value:.1f}"


def measurement_data(kind, a=4.0, b=3.0, h=5.0, r=2.0):
    """도형별 겉넓이·부피와 설명에 필요한 값을 계산합니다."""
    values = {"kind": kind, "a": float(a), "b": float(b), "h": float(h), "r": float(r)}

    if kind == "prism":
        base_area = a * b
        perimeter = 2 * (a + b)
        lateral_area = perimeter * h
        surface_area = 2 * base_area + lateral_area
        volume = base_area * h
        values.update(
            name="직육면체 기둥",
            child_name="똑같은 직사각형을 높이만큼 곧게 쌓은 상자",
            base_area=base_area,
            perimeter=perimeter,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
            surface_formula=r"S=2B+Ph",
            volume_formula=r"V=Bh",
            base_formula=rf"B={format_number(a)}\times {format_number(b)}={format_number(base_area)}",
            surface_calc=(
                rf"S=2\times {format_number(base_area)}+{format_number(perimeter)}"
                rf"\times {format_number(h)}={format_number(surface_area)}"
            ),
            volume_calc=(
                rf"V={format_number(base_area)}\times {format_number(h)}={format_number(volume)}"
            ),
        )
    elif kind == "pyramid":
        base_area = a * a
        perimeter = 4 * a
        slant_height = math.sqrt(h * h + (a / 2) ** 2)
        lateral_area = 2 * a * slant_height
        surface_area = base_area + lateral_area
        volume = base_area * h / 3
        values.update(
            name="사각뿔",
            child_name="정사각형 밑면에서 꼭대기 한 점으로 모이는 뾰족한 도형",
            base_area=base_area,
            perimeter=perimeter,
            slant_height=slant_height,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
            surface_formula=r"S=B+\frac{1}{2}Pl",
            volume_formula=r"V=\frac{1}{3}Bh",
            base_formula=rf"B={format_number(a)}\times {format_number(a)}={format_number(base_area)}",
            surface_calc=(
                rf"S={format_number(base_area)}+2\times {format_number(a)}"
                rf"\times {format_number(slant_height)}\approx {format_number(surface_area)}"
            ),
            volume_calc=(
                rf"V=\frac{{{format_number(base_area)}\times {format_number(h)}}}{{3}}"
                rf"\approx {format_number(volume)}"
            ),
        )
    elif kind == "cylinder":
        base_area = math.pi * r * r
        perimeter = 2 * math.pi * r
        lateral_area = perimeter * h
        surface_area = 2 * base_area + lateral_area
        volume = base_area * h
        values.update(
            name="원기둥",
            child_name="똑같은 원을 높이만큼 곧게 쌓은 둥근 기둥",
            base_area=base_area,
            perimeter=perimeter,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
            surface_formula=r"S=2\pi r^2+2\pi rh",
            volume_formula=r"V=\pi r^2h",
            base_formula=rf"B=\pi\times {format_number(r)}^2={format_number(base_area)}",
            surface_calc=(
                rf"S=2\pi\times {format_number(r)}^2+2\pi\times {format_number(r)}"
                rf"\times {format_number(h)}\approx {format_number(surface_area)}"
            ),
            volume_calc=(
                rf"V=\pi\times {format_number(r)}^2\times {format_number(h)}"
                rf"\approx {format_number(volume)}"
            ),
        )
    elif kind == "cone":
        base_area = math.pi * r * r
        slant_height = math.sqrt(r * r + h * h)
        lateral_area = math.pi * r * slant_height
        surface_area = base_area + lateral_area
        volume = base_area * h / 3
        values.update(
            name="원뿔",
            child_name="원 모양 밑면에서 꼭대기 한 점으로 모이는 둥근 뿔",
            base_area=base_area,
            slant_height=slant_height,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
            surface_formula=r"S=\pi r^2+\pi rl",
            volume_formula=r"V=\frac{1}{3}\pi r^2h",
            base_formula=rf"B=\pi\times {format_number(r)}^2={format_number(base_area)}",
            surface_calc=(
                rf"S=\pi\times {format_number(r)}^2+\pi\times {format_number(r)}"
                rf"\times {format_number(slant_height)}\approx {format_number(surface_area)}"
            ),
            volume_calc=(
                rf"V=\frac{{\pi\times {format_number(r)}^2\times {format_number(h)}}}{{3}}"
                rf"\approx {format_number(volume)}"
            ),
        )
    elif kind == "sphere":
        great_circle_area = math.pi * r * r
        surface_area = 4 * great_circle_area
        volume = 4 * math.pi * r ** 3 / 3
        values.update(
            name="구",
            child_name="어느 방향에서 보아도 둥근 공 모양",
            great_circle_area=great_circle_area,
            surface_area=surface_area,
            volume=volume,
            surface_formula=r"S=4\pi r^2",
            volume_formula=r"V=\frac{4}{3}\pi r^3",
            base_formula=rf"\text{{큰 원의 넓이}}=\pi\times {format_number(r)}^2={format_number(great_circle_area)}",
            surface_calc=(
                rf"S=4\pi\times {format_number(r)}^2\approx {format_number(surface_area)}"
            ),
            volume_calc=(
                rf"V=\frac{{4}}{{3}}\pi\times {format_number(r)}^3"
                rf"\approx {format_number(volume)}"
            ),
        )
    else:
        raise ValueError("지원하지 않는 도형입니다.")
    return values


def face_triangles(vertex_count):
    return [(0, index, index + 1) for index in range(1, vertex_count - 1)]


def base_figure(title, top_view=False, height=345):
    import plotly.graph_objects as go

    # 휴대폰에서도 도형 전체가 보이도록 카메라를 조금 멀리 둡니다.
    eye = dict(x=0.01, y=0.01, z=3.0) if top_view else dict(x=1.85, y=1.85, z=1.45)
    figure = go.Figure()
    figure.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=15)),
        height=height,
        margin=dict(l=0, r=0, t=38, b=0),
        showlegend=False,
        scene=dict(
            camera=dict(
                eye=eye,
                projection=dict(type="orthographic"),
            ),
            aspectmode="cube",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def fit_mobile_view(figure, x_extent, y_extent, z_min, z_max, padding=1.10):
    """평면만 보이는 장면도 갑자기 확대되지 않도록 3D 범위를 고정합니다."""
    x_extent = max(float(x_extent), 0.5)
    y_extent = max(float(y_extent), 0.5)
    z_min, z_max = float(z_min), float(z_max)
    z_center = (z_min + z_max) / 2
    half_span = max(x_extent, y_extent, (z_max - z_min) / 2, 1.0) * float(padding)

    figure.update_layout(
        scene=dict(
            aspectmode="cube",
            xaxis=dict(range=[-half_span, half_span], visible=False),
            yaxis=dict(range=[-half_span, half_span], visible=False),
            zaxis=dict(
                range=[z_center - half_span, z_center + half_span],
                visible=False,
            ),
        )
    )
    return figure


def add_face(figure, points, color, opacity=0.55, label="면"):
    import plotly.graph_objects as go

    triangles = face_triangles(len(points))
    figure.add_trace(go.Mesh3d(
        x=[point[0] for point in points],
        y=[point[1] for point in points],
        z=[point[2] for point in points],
        i=[triangle[0] for triangle in triangles],
        j=[triangle[1] for triangle in triangles],
        k=[triangle[2] for triangle in triangles],
        color=color,
        opacity=opacity,
        flatshading=True,
        hovertemplate=f"{label}<extra></extra>",
    ))


def add_polyline(figure, points, color="#1D4ED8", width=6, dash=None, label="선"):
    import plotly.graph_objects as go

    figure.add_trace(go.Scatter3d(
        x=[point[0] for point in points],
        y=[point[1] for point in points],
        z=[point[2] for point in points],
        mode="lines",
        line=dict(color=color, width=width, dash=dash),
        hovertemplate=f"{label}<extra></extra>",
    ))


def add_text(figure, point, text, color="#111827", size=15):
    import plotly.graph_objects as go

    figure.add_trace(go.Scatter3d(
        x=[point[0]], y=[point[1]], z=[point[2]],
        mode="text", text=[text], textfont=dict(color=color, size=size),
        hoverinfo="skip",
    ))


def rectangle(z, a, b):
    return [(-a / 2, -b / 2, z), (a / 2, -b / 2, z),
            (a / 2, b / 2, z), (-a / 2, b / 2, z)]


def add_box(figure, a, b, h, opacity=0.30, base_color="#60A5FA", side_color="#FBBF24"):
    bottom = rectangle(0, a, b)
    top = rectangle(h, a, b)
    faces = [
        (bottom, base_color, "아랫면"),
        (top, base_color, "윗면"),
        ([bottom[0], bottom[1], top[1], top[0]], side_color, "옆면"),
        ([bottom[1], bottom[2], top[2], top[1]], side_color, "옆면"),
        ([bottom[2], bottom[3], top[3], top[2]], side_color, "옆면"),
        ([bottom[3], bottom[0], top[0], top[3]], side_color, "옆면"),
    ]
    for points, color, label in faces:
        add_face(figure, points, color, opacity, label)
        add_polyline(figure, [*points, points[0]], width=4, label=label)


def circle_points(radius, z, samples=72):
    return [
        (radius * math.cos(2 * math.pi * index / samples),
         radius * math.sin(2 * math.pi * index / samples), z)
        for index in range(samples)
    ]


def add_disk(figure, radius, z, color="#60A5FA", opacity=0.55, label="원"):
    ring = circle_points(radius, z)
    points = [(0, 0, z), *ring]
    triangles = [(0, index + 1, ((index + 1) % len(ring)) + 1) for index in range(len(ring))]
    import plotly.graph_objects as go

    figure.add_trace(go.Mesh3d(
        x=[point[0] for point in points],
        y=[point[1] for point in points],
        z=[point[2] for point in points],
        i=[triangle[0] for triangle in triangles],
        j=[triangle[1] for triangle in triangles],
        k=[triangle[2] for triangle in triangles],
        color=color, opacity=opacity, flatshading=True,
        hovertemplate=f"{label}<extra></extra>",
    ))
    add_polyline(figure, [*ring, ring[0]], width=4, label=label)


def add_cylinder_side(figure, radius, height, color="#FBBF24", opacity=0.35):
    import plotly.graph_objects as go

    angles = [2 * math.pi * index / 72 for index in range(73)]
    z_values = [0, height]
    x = [[radius * math.cos(angle) for angle in angles] for _ in z_values]
    y = [[radius * math.sin(angle) for angle in angles] for _ in z_values]
    z = [[current_z] * len(angles) for current_z in z_values]
    figure.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, color], [1, color]], showscale=False,
        opacity=opacity, hovertemplate="둥근 옆면<extra></extra>",
    ))


def add_cone_side(figure, radius, height, color="#FBBF24", opacity=0.40):
    import plotly.graph_objects as go

    angles = [2 * math.pi * index / 72 for index in range(73)]
    levels = [index / 20 for index in range(21)]
    x, y, z = [], [], []
    for fraction in levels:
        current_radius = radius * (1 - fraction)
        x.append([current_radius * math.cos(angle) for angle in angles])
        y.append([current_radius * math.sin(angle) for angle in angles])
        z.append([height * fraction] * len(angles))
    figure.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, color], [1, color]], showscale=False,
        opacity=opacity, hovertemplate="원뿔의 옆면<extra></extra>",
    ))


def add_sphere(figure, radius, color="#34D399", opacity=0.55):
    import plotly.graph_objects as go

    longitudes = [2 * math.pi * index / 48 for index in range(49)]
    latitudes = [-math.pi / 2 + math.pi * index / 30 for index in range(31)]
    x = [[radius * math.cos(latitude) * math.cos(longitude) for longitude in longitudes]
         for latitude in latitudes]
    y = [[radius * math.cos(latitude) * math.sin(longitude) for longitude in longitudes]
         for latitude in latitudes]
    z = [[radius * math.sin(latitude)] * len(longitudes) for latitude in latitudes]
    figure.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, color], [1, color]], showscale=False,
        opacity=opacity, hovertemplate="구의 둥근 겉면<extra></extra>",
    ))


def add_height_and_radius(figure, h=None, r=None, a=None, b=None, apex=False):
    """도형 위에 높이·반지름·밑변 표시를 더합니다."""
    if h is not None:
        add_polyline(figure, [(0, 0, 0), (0, 0, h)], "#EF4444", 7, "dash", "높이")
        add_text(figure, (0.15, 0, h / 2), f"높이 h={format_number(h)}", "#B91C1C", 14)
    if r is not None:
        add_polyline(figure, [(0, 0, 0), (r, 0, 0)], "#7C3AED", 7, None, "반지름")
        add_text(figure, (r / 2, -0.15, 0.12), f"r={format_number(r)}", "#6D28D9", 14)
    if a is not None:
        y = -b / 2 if b is not None else -a / 2
        add_text(figure, (0, y - 0.25, 0), f"가로={format_number(a)}", "#1E3A8A", 13)
    if b is not None:
        add_text(figure, (a / 2 + 0.25, 0, 0), f"세로={format_number(b)}", "#1E3A8A", 13)


def prism_figure(step, values, top_view=False):
    a, b, h = values["a"], values["b"], values["h"]
    figure = base_figure(
        f"{step}단계 · {STEP_TITLES[step]}",
        top_view or step == 2,
    )

    if step == 2:
        add_face(figure, rectangle(0, a, b), "#93C5FD", 0.88, "밑면 B")
        add_polyline(figure, [*rectangle(0, a, b), rectangle(0, a, b)[0]], width=6, label="밑면")
        add_text(figure, (0, 0, 0.15), "밑넓이 B = 가로 × 세로", "#172554", 16)
    elif step == 4:
        add_box(figure, a, b, h, opacity=0.10)
        for fraction in (0.15, 0.32, 0.49, 0.66, 0.83):
            add_face(figure, rectangle(h * fraction, a * 0.96, b * 0.96), "#38BDF8", 0.30, "넓이가 같은 한 층")
        add_text(figure, (0, 0, h + 0.35), "같은 밑면이 높이만큼 쌓여요", "#075985", 15)
    else:
        add_box(figure, a, b, h, opacity=0.55 if step == 3 else 0.34)
        if step == 3:
            add_text(figure, (0, 0, h + 0.38), "파란 밑면 2개 + 노란 옆면 4개", "#92400E", 15)

    if step == 1:
        add_height_and_radius(figure, h=h, a=a, b=b)
    if step == 5:
        add_text(figure, (0, 0, h + 0.45), "S = 2B + Ph   ·   V = Bh", "#111827", 16)
    view_height = 0.45 if step == 2 else h + 0.75
    return fit_mobile_view(figure, a / 2 + 0.35, b / 2 + 0.35, 0, view_height)


def pyramid_faces(a, h):
    base = rectangle(0, a, a)
    apex = (0, 0, h)
    return base, [[base[index], base[(index + 1) % 4], apex] for index in range(4)]


def pyramid_figure(step, values, top_view=False):
    a, h = values["a"], values["h"]
    figure = base_figure(
        f"{step}단계 · {STEP_TITLES[step]}",
        top_view or step == 2,
    )
    base, sides = pyramid_faces(a, h)

    if step == 2:
        add_face(figure, base, "#93C5FD", 0.88, "밑면 B")
        add_polyline(figure, [*base, base[0]], width=6, label="밑면")
        add_text(figure, (0, 0, 0.14), "밑넓이 B = 한 변 × 한 변", "#172554", 16)
    else:
        add_face(figure, base, "#60A5FA", 0.38, "정사각형 밑면")
        for index, side in enumerate(sides):
            add_face(figure, side, "#FBBF24" if step == 3 else "#A78BFA", 0.48, f"삼각형 옆면 {index + 1}")
            add_polyline(figure, [*side, side[0]], width=4, label="모서리")
        add_polyline(figure, [*base, base[0]], width=4, label="밑면 모서리")

    if step == 1:
        add_height_and_radius(figure, h=h, a=a, b=a)
    elif step == 3:
        add_polyline(figure, [(0, -a / 2, 0), (0, 0, h)], "#F97316", 7, None, "빗면 높이")
        add_text(figure, (0, -a / 4, h / 2), f"빗면 높이 l={format_number(values['slant_height'])}", "#C2410C", 14)
    elif step == 4:
        add_box(figure, a, a, h, opacity=0.08, base_color="#CBD5E1", side_color="#CBD5E1")
        for fraction in (0.18, 0.36, 0.54, 0.72):
            size = a * (1 - fraction)
            add_face(figure, rectangle(h * fraction, size, size), "#A78BFA", 0.28, "점점 작아지는 한 층")
        add_text(figure, (0, 0, h + 0.45), "같은 기둥 부피의 1/3", "#6D28D9", 16)
    elif step == 5:
        add_text(figure, (0, 0, h + 0.45), "S = B + ½Pl   ·   V = ⅓Bh", "#111827", 16)
    view_height = 0.45 if step == 2 else h + 0.80
    return fit_mobile_view(figure, a / 2 + 0.35, a / 2 + 0.35, 0, view_height)


def cylinder_figure(step, values, top_view=False):
    r, h = values["r"], values["h"]
    figure = base_figure(
        f"{step}단계 · {STEP_TITLES[step]}",
        top_view or step == 2,
    )

    if step == 2:
        add_disk(figure, r, 0, "#93C5FD", 0.90, "밑면 B")
        add_text(figure, (0, 0, 0.18), "밑넓이 B = πr²", "#172554", 17)
    else:
        add_cylinder_side(figure, r, h, opacity=0.48 if step == 3 else 0.26)
        add_disk(figure, r, 0, "#60A5FA", 0.45, "아랫면")
        add_disk(figure, r, h, "#60A5FA", 0.45, "윗면")

    if step == 1:
        add_height_and_radius(figure, h=h, r=r)
    elif step == 3:
        add_text(figure, (0, 0, h + 0.38), "원 2개 + 직사각형이 되는 옆면", "#92400E", 15)
    elif step == 4:
        for fraction in (0.14, 0.30, 0.46, 0.62, 0.78, 0.94):
            add_disk(figure, r * 0.96, h * fraction, "#22D3EE", 0.22, "넓이가 같은 원 한 층")
        add_text(figure, (0, 0, h + 0.38), "같은 원이 높이만큼 쌓여요", "#0E7490", 15)
    elif step == 5:
        add_text(figure, (0, 0, h + 0.40), "S = 2πr² + 2πrh   ·   V = πr²h", "#111827", 15)
    view_height = 0.45 if step == 2 else h + 0.72
    return fit_mobile_view(figure, r + 0.30, r + 0.30, 0, view_height)


def cone_figure(step, values, top_view=False):
    r, h = values["r"], values["h"]
    figure = base_figure(
        f"{step}단계 · {STEP_TITLES[step]}",
        top_view or step == 2,
    )

    if step == 2:
        add_disk(figure, r, 0, "#93C5FD", 0.90, "밑면 B")
        add_text(figure, (0, 0, 0.18), "밑넓이 B = πr²", "#172554", 17)
    else:
        add_cone_side(figure, r, h, opacity=0.52 if step == 3 else 0.35)
        add_disk(figure, r, 0, "#60A5FA", 0.48, "원 모양 밑면")

    if step == 1:
        add_height_and_radius(figure, h=h, r=r)
    elif step == 3:
        add_polyline(figure, [(r, 0, 0), (0, 0, h)], "#F97316", 7, None, "모선")
        add_text(figure, (r / 2, 0, h / 2), f"빗면 길이 l={format_number(values['slant_height'])}", "#C2410C", 14)
    elif step == 4:
        add_cylinder_side(figure, r, h, "#CBD5E1", 0.09)
        add_disk(figure, r, h, "#CBD5E1", 0.08, "비교 원기둥 윗면")
        for fraction in (0.18, 0.36, 0.54, 0.72):
            add_disk(figure, r * (1 - fraction), h * fraction, "#FBBF24", 0.23, "점점 작아지는 원 한 층")
        add_text(figure, (0, 0, h + 0.42), "같은 원기둥 부피의 1/3", "#B45309", 16)
    elif step == 5:
        add_text(figure, (0, 0, h + 0.42), "S = πr² + πrl   ·   V = ⅓πr²h", "#111827", 15)
    view_height = 0.45 if step == 2 else h + 0.76
    return fit_mobile_view(figure, r + 0.30, r + 0.30, 0, view_height)


def sphere_figure(step, values, top_view=False):
    r = values["r"]
    figure = base_figure(f"{step}단계 · {STEP_TITLES[step]}", top_view)
    add_sphere(figure, r, opacity=0.68 if step == 3 else 0.46)

    if step == 1:
        add_polyline(figure, [(0, 0, 0), (r, 0, 0)], "#7C3AED", 8, None, "반지름")
        add_text(figure, (r / 2, 0, 0.18), f"반지름 r={format_number(r)}", "#6D28D9", 15)
    elif step == 2:
        ring = circle_points(r, 0)
        add_polyline(figure, [*ring, ring[0]], "#2563EB", 8, None, "구의 가장 큰 원")
        add_text(figure, (0, 0, r + 0.30), "가장 큰 원의 넓이 = πr²", "#1E3A8A", 15)
    elif step == 3:
        for axis in ("xz", "yz"):
            points = []
            for index in range(73):
                angle = 2 * math.pi * index / 72
                if axis == "xz":
                    points.append((r * math.cos(angle), 0, r * math.sin(angle)))
                else:
                    points.append((0, r * math.cos(angle), r * math.sin(angle)))
            add_polyline(figure, points, "#F59E0B", 5, None, "구의 큰 원")
        add_text(figure, (0, 0, r + 0.35), "겉넓이 = 큰 원 4개의 넓이", "#92400E", 15)
    elif step == 4:
        add_cylinder_side(figure, r, 2 * r, "#CBD5E1", 0.13)
        # 비교 원기둥의 중심이 구의 중심과 같도록 z좌표를 아래로 옮깁니다.
        figure.data[-1].z = [[z - r for z in row] for row in figure.data[-1].z]
        add_disk(figure, r, -r, "#CBD5E1", 0.10, "비교 원기둥 아랫면")
        add_disk(figure, r, r, "#CBD5E1", 0.10, "비교 원기둥 윗면")
        add_text(figure, (0, 0, r + 0.38), "구 = 둘러싼 원기둥 부피의 2/3", "#047857", 15)
    elif step == 5:
        add_text(figure, (0, 0, r + 0.38), "S = 4πr²   ·   V = ⁴⁄₃πr³", "#111827", 16)
    return fit_mobile_view(figure, r + 0.32, r + 0.32, -r - 0.20, r + 0.60)


def lesson_content(kind, step, values):
    """수학을 어려워하는 학생도 따라갈 수 있는 단계 설명입니다."""
    name = values["name"]
    if step == 1:
        if kind == "sphere":
            explanation = (
                "구에는 밑면과 높이가 없습니다. 중심에서 겉면까지의 거리인 "
                "반지름 r 하나만 알면 크기를 나타낼 수 있어요."
            )
            key = "먼저 중심과 반지름을 찾습니다."
        else:
            explanation = (
                f"{name}은(는) {values['child_name']}입니다. "
                "빨간 점선은 밑면과 밑면 또는 꼭대기 사이의 수직 높이 h예요."
            )
            key = "비스듬한 선이 아니라 수직 높이를 사용합니다."
        formula = None
    elif step == 2:
        if kind == "sphere":
            explanation = (
                "구의 한가운데를 자르면 가장 큰 원이 나옵니다. "
                "이 큰 원의 넓이 πr²가 구의 공식을 이해하는 기준이 돼요."
            )
            key = "구의 가장 큰 원 넓이는 πr²입니다."
        else:
            explanation = (
                "부피를 바로 계산하지 말고 파란 밑면부터 봅니다. "
                "밑면 한 장의 넓이를 B라고 약속하면 복잡한 공식이 짧아져요."
            )
            key = "B는 밑면 한 장의 넓이입니다."
        formula = values["base_formula"]
    elif step == 3:
        if kind == "prism":
            explanation = (
                "겉넓이는 상자의 바깥을 종이로 완전히 감싸는 데 필요한 넓이입니다. "
                "똑같은 밑면 2개와 네 옆면을 모두 더해요."
            )
            key = "옆면의 합은 밑면 둘레 P × 높이 h입니다."
        elif kind == "pyramid":
            explanation = (
                "정사각형 밑면 1개와 삼각형 옆면 4개를 모두 더합니다. "
                "삼각형 넓이에는 수직 높이 h가 아니라 주황색 빗면 높이 l을 써요."
            )
            key = "겉넓이 계산에서는 빗면 높이 l을 사용합니다."
        elif kind == "cylinder":
            explanation = (
                "원기둥의 겉면은 원 2개와 둥근 옆면입니다. "
                "둥근 옆면을 펼치면 가로가 원의 둘레 2πr, 세로가 h인 직사각형이 돼요."
            )
            key = "옆넓이 = 원의 둘레 2πr × 높이 h"
        elif kind == "cone":
            explanation = (
                "원뿔의 겉면은 원 1개와 부채꼴처럼 펼쳐지는 옆면입니다. "
                "옆넓이에는 주황색 빗면 길이 l이 필요해요."
            )
            key = "원뿔의 옆넓이는 πrl입니다."
        else:
            explanation = (
                "구의 껍질을 잘게 나누어 넓이를 모으면, 반지름이 같은 큰 원 "
                "4개의 넓이와 같습니다. 그래서 4πr²이에요."
            )
            key = "구의 겉넓이 = 큰 원 4개의 넓이"
        formula = values["surface_formula"]
    elif step == 4:
        if kind in ("prism", "cylinder"):
            explanation = (
                "넓이가 같은 밑면을 얇은 종이처럼 계속 쌓는 모습을 보세요. "
                "한 층의 넓이 B를 높이 h만큼 쌓으므로 부피는 B×h입니다."
            )
            key = "기둥의 부피 = 밑넓이 × 높이"
        elif kind in ("pyramid", "cone"):
            explanation = (
                "같은 밑면과 같은 높이를 가진 기둥과 비교합니다. 물이나 모래로 실험하면 "
                f"{name} 모양 그릇 3번이 기둥 1개를 채워요."
            )
            key = "뿔의 부피 = 같은 기둥 부피의 1/3"
        else:
            explanation = (
                "반지름 r인 구를 반지름 r, 높이 2r인 원기둥에 꼭 맞게 넣어 비교합니다. "
                "구의 부피는 이 원기둥 부피의 2/3입니다."
            )
            key = "구의 부피 = 둘러싼 원기둥 부피의 2/3"
        formula = values["volume_formula"]
    elif step == 5:
        explanation = (
            "이제 그림에서 찾은 길이를 공식에 넣어 계산합니다. "
            "겉넓이는 제곱단위(㎠), 부피는 세제곱단위(㎤)라는 점도 꼭 확인하세요."
        )
        key = (
            f"겉넓이 약 {format_number(values['surface_area'])}㎠ · "
            f"부피 약 {format_number(values['volume'])}㎤"
        )
        formula = None
    else:
        raise ValueError("설명 단계는 1부터 5까지입니다.")

    return {
        "title": f"{step}. {STEP_TITLES[step]}",
        "explanation": explanation,
        "key": key,
        "formula": formula,
    }


def make_figure(kind, step, values, top_view=False):
    if kind == "prism":
        return prism_figure(step, values, top_view)
    if kind == "pyramid":
        return pyramid_figure(step, values, top_view)
    if kind == "cylinder":
        return cylinder_figure(step, values, top_view)
    if kind == "cone":
        return cone_figure(step, values, top_view)
    if kind == "sphere":
        return sphere_figure(step, values, top_view)
    raise ValueError("지원하지 않는 도형입니다.")


def show_step_card(st, kind, step, values):
    content = lesson_content(kind, step, values)
    st.progress(step / 5)
    st.markdown(f"### {content['title']}")
    st.info(content["explanation"])
    if content["formula"]:
        st.latex(content["formula"])
    if step == 5:
        first, second = st.columns(2)
        first.markdown("**겉넓이 계산**")
        first.latex(values["surface_calc"])
        second.markdown("**부피 계산**")
        second.latex(values["volume_calc"])
    st.success(f"⭐ {content['key']}")


def main():
    import streamlit as st

    st.set_page_config(
        page_title="틈새 공부 3D 겉넓이·부피 교실",
        page_icon="📦",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
<style>
    .block-container {max-width: 720px; padding-top: 0.65rem; padding-bottom: 1rem;}
    h1 {font-size: 1.72rem !important; line-height: 1.2 !important; margin-bottom: 0.15rem !important;}
    h2 {font-size: 1.24rem !important;}
    h3 {font-size: 1.06rem !important;}
    [data-testid="stAlert"] {padding: 0.65rem 0.8rem;}
    [data-testid="stMetricValue"] {font-size: 1.55rem;}
    @media (max-width: 640px) {
        .block-container {padding: 0.35rem 0.48rem 0.85rem;}
        h1 {font-size: 1.32rem !important;}
        h2 {font-size: 1.03rem !important;}
        h3 {font-size: 0.96rem !important;}
        p, label, [data-testid="stCaptionContainer"] {font-size: 0.86rem !important;}
        [data-testid="stAlert"] {font-size: 0.84rem; padding: 0.52rem 0.62rem;}
        [data-testid="stMetricValue"] {font-size: 1.25rem;}
        .stButton button {min-height: 2.1rem; padding: 0.2rem 0.35rem;}
        [data-testid="stPlotlyChart"] {max-width: 100% !important; overflow: hidden;}
    }
</style>
""", unsafe_allow_html=True)

    st.title("📦 틈새 공부 3D 수학 교실")
    st.subheader("③ 겉넓이와 부피")
    st.caption(
        "처음부터 자동으로 재생됩니다. 멈추고 싶을 때 ‘일시정지’를 누르세요. "
        "그림은 손가락으로 돌리고 확대할 수 있습니다."
    )

    shape_label = st.selectbox("공부할 도형", list(SHAPE_LABELS))
    kind = SHAPE_LABELS[shape_label]

    if "surface_volume_step" not in st.session_state:
        st.session_state.surface_volume_step = 1
    if st.session_state.get("surface_volume_last_shape") != kind:
        st.session_state.surface_volume_step = 1
        st.session_state.surface_volume_last_shape = kind

    first_control, second_control = st.columns(2)
    with first_control:
        paused = st.toggle("⏸ 일시정지", value=False)
    with second_control:
        top_view = st.checkbox("⬇ 위에서 보기", value=False)

    speed = st.slider(
        "장면 전환 시간(초)", 2.0, 7.0, 3.5, 0.5,
        disabled=paused,
    )

    with st.expander("📏 도형의 크기 바꾸기"):
        if kind == "prism":
            a = st.slider("가로 a", 2.0, 6.0, 4.0, 0.5)
            b = st.slider("세로 b", 2.0, 6.0, 3.0, 0.5)
            h = st.slider("높이 h", 2.0, 7.0, 5.0, 0.5)
            r = 2.0
        elif kind == "pyramid":
            a = st.slider("밑면 한 변 a", 2.0, 6.0, 4.0, 0.5)
            b = a
            h = st.slider("수직 높이 h", 2.0, 7.0, 5.0, 0.5)
            r = 2.0
        elif kind in ("cylinder", "cone"):
            r = st.slider("반지름 r", 1.0, 4.0, 2.0, 0.5)
            h = st.slider("수직 높이 h", 2.0, 7.0, 5.0, 0.5)
            a, b = 4.0, 3.0
        else:
            r = st.slider("반지름 r", 1.0, 4.0, 2.0, 0.5)
            a, b, h = 4.0, 3.0, 5.0

    values = measurement_data(kind, a, b, h, r)
    supports_auto = hasattr(st, "fragment")
    if not supports_auto:
        st.warning(
            "자동 재생에는 Streamlit 1.37 이상이 필요합니다. 터미널에서 "
            "`python -m pip install --upgrade streamlit`을 실행해 주세요."
        )
    run_interval = f"{speed}s" if supports_auto and not paused else None
    decorator = st.fragment(run_every=run_interval) if supports_auto else (lambda function: function)

    @decorator
    def show_simulation():
        step = st.session_state.surface_volume_step

        if paused:
            previous, replay, next_scene = st.columns(3)
            if previous.button("◀ 이전", use_container_width=True):
                step = 5 if step == 1 else step - 1
                st.session_state.surface_volume_step = step
            if replay.button("↺ 처음", use_container_width=True):
                step = 1
                st.session_state.surface_volume_step = step
            if next_scene.button("다음 ▶", use_container_width=True):
                step = 1 if step == 5 else step + 1
                st.session_state.surface_volume_step = step

        state_text = "멈춘 상태 · 버튼으로 장면 이동" if paused else f"{speed:g}초마다 자동 재생 중"
        st.markdown(f"**현재 {step}/5장면** · {state_text}")
        show_step_card(st, kind, step, values)

        figure = make_figure(kind, step, values, top_view)
        st.plotly_chart(
            figure,
            use_container_width=True,
            config={"displaylogo": False, "displayModeBar": False, "responsive": True},
        )
        st.caption("☝️ 한 손가락으로 회전 · 두 손가락으로 확대/축소")

        if supports_auto and not paused:
            st.session_state.surface_volume_step = 1 if step == 5 else step + 1

    show_simulation()

    with st.expander("🧠 다섯 도형 공식을 한눈에 보기"):
        st.markdown(r"""
| 도형 | 겉넓이 | 부피 |
|---|---:|---:|
| 기둥 | $2B+Ph$ | $Bh$ |
| 뿔 | $B+\frac12Pl$ | $\frac13Bh$ |
| 원기둥 | $2\pi r^2+2\pi rh$ | $\pi r^2h$ |
| 원뿔 | $\pi r^2+\pi rl$ | $\frac13\pi r^2h$ |
| 구 | $4\pi r^2$ | $\frac43\pi r^3$ |

- **B:** 밑넓이 · **P:** 밑면의 둘레 · **h:** 수직 높이
- **r:** 반지름 · **l:** 뿔의 빗면 높이(원뿔에서는 모선의 길이)
- **겉넓이는 제곱단위**, **부피는 세제곱단위**를 사용합니다.
""")


if __name__ == "__main__":
    main()
