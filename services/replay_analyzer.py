import json
import os
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Tuple

HAZARDS = {
    "Stealth Rock": "rocks",
    "Spikes": "spikes",
    "Toxic Spikes": "tspikes",
    "Sticky Web": "web",
}


def _is_valid_replay_url(url: str) -> bool:
    return url.startswith("https://replay.pokemonshowdown.com/")


def _normalize_replay_url(url: str) -> str:
    # Ensure .json endpoint
    if not url.endswith(".json"):
        if url.endswith(".log"):
            url = url[:-4]
        url = url + ".json"
    return url


def fetch_replay(url: str) -> Dict:
    if not _is_valid_replay_url(url):
        raise ValueError("Link inválido. Use um replay do replay.pokemonshowdown.com")
    json_url = _normalize_replay_url(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BattleDexBot/1.0)",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://replay.pokemonshowdown.com/",
    }

    def _try(url_candidate: str):
        req = urllib.request.Request(url_candidate, headers=headers)
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                raise ValueError(f"Falha ao baixar replay (status {resp.status})")
            return resp.read()

    try:
        data = _try(json_url)
    except Exception as exc1:
        # Fallback: tentar .log se .json falhar (padrão PS)
        try:
            log_url = json_url.replace(".json", ".log")
            data = _try(log_url)
        except Exception as exc2:
            raise ValueError(f"Falha ao baixar replay (.json e .log): {exc1} / {exc2}") from exc2

    try:
        return json.loads(data)
    except Exception as exc:
        raise ValueError(f"Replay retornou JSON inválido: {exc}")


def _parse_hazards_line(parts: List[str]) -> Tuple[str, str, str] | None:
    # examples: ['-sidestart', 'p1a: Foo', 'move: Stealth Rock']
    if len(parts) < 3:
        return None
    side = parts[1][:2]  # p1 / p2
    move = parts[2].replace("move: ", "").strip()
    hazard_key = HAZARDS.get(move)
    if not hazard_key:
        return None
    action = "placed" if parts[0] == "-sidestart" else "removed"
    return side, action, hazard_key


def analyze_log(log_text: str):
    turns = 0
    kos = {"p1": 0, "p2": 0}
    hazards = {
        "p1": {"placed": [], "removed": []},
        "p2": {"placed": [], "removed": []},
    }

    for raw_line in log_text.splitlines():
        if not raw_line.startswith("|"):
            continue
        parts = raw_line.split("|")[1:]  # drop leading empty
        if not parts:
            continue

        tag = parts[0]
        if tag == "turn" and len(parts) > 1:
            try:
                turns = int(parts[1])
            except ValueError:
                pass
        elif tag == "faint" and len(parts) > 1:
            side = parts[1][:2]  # p1a:, p2a:
            if side in kos:
                # This faint belongs to the side of the fainted mon, so opponent got a KO
                if side == "p1":
                    kos["p2"] += 1
                elif side == "p2":
                    kos["p1"] += 1
        elif tag in {"-sidestart", "-sideend"}:
            parsed = _parse_hazards_line(parts)
            if parsed:
                side, action, hazard = parsed
                if side in hazards:
                    hazards[side][action].append(hazard)

    return {"turns": turns, "kos": kos, "hazards": hazards}


def summarize_replay(data: Dict) -> Dict:
    log_text = data.get("log", "")
    winner = data.get("winner") or "?"
    # Extrai nomes dos jogadores
    p1, p2 = None, None
    players_list = data.get("players")
    if isinstance(players_list, list) and len(players_list) >= 2:
        p1, p2 = players_list[0], players_list[1]
    if not p1 or not p2:
        for line in log_text.splitlines():
            if line.startswith("|player|p1|"):
                parts = line.split("|")
                if len(parts) > 3:
                    p1 = parts[3]
            if line.startswith("|player|p2|"):
                parts = line.split("|")
                if len(parts) > 3:
                    p2 = parts[3]
            if p1 and p2:
                break
    if not p1:
        p1 = data.get("p1", "p1")
    if not p2:
        p2 = data.get("p2", "p2")

    # Se winner não veio no JSON, tentar extrair da linha '|win|Nome'
    if winner == "?":
        for line in log_text.splitlines():
            if line.startswith("|win|"):
                parts = line.split("|")
                if len(parts) > 2:
                    winner = parts[2]
                    break
        # Regex fallback: captura qualquer '|win|nome'
        if winner == "?":
            import re as _re
            m = _re.search(r"\|win\|([^|\n]+)", log_text)
            if m:
                winner = m.group(1)
        # Fallback final: procurar mensagem 'won the battle'
        if winner == "?":
            m = _re.search(r"([^|\n]+) won the battle!", log_text)
            if m:
                winner = m.group(1).strip()
    tier = data.get("format", "?")

    parsed = analyze_log(log_text)
    return {
        "winner": winner,
        "p1": p1,
        "p2": p2,
        "tier": tier,
        "turns": parsed.get("turns", 0),
        "kos": parsed.get("kos", {}),
        "hazards": parsed.get("hazards", {}),
    }


def build_text_summary(summary: Dict) -> str:
    p1 = summary["p1"]
    p2 = summary["p2"]
    winner = summary["winner"]
    turns = summary["turns"]
    tier = summary["tier"]
    kos = summary["kos"]
    hazards = summary["hazards"]

    def _haz_line(side: str) -> str:
        placed = hazards.get(side, {}).get("placed", [])
        removed = hazards.get(side, {}).get("removed", [])
        def fmt(arr):
            return ", ".join(arr) if arr else "—"
        return f"Colocou: {fmt(placed)} | Removeu: {fmt(removed)}"

    lines = [
        f"🏆 Vencedor: {winner}",
        f"Tier: {tier}",
        f"Turnos: {turns}",
        f"KOs — {p1}: {kos.get('p1', 0)} | {p2}: {kos.get('p2', 0)}",
        f"Hazards {p1}: {_haz_line('p1')}",
        f"Hazards {p2}: {_haz_line('p2')}",
    ]
    return "\n".join(lines)


def _load_stats(path: str) -> Dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_stats(path: str, data: Dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_player_stats(path: str, summary: Dict):
    stats = _load_stats(path)
    p1 = summary["p1"]
    p2 = summary["p2"]
    winner = summary["winner"]
    tier = summary.get("tier") or "?"
    turns = summary.get("turns", 0)
    hazards = summary.get("hazards", {})

    def ensure_player(name: str):
        stats.setdefault(name, {})
        stats[name].setdefault(tier, {
            "wins": 0,
            "losses": 0,
            "games": 0,
            "turns_total": 0,
            "hazards_placed": 0,
            "hazards_removed": 0,
        })

    for player, side in ((p1, "p1"), (p2, "p2")):
        ensure_player(player)
        entry = stats[player][tier]
        entry["games"] += 1
        entry["turns_total"] += turns
        entry["hazards_placed"] += len(hazards.get(side, {}).get("placed", []))
        entry["hazards_removed"] += len(hazards.get(side, {}).get("removed", []))

    if winner == p1:
        stats[p1][tier]["wins"] += 1
        stats[p2][tier]["losses"] += 1
    elif winner == p2:
        stats[p2][tier]["wins"] += 1
        stats[p1][tier]["losses"] += 1

    _save_stats(path, stats)


def format_player_stats(path: str, player: str, tier: str | None = None) -> str:
    stats = _load_stats(path)
    if player not in stats:
        return "Nenhuma estatística registrada para esse jogador."
    tiers = [tier] if tier else sorted(stats[player].keys())
    lines = []
    for t in tiers:
        entry = stats[player].get(t)
        if not entry:
            continue
        games = entry.get("games", 0)
        wins = entry.get("wins", 0)
        losses = entry.get("losses", 0)
        avg_turns = round(entry.get("turns_total", 0) / games, 1) if games else 0
        hz_p = entry.get("hazards_placed", 0)
        hz_r = entry.get("hazards_removed", 0)
        lines.append(
            f"Tier {t}: {wins}W/{losses}L ({games} jogos) | Turnos médios: {avg_turns} | Hazards colocados/removidos: {hz_p}/{hz_r}"
        )
    return "\n".join(lines) if lines else "Nenhuma estatística encontrada."


def analyze_replay(url: str, stats_path: str | None = None) -> Tuple[str, Dict]:
    data = fetch_replay(url)
    summary = summarize_replay(data)
    if stats_path:
        update_player_stats(stats_path, summary)
    text = build_text_summary(summary)
    return text, summary
