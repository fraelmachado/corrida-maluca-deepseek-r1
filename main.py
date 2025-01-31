import streamlit as st
import random
import time

# Configurações do jogo
st.set_page_config(page_title="PyRace Pro", layout="wide")


class GameEngine:
    def __init__(self):
        self.track_length = 40
        self.finish_line = 35
        self.max_speed = 8
        self.players = {
            'player': {'pos': 0, 'speed': 0, 'color': '🟦', 'icon': '🚗'},
            'cpu': {'pos': 0, 'speed': 0, 'color': '🟥', 'icon': '🤖'}
        }
        self.obstacles = []
        self.game_over = False
        self.lap_time = 0

    def reset(self):
        for p in self.players.values():
            p.update({'pos': 0, 'speed': 0})
        self.obstacles = []
        self.game_over = False
        self.lap_time = time.time()

    def generate_obstacles(self):
        if len(self.obstacles) < 3:
            new_obstacle = random.randint(10, self.track_length-5)
            if all(abs(new_obstacle - o) > 5 for o in self.obstacles):
                self.obstacles.append(new_obstacle)

    def calculate_cpu_move(self):
        player = self.players['cpu']
        distance = self.players['player']['pos'] - player['pos']

        if player['speed'] == 0:
            return random.randint(2, 3)
        elif distance > 5:
            return min(player['speed'] + 2, self.max_speed)
        elif distance < -3:
            return max(player['speed'] - 1, 1)
        else:
            return player['speed'] + (-1 if random.random() < 0.3 else 1)

    def update_player(self, player_key, acceleration):
        player = self.players[player_key]
        new_speed = player['speed'] + acceleration
        player['speed'] = max(0, min(self.max_speed, new_speed))
        player['pos'] += player['speed']

        if player['pos'] in self.obstacles:
            player['speed'] = max(0, player['speed'] - 3)
            self.obstacles.remove(player['pos'])

    def check_collisions(self):
        if abs(self.players['player']['pos'] - self.players['cpu']['pos']) < 2:
            self.players['player']['speed'] = max(
                0, self.players['player']['speed'] - 2)
            self.players['cpu']['speed'] = max(
                0, self.players['cpu']['speed'] - 2)

    def draw_track(self):
        track = []
        for pos in range(self.track_length):
            cell = '⬜'
            if pos == self.finish_line:
                cell = '🏁'
            elif pos in self.obstacles:
                cell = '💥'
            for p in self.players.values():
                if pos == p['pos']:
                    cell = p['icon']
                elif pos == p['pos'] - 1:
                    cell = p['color']
            track.append(cell)
        return ''.join(track)


# Inicialização do jogo
if 'engine' not in st.session_state:
    st.session_state.engine = GameEngine()
    st.session_state.engine.reset()

engine = st.session_state.engine

# Interface do usuário
st.title("🏎️ PyRace Pro Championship")
st.markdown("---")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Controles de Piloto 🕹️")

    if not engine.game_over:
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            if st.button("Acelerar 🚀", help="Aumenta velocidade gradualmente"):
                engine.update_player('player', 1)
        with col1b:
            if st.button("Manter ⏩", help="Mantém velocidade atual"):
                engine.update_player('player', 0)
        with col1c:
            if st.button("Frear 🛑", help="Reduz velocidade rapidamente"):
                engine.update_player('player', -2)

        engine.update_player('cpu', random.choice([-1, 0, 1]))
        engine.generate_obstacles()
        engine.check_collisions()

    # Sistema de telemetria
    st.subheader("Telemetria 📊")
    st.metric("Sua Velocidade", f"{engine.players['player']['speed']} km/h")
    st.metric("Velocidade CPU", f"{engine.players['cpu']['speed']} km/h")
    st.metric("Tempo de Volta", f"{time.time() - engine.lap_time:.1f}s")

    if engine.players['player']['pos'] >= engine.finish_line:
        engine.game_over = True
        st.success("🏆 Vitória! Novo recorde!")
    elif engine.players['cpu']['pos'] >= engine.finish_line:
        engine.game_over = True
        st.error("💥 Derrota! Tente novamente!")

    if engine.game_over:
        if st.button("Reiniciar Corrida 🔄"):
            engine.reset()

with col2:
    st.subheader("Circuito de Corrida 🏁")

    # Desenhar pista dinâmica
    track_display = engine.draw_track()
    st.markdown(f"```\n{track_display}\n```")

    # Legenda da pista
    st.caption(
        "Legenda: 🚗 Seu carro | 🤖 Oponente | 💥 Obstáculo | 🏁 Linha de Chegada")

    # Mapa estratégico
    with st.expander("Mapa Tático 🗺️"):
        progress = min(engine.players['player']['pos']/engine.finish_line, 1.0)
        st.progress(progress)
        st.write(f"Distância até a chegada: {
                 max(engine.finish_line - engine.players['player']['pos'], 0)}m")

        col2a, col2b = st.columns(2)
        with col2a:
            st.write("**Seu Carro**")
            st.write(f"Posição: {engine.players['player']['pos']}m")
            st.write(f"Velocidade: {engine.players['player']['speed']} km/h")

        with col2b:
            st.write("**Oponente**")
            st.write(f"Posição: {engine.players['cpu']['pos']}m")
            st.write(f"Velocidade: {engine.players['cpu']['speed']} km/h")

# Manual do jogador
with st.expander("📘 Manual do Piloto"):
    st.markdown("""
    ## Como Jogar:
    1. **Acelerar**: Aumenta gradualmente sua velocidade
    2. **Manter**: Mantém a velocidade atual para curvas
    3. **Frear**: Reduz velocidade rapidamente para evitar colisões
    
    ## Elementos da Pista:
    - 💥 **Obstáculos**: Reduzem velocidade ao passar por cima
    - 🏁 **Linha de Chegada**: Objetivo final (35m)
    - 🤖 **Oponente**: IA adaptativa com estratégia dinâmica
    
    ## Estratégias Avançadas:
    - Gerencie desgaste dos pneus (velocidade constante)
    - Antecipe os movimentos do oponente
    - Use obstáculos para bloquear o adversário
    """)

st.markdown("---")
st.caption("Desenvolvido com padrões profissionais - PyRace Pro v2.0")
