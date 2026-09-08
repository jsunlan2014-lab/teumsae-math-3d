"""틈새 공부 3D 수학 교실 ②: 다면체·회전체·전개도.

설치: python -m pip install --upgrade "streamlit>=1.37" plotly
실행: python -m streamlit run lesson11_solid_geometry_3d.py
"""

import math


SHAPE_LABELS = {
    "정육면체": "cube",
    "삼각기둥": "triangular_prism",
    "사각뿔": "square_pyramid",
}

REVOLUTION_LABELS = {
    "직사각형 → 원기둥": "cylinder",
    "직각삼각형 → 원뿔": "cone",
    "반원 → 구": "sphere",
}


def unique_edges(faces):
    """면 목록에서 중복되지 않는 모서리를 찾습니다."""
    edges = set()
    for face in faces:
        for index, first in enumerate(face):
            second = face[(index + 1) % len(face)]
            edges.add(tuple(sorted((first, second))))
    return sorted(edges)


def polyhedron_data(shape):
    """다면체의 꼭짓점과 면 정보를 반환합니다."""
    if shape == "cube":
        points = [
            (-1.5, -1.5, -1.5), (1.5, -1.5, -1.5),
            (1.5, 1.5, -1.5), (-1.5, 1.5, -1.5),
            (-1.5, -1.5, 1.5), (1.5, -1.5, 1.5),
            (1.5, 1.5, 1.5), (-1.5, 1.5, 1.5),
        ]
        faces = [
            [0, 3, 2, 1], [4, 5, 6, 7],
            [0, 1, 5, 4], [1, 2, 6, 5],
            [2, 3, 7, 6], [3, 0, 4, 7],
        ]
        name, child_name = "정육면체", "똑같은 정사각형 6개로 만든 상자"
    elif shape == "triangular_prism":
        points = [
            (-1.6, -1.2, -1.5), (1.6, -1.2, -1.5), (0.0, 1.5, -1.5),
            (-1.6, -1.2, 1.5), (1.6, -1.2, 1.5), (0.0, 1.5, 1.5),
        ]
        faces = [
            [0, 2, 1], [3, 4, 5],
            [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5],
        ]
        name, child_name = "삼각기둥", "삼각형 두 개를 나란히 세운 기둥"
    elif shape == "square_pyramid":
        points = [
            (-1.6, -1.6, -1.2), (1.6, -1.6, -1.2),
            (1.6, 1.6, -1.2), (-1.6, 1.6, -1.2),
            (0.0, 0.0, 2.0),
        ]
        faces = [[0, 3, 2, 1], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
        name, child_name = "사각뿔", "정사각형 위의 점 하나로 모이는 뾰족한 도형"
    else:
        raise ValueError("지원하지 않는 다면체입니다.")

    edges = unique_edges(faces)
    return {
        "name": name,
        "child_name": child_name,
        "points": points,
        "faces": faces,
        "edges": edges,
        "vertices_count": len(points),
        "edges_count": len(edges),
        "faces_count": len(faces),
    }


def face_centroid(points, face):
    count = len(face)
    return tuple(sum(points[index][axis] for index in face) / count for axis in range(3))


def face_triangles(vertex_count):
    """한 다각형 면을 삼각형 여러 개로 나눕니다."""
    if vertex_count < 3:
        raise ValueError("면에는 꼭짓점이 3개 이상 필요합니다.")
    return [(0, index, index + 1) for index in range(1, vertex_count - 1)]


def base_figure(title, camera="perspective", height=410):
    import plotly.graph_objects as go

    eye = (
        dict(x=0.01, y=0.01, z=2.65)
        if camera == "top"
        else dict(x=1.45, y=1.45, z=1.15)
    )
    figure = go.Figure()
    figure.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=18)),
        margin=dict(l=0, r=0, t=42, b=0),
        height=height,
        showlegend=False,
        scene=dict(
            camera=dict(eye=eye),
            aspectmode="data",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def add_face_mesh(figure, face_points, color, opacity=0.50, hover_text="면"):
    import plotly.graph_objects as go

    triangles = face_triangles(len(face_points))
    figure.add_trace(go.Mesh3d(
        x=[point[0] for point in face_points],
        y=[point[1] for point in face_points],
        z=[point[2] for point in face_points],
        i=[triangle[0] for triangle in triangles],
        j=[triangle[1] for triangle in triangles],
        k=[triangle[2] for triangle in triangles],
        color=color,
        opacity=opacity,
        flatshading=True,
        hovertemplate=f"{hover_text}<extra></extra>",
    ))


def polyhedron_figure(shape, step, top_view=False):
    """면·모서리·꼭짓점을 단계별로 보여 주는 다면체 그림입니다."""
    import plotly.graph_objects as go

    data = polyhedron_data(shape)
    points, faces, edges = data["points"], data["faces"], data["edges"]
    figure = base_figure(data["name"], "top" if top_view else "perspective")
    colors = ["#93C5FD", "#86EFAC", "#FDE68A", "#F9A8D4", "#C4B5FD", "#FDBA74"]

    for index, face in enumerate(faces):
        face_points = [points[vertex] for vertex in face]
        add_face_mesh(
            figure,
            face_points,
            colors[index % len(colors)],
            opacity=0.62 if step == 1 else 0.42,
            hover_text=f"{index + 1}번째 면",
        )

    edge_x, edge_y, edge_z = [], [], []
    for first, second in edges:
        edge_x.extend([points[first][0], points[second][0], None])
        edge_y.extend([points[first][1], points[second][1], None])
        edge_z.extend([points[first][2], points[second][2], None])
    figure.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z, mode="lines",
        line=dict(color="#1E3A8A", width=7 if step >= 2 else 4),
        hovertemplate="모서리<extra></extra>",
    ))

    if step == 1:
        centroids = [face_centroid(points, face) for face in faces]
        figure.add_trace(go.Scatter3d(
            x=[point[0] for point in centroids],
            y=[point[1] for point in centroids],
            z=[point[2] for point in centroids],
            mode="text",
            text=[f"면 {index + 1}" for index in range(len(faces))],
            textfont=dict(size=15, color="#7C2D12"),
            hoverinfo="skip",
        ))

    if step >= 2:
        figure.add_trace(go.Scatter3d(
            x=[point[0] for point in points],
            y=[point[1] for point in points],
            z=[point[2] for point in points],
            mode="markers+text",
            marker=dict(size=7, color="#DC2626"),
            text=[f"꼭짓점 {index + 1}" for index in range(len(points))],
            textposition="top center",
            textfont=dict(size=12, color="#991B1B"),
            hovertemplate="%{text}<extra></extra>",
        ))

    if step >= 3:
        figure.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0], mode="text",
            text=[
                f"꼭짓점 {data['vertices_count']} - 모서리 {data['edges_count']} "
                f"+ 면 {data['faces_count']} = 2"
            ],
            textfont=dict(size=18, color="#111827"),
            hoverinfo="skip",
        ))
    return figure


def profile_points(kind, radius=2.0, height=4.0, samples=32):
    """회전시키기 전 평면도형을 (반지름 방향, 높이) 좌표로 만듭니다."""
    half_height = height / 2
    if kind == "cylinder":
        return [(0, -half_height), (radius, -half_height),
                (radius, half_height), (0, half_height), (0, -half_height)]
    if kind == "cone":
        return [(0, -half_height), (radius, -half_height),
                (0, half_height), (0, -half_height)]
    if kind == "sphere":
        angles = [-math.pi / 2 + math.pi * index / samples for index in range(samples + 1)]
        curve = [(radius * math.cos(angle), radius * math.sin(angle)) for angle in angles]
        return [*curve, (0, -radius)]
    raise ValueError("지원하지 않는 회전체입니다.")


def rotated_profile(points, angle):
    """반지름-높이 평면도형을 z축 둘레로 회전합니다."""
    return [
        (radius * math.cos(angle), radius * math.sin(angle), z)
        for radius, z in points
    ]


def revolution_surface(kind, radius=2.0, height=4.0, rings=25, samples=48):
    """원기둥·원뿔·구의 3D 표면 좌표를 만듭니다."""
    angles = [2 * math.pi * index / samples for index in range(samples + 1)]
    if kind in ("cylinder", "cone"):
        z_values = [-height / 2 + height * index / (rings - 1) for index in range(rings)]
        x, y, z = [], [], []
        for current_z in z_values:
            if kind == "cylinder":
                current_radius = radius
            else:
                current_radius = radius * (height / 2 - current_z) / height
            x.append([current_radius * math.cos(angle) for angle in angles])
            y.append([current_radius * math.sin(angle) for angle in angles])
            z.append([current_z] * len(angles))
        return x, y, z

    if kind == "sphere":
        latitudes = [-math.pi / 2 + math.pi * index / (rings - 1) for index in range(rings)]
        x = [[radius * math.cos(latitude) * math.cos(angle) for angle in angles]
             for latitude in latitudes]
        y = [[radius * math.cos(latitude) * math.sin(angle) for angle in angles]
             for latitude in latitudes]
        z = [[radius * math.sin(latitude)] * len(angles) for latitude in latitudes]
        return x, y, z
    raise ValueError("지원하지 않는 회전체입니다.")


def revolution_name(kind):
    names = {
        "cylinder": ("직사각형", "원기둥"),
        "cone": ("직각삼각형", "원뿔"),
        "sphere": ("반원", "구"),
    }
    if kind not in names:
        raise ValueError("지원하지 않는 회전체입니다.")
    return names[kind]


def revolution_figure(kind, step, top_view=False):
    """평면도형을 돌려 회전체가 되는 과정을 보여 줍니다."""
    import plotly.graph_objects as go

    flat_name, solid_name = revolution_name(kind)
    figure = base_figure(
        f"{flat_name}을 돌리면 {solid_name}",
        "top" if top_view else "perspective",
    )
    radius, height = 2.0, 4.0
    profile = profile_points(kind, radius, height)

    figure.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[-2.7, 2.7], mode="lines+text",
        line=dict(color="#DC2626", width=6, dash="dash"),
        text=["", "회전축"], textposition="top center",
        hovertemplate="회전축<extra></extra>",
    ))

    angles = [0.0] if step == 1 else [2 * math.pi * index / 8 for index in range(8)]
    for index, angle in enumerate(angles):
        rotated = rotated_profile(profile, angle)
        figure.add_trace(go.Scatter3d(
            x=[point[0] for point in rotated],
            y=[point[1] for point in rotated],
            z=[point[2] for point in rotated],
            mode="lines",
            line=dict(
                color="#7C3AED" if index == 0 else "#A78BFA",
                width=8 if index == 0 else 3,
            ),
            opacity=1.0 if index == 0 else 0.45,
            hovertemplate=f"회전하는 {flat_name}<extra></extra>",
        ))

    if step >= 3:
        x, y, z = revolution_surface(kind, radius, height)
        colors = {
            "cylinder": "#38BDF8",
            "cone": "#FBBF24",
            "sphere": "#34D399",
        }
        color = colors[kind]
        figure.add_trace(go.Surface(
            x=x, y=y, z=z,
            colorscale=[[0, color], [1, color]],
            showscale=False,
            opacity=0.72,
            hovertemplate=f"{solid_name}<extra></extra>",
        ))
        figure.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0], mode="text",
            text=[f"완성: {solid_name}"],
            textfont=dict(size=20, color="#064E3B"),
            hoverinfo="skip",
        ))
    return figure


def cube_net_faces(fold_fraction, size=2.0):
    """정육면체 전개도가 접히는 여섯 면의 좌표를 계산합니다.

    fold_fraction=0이면 완전히 펼쳐지고, 1이면 정육면체가 됩니다.
    """
    fold_fraction = float(fold_fraction)
    if not 0 <= fold_fraction <= 1:
        raise ValueError("접기 정도는 0부터 1 사이여야 합니다.")

    half = size / 2
    angle = math.pi / 2 * fold_fraction
    cosine, sine = math.cos(angle), math.sin(angle)
    top_cosine, top_sine = math.cos(2 * angle), math.sin(2 * angle)

    south_y, side_z = -half - size * cosine, size * sine
    north_y = half + size * cosine
    east_x, west_x = half + size * cosine, -half - size * cosine

    bottom = [(-half, -half, 0), (half, -half, 0),
              (half, half, 0), (-half, half, 0)]
    south = [(-half, -half, 0), (half, -half, 0),
             (half, south_y, side_z), (-half, south_y, side_z)]
    north = [(-half, half, 0), (half, half, 0),
             (half, north_y, side_z), (-half, north_y, side_z)]
    east = [(half, -half, 0), (half, half, 0),
            (east_x, half, side_z), (east_x, -half, side_z)]
    west = [(-half, -half, 0), (-half, half, 0),
            (west_x, half, side_z), (west_x, -half, side_z)]

    far_y = north_y + size * top_cosine
    far_z = side_z + size * top_sine
    top = [(-half, north_y, side_z), (half, north_y, side_z),
           (half, far_y, far_z), (-half, far_y, far_z)]

    return [
        ("밑면", bottom), ("앞면", south), ("뒷면", north),
        ("오른쪽 면", east), ("왼쪽 면", west), ("윗면", top),
    ]


def cube_net_figure(step, top_view=False):
    """정육면체 전개도가 단계별로 접히는 그림입니다."""
    import plotly.graph_objects as go

    fold_fraction = {1: 0.0, 2: 0.5, 3: 1.0}[step]
    title = {
        1: "전개도: 완전히 펼친 모습",
        2: "전개도: 접는 중",
        3: "전개도: 정육면체 완성",
    }[step]
    camera = "top" if top_view and step == 1 else "perspective"
    figure = base_figure(title, camera)
    faces = cube_net_faces(fold_fraction)
    colors = ["#93C5FD", "#86EFAC", "#FDE68A", "#F9A8D4", "#C4B5FD", "#FDBA74"]

    label_x, label_y, label_z, labels = [], [], [], []
    for index, (name, points) in enumerate(faces):
        add_face_mesh(figure, points, colors[index], 0.68, name)
        closed = [*points, points[0]]
        figure.add_trace(go.Scatter3d(
            x=[point[0] for point in closed],
            y=[point[1] for point in closed],
            z=[point[2] for point in closed],
            mode="lines", line=dict(color="#1E3A8A", width=6),
            hovertemplate=f"{name}의 접는 선<extra></extra>",
        ))
        center = tuple(sum(point[axis] for point in points) / 4 for axis in range(3))
        label_x.append(center[0])
        label_y.append(center[1])
        label_z.append(center[2] + 0.06)
        labels.append(name)

    figure.add_trace(go.Scatter3d(
        x=label_x, y=label_y, z=label_z, mode="text", text=labels,
        textfont=dict(size=15, color="#172554"), hoverinfo="skip",
    ))
    if step == 2:
        figure.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[2.7], mode="text", text=["접는 중!"],
            textfont=dict(size=22, color="#DC2626"), hoverinfo="skip",
        ))
    return figure


def lesson_step_content(concept, step, shape="cube", revolution="cylinder"):
    """현재 단계에 맞는 어린이용 설명을 반환합니다."""
    if step not in (1, 2, 3):
        raise ValueError("설명 단계는 1, 2, 3 중 하나여야 합니다.")

    if concept == "polyhedron":
        data = polyhedron_data(shape)
        contents = {
            1: (
                "① 평평한 면으로 둘러싸여 있어요",
                f"{data['name']}은(는) {data['child_name']}입니다. "
                "색칠된 평평한 조각 하나하나를 면이라고 합니다.",
                f"면은 모두 {data['faces_count']}개",
            ),
            2: (
                "② 선과 점에도 이름이 있어요",
                "면과 면이 만나는 파란 선은 모서리, 모서리들이 만나는 빨간 점은 꼭짓점입니다.",
                f"모서리 {data['edges_count']}개 · 꼭짓점 {data['vertices_count']}개",
            ),
            3: (
                "③ 개수를 세어 확인해요",
                "구멍이 없는 볼록한 다면체에서는 ‘꼭짓점−모서리+면’을 계산하면 언제나 2가 됩니다.",
                f"{data['vertices_count']} − {data['edges_count']} + "
                f"{data['faces_count']} = 2",
            ),
        }
    elif concept == "revolution":
        flat_name, solid_name = revolution_name(revolution)
        contents = {
            1: (
                "① 평면도형과 회전축을 살펴봐요",
                f"보라색 {flat_name} 옆의 빨간 점선을 회전축이라고 합니다.",
                f"{flat_name} + 회전축",
            ),
            2: (
                "② 회전축 둘레로 한 바퀴 돌려요",
                f"{flat_name}을 회전축에서 떼지 않고 빙글빙글 한 바퀴 돌립니다.",
                "평면도형이 지나간 자리가 입체가 돼요",
            ),
            3: (
                f"③ {solid_name}이(가) 완성됐어요",
                f"{flat_name}이(가) 지나간 자리를 모두 모으면 {solid_name}이(가) 됩니다. "
                "이렇게 만든 입체도형을 회전체라고 합니다.",
                f"{flat_name} → {solid_name}",
            ),
        }
    elif concept == "net":
        contents = {
            1: (
                "① 상자를 펼치면 전개도가 돼요",
                "정육면체의 모서리를 잘라 바닥에 펼치면 정사각형 6개가 이어진 모양이 됩니다.",
                "전개도 = 입체도형을 펼친 그림",
            ),
            2: (
                "② 이어진 모서리를 따라 접어요",
                "밑면은 그대로 두고 나머지 면을 파란 모서리를 따라 천천히 접어 올립니다.",
                "서로 겹치지 않게 한 면씩 접어요",
            ),
            3: (
                "③ 여섯 면이 만나 정육면체가 돼요",
                "펼쳐져 있던 정사각형 6개가 빈틈없이 만나 하나의 정육면체가 됩니다.",
                "정사각형 6개 → 정육면체 1개",
            ),
        }
    else:
        raise ValueError("지원하지 않는 학습 개념입니다.")

    title, explanation, key_point = contents[step]
    return {"title": title, "explanation": explanation, "key_point": key_point}


def show_step_card(st, concept, step, shape="cube", revolution="cylinder"):
    content = lesson_step_content(concept, step, shape, revolution)
    st.progress(step / 3)
    st.markdown(f"### {content['title']}")
    st.info(content["explanation"])
    st.success(f"⭐ {content['key_point']}")


def main():
    import streamlit as st

    st.set_page_config(
        page_title="틈새 공부 3D 입체도형 교실",
        page_icon="🧊",
        layout="centered",
    )
    st.markdown("""
<style>
    .block-container {max-width: 820px; padding-top: 1rem; padding-bottom: 1.5rem;}
    h1 {font-size: 2rem !important; margin-bottom: 0.25rem !important;}
    h2 {font-size: 1.35rem !important;}
    h3 {font-size: 1.15rem !important;}
    @media (max-width: 640px) {
        .block-container {padding: 0.55rem 0.75rem 1.2rem;}
        h1 {font-size: 1.48rem !important; line-height: 1.2 !important;}
        h2 {font-size: 1.12rem !important;}
        h3 {font-size: 1rem !important;}
        [data-testid="stMetricValue"] {font-size: 1.5rem;}
        [data-testid="stAlert"] {font-size: 0.9rem;}
    }
</style>
""", unsafe_allow_html=True)
    st.title("🧊 틈새 공부 3D 입체도형 교실")
    st.subheader("② 다면체·회전체·전개도")
    st.caption(
        "설명이 1→2→3단계로 자동 재생됩니다. 도형을 마우스나 손가락으로 돌리고 확대해 보세요."
    )

    concept_label = st.radio(
        "학습할 개념",
        ["다면체", "회전체", "전개도"],
        horizontal=True,
    )
    concept = {"다면체": "polyhedron", "회전체": "revolution", "전개도": "net"}[
        concept_label
    ]

    if "solid_auto_step" not in st.session_state:
        st.session_state.solid_auto_step = 1
    if st.session_state.get("solid_last_concept") != concept:
        st.session_state.solid_auto_step = 1
        st.session_state.solid_last_concept = concept

    control1, control2 = st.columns(2)
    with control1:
        auto_play = st.toggle("▶ 자동 설명 재생", value=True)
    with control2:
        speed = st.slider("단계 전환(초)", 2.0, 7.0, 4.0, 0.5, disabled=not auto_play)
    control3, control4 = st.columns(2)
    with control3:
        top_view = st.checkbox(
            "위에서 보기", value=False,
            help="전개도를 펼친 모양이나 입체의 윗모습을 확인할 때 사용합니다.",
        )
    with control4:
        manual_step = st.slider(
            "직접 선택할 단계", 1, 3, 1,
            disabled=auto_play,
            help="자동 재생을 끄면 원하는 장면을 직접 고를 수 있습니다.",
        )

    supports_auto = hasattr(st, "fragment")
    effective_auto = auto_play and supports_auto
    if auto_play and not supports_auto:
        st.warning(
            "자동 재생에는 Streamlit 1.37 이상이 필요합니다. 터미널에서 "
            "`python -m pip install --upgrade streamlit`을 실행해 주세요."
        )

    run_interval = f"{speed}s" if effective_auto else None
    player_decorator = (
        st.fragment(run_every=run_interval)
        if supports_auto
        else (lambda function: function)
    )

    @player_decorator
    def show_simulation():
        step = st.session_state.solid_auto_step if effective_auto else manual_step
        st.markdown(
            f"**현재 {step}단계** · "
            + (f"{speed:g}초마다 자동 전환 중" if effective_auto else "직접 탐색 중")
        )

        if concept == "polyhedron":
            shape_label = st.selectbox("관찰할 다면체", list(SHAPE_LABELS))
            shape = SHAPE_LABELS[shape_label]
            data = polyhedron_data(shape)
            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("면", data["faces_count"])
            metric2.metric("모서리", data["edges_count"])
            metric3.metric("꼭짓점", data["vertices_count"])
            show_step_card(st, concept, step, shape=shape)
        elif concept == "revolution":
            revolution_label = st.selectbox("돌려 볼 평면도형", list(REVOLUTION_LABELS))
            revolution = REVOLUTION_LABELS[revolution_label]
            flat_name, solid_name = revolution_name(revolution)
            metric1, metric2 = st.columns(2)
            metric1.metric("돌리기 전", flat_name)
            metric2.metric("돌린 후", solid_name)
            show_step_card(st, concept, step, revolution=revolution)
        else:
            st.metric("정육면체의 면", "정사각형 6개")
            st.write("전개도의 각 면에 이름을 표시했습니다.")
            show_step_card(st, concept, step)

        if concept == "polyhedron":
            figure = polyhedron_figure(shape, step, top_view)
        elif concept == "revolution":
            figure = revolution_figure(revolution, step, top_view)
        else:
            figure = cube_net_figure(step, top_view)
        st.plotly_chart(
            figure,
            width="stretch",
            config={"displaylogo": False, "displayModeBar": False, "responsive": True},
        )
        st.caption(
            "그림을 손가락으로 돌리고, 두 손가락으로 확대·축소할 수 있습니다."
        )

        if effective_auto:
            st.session_state.solid_auto_step = 1 if step == 3 else step + 1

    show_simulation()

    with st.expander("꼭 기억할 낱말"):
        st.markdown("""
- **다면체:** 평평한 다각형 면으로 둘러싸인 입체도형
- **면:** 입체도형을 둘러싼 평평한 부분
- **모서리:** 두 면이 만나는 선분
- **꼭짓점:** 여러 모서리가 만나는 점
- **회전체:** 평면도형을 한 직선 둘레로 한 바퀴 돌려 만든 입체도형
- **전개도:** 입체도형의 모서리를 잘라 겹치지 않게 펼친 그림

정육면체 전개도는 정사각형 6개로 이루어지지만, 정사각형 6개를 아무렇게나 붙인다고
모두 정육면체로 접히는 것은 아닙니다.
""")


if __name__ == "__main__":
    main()
