"""
BattleDex Arena - Quiz Service
Serviço compartilhado para gerenciamento de quiz
"""

import os
import sqlite3
import random
from typing import List, Dict, Optional

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
QUIZ_DB_PATH = os.path.join(STORAGE_DIR, "quiz.db")

class QuizService:
    """Serviço para gerenciamento de quiz"""
    
    @staticmethod
    def create_connection():
        """Criar conexão com banco de dados"""
        os.makedirs(os.path.dirname(QUIZ_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(QUIZ_DB_PATH)
        return conn
    
    @staticmethod
    def create_tables():
        """Criar tabelas do quiz"""
        conn = QuizService.create_connection()
        cursor = conn.cursor()
        
        # Tabela de perguntas
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT DEFAULT 'geral',
            difficulty INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Tabela de estatísticas
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            last_play TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def add_question(question: str, options: List[str], correct_answer: str, category: str = "geral", difficulty: int = 1) -> bool:
        """Adicionar pergunta ao quiz"""
        try:
            if len(options) != 4:
                return False
            
            conn = QuizService.create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz_questions (question, option_a, option_b, option_c, option_d, correct_answer, category, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (question, options[0], options[1], options[2], options[3], correct_answer, category, difficulty))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar pergunta: {e}")
            return False
    
    @staticmethod
    def get_random_question() -> Optional[Dict]:
        """Obter pergunta aleatória"""
        try:
            conn = QuizService.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT question, option_a, option_b, option_c, option_d, correct_answer FROM quiz_questions ORDER BY RANDOM() LIMIT 1')
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'question': row[0],
                    'options': [row[1], row[2], row[3], row[4]],
                    'correct_answer': row[5]
                }
            return None
        except Exception as e:
            print(f"Erro ao obter pergunta aleatória: {e}")
            return None
    
    @staticmethod
    def get_questions_by_category(category: str, limit: int = 10) -> List[Dict]:
        """Obter perguntas por categoria"""
        try:
            conn = QuizService.create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT question, option_a, option_b, option_c, option_d, correct_answer 
                FROM quiz_questions 
                WHERE category = ? 
                ORDER BY RANDOM() 
                LIMIT ?
            ''', (category, limit))
            rows = cursor.fetchall()
            conn.close()
            
            questions = []
            for row in rows:
                questions.append({
                    'question': row[0],
                    'options': [row[1], row[2], row[3], row[4]],
                    'correct_answer': row[5]
                })
            return questions
        except Exception as e:
            print(f"Erro ao obter perguntas da categoria {category}: {e}")
            return []
    
    @staticmethod
    def update_user_stats(user_id: str, correct: bool) -> bool:
        """Atualizar estatísticas do usuário"""
        try:
            conn = QuizService.create_connection()
            cursor = conn.cursor()
            
            # Inserir ou atualizar estatísticas
            cursor.execute('''
                INSERT OR REPLACE INTO quiz_stats (user_id, total_questions, correct_answers, last_play)
                VALUES (?, COALESCE((SELECT total_questions FROM quiz_stats WHERE user_id = ?), 0) + 1,
                        COALESCE((SELECT correct_answers FROM quiz_stats WHERE user_id = ?), 0) + ?, CURRENT_TIMESTAMP)
            ''', (user_id, user_id, user_id, 1 if correct else 0))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar estatísticas de {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_stats(user_id: str) -> Optional[Dict]:
        """Obter estatísticas do usuário"""
        try:
            conn = QuizService.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT total_questions, correct_answers FROM quiz_stats WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                total, correct = row
                accuracy = (correct / total * 100) if total > 0 else 0
                return {
                    'total_questions': total,
                    'correct_answers': correct,
                    'accuracy': accuracy
                }
            return None
        except Exception as e:
            print(f"Erro ao obter estatísticas de {user_id}: {e}")
            return None
    
    @staticmethod
    def get_top_players(limit: int = 10) -> List[Dict]:
        """Obter top jogadores do quiz"""
        try:
            conn = QuizService.create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, total_questions, correct_answers,
                       (CAST(correct_answers AS FLOAT) / total_questions * 100) as accuracy
                FROM quiz_stats 
                WHERE total_questions >= 5
                ORDER BY accuracy DESC, correct_answers DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            players = []
            for row in rows:
                players.append({
                    'user_id': row[0],
                    'total_questions': row[1],
                    'correct_answers': row[2],
                    'accuracy': row[3]
                })
            return players
        except Exception as e:
            print(f"Erro ao obter top jogadores: {e}")
            return []
    
    @staticmethod
    def initialize_default_questions():
        """Inicializar perguntas padrão do quiz"""
        default_questions = [
            ("Qual é o tipo mais forte de BattleDex?", ["Fogo", "Água", "Terra", "Ar"], "Fogo", "elementos", 1),
            ("Quantos jogadores podem participar de uma batalha?", ["2", "4", "6", "8"], "2", "batalha", 1),
            ("Qual é o nível máximo de ELO?", ["1000", "1500", "2000", "3000"], "3000", "ranking", 2),
            ("Como se ganha moedas no jogo?", ["Vencendo batalhas", "Comprando", "Doando", "Hackeando"], "Vencendo batalhas", "economia", 1),
            ("O que significa 'ELO'?", ["Elo Rating System", "Exército Lendário", "Estrela do Ouro", "Elemento Luminoso"], "Elo Rating System", "geral", 3),
        ]
        
        for question, options, correct, category, difficulty in default_questions:
            QuizService.add_question(question, options, correct, category, difficulty)

# Inicializar tabelas ao importar
QuizService.create_tables()
QuizService.initialize_default_questions()
