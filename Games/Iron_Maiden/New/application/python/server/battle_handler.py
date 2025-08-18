# import modules
import pickle

class BattleHandler:
    def __init__(self):
        pass

    def handle_battle_command(self, command, player, players, player_connections):
        if command['action'] == 'attack':
            # Find opponent
            opponent = next((p for p in players if p != player), None)
            if opponent:
                # Apply damage
                opponent.health -= player.attack
                
                # Broadcast battle update to all players
                battle_state = {
                    'type': 'battle_update',
                    'attacker': player.name,
                    'defender': opponent.name,
                    'damage': player.attack,
                    'defender_health': opponent.health
                }
                self.broadcast(battle_state, player_connections)
                
                # Check for game over
                if opponent.health <= 0:
                    game_over = {
                        'type': 'game_over',
                        'winner': player.name,
                        'loser': opponent.name
                    }
                    self.broadcast(game_over, player_connections)

    def start_battle(self, players, player_connections):
        # Send battle start message to all players
        battle_start = {
            'type': 'battle_start',
            'players': [{'name': p.name, 'health': p.health, 'attack': p.attack} for p in players]
        }
        self.broadcast(battle_start, player_connections)

    def broadcast(self, message, player_connections):
        data = pickle.dumps(message)
        for conn in player_connections:
            try:
                conn.send(data)
            except:
                continue