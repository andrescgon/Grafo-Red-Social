#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Grafo social Instagram (para múltiples personas × {followers, following, topics}) con NetworkX.
"""

import argparse
import json
import math
import os
import re
from glob import glob
from collections import defaultdict

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go

# ----------------------------
# Patrones de nombres de archivo
# ----------------------------
FOLLOWERS_PATTERN = re.compile(r"(.+?)_followers\.json$", re.IGNORECASE)
FOLLOWING_PATTERN = re.compile(r"(.+?)_following\.json$", re.IGNORECASE)
TOPICS_PATTERN   = re.compile(r"(.+?)_topics\.json$",   re.IGNORECASE)

LAYOUT_SEED = 42


# ----------------------------
# Utilidades generales
# ----------------------------
def normalize_username(s: str) -> str:
    if s is None: return ""
    s = s.strip().lower()
    if s.startswith("@"):
        s = s[1:]
    return s

def normalize_topic(s: str) -> str:
    if s is None: return ""
    return s.strip().lower()

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def find_triplets_by_person(data_dir):
    files = glob(os.path.join(data_dir, "*.json"))
    buckets = defaultdict(list)
    for p in files:
        base = os.path.basename(p)
        m = FOLLOWERS_PATTERN.search(base) or FOLLOWING_PATTERN.search(base) or TOPICS_PATTERN.search(base)
        if m:
            buckets[m.group(1)].append(p)
    return dict(buckets)


# ----------------------------
# Parsers EXACTOS al formato indicado
# ----------------------------
def parse_followers(path: str) -> set:
    """
    followers: lista raíz; cada item con "string_list_data": [{ "value": "<usuario>" }, ...]
    """
    data = load_json(path)
    out = set()
    if isinstance(data, list):
        for item in data:
            sld = item.get("string_list_data") or []
            if isinstance(sld, list):
                for e in sld:
                    val = e.get("value")
                    if val:
                        out.add(normalize_username(val))
    return {u for u in out if u}

def parse_following(path: str) -> set:
    """
    following: objeto con "relationships_following": [ {"title": "<usuario>"}, ... ]
    """
    data = load_json(path)
    out = set()
    rel = data.get("relationships_following") or []
    if isinstance(rel, list):
        for item in rel:
            title = item.get("title")
            if title:
                out.add(normalize_username(title))
    return {u for u in out if u}

def parse_topics(path: str) -> set:
    """
    topics: objeto con "topics_your_topics": [
      {"string_map_data": {"Name": {"value": "<topic>"}}}, ...
    ]
    """
    data = load_json(path)
    out = set()
    arr = data.get("topics_your_topics") or []
    if isinstance(arr, list):
        for item in arr:
            smd = item.get("string_map_data") or {}
            name = (smd.get("Name") or {}).get("value")
            if name:
                out.add(normalize_topic(name))
    return {t for t in out if t}

def parse_person_files(filepaths):
    """
    Devuelve dict con:
      - person: nombre base del archivo (prefijo)
      - followers, following, topics: sets
    """
    person_name = None
    for p in filepaths:
        base = os.path.basename(p)
        for pat in (FOLLOWERS_PATTERN, FOLLOWING_PATTERN, TOPICS_PATTERN):
            m = pat.search(base)
            if m:
                person_name = m.group(1)
                break
        if person_name:
            break
    if not person_name:
        person_name = os.path.basename(os.path.dirname(filepaths[0]))

    followers, following, topics = set(), set(), set()
    for p in filepaths:
        base = os.path.basename(p)
        if FOLLOWERS_PATTERN.search(base):
            followers |= parse_followers(p)
        elif FOLLOWING_PATTERN.search(base):
            following |= parse_following(p)
        elif TOPICS_PATTERN.search(base):
            topics |= parse_topics(p)

    return {
        "person": person_name,
        "followers": followers,
        "following": following,
        "topics": topics
    }


# ----------------------------
# Construcción de grafos
# ----------------------------
def build_ego_graph(person_blob):
    """
    Crea un DiGraph:
    - Nodo persona (type=person)
    - Followers: account -> persona (edge_type='follows', direction='inbound')
    - Following: persona -> account (edge_type='follows', direction='outbound')
    - Topics: persona -> topic (edge_type='has_topic')
    """
    G = nx.DiGraph()
    ego = person_blob["person"]
    G.add_node(ego, type="person", label=ego)

    for acc in sorted(person_blob["followers"]):
        an = f"acc:{acc}"
        G.add_node(an, type="account", label=acc)
        G.add_edge(an, ego, edge_type="follows", direction="inbound")

    for acc in sorted(person_blob["following"]):
        an = f"acc:{acc}"
        if an not in G:
            G.add_node(an, type="account", label=acc)
        G.add_edge(ego, an, edge_type="follows", direction="outbound")

    for t in sorted(person_blob["topics"]):
        tn = f"topic:{t}"
        G.add_node(tn, type="topic", label=t)
        G.add_edge(ego, tn, edge_type="has_topic")

    return G

def compose_graphs(graphs):
    return nx.compose_all(graphs)


# ----------------------------
# Métricas y similitudes
# ----------------------------
def jaccard_similarity(A: set, B: set) -> float:
    if not A and not B:
        return 0.0
    return len(A & B) / max(1, len(A | B))

def compute_similarity_matrix(person_blobs):
    person_sets = {}
    for p in person_blobs:
        accs = {f"acc:{u}" for u in p["followers"] | p["following"]}
        tops = {f"topic:{t}" for t in p["topics"]}
        person_sets[p["person"]] = accs | tops

    persons = sorted(person_sets)
    M = pd.DataFrame(index=persons, columns=persons, dtype=float)
    for a in persons:
        for b in persons:
            M.loc[a, b] = jaccard_similarity(person_sets[a], person_sets[b])
    return M

def compute_person_overlap(person_blobs):
    person_sets = {}
    for p in person_blobs:
        accs = {f"acc:{u}" for u in p["followers"] | p["following"]}
        tops = {f"topic:{t}" for t in p["topics"]}
        person_sets[p["person"]] = accs | tops

    persons = sorted(person_sets)
    overlap_counts = {}
    shared_rows = []
    for i in range(len(persons)):
        for j in range(i+1, len(persons)):
            a, b = persons[i], persons[j]
            inter = person_sets[a] & person_sets[b]
            overlap_counts[(a, b)] = len(inter)
            for ent in inter:
                etype = "account" if ent.startswith("acc:") else "topic"
                shared_rows.append({
                    "person_a": a,
                    "person_b": b,
                    "entity": ent.split(":", 1)[1],
                    "type": etype
                })
    return overlap_counts, shared_rows

def export_centrality(G, person_name, out_dir):
    btw = nx.betweenness_centrality(G, normalized=True)
    try:
        pr = nx.pagerank(G, alpha=0.85, max_iter=200)
    except nx.PowerIterationFailedConvergence:
        pr = {n: 0.0 for n in G.nodes()}
    rows = []
    for n in G.nodes():
        rows.append({
            "node": n,
            "label": G.nodes[n].get("label", n),
            "type": G.nodes[n].get("type", ""),
            "degree": G.degree(n),
            "in_degree": G.in_degree(n) if isinstance(G, nx.DiGraph) else None,
            "out_degree": G.out_degree(n) if isinstance(G, nx.DiGraph) else None,
            "betweenness": btw.get(n, 0.0),
            "pagerank": pr.get(n, 0.0),
        })
    pd.DataFrame(rows).sort_values(
        ["type", "degree", "pagerank"], ascending=[True, False, False]
    ).to_csv(os.path.join(out_dir, f"centralidad_{person_name}.csv"), index=False)


# ----------------------------
# Posicionamiento anclado de personas
# ----------------------------
def anchored_person_positions(persons, radius=3.2):
    """
    Devuelve posiciones ancla en círculo para los nodos persona.
    - 1 persona: centro (0,0)
    - 2+ personas: ubicadas en círculo de radio 'radius'
    """
    pos = {}
    n = len(persons)
    if n == 1:
        pos[persons[0]] = (0.0, 0.0)
        return pos
    for i, p in enumerate(sorted(persons)):
        theta = 2.0 * math.pi * i / n
        pos[p] = (radius * math.cos(theta), radius * math.sin(theta))
    return pos


# ----------------------------
# Dibujo PNG con colores, tamaños, leyenda y anclaje
# ----------------------------
def draw_graph(G, title, out_path, show_labels=False, label_persons=True):
    """
    Dibuja el grafo con colores diferenciados, tamaños reducidos, leyenda y
    posiciones ancladas para las personas (evita solapamientos entre egos).
    - show_labels: si True, etiqueta TODOS los nodos (no recomendado en grafos grandes)
    - label_persons: si True, muestra SIEMPRE la etiqueta de cada ego sobre su nodo
    """
    plt.figure(figsize=(13, 9))

    # Identificar tipos de nodos para anclar personas
    persons = [n for n, d in G.nodes(data=True) if d.get("type") == "person"]
    accounts = [n for n, d in G.nodes(data=True) if d.get("type") == "account"]
    topics   = [n for n, d in G.nodes(data=True) if d.get("type") == "topic"]
    person_nodes = set(persons)

    # Layout con personas ancladas
    pos_init = anchored_person_positions(persons, radius=3.2)
    pos = nx.spring_layout(
        G,
        seed=LAYOUT_SEED,
        k=0.45,
        iterations=80,
        pos=pos_init,
        fixed=persons
    )

    # Conexiones de cada nodo con personas (para marcar compartidos)
    connection_count = {}
    for n in G.nodes():
        if G.nodes[n].get("type") != "person":
            linked_persons = {p for p in person_nodes if G.has_edge(p, n) or G.has_edge(n, p)}
            connection_count[n] = len(linked_persons)

    # Colores para followers/following
    account_colors = []
    for n in accounts:
        conns = connection_count.get(n, 0)
        in_to_person = any(G.has_edge(n, p) for p in persons)
        out_from_person = any(G.has_edge(p, n) for p in persons)

        if in_to_person and not out_from_person:
            base_color = "#2ecc71"  # verde followers
        elif out_from_person and not in_to_person:
            base_color = "#3498db"  # azul following
        else:
            base_color = "#9b59b6"  # púrpura (mutuo)

        if conns == 2:
            base_color = "#f1c40f"  # amarillo (compartido por 2)
        elif conns >= 3:
            base_color = "#e74c3c"  # rojo (compartido por 3+)
        account_colors.append(base_color)

    # Colores para tópicos
    topic_colors = []
    for n in topics:
        conns = connection_count.get(n, 0)
        if conns == 0:
            base_color = "#7f8c8d"  # gris
        elif conns == 2:
            base_color = "#f39c12"  # naranja (2 personas)
        elif conns >= 3:
            base_color = "#c0392b"  # rojo oscuro (3+)
        else:
            base_color = "#95a5a6"  # gris medio
        topic_colors.append(base_color)

    # Tamaños (reducidos)
    ego_size = 700
    account_size = 120
    topic_size = 90

    # Nodos
    nx.draw_networkx_nodes(G, pos, nodelist=persons, node_shape="s", node_size=ego_size,
                           node_color="#2f4858", alpha=0.95, label="Ego (persona principal)")
    nx.draw_networkx_nodes(G, pos, nodelist=accounts, node_shape="o", node_size=account_size,
                           node_color=account_colors, alpha=0.85)
    nx.draw_networkx_nodes(G, pos, nodelist=topics, node_shape="^", node_size=topic_size,
                           node_color=topic_colors, alpha=0.85)

    # Aristas
    follows_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "follows"]
    topic_edges   = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "has_topic"]
    nx.draw_networkx_edges(G, pos, edgelist=follows_edges, width=0.4, alpha=0.25,
                           arrows=True, arrowstyle="-|>", edge_color="#bdc3c7")
    nx.draw_networkx_edges(G, pos, edgelist=topic_edges, width=0.7, alpha=0.3,
                           arrows=True, arrowstyle="-|>", edge_color="#7f8c8d")

    # Etiquetas (opcional: todos los nodos)
    if show_labels:
        labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=7)

    # Etiquetas SIEMPRE visibles para egos
    if label_persons and persons:
        for p in persons:
            lbl = G.nodes[p].get("label", p)
            x, y = pos[p]
            plt.text(x, y + 0.06, lbl, ha="center", va="bottom",
                     fontsize=10, fontweight="bold", color="#111")

    # Leyenda
    legend_handles = [
        mpatches.Patch(color="#2ecc71", label="Follower (te sigue)"),
        mpatches.Patch(color="#3498db", label="Following (sigues tú)"),
        mpatches.Patch(color="#9b59b6", label="Conexión mutua"),
        mpatches.Patch(color="#7f8c8d", label="Tópico individual"),
        mpatches.Patch(color="#f1c40f", label="Cuenta compartida por 2 personas"),
        mpatches.Patch(color="#e74c3c", label="Cuenta compartida por 3+ personas"),
        mpatches.Patch(color="#f39c12", label="Tópico compartido por 2 personas"),
        mpatches.Patch(color="#c0392b", label="Tópico compartido por 3+ personas"),
        mpatches.Patch(color="#2f4858", label="Ego (persona principal)")
    ]
    plt.legend(handles=legend_handles, loc="upper right", fontsize=8, frameon=True)

    plt.title(title, fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


# ----------------------------
# Dibujo INTERACTIVO (HTML) con la misma paleta y etiquetas fijas en egos
# ----------------------------
def draw_interactive_graph(G, title, out_html):
    """
    Versión interactiva HTML con el mismo esquema de colores/tipos que el PNG:
    - Followers (solo edge hacia persona): verde
    - Following (solo edge desde persona): azul
    - Conexión mutua (ambas): púrpura
    - Topics: gris (naranja/rojo si compartidos por 2/3 personas)
    - Nodos compartidos por 2/3 personas: amarillo/rojo
    - Egos: cuadrados gris oscuro con etiqueta fija encima
    Posiciones de personas ancladas para evitar superposición.
    """
    persons = [n for n, d in G.nodes(data=True) if d.get("type") == "person"]
    accounts = [n for n, d in G.nodes(data=True) if d.get("type") == "account"]
    topics   = [n for n, d in G.nodes(data=True) if d.get("type") == "topic"]
    person_nodes = set(persons)

    # Posiciones (ancladas como en PNG)
    pos_init = anchored_person_positions(persons, radius=3.2)
    pos = nx.spring_layout(
        G, seed=LAYOUT_SEED, k=0.45, iterations=80, pos=pos_init, fixed=persons
    )

    # Conteo de en cuántas personas aparece cada nodo (para marcar compartidos)
    connection_count = {}
    for n in G.nodes():
        if G.nodes[n].get("type") != "person":
            linked_persons = {p for p in person_nodes if G.has_edge(p, n) or G.has_edge(n, p)}
            connection_count[n] = len(linked_persons)

    # Listas para un único scatter de nodos
    node_x, node_y, node_color, node_symbol, node_size, node_text = [], [], [], [], [], []

    def add_node(n, color, symbol, size, label_text):
        node_x.append(pos[n][0]); node_y.append(pos[n][1])
        node_color.append(color); node_symbol.append(symbol)
        node_size.append(size);   node_text.append(label_text)

    # Egos
    for n in persons:
        add_node(n, "#2f4858", "square", 16, f"{G.nodes[n].get('label', n)} (persona)")

    # Accounts (followers/following/mutuos + compartidos)
    for n in accounts:
        conns = connection_count.get(n, 0)
        in_to_person = any(G.has_edge(n, p) for p in persons)
        out_from_person = any(G.has_edge(p, n) for p in persons)

        if in_to_person and not out_from_person:
            base_color = "#2ecc71"  # follower
        elif out_from_person and not in_to_person:
            base_color = "#3498db"  # following
        else:
            base_color = "#9b59b6"  # mutuo

        if conns == 2:
            base_color = "#f1c40f"  # compartido por 2
        elif conns >= 3:
            base_color = "#e74c3c"  # compartido por 3

        add_node(n, base_color, "circle", 8, f"{G.nodes[n].get('label', n)} (cuenta)")

    # Topics
    for n in topics:
        conns = connection_count.get(n, 0)
        if conns == 0:
            base_color = "#7f8c8d"
        elif conns == 2:
            base_color = "#f39c12"
        elif conns >= 3:
            base_color = "#c0392b"
        else:
            base_color = "#95a5a6"
        add_node(n, base_color, "triangle-up", 7, f"{G.nodes[n].get('label', n)} (tópico)")

    # Aristas
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]

    fig = go.Figure()

    # Trazo de aristas
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=0.5, color="#cfcfcf"),
        hoverinfo="none", showlegend=False
    ))

    # Trazo de nodos
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers",
        marker=dict(size=node_size, color=node_color, symbol=node_symbol, line=dict(width=0)),
        text=[t for t in node_text],
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    ))

    # Etiquetas fijas para PERSONAS (egos)
    ego_x = [pos[n][0] for n in persons]
    ego_y = [pos[n][1] for n in persons]
    ego_text = [G.nodes[n].get("label", n) for n in persons]
    fig.add_trace(go.Scatter(
        x=ego_x, y=ego_y,
        mode="text",
        text=ego_text,
        textposition="top center",
        textfont=dict(size=12, color="#111"),
        showlegend=False, hoverinfo="skip"
    ))

    # Leyenda manual
    legend_items = [
        ("Follower (te sigue)", "#2ecc71", "circle"),
        ("Following (sigues tú)", "#3498db", "circle"),
        ("Conexión mutua", "#9b59b6", "circle"),
        ("Tópico individual", "#7f8c8d", "triangle-up"),
        ("Cuenta compartida por 2 personas", "#f1c40f", "circle"),
        ("Cuenta compartida por 3+ personas", "#e74c3c", "circle"),
        ("Tópico compartido por 2 personas", "#f39c12", "triangle-up"),
        ("Tópico compartido por 3+ personas", "#c0392b", "triangle-up"),
        ("Ego (persona principal)", "#2f4858", "square"),
    ]
    for name, color, symbol in legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=color, symbol=symbol),
            legendgroup=name, showlegend=True, name=name, hoverinfo="skip"
        ))

    fig.update_layout(
        title=title,
        hovermode="closest",
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(x=0.99, y=0.99, xanchor="right", yanchor="top",
                    bgcolor="rgba(255,255,255,0.8)", font=dict(size=10))
    )
    fig.write_html(out_html)
    print(f"Grafo interactivo guardado en {out_html}")


# ----------------------------
# Programa principal
# ----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="./data", help="Carpeta con JSON (default: ./data)")
    ap.add_argument("--out", default="./out",  help="Carpeta de salida (default: ./out)")
    args = ap.parse_args()

    ensure_dir(args.out)

    groups = find_triplets_by_person(args.data)
    if not groups:
        raise SystemExit("No se detectaron JSON válidos en --data (nombres *_followers/_following/_topics).")

    # Procesa todas las personas encontradas en los archivos
    persons = sorted(groups.keys())
    person_blobs, ego_graphs = [], []

    for person in persons:
        blob = parse_person_files(groups[person])
        person_blobs.append(blob)

        Gp = build_ego_graph(blob)
        ego_graphs.append(Gp)

        # Ego PNG (sin etiqueta fija de persona para evitar redundancia con el título)
        draw_graph(Gp,
                   f"Grafo: {blob['person']}",
                   os.path.join(args.out, f"grafo_individual_{blob['person']}.png"),
                   show_labels=False,
                   label_persons=True)

        export_centrality(Gp, blob['person'], args.out)

    # Grafo unificado
    G_merged = compose_graphs(ego_graphs)
    nx.write_gexf(G_merged, os.path.join(args.out, "grafo_unificado.gexf"))

    # PNG con etiquetas fijas sobre cada ego
    draw_graph(G_merged,
               "Grafo Unificado (entidades compartidas)",
               os.path.join(args.out, "grafo_unificado.png"),
               show_labels=False,
               label_persons=True)

    # Interactivo con tooltips y etiquetas fijas de egos
    draw_interactive_graph(
        G_merged,
        "Grafo interactivo (pasa el cursor para ver nombres)",
        os.path.join(args.out, "grafo_interactivo.html")
    )

    # Similitud y entidades compartidas
    overlap_counts, shared_rows = compute_person_overlap(person_blobs)
    simM = compute_similarity_matrix(person_blobs)
    simM.to_csv(os.path.join(args.out, "matriz_similitud.csv"))

    shared_df = pd.DataFrame(shared_rows)
    if not shared_df.empty:
        shared_df = shared_df.sort_values(["type", "entity", "person_a", "person_b"])
    shared_df.to_csv(os.path.join(args.out, "entidades_compartidas.csv"), index=False)

    # Meta-grafo de personas ponderado por entidades compartidas
    H = nx.Graph()
    for p in [b["person"] for b in person_blobs]:
        H.add_node(p, type="person")
    for (a, b), w in overlap_counts.items():
        H.add_edge(a, b, weight=w)

    plt.figure(figsize=(6, 5))
    posH = nx.spring_layout(H, seed=LAYOUT_SEED)
    weights = [H[u][v]["weight"] for u, v in H.edges()] if H.number_of_edges() else []
    nx.draw_networkx_nodes(H, posH, node_color="#2f4858", node_size=900)
    nx.draw_networkx_labels(H, posH, font_size=10, font_color="white")
    if weights:
        nx.draw_networkx_edges(H, posH, width=[0.8 + 0.4*w for w in weights], edge_color="#888888")
        nx.draw_networkx_edge_labels(H, posH, edge_labels={(u, v): H[u][v]["weight"] for u, v in H.edges()}, font_size=9)
    plt.title("Personas conectadas por entidades compartidas (peso = conteo)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(args.out, "conexiones_entre_personas.png"), dpi=140)
    plt.close()

    print("Listo. Revisa la carpeta:", os.path.abspath(args.out))


if __name__ == "__main__":
    main()
