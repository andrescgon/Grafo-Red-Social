#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analizador de datos sociales de Instagram
Genera reportes legibles sobre personas, gustos compartidos, cuentas en común, etc.
"""

import os
import json
import pandas as pd
from collections import defaultdict
from glob import glob
import re

# Patrones de archivos
FOLLOWERS_PATTERN = re.compile(r"(.+?)_followers\.json$", re.IGNORECASE)
FOLLOWING_PATTERN = re.compile(r"(.+?)_following\.json$", re.IGNORECASE)
TOPICS_PATTERN   = re.compile(r"(.+?)_topics\.json$",   re.IGNORECASE)


def normalize_username(s):
    if s is None: return ""
    s = s.strip().lower()
    if s.startswith("@"):
        s = s[1:]
    return s


def normalize_topic(s):
    if s is None: return ""
    return s.strip().lower()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_followers(path):
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


def parse_following(path):
    data = load_json(path)
    out = set()
    rel = data.get("relationships_following") or []
    if isinstance(rel, list):
        for item in rel:
            title = item.get("title")
            if title:
                out.add(normalize_username(title))
    return {u for u in out if u}


def parse_topics(path):
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


def find_person_files(data_dir):
    files = glob(os.path.join(data_dir, "*.json"))
    buckets = defaultdict(dict)

    for p in files:
        base = os.path.basename(p)

        if FOLLOWERS_PATTERN.search(base):
            m = FOLLOWERS_PATTERN.search(base)
            person = m.group(1)
            buckets[person]['followers'] = p
        elif FOLLOWING_PATTERN.search(base):
            m = FOLLOWING_PATTERN.search(base)
            person = m.group(1)
            buckets[person]['following'] = p
        elif TOPICS_PATTERN.search(base):
            m = TOPICS_PATTERN.search(base)
            person = m.group(1)
            buckets[person]['topics'] = p

    return dict(buckets)


def load_person_data(data_dir):
    """Carga todos los datos de las personas"""
    person_files = find_person_files(data_dir)
    person_data = {}

    for person, files in person_files.items():
        data = {
            'followers': set(),
            'following': set(),
            'topics': set()
        }

        if 'followers' in files:
            data['followers'] = parse_followers(files['followers'])
        if 'following' in files:
            data['following'] = parse_following(files['following'])
        if 'topics' in files:
            data['topics'] = parse_topics(files['topics'])

        person_data[person] = data

    return person_data


def analyze_topics(person_data):
    """Analiza tópicos/gustos de las personas"""
    print("\n" + "="*70)
    print("ANÁLISIS DE GUSTOS/TÓPICOS")
    print("="*70)

    # Tópicos por persona
    for person, data in sorted(person_data.items()):
        topics = data['topics']
        print(f"\n{person.upper()} - {len(topics)} tópicos:")
        if topics:
            for topic in sorted(topics):
                print(f"  • {topic}")
        else:
            print("  (sin tópicos)")

    # Tópicos compartidos
    print("\n" + "-"*70)
    print("TÓPICOS COMPARTIDOS:")
    print("-"*70)

    persons = sorted(person_data.keys())
    shared_topics = defaultdict(list)

    # Comparar cada par de personas
    for i in range(len(persons)):
        for j in range(i+1, len(persons)):
            p1, p2 = persons[i], persons[j]
            common = person_data[p1]['topics'] & person_data[p2]['topics']
            if common:
                shared_topics[frozenset([p1, p2])] = sorted(common)

    if shared_topics:
        for pair, topics in sorted(shared_topics.items(), key=lambda x: len(x[1]), reverse=True):
            pair_list = sorted(list(pair))
            print(f"\n{pair_list[0]} ↔ {pair_list[1]} ({len(topics)} en común):")
            for topic in topics:
                print(f"  • {topic}")
    else:
        print("\nNo hay tópicos compartidos entre las personas.")

    # Tópicos que tienen TODAS las personas
    if len(persons) > 1:
        all_topics = person_data[persons[0]]['topics'].copy()
        for person in persons[1:]:
            all_topics &= person_data[person]['topics']

        print("\n" + "-"*70)
        print(f"TÓPICOS QUE COMPARTEN TODAS LAS PERSONAS ({len(all_topics)}):")
        print("-"*70)
        if all_topics:
            for topic in sorted(all_topics):
                print(f"  • {topic}")
        else:
            print("\nNo hay tópicos compartidos por todas las personas.")


def analyze_accounts(person_data):
    """Analiza cuentas seguidas y seguidores"""
    print("\n" + "="*70)
    print("ANÁLISIS DE CUENTAS")
    print("="*70)

    # Estadísticas por persona
    for person, data in sorted(person_data.items()):
        followers = data['followers']
        following = data['following']
        mutual = followers & following

        print(f"\n{person.upper()}:")
        print(f"  • Seguidores: {len(followers)}")
        print(f"  • Siguiendo: {len(following)}")
        print(f"  • Conexiones mutuas: {len(mutual)}")

    # Cuentas que TODAS las personas siguen
    persons = sorted(person_data.keys())
    if len(persons) > 1:
        all_following = person_data[persons[0]]['following'].copy()
        for person in persons[1:]:
            all_following &= person_data[person]['following']

        print("\n" + "-"*70)
        print(f"CUENTAS QUE TODAS LAS PERSONAS SIGUEN ({len(all_following)}):")
        print("-"*70)
        if all_following:
            for acc in sorted(all_following)[:50]:  # Limitar a 50
                print(f"  • {acc}")
            if len(all_following) > 50:
                print(f"  ... y {len(all_following) - 50} más")
        else:
            print("\nNo hay cuentas que todas las personas sigan.")

    # Cuentas compartidas por pares
    print("\n" + "-"*70)
    print("CUENTAS COMPARTIDAS ENTRE PARES DE PERSONAS:")
    print("-"*70)

    shared_following = defaultdict(list)
    for i in range(len(persons)):
        for j in range(i+1, len(persons)):
            p1, p2 = persons[i], persons[j]
            common = person_data[p1]['following'] & person_data[p2]['following']
            if common:
                shared_following[frozenset([p1, p2])] = sorted(common)

    for pair, accounts in sorted(shared_following.items(), key=lambda x: len(x[1]), reverse=True):
        pair_list = sorted(list(pair))
        print(f"\n{pair_list[0]} ↔ {pair_list[1]} ({len(accounts)} cuentas en común)")
        # Mostrar solo las primeras 20
        for acc in accounts[:20]:
            print(f"  • {acc}")
        if len(accounts) > 20:
            print(f"  ... y {len(accounts) - 20} más")

    # Seguidores compartidos
    print("\n" + "-"*70)
    print("SEGUIDORES COMPARTIDOS ENTRE PARES:")
    print("-"*70)

    shared_followers = defaultdict(list)
    for i in range(len(persons)):
        for j in range(i+1, len(persons)):
            p1, p2 = persons[i], persons[j]
            common = person_data[p1]['followers'] & person_data[p2]['followers']
            if common:
                shared_followers[frozenset([p1, p2])] = sorted(common)

    for pair, accounts in sorted(shared_followers.items(), key=lambda x: len(x[1]), reverse=True):
        pair_list = sorted(list(pair))
        print(f"\n{pair_list[0]} ↔ {pair_list[1]} ({len(accounts)} seguidores en común)")
        for acc in accounts[:20]:
            print(f"  • {acc}")
        if len(accounts) > 20:
            print(f"  ... y {len(accounts) - 20} más")


def generate_summary_report(person_data, output_file="reporte_completo.txt"):
    """Genera un reporte completo y detallado en archivo de texto"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("REPORTE COMPLETO DE ANÁLISIS SOCIAL - INSTAGRAM\n")
        f.write("="*70 + "\n\n")

        persons = sorted(person_data.keys())
        f.write(f"Número de personas analizadas: {len(persons)}\n")
        f.write(f"Personas: {', '.join(persons)}\n\n")

        # Estadísticas generales
        f.write("ESTADÍSTICAS GENERALES:\n")
        f.write("-"*70 + "\n")
        for person, data in sorted(person_data.items()):
            f.write(f"\n{person.upper()}:\n")
            f.write(f"  Seguidores: {len(data['followers'])}\n")
            f.write(f"  Siguiendo: {len(data['following'])}\n")
            f.write(f"  Tópicos de interés: {len(data['topics'])}\n")
            mutual = data['followers'] & data['following']
            f.write(f"  Conexiones mutuas: {len(mutual)}\n")

        # TÓPICOS INDIVIDUALES COMPLETOS
        f.write("\n" + "="*70 + "\n")
        f.write("TÓPICOS/GUSTOS POR PERSONA (COMPLETO):\n")
        f.write("="*70 + "\n")
        for person, data in sorted(person_data.items()):
            topics = data['topics']
            f.write(f"\n{person.upper()} - {len(topics)} tópicos:\n")
            if topics:
                for topic in sorted(topics):
                    f.write(f"  • {topic}\n")
            else:
                f.write("  (sin tópicos)\n")

        # Tópicos compartidos entre TODAS las personas
        if len(persons) > 1:
            all_topics = person_data[persons[0]]['topics'].copy()
            for person in persons[1:]:
                all_topics &= person_data[person]['topics']

            f.write("\n" + "="*70 + "\n")
            f.write(f"TÓPICOS COMPARTIDOS POR TODAS LAS PERSONAS ({len(all_topics)}):\n")
            f.write("="*70 + "\n")
            if all_topics:
                for topic in sorted(all_topics):
                    f.write(f"  • {topic}\n")
            else:
                f.write("\n(No hay tópicos compartidos por todas las personas)\n")

        # Tópicos compartidos por pares
        f.write("\n" + "="*70 + "\n")
        f.write("TÓPICOS/GUSTOS COMPARTIDOS ENTRE PARES:\n")
        f.write("="*70 + "\n")

        for i in range(len(persons)):
            for j in range(i+1, len(persons)):
                p1, p2 = persons[i], persons[j]
                common = person_data[p1]['topics'] & person_data[p2]['topics']
                f.write(f"\n{p1} ↔ {p2}: {len(common)} tópicos en común\n")
                if common:
                    for topic in sorted(common):
                        f.write(f"  • {topic}\n")
                else:
                    f.write("  (sin tópicos en común)\n")

        # CUENTAS QUE SIGUEN - PRIMEROS 5
        f.write("\n" + "="*70 + "\n")
        f.write("CUENTAS QUE SIGUE CADA PERSONA (primeros 5):\n")
        f.write("="*70 + "\n")
        for person, data in sorted(person_data.items()):
            following = data['following']
            f.write(f"\n{person.upper()} - sigue a {len(following)} cuentas:\n")
            if following:
                for acc in sorted(following)[:5]:
                    f.write(f"  • {acc}\n")
                if len(following) > 5:
                    f.write(f"  ... y {len(following) - 5} más\n")
            else:
                f.write("  (no sigue a nadie)\n")

        # SEGUIDORES - PRIMEROS 5
        f.write("\n" + "="*70 + "\n")
        f.write("SEGUIDORES DE CADA PERSONA (primeros 5):\n")
        f.write("="*70 + "\n")
        for person, data in sorted(person_data.items()):
            followers = data['followers']
            f.write(f"\n{person.upper()} - {len(followers)} seguidores:\n")
            if followers:
                for acc in sorted(followers)[:5]:
                    f.write(f"  • {acc}\n")
                if len(followers) > 5:
                    f.write(f"  ... y {len(followers) - 5} más\n")
            else:
                f.write("  (sin seguidores)\n")

        # CONEXIONES MUTUAS - PRIMEROS 5
        f.write("\n" + "="*70 + "\n")
        f.write("CONEXIONES MUTUAS POR PERSONA (primeros 5):\n")
        f.write("="*70 + "\n")
        for person, data in sorted(person_data.items()):
            mutual = data['followers'] & data['following']
            f.write(f"\n{person.upper()} - {len(mutual)} conexiones mutuas:\n")
            if mutual:
                for acc in sorted(mutual)[:5]:
                    f.write(f"  • {acc}\n")
                if len(mutual) > 5:
                    f.write(f"  ... y {len(mutual) - 5} más\n")
            else:
                f.write("  (sin conexiones mutuas)\n")

        # Cuentas que TODAS las personas siguen
        if len(persons) > 1:
            all_following = person_data[persons[0]]['following'].copy()
            for person in persons[1:]:
                all_following &= person_data[person]['following']

            f.write("\n" + "="*70 + "\n")
            f.write(f"CUENTAS QUE TODAS LAS PERSONAS SIGUEN ({len(all_following)}):\n")
            f.write("="*70 + "\n")
            if all_following:
                for acc in sorted(all_following):
                    f.write(f"  • {acc}\n")
            else:
                f.write("\n(No hay cuentas que todas las personas sigan)\n")

        # Cuentas compartidas por pares
        f.write("\n" + "="*70 + "\n")
        f.write("CUENTAS SEGUIDAS EN COMÚN ENTRE PARES (COMPLETO):\n")
        f.write("="*70 + "\n")

        for i in range(len(persons)):
            for j in range(i+1, len(persons)):
                p1, p2 = persons[i], persons[j]
                common = person_data[p1]['following'] & person_data[p2]['following']
                f.write(f"\n{p1} ↔ {p2}: {len(common)} cuentas en común\n")
                if common:
                    for acc in sorted(common):
                        f.write(f"  • {acc}\n")
                else:
                    f.write("  (sin cuentas en común)\n")

        # Seguidores compartidos por pares
        f.write("\n" + "="*70 + "\n")
        f.write("SEGUIDORES COMPARTIDOS ENTRE PARES (COMPLETO):\n")
        f.write("="*70 + "\n")

        for i in range(len(persons)):
            for j in range(i+1, len(persons)):
                p1, p2 = persons[i], persons[j]
                common = person_data[p1]['followers'] & person_data[p2]['followers']
                f.write(f"\n{p1} ↔ {p2}: {len(common)} seguidores en común\n")
                if common:
                    for acc in sorted(common):
                        f.write(f"  • {acc}\n")
                else:
                    f.write("  (sin seguidores en común)\n")

    print(f"\n✓ Reporte completo guardado en: {output_file}")


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Analiza datos sociales de Instagram")
    ap.add_argument("--data", default="./data", help="Carpeta con archivos JSON (default: ./data)")
    ap.add_argument("--out", default="./out", help="Carpeta de salida para reportes (default: ./out)")
    args = ap.parse_args()

    print("Cargando datos...")
    person_data = load_person_data(args.data)

    if not person_data:
        print("ERROR: No se encontraron datos de personas en la carpeta especificada.")
        return

    print(f"✓ Se cargaron datos de {len(person_data)} persona(s): {', '.join(sorted(person_data.keys()))}")

    # Análisis de tópicos
    analyze_topics(person_data)

    # Análisis de cuentas
    analyze_accounts(person_data)

    # Generar reporte en archivo
    os.makedirs(args.out, exist_ok=True)
    output_file = os.path.join(args.out, "reporte_completo.txt")
    generate_summary_report(person_data, output_file)

    print("\n" + "="*70)
    print("✓ ANÁLISIS COMPLETADO")
    print("="*70)


if __name__ == "__main__":
    main()
