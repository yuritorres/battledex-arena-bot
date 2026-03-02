import os
import json
import random
import asyncio
import sqlite3
from datetime import datetime, timedelta, time
from typing import Dict, Optional, List

from telegram.ext import CommandHandler, PollAnswerHandler
from telegram import Update

try:
    from openai import OpenAI
except ImportError:  # openai package name fallback
    OpenAI = None


class QuizConfig:
    def __init__(
        self,
        storage_dir: str,
        quiz_group_id: Optional[int],
        quiz_topic_id: Optional[int],
        questions_per_day: int = 5,
        expire_minutes: int = 1,
        expire_buffer_seconds: int = 15,
        model: str = "gpt-4o-mini",
    ):
        self.storage_dir = storage_dir
        self.quiz_group_id = quiz_group_id
        self.quiz_topic_id = quiz_topic_id
        self.questions_per_day = questions_per_day
        self.expire_minutes = expire_minutes
        self.expire_buffer_seconds = expire_buffer_seconds
        self.model = model

        os.makedirs(self.storage_dir, exist_ok=True)
        self.questions_file = os.path.join(self.storage_dir, "questions.json")
        self.scores_db = os.path.join(self.storage_dir, "scores.db")
        self.questions_db = os.path.join(self.storage_dir, "questions.db")


def _ensure_questions_list(cfg: QuizConfig):
    if not os.path.exists(cfg.questions_file):
        sample = ["pikachu", "charizard", "bulbasaur", "squirtle"]
        with open(cfg.questions_file, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
    with open(cfg.questions_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OpenAI:
        return None
    return OpenAI(api_key=api_key)


def _init_dbs(cfg: QuizConfig):
    conn_scores = sqlite3.connect(cfg.scores_db)
    cur = conn_scores.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            user_id INTEGER PRIMARY KEY,
            score INTEGER
        )
        """
    )
    conn_scores.commit()
    conn_scores.close()

    conn_questions = sqlite3.connect(cfg.questions_db)
    cur = conn_questions.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pokemon TEXT,
            question TEXT,
            options TEXT,
            answer_index INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn_questions.commit()
    conn_questions.close()


def _insert_question(cfg: QuizConfig, pokemon: str, question: str, options, answer_idx: int):
    conn = sqlite3.connect(cfg.questions_db)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO questions (pokemon, question, options, answer_index) VALUES (?, ?, ?, ?)",
        [pokemon, question, json.dumps(options, ensure_ascii=False), answer_idx],
    )
    conn.commit()
    conn.close()


def _add_score(cfg: QuizConfig, user_id: int):
    conn = sqlite3.connect(cfg.scores_db)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scores VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET score = scores.score + 1;",
        [user_id],
    )
    conn.commit()
    conn.close()


def _load_scores(cfg: QuizConfig):
    conn = sqlite3.connect(cfg.scores_db)
    cur = conn.cursor()
    cur.execute("SELECT user_id, score FROM scores ORDER BY score DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def register_quiz_handlers(app, storage_dir: str, quiz_group_id: Optional[int], quiz_topic_id: Optional[int]):
    """
    Integra o quiz ao app principal. Requer OPENAI_API_KEY e chat configurado.
    Se quiz_group_id não for fornecido, o módulo é ignorado com log.
    """
    cfg = QuizConfig(
        storage_dir=storage_dir,
        quiz_group_id=quiz_group_id,
        quiz_topic_id=quiz_topic_id,
    )
    client = _get_client()
    if not client:
        app.logger.warning("Quiz desabilitado: OPENAI_API_KEY ausente ou pacote openai não instalado.")
        return
    if not cfg.quiz_group_id:
        app.logger.warning("Quiz desabilitado: defina QUIZ_GROUP_ID ou CHAT_ID_BF_ADM_QUIZ no .env")
        return

    _init_dbs(cfg)
    pokemon_list = _ensure_questions_list(cfg)

    state: Dict[str, object] = {
        "cfg": cfg,
        "client": client,
        "pokemon_list": pokemon_list,
        "active_polls": {},
        "answered_polls": set(),
    }

    async def generate_ai_question(pokemon: str):
        prompt = (
            f"Crie uma pergunta de múltipla escolha sobre o Pokémon '{pokemon}'. "
            "Retorne apenas um JSON com as chaves: question, options (lista de 4 strings), answer_index (índice da opção correta)."
        )
        resp = client.chat.completions.create(
            model=cfg.model,
            messages=[{"role": "system", "content": "Você gera quizzes de Pokémon."}, {"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = resp.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        _insert_question(cfg, pokemon, data["question"], data["options"], data["answer_index"])
        return data["question"], data["options"], data["answer_index"]

    async def send_quiz(ctx_bot, ctx_job=None):
        if state["active_polls"]:
            return
        pokemon = random.choice(state["pokemon_list"])
        question, options, answer_id = await generate_ai_question(pokemon)
        poll = await ctx_bot.send_poll(
            chat_id=cfg.quiz_group_id,
            message_thread_id=cfg.quiz_topic_id,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False,
            open_period=cfg.expire_minutes * 60,
        )
        state["active_polls"][poll.poll.id] = answer_id
        loop = asyncio.get_event_loop()
        loop.call_later(cfg.expire_minutes * 60 + cfg.expire_buffer_seconds, lambda pid=poll.poll.id: state["active_polls"].pop(pid, None))
        if ctx_job:
            app.job_queue.run_once(delete_quiz, when=cfg.expire_minutes * 60 + cfg.expire_buffer_seconds, data=poll, name=f"delete_quiz_{poll.message_id}")

    async def handle_poll_answer(update: Update, context):
        ans = update.poll_answer
        poll_id = ans.poll_id
        if poll_id in state["answered_polls"]:
            return
        state["answered_polls"].add(poll_id)
        correct = state["active_polls"].get(poll_id)
        if correct is None:
            return
        if ans.option_ids and ans.option_ids[0] == correct:
            _add_score(cfg, ans.user.id)
            await context.bot.send_message(
                chat_id=cfg.quiz_group_id,
                message_thread_id=cfg.quiz_topic_id,
                text=f"{ans.user.mention_html()} 🎉 Resposta correta! Pontuação atualizada.",
                parse_mode="HTML",
            )
        else:
            await context.bot.send_message(
                chat_id=cfg.quiz_group_id,
                message_thread_id=cfg.quiz_topic_id,
                text=f"{ans.user.mention_html()} ❌ Resposta incorreta. Tente novamente!",
                parse_mode="HTML",
            )

    async def quiz_test_command(update: Update, context):
        user_id = update.effective_user.id
        if user_id not in context.application.bot_data.get("ADMINS", set()):
            await update.message.reply_text("❌ Acesso negado. Apenas admins.")
            return
        if state["active_polls"]:
            await update.message.reply_text("❌ Já há uma pergunta ativa. Aguarde a expiração.")
            return
        await send_quiz(context.bot)

    def _clear_jobs(name: str):
        for job in app.job_queue.jobs():
            if job.name == name:
                job.schedule_removal()

    def schedule_daily_quizzes():
        now = datetime.now()
        start = datetime.combine(now.date(), time(hour=8))
        end = datetime.combine(now.date(), time(hour=22))
        if now > end:
            start += timedelta(days=1)
            end += timedelta(days=1)
        _clear_jobs("daily_quiz")
        for _ in range(cfg.questions_per_day):
            rand = random.randint(0, int((end - start).total_seconds()))
            run_time = start + timedelta(seconds=rand)
            app.job_queue.run_once(lambda ctx: asyncio.create_task(send_quiz(ctx.bot)), when=run_time, name="daily_quiz")
        next_mid = datetime.combine((now + timedelta(days=1)).date(), time.min)
        app.job_queue.run_once(lambda ctx: schedule_daily_quizzes(), when=next_mid, name="daily_quiz_reschedule")

    async def delete_quiz(context):
        msg = context.job.data
        await msg.delete()

    # Guarda admins para checagem rápida
    admins = set()
    from config import ADMINS as ADMINS_ENV
    admins = set(int(x) for x in ADMINS_ENV) if ADMINS_ENV else set()
    app.bot_data["ADMINS"] = admins

    # Handlers
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(CommandHandler("quiztest", quiz_test_command))

    # Agenda quizzes diários e um quiz inicial
    app.job_queue.run_once(lambda ctx: asyncio.create_task(send_quiz(ctx.bot)), when=0, name="startup_quiz")
    schedule_daily_quizzes()

    app.logger.info("Quiz habilitado e integrado (grupo=%s, tópico=%s)", cfg.quiz_group_id, cfg.quiz_topic_id)
