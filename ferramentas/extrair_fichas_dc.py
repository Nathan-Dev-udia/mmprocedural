"""Extrai dados mecanicos das fichas publicadas em DC Adventures H&V."""

import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
SOURCE = {
    "volume1": ROOT / "dc" / "dc adventures heroes and villains vol1.pdf",
    "volume2": ROOT / "dc" / "dc adventures heroes and villains vol 2.pdf",
}
OUTPUT = ROOT / "dc" / "fichas"
ABILITIES = ("STR", "STA", "AGL", "DEX", "FGT", "INT", "AWE", "PRE")
SECTIONS = (
    ("poderes", "Powers"),
    ("equipamento", "Equipment"),
    ("vantagens", "Advantages"),
    ("pericias", "Skills"),
    ("ataques", "Offense"),
    ("defesas", "Defense"),
    ("pontos_poder", "Power Points"),
    ("complicacoes", "Complications"),
)


def _word_pattern(word):
    letters = [char for char in word if char.isalpha()]
    return r"\s*".join(re.escape(char) for char in letters)


def _section_pattern(label):
    words = label.split()
    body = r"\s+".join(_word_pattern(word) for word in words)
    return re.compile(r"(?im)^[ \t]*" + body + r"[ \t]*$")


def _display_name(raw):
    raw = " ".join(raw.replace("\xa0", " ").replace("�", "'").split())
    raw = raw.strip(" .,:;|-")
    raw = re.sub(r"(?i)^PL\s*\d{1,2}\s*", "", raw)
    raw = re.sub(r"^\d+\s+", "", raw)
    if len(raw) > 65:
        tail = re.search(
            r"([A-Za-z][A-Za-z0-9'’.-]*(?:\s+[A-Za-z][A-Za-z0-9'’.-]*){0,5}"
            r"(?:\s*\([^)]{1,45}\))?)$",
            raw,
        )
        raw = tail.group(1) if tail else raw[-55:]
    raw = raw.title()
    raw = re.sub(r"\bI\.q\.\b", "I.Q.", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\bO\.m\.a\.c\.\b", "O.M.A.C.", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\bH\.i\.v\.e\.\b", "H.I.V.E.", raw, flags=re.IGNORECASE)
    return raw.strip()


def _slug(name):
    value = unicodedata.normalize("NFKD", name)
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "personagem"


def _read_abilities(text, start, column_index=0):
    signature = re.compile(
        r"(?i)\bS\s*T\s*R\b\s+\bS\s*T\s*A\b\s+\bA\s*G\s*L\b"
        r"\s+\bD\s*E\s*X\b\s+\bF\s*G\s*T\b\s+\bI\s*N\s*T\b"
        r"\s+\bA\s*W\s*E\b\s+\bP\s*R\s*E\b"
    )
    end = min(len(text), start + 700)
    region = text[start:end]

    compact = list(
        re.finditer(
            r"(?is)A\s*B\s*I\s*L\s*I\s*T\s*I\s*E\s*S\s*:\s*(.{0,350})",
            region,
        )
    )
    if compact:
        selected = compact[min(column_index, len(compact) - 1)]
        pairs = re.findall(
            r"(?i)\b(STR|STA|AGL|DEX|FGT|INT|AWE|PRE)\b\s*"
            r"([-+]?\d+(?:/\d+)?|--+|[—–-])",
            selected.group(1),
        )
        groups = [pairs[index:index + 8] for index in range(0, len(pairs) - 7, 8)]
        valid_groups = [
            group for group in groups
            if tuple(key.upper() for key, _ in group) == ABILITIES
        ]
        if valid_groups:
            values = {
                key.upper(): value
                for key, value in valid_groups[min(column_index, len(valid_groups) - 1)]
            }
            return {key: values[key] for key in ABILITIES}

    signatures = list(signature.finditer(region))
    if signatures:
        selected = signatures[min(column_index, len(signatures) - 1)]
        for line in region[selected.end():].splitlines()[:5]:
            values = re.findall(r"[-+]?\d+(?:/\d+)?|--+|[—–-]", line)
            if len(values) >= 8:
                offset = column_index * 8 if len(values) >= (column_index + 1) * 8 else 0
                if len(values) >= offset + 8:
                    return dict(zip(ABILITIES, values[offset:offset + 8]))

    return None


def _title_fragment(text, match):
    line_start = text.rfind("\n", 0, match.start()) + 1
    prefix = text[line_start:match.start()]
    previous_matches = list(
        re.finditer(r"(?i)\bP\s*L\s*\d{1,2}\b", prefix)
    )
    if previous_matches:
        prefix = prefix[previous_matches[-1].end():]
    chunks = [chunk.strip() for chunk in re.split(r"\s{3,}", prefix) if chunk.strip()]
    if chunks:
        prefix = chunks[-1]
    prefix = re.sub(r"(?i)\b\d{1,4}\s*POINTS?\b.*$", "", prefix).strip()
    title_position = line_start + text[line_start:match.start()].rfind(prefix)
    return prefix, title_position


def _record_title(text, match):
    raw, _ = _title_fragment(text, match)
    return _display_name(raw)


def _find_profiles(text, uppercase_only=False):
    profiles = []
    matches = list(re.finditer(r"(?i)\bP\s*L\s*(\d{1,2})\b", text))
    for match in matches:
        line_start = text.rfind("\n", 0, match.start()) + 1
        prefix = text[line_start:match.start()]
        column_index = len(
            re.findall(r"(?i)\bP\s*L\s*\d{1,2}\b", prefix)
        )
        abilities = _read_abilities(text, match.end(), column_index)
        if not abilities:
            continue
        name = _record_title(text, match)
        if not name or len(name) > 65 or not re.search(r"[A-Za-z]", name):
            continue
        if re.search(
            r"\b(?:abilities|advantages|attack|complications|damage|defense|"
            r"defenses|equipment|offense|points|powers|sidekick|skills|total)\b"
            r"|the following.{0,20}lower statistics",
            name,
            re.IGNORECASE,
        ):
            continue
        if uppercase_only and not prefix.strip().replace("�", "").isupper():
            continue
        profiles.append(
            {
                "match": match,
                "nome": name,
                "nivel_poder": int(match.group(1)),
                "habilidades": abilities,
                "coluna": column_index,
                "title_position": _title_fragment(text, match)[1],
            }
        )
    return profiles


def _layout_profile_blocks(text, profiles):
    lines = text.splitlines()
    locations = []
    for profile in profiles:
        line_index = text.count("\n", 0, profile["match"].start())
        line_start = text.rfind("\n", 0, profile["match"].start()) + 1
        column_position = profile["title_position"] - line_start
        locations.append((profile, line_index, column_position))

    positions = sorted(location[2] for location in locations)
    gaps = [
        (positions[index + 1] - positions[index], index)
        for index in range(len(positions) - 1)
    ]
    split = None
    if gaps:
        gap, index = max(gaps)
        if gap >= 20:
            split = (positions[index] + positions[index + 1]) // 2

    columns = []
    for line in lines:
        if split is None:
            columns.append([line])
        else:
            columns.append([line[:split], line[split:]])

    blocks = {}
    for profile, line_index, position in locations:
        column_index = 0 if split is None or position < split else 1
        next_lines = [
            other_line
            for other_profile, other_line, other_position in locations
            if other_profile is not profile
            and other_line > line_index
            and (0 if split is None or other_position < split else 1) == column_index
        ]
        end_line = min(next_lines) if next_lines else len(lines)
        block = "\n".join(line[column_index] for line in columns[line_index:end_line])
        blocks[id(profile)] = block
    return blocks


def _normalize_text(value):
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", normalized.casefold())


def _coordinate_profile_sections(page, profiles):
    items = []

    def collect(text, cm, tm, font, font_size):
        if text.strip():
            items.append((tm[4], tm[5], text))

    page.extract_text(visitor_text=collect)
    rows = {}
    for x, y, text in items:
        rows.setdefault(round(y, 1), []).append((x, text))

    locations = []
    for profile in profiles:
        name = _normalize_text(profile["nome"])
        level = profile["nivel_poder"]
        selected = None
        for y, row in sorted(rows.items(), reverse=True):
            row_items = sorted(row)
            row_text = "".join(text for _, text in row_items)
            normalized_row = _normalize_text(row_text)
            name_start = normalized_row.find(name)
            if name_start < 0:
                continue
            if f"pl{level}" not in normalized_row[name_start + len(name):]:
                continue
            name_tokens = [
                token for token in re.findall(r"[a-z0-9]+", profile["nome"].casefold())
                if len(token) >= 3
            ]
            matches = [
                x for x, text in row_items
                if any(token in _normalize_text(text) for token in name_tokens)
            ]
            selected = (y, min(matches) if matches else row_items[0][0])
            break
        if selected:
            locations.append((profile, selected[0], selected[1]))

    if not locations:
        return {}

    left = any(x < 261 for _, _, x in locations)
    right = any(x >= 261 for _, _, x in locations)
    separate_columns = left and right
    blocks = {}
    for profile, y, x in locations:
        column = 0 if x < 261 else 1
        following = [
            next_y for other, next_y, other_x in locations
            if other is not profile
            and next_y < y
            and (0 if other_x < 261 else 1) == column
        ]
        lower_y = max(following) + 2 if following else float("-inf")
        selected_items = [
            (item_x, item_y, text)
            for item_x, item_y, text in items
            if lower_y < item_y <= y + 1
            and (
                not separate_columns
                or (item_x < 261 if column == 0 else item_x >= 261)
            )
        ]
        row_texts = {}
        for item_x, item_y, text in selected_items:
            row_texts.setdefault(round(item_y, 1), []).append((item_x, text))
        ordered_rows = [
            (row_y, _normalize_text("".join(text for _, text in sorted(row))))
            for row_y, row in sorted(row_texts.items(), reverse=True)
        ]
        complication_row = None
        for start in range(len(ordered_rows)):
            combined = ""
            for end in range(start, min(start + 5, len(ordered_rows))):
                combined += ordered_rows[end][1]
                if combined.startswith("complications"):
                    complication_row = end
                    break
            if complication_row is not None:
                break
        if complication_row is not None:
            previous_y = ordered_rows[complication_row][0]
            for row_y, _ in ordered_rows[complication_row + 1:]:
                if previous_y - row_y > 18:
                    selected_items = [
                        item for item in selected_items
                        if item[1] >= previous_y - 1
                    ]
                    break
                previous_y = row_y
        selected_items.sort(key=lambda item: (-item[1], item[0]))
        column_texts = {}
        for item_x, _, text in selected_items:
            item_column = 0 if item_x < 261 else 1
            column_texts.setdefault(item_column, []).extend(text.splitlines())
        blocks[id(profile)] = {
            column: "\n".join(lines)
            for column, lines in column_texts.items()
        }
    return blocks


def _extract_sections(block, inline=False):
    markers = []
    for key, label in SECTIONS:
        patterns = [
            _section_pattern(label),
            re.compile(
            r"(?im)(?<![A-Za-z])" + _word_pattern(label) + r"\s*:"
            ),
        ]
        if inline:
            patterns.append(
                re.compile(
                    r"(?im)(?<![A-Za-z])" + _word_pattern(label)
                    + r"(?=\s+(?![\d*+\-])\S)"
                )
            )
        found = [
            result
            for pattern in patterns
            if (result := pattern.search(block))
        ]
        if found:
            marker = min(found, key=lambda item: item.start())
            markers.append((marker.start(), marker.end(), key))
    totals = re.search(
        r"(?im)(?<![A-Za-z])" + _word_pattern("Totals") + r"\s*:",
        block,
    )
    if totals:
        markers.append((totals.start(), totals.end(), "pontos_poder"))
    markers.sort()
    point_marker = next(
        (start for start, _, key in markers if key == "pontos_poder"),
        None,
    )
    if point_marker is not None:
        markers = [
            marker for marker in markers
            if marker[0] <= point_marker or marker[2] == "complicacoes"
        ]

    stop_labels = [
        _word_pattern("Personality"),
        _word_pattern("Powers") + r"\s*&\s*" + _word_pattern("Abilities"),
        _word_pattern("Allies"),
        _word_pattern("Enemies"),
        _word_pattern("Real Name"),
        _word_pattern("Occupation"),
        _word_pattern("Base"),
    ]
    stop = re.search(
        r"(?im)^[ \t]*(?:" + "|".join(stop_labels) + r")\b",
        block,
    )
    complication_marker = next(
        (start for start, _, key in markers if key == "complicacoes"),
        None,
    )
    end = (
        stop.start()
        if stop and (complication_marker is None or stop.start() < complication_marker)
        else len(block)
    )
    markers = [item for item in markers if item[0] < end]
    sections = {}
    for index, (start, body_start, key) in enumerate(markers):
        next_start = markers[index + 1][0] if index + 1 < len(markers) else end
        value = " ".join(block[body_start:next_start].split())
        if value:
            sections[key] = value
    return sections


def _extract_layout_section(block, key):
    label = dict(SECTIONS)[key]
    pattern = re.compile(
        r"(?i)(?<![A-Za-z])" + _word_pattern(label) + r"(?![A-Za-z])"
    )
    lines = block.splitlines()
    gaps = []
    for line in lines:
        gaps.extend(
            (match.start(), len(match.group()))
            for match in re.finditer(r" {12,}(?=\S)", line)
        )
    gap_counts = {}
    for position, length in gaps:
        if position > 10 and length >= 18:
            bucket = position // 10
            gap_counts[bucket] = gap_counts.get(bucket, 0) + 1
    boundary = None
    if gap_counts:
        bucket, count = max(gap_counts.items(), key=lambda item: item[1])
        if count >= 4:
            boundary = bucket * 10 + 5

    for line_index, line in enumerate(lines):
        found = pattern.search(line)
        if not found:
            continue
        remainder = line[found.end():]
        if re.match(r"\s*(?:\d|\*)", remainder):
            continue

        if boundary is None:
            column_start = found.start()
            column_end = None
        elif found.start() < boundary:
            column_start = 0
            column_end = boundary
        else:
            column_start = boundary
            column_end = None
        values = []
        inline_body = (
            line[found.end():column_end].strip()
            if column_end is not None
            else remainder.strip()
        )
        if ":" in line[found.start():found.end() + 2]:
            values.append(inline_body)
        for next_line in lines[line_index + 1:]:
            column = next_line[column_start:column_end].strip()
            if not column:
                continue
            if any(
                re.match(
                    r"(?i)^\s*" + _word_pattern(section_label) + r"(?![A-Za-z])",
                    column,
                )
                for _, section_label in SECTIONS
            ):
                break
            if re.match(
                r"(?i)^\s*(?:PERSONALITY|POWERS\s*&\s*ABILITIES|ALLIES|"
                r"ENEMIES|REAL\s+NAME|OCCUPATION|BASE)\b",
                column,
            ):
                break
            values.append(column)
        value = " ".join(" ".join(values).split())
        if value:
            return value
    return ""


def _clean_complications(value):
    first_label = re.search(
        r"(?i)\b[A-Za-z][A-Za-z’'-]*(?:\s+[A-Za-z][A-Za-z’'-]*){0,3}:\s*",
        value,
    )
    if first_label:
        value = value[first_label.start():]
    for marker in (
        r"\bReal\s+Name\s*:",
        r"\bOccupation\s*:",
        r"\bBase\s*:",
        r"\bHeroes\s*&\s*Villains\b",
        r"\bAndre\s+Nutter\b",
        r"\b\d{1,3}\s+\d{1,3}\s+178\.76\.\d{1,3}\.\d{1,3}\b",
        r"\bLuthor['’]s\s+war\s*S\s*u\s*I\s*t\b",
        r"\bOrange\s+Lantern\s+ring\b",
    ):
        found = re.search(marker, value, re.IGNORECASE)
        if found:
            value = value[:found.start()]
    return value.strip()


def _total_points(text):
    compact = re.sub(r"\s+", "", text).casefold()
    match = re.search(r"total(\d{1,4})", compact)
    if not match:
        match = re.search(r"=\s*(\d{1,4})\b", text)
    return int(match.group(1)) if match else None


def extract_volume(volume, source):
    reader = PdfReader(str(source))
    profiles = []
    seen = set()
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text(extraction_mode="layout") or ""
        plain_text = page.extract_text() or ""
        accepted = _find_profiles(text)
        for profile in accepted:
            profile["layout"] = True
        layout_profiles = accepted.copy()
        layout_profiles.sort(key=lambda item: item["match"].start())
        layout_blocks = _layout_profile_blocks(text, layout_profiles)
        plain_profiles = _find_profiles(plain_text, uppercase_only=True)
        for profile in plain_profiles:
            same_name = next(
                (
                    item for item in accepted
                    if item["nome"].casefold() == profile["nome"].casefold()
                    and item["nivel_poder"] == profile["nivel_poder"]
                ),
                None,
            )
            same_stats = [
                item for item in accepted
                if item["nivel_poder"] == profile["nivel_poder"]
                and item["habilidades"] == profile["habilidades"]
            ]
            if same_name:
                continue
            if len(same_stats) == 1 and (
                same_stats[0]["nome"].casefold() in profile["nome"].casefold()
                or profile["nome"].casefold() in same_stats[0]["nome"].casefold()
            ):
                same_stats[0]["nome"] = profile["nome"]
                continue
            if not same_stats:
                profile["layout"] = False
                accepted.append(profile)

        accepted_names = {
            (profile["nome"].casefold(), profile["nivel_poder"])
            for profile in accepted
        }
        plain_matches = _find_profiles(plain_text)
        coordinate_blocks = _coordinate_profile_sections(page, accepted)
        for index, profile in enumerate(accepted):
            name = profile["nome"]
            abilities = profile["habilidades"]
            layout_block = layout_blocks.get(id(profile))
            if layout_block:
                block_abilities = _read_abilities(layout_block, 0)
                if block_abilities:
                    abilities = block_abilities
            mapped = next(
                (
                    item for item in plain_matches
                    if item["nome"].casefold() == name.casefold()
                    and item["nivel_poder"] == profile["nivel_poder"]
                ),
                None,
            )
            if mapped:
                same_stats = [
                    item for item in plain_matches
                    if item["habilidades"] == mapped["habilidades"]
                    and item["nome"].casefold() != mapped["nome"].casefold()
                ]
                if not same_stats:
                    abilities = mapped["habilidades"]
            if len(accepted) == 1:
                sections = _extract_sections(plain_text)
            elif mapped:
                following = [
                    item["match"].start()
                    for item in plain_matches
                    if item["match"].start() > mapped["match"].start()
                    and (item["nome"].casefold(), item["nivel_poder"])
                    in accepted_names
                ]
                block_end = min(following) if following else len(plain_text)
                sections = _extract_sections(
                    plain_text[mapped["match"].start():block_end]
                )
                prefix_sections = _extract_sections(
                    plain_text[:mapped["match"].start()]
                )
                if (
                    not any(
                        item["match"].start() < mapped["match"].start()
                        for item in plain_matches
                    )
                    and len(prefix_sections) >= 4
                ):
                    sections = prefix_sections
            else:
                sections = {}
            if profile.get("layout") and not coordinate_blocks.get(id(profile)):
                layout_block = layout_blocks[id(profile)]
                layout_sections = _extract_sections(
                    layout_block,
                    inline=True,
                )
                for key, value in layout_sections.items():
                    sections.setdefault(key, value)
                for key, _ in SECTIONS:
                    column_value = _extract_layout_section(layout_block, key)
                    if column_value and (
                        key not in sections
                        or (key == "complicacoes" and len(column_value) < len(sections[key]))
                    ):
                        sections[key] = column_value
            coordinate_sections = {}
            for column in sorted(coordinate_blocks.get(id(profile), {})):
                column_sections = _extract_sections(
                    coordinate_blocks[id(profile)][column],
                    inline=True,
                )
                coordinate_sections.update(column_sections)
            if coordinate_sections:
                powers = coordinate_sections.get("poderes", "")
                embedded_advantages = re.search(
                    r"(?i)(?<![A-Za-z])Benefit\s*\(",
                    powers,
                )
                if "vantagens" not in coordinate_sections and embedded_advantages:
                    coordinate_sections["poderes"] = powers[:embedded_advantages.start()].strip()
                    coordinate_sections["vantagens"] = powers[embedded_advantages.start():].strip()
                sections = coordinate_sections
            point_summary = sections.get("pontos_poder", "")
            point_total = re.search(
                r"(?i)\bTotal\s*:?\s*\d{1,4}\b|=\s*\d{1,4}\b",
                point_summary,
            )
            if point_total:
                sections["pontos_poder"] = point_summary[:point_total.end()].strip()
            if "complicacoes" in sections:
                sections["complicacoes"] = _clean_complications(
                    sections["complicacoes"]
                )

            slug = _slug(name)
            if slug in seen:
                slug = f"{slug}_p{page_number}"
                duplicate_index = 2
                while slug in seen:
                    slug = f"{_slug(name)}_p{page_number}_{duplicate_index}"
                    duplicate_index += 1
            seen.add(slug)
            profile = {
                "nome": name,
                "sistema": "DC Adventures / Mutants & Masterminds 3e",
                "nivel_poder": profile["nivel_poder"],
                "pontos_poder_publicados": _total_points(sections.get("pontos_poder", "")),
                "fonte": {
                    "arquivo": source.name,
                    "pagina_pdf": page_number,
                },
                "ficha_publicada": {
                    "habilidades": abilities,
                    **sections,
                },
            }
            profiles.append((slug, profile))
    return profiles


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for volume, source in SOURCE.items():
        destination = OUTPUT / volume
        destination.mkdir(parents=True, exist_ok=True)
        profiles = extract_volume(volume, source)
        written = set()
        for slug, profile in profiles:
            target = destination / f"{slug}.json"
            target.write_text(
                json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            written.add(target.name)
        for target in destination.glob("*.json"):
            if target.name not in written:
                target.unlink()
        print(f"{volume}: {len(profiles)} fichas extraidas para {destination}")


if __name__ == "__main__":
    main()
