"""
BattleDex Arena - AI Service
Serviço compartilhado para assistente de IA
"""

import os
import random
from typing import Dict, List, Optional

class AIService:
    """Serviço para assistente de IA"""
    
    # Respostas pré-definidas para perguntas comuns
    PREDEFINED_RESPONSES = {
        "battledex": {
            "o que é battledex": "BattleDex é um jogo de batalha estratégica onde jogadores usam criaturas digitais com poderes elementares para competir em duelos emocionantes.",
            "como jogar": "Para jogar BattleDex, você precisa montar um time de criaturas, escolher suas habilidades estrategicamente e duelar contra outros jogadores em batalhas turn-based.",
            "melhores tipos": "Os melhores tipos dependem da estratégia, mas Fogo é forte contra Terra, Terra contra Água, Água contra Fogo, e Ar é balanceado contra todos.",
            "como ganhar": "Para ganhar em BattleDex, foque em: 1) Montar um time balanceado, 2) Conhecer as vantagens tipo vs tipo, 3) Gerenciar seu ELO estrategicamente, 4) Praticar regularmente."
        },
        "ranking": {
            "o que é elo": "ELO é um sistema de rating que mede sua habilidade no jogo. Quanto maior seu ELO, mais forte você é considerado na comunidade.",
            "como subir elo": "Para subir ELO: 1) Vença batalhas contra jogadores com ELO similar ou maior, 2) Mantenha uma taxa de vitória acima de 50%, 3) Evite perder para jogadores com ELO muito menor.",
            "elo máximo": "O ELO máximo em BattleDex é 3000, considerado o nível de Mestre. Jogadores com 2000+ são considerados Experts."
        },
        "estratégia": {
            "time inicial": "Para um time inicial, recomendo: 1 criatura Fogo, 1 Água, 1 Terra e 1 Ar. Isso te dá flexibilidade contra qualquer tipo de oponente.",
            "contra fogo": "Contra times Fogo, use criaturas Terra. Elas têm vantagem tipo e resistem bem aos ataques de fogo.",
            "melhor habilidade": "As melhores habilidades dependem da situação, mas habilidades que curam ou dão buff no time geralmente são mais valiosas em batalhas longas."
        }
    }
    
    @staticmethod
    def ask_question(question: str, user_id: str = None) -> Optional[str]:
        """Fazer pergunta para IA"""
        try:
            # Normalizar pergunta
            question_lower = question.lower().strip()
            
            # Buscar resposta pré-definida
            for category, responses in AIService.PREDEFINED_RESPONSES.items():
                for key, response in responses.items():
                    if key in question_lower:
                        return response
            
            # Respostas genéricas baseadas em palavras-chave
            if any(word in question_lower for word in ["oi", "olá", "hello"]):
                return f"Olá! Sou a assistente IA do BattleDex Arena. Como posso ajudar você hoje?"
            
            if any(word in question_lower for word in ["ajuda", "help", "como"]):
                return "Posso ajudar com informações sobre BattleDex, ranking, estratégias e dicas. Seja específico na sua pergunta!"
            
            if any(word in question_lower for word in ["tchau", "bye", "adeus"]):
                return "Até logo! Boa sorte nas suas batalhas de BattleDex!"
            
            # Resposta padrão se não encontrar nada específico
            default_responses = [
                "Essa é uma ótima pergunta! No momento, estou aprendendo mais sobre esse tópico. Recomendo verificar o guia oficial do BattleDex.",
                "Interessante! Como IA, estou sempre evoluindo. Para informações detalhadas, sugiro consultar a comunidade BattleDex ou o wiki oficial.",
                "Hmm, essa pergunta é complexa! Recomendo experimentar diferentes abordagens no jogo e observar o que funciona melhor para seu estilo.",
                "Ótima questão! A melhor maneira de aprender é praticando. Tente diferentes estratégias e veja o que funciona para você!"
            ]
            
            return random.choice(default_responses)
            
        except Exception as e:
            print(f"Erro ao processar pergunta: {e}")
            return "Desculpe, tive um problema ao processar sua pergunta. Tente novamente!"
    
    @staticmethod
    def analyze_player(player_name: str, stats: tuple = None) -> Optional[str]:
        """Analisar jogador com base nas estatísticas"""
        try:
            if not stats:
                return f"Não consegui encontrar estatísticas para {player_name}. Verifique se o nome está correto."
            
            elo, vitorias, derrotas = stats
            total_battles = vitorias + derrotas
            win_rate = (vitorias / total_battles * 100) if total_battles > 0 else 0
            
            # Análise baseada no ELO
            if elo >= 2500:
                level = "Mestre Lendário"
                strengths = "Elo excepcional, experiência avançada"
                improvements = "Manter consistência, ajudar novos jogadores"
            elif elo >= 2000:
                level = "Expert"
                strengths = "ELO muito alto, ótimo desempenho"
                improvements = "Refinar estratégias avançadas"
            elif elo >= 1500:
                level = "Avançado"
                strengths = "Bom ELO, sólido conhecimento"
                improvements = "Estudar matchups específicos"
            elif elo >= 1000:
                level = "Intermediário"
                strengths = "ELO decente, compreensão básica"
                improvements = "Praticar mais, estudar fundamentos"
            else:
                level = "Iniciante"
                strengths = "Potencial de crescimento"
                improvements = "Aprender basics, praticar consistentemente"
            
            # Análise baseada na taxa de vitória
            if win_rate >= 60:
                performance = "excelente"
            elif win_rate >= 50:
                performance = "boa"
            elif win_rate >= 40:
                performance = "regular"
            else:
                performance = "precisa melhorar"
            
            analysis = f"""
**Análise de {player_name}**

🎯 **Nível:** {level}
📊 **ELO Atual:** {elo}
⚔️ **Taxa de Vitória:** {win_rate:.1f}% ({vitorias}V/{derrotas}D)
📈 **Desempenho:** {performance}

**Pontos Fortes:**
{strengths}

**Áreas de Melhoria:**
{improvements}

**Dicas Personalizadas:**
"""
            
            if win_rate < 50:
                analysis += "\n• Foque em melhorar a taxa de vitória antes de buscar ELO mais alto"
                analysis += "\n• Estude os fundamentos e pratique contra jogadores de nível similar"
            elif elo < 1500:
                analysis += "\n• Continue praticando para subir para o nível Avançado"
                analysis += "\n• Participe de torneios para ganhar experiência"
            else:
                analysis += "\n• Você está no caminho certo! Continue assim"
                analysis += "\n• Considere ajudar jogadores mais novos a solidificar seu conhecimento"
            
            return analysis
            
        except Exception as e:
            print(f"Erro na análise do jogador: {e}")
            return "Desculpe, não consegui analisar este jogador no momento."
    
    @staticmethod
    def get_tip(topic: str = "geral") -> Optional[str]:
        """Obter dica sobre um tópico específico"""
        try:
            topic_lower = topic.lower()
            
            tips = {
                "ataque": [
                    "Sempre comece com sua criatura mais forte para pressão inicial.",
                    "Use habilidades de buff antes de ataques poderosos para maximizar dano.",
                    "Conserve habilidades especiais para momentos cruciais da batalha."
                ],
                "defesa": [
                    "Mantenha uma criatura tank na reserva para situações de emergência.",
                    "Use habilidades de cura no momento certo - não muito cedo, não muito tarde.",
                    "Preveja os movimentos do oponente baseado nas criaturas dele."
                ],
                "estratégia": [
                    "Conheça as vantagens tipo vs tipo: Fogo > Terra > Água > Fogo.",
                    "Mantenha um time balanceado com diferentes tipos e funções.",
                    "Adapte sua estratégia baseada no time do oponente."
                ],
                "geral": [
                    "Pratique regularmente para manter seus reflexos afiados.",
                    "Assista a batalhas de jogadores Experts para aprender novas estratégias.",
                    "Participe da comunidade para trocar dicas e experiências.",
                    "Não tenha medo de experimentar - a inovação leva a novas estratégias!"
                ]
            }
            
            # Buscar dicas específicas do tópico
            for key, tip_list in tips.items():
                if key in topic_lower:
                    return random.choice(tip_list)
            
            # Se não encontrar tópico específico, retornar dica geral
            return random.choice(tips["geral"])
            
        except Exception as e:
            print(f"Erro ao obter dica: {e}")
            return "Desculpe, não consegui gerar uma dica no momento. Tente novamente!"
