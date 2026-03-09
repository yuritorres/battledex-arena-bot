"""
YouTube Notifier para Discord
Funciona igual ao Telegram notifier mas para Discord
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

FEED_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


class DiscordYouTubeNotifier:
    """Notificador YouTube para Discord"""
    
    def __init__(self, bot):
        self.bot = bot
        # Canal do Discord para notificações (via variável de ambiente)
        self.youtube_channel_id = os.getenv('DISCORD_YOUTUBE_CHANNEL_ID', '')
        self.storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
        self.state_file = os.path.join(self.storage_dir, "youtube_state.json")
    
    async def start_monitoring(self):
        """Iniciar monitoramento do YouTube"""
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        discord_channel = os.getenv('DISCORD_YOUTUBE_CHANNEL_ID')
        
        logger.info(f"YouTube notifier configurado:")
        logger.info(f"  - Canal YouTube: {channel_id}")
        logger.info(f"  - Canal Discord: {discord_channel}")
        
        if not channel_id:
            logger.warning("YouTube notifier desabilitado: YOUTUBE_CHANNEL_ID não configurado")
            return
        
        if not discord_channel:
            logger.warning("YouTube notifier desabilitado: DISCORD_YOUTUBE_CHANNEL_ID não configurado")
            return
        
        logger.info(f"YouTube notifier iniciado para Discord")
        
        # Iniciar tarefa de monitoramento
        asyncio.create_task(self._monitor_loop())
    
    async def _monitor_loop(self):
        """Loop de monitoramento do YouTube"""
        while True:
            try:
                await self._check_for_new_videos()
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
            except Exception as e:
                logger.error(f"Erro no monitoramento YouTube: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto em caso de erro
    
    async def _check_for_new_videos(self):
        """Verificar novos vídeos"""
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        if not channel_id:
            return
        
        feed_url = FEED_TEMPLATE.format(channel_id=channel_id)
        
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(feed_url) as response:
                    if response.status != 200:
                        logger.error(f"HTTP {response.status} ao buscar feed YouTube")
                        return
                    
                    body = await response.text()
                    await self._parse_and_notify(body)
                    
        except Exception as e:
            logger.error(f"Erro ao buscar feed YouTube: {e}")
    
    async def _parse_and_notify(self, xml_content: str):
        """Parsear XML e notificar sobre novos vídeos"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_content)
            
            # Namespace do YouTube
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015'}
            
            # Carregar estado anterior
            state = self._load_state()
            
            for entry in root.findall('entry'):
                video_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                video_id = video_id.split(':')[-1]  # Extrair ID do vídeo
                
                # Se já notificado, pular
                if video_id in state.get('notified_videos', []):
                    continue
                
                # Obter informações do vídeo
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                link = entry.find('{http://www.w3.org/2005/Atom}link').attrib.get('href', '')
                
                # Notificar no Discord
                await self._notify_discord(title, link, published, video_id)
                
                # Marcar como notificado
                if 'notified_videos' not in state:
                    state['notified_videos'] = []
                state['notified_videos'].append(video_id)
                
                # Manter apenas últimos 50 vídeos no estado
                if len(state['notified_videos']) > 50:
                    state['notified_videos'] = state['notified_videos'][-50:]
            
            # Salvar estado
            self._save_state(state)
            
        except Exception as e:
            logger.error(f"Erro ao parsear XML do YouTube: {e}")
    
    async def _notify_discord(self, title: str, link: str, published: str, video_id: str):
        """Notificar no Discord sobre novo vídeo"""
        try:
            # Obter canal do Discord
            channel = self.bot.get_channel(int(self.youtube_channel_id))
            if not channel:
                logger.error(f"Canal Discord não encontrado: {self.youtube_channel_id}")
                return
            
            # Criar embed
            embed = discord.Embed(
                title="🎬 NOVO VÍDEO NO YOUTUBE!",
                description=f"**{title}**",
                url=link,
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="📺 Canal",
                value="BattleDex Arena",
                inline=False
            )
            
            embed.add_field(
                name="📅 Publicado em",
                value=published[:10] if published else "Data não disponível",
                inline=False
            )
            
            embed.add_field(
                name="🔗 Assista Agora",
                value=f"[Clique aqui]({link})",
                inline=False
            )
            
            # Thumbnail do vídeo
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            embed.set_thumbnail(url=thumbnail_url)
            
            embed.set_footer(text="Notificação automática • YouTube Notifier")
            embed.timestamp = datetime.now()
            
            # Enviar mensagem
            await channel.send(content="@everyone Novo vídeo disponível!", embed=embed)
            
            logger.info(f"Notificação enviada para Discord: {title}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar Discord: {e}")
    
    def _load_state(self) -> dict:
        """Carregar estado anterior"""
        try:
            import json
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar estado YouTube: {e}")
        
        return {}
    
    def _save_state(self, state: dict):
        """Salvar estado atual"""
        try:
            import json
            os.makedirs(self.storage_dir, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estado YouTube: {e}")
    
    async def send_test_notification(self):
        """Enviar notificação de teste"""
        try:
            channel = self.bot.get_channel(int(self.youtube_channel_id))
            if not channel:
                return False, "Canal não encontrado"
            
            embed = discord.Embed(
                title="🧪 TESTE - YouTube Notifier",
                description="Sistema de notificação YouTube funcionando!",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="📺 Status",
                value="🟢 Ativo e monitorando",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Canal",
                value=f"<#{self.youtube_channel_id}>",
                inline=False
            )
            
            embed.set_footer(text="Teste do YouTube Notifier para Discord")
            
            await channel.send(embed=embed)
            return True, "Teste enviado com sucesso"
            
        except Exception as e:
            return False, f"Erro: {str(e)}"


# Importar discord para o embed
import discord
