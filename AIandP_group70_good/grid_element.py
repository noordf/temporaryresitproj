
class Gridelement:
    def __init__(self, pos, greedy):
        self.grid_pos = pos
        self.gscore = greedy

    def update_gscore(self, greedy):
        self.gscore = greedy

    def __eq__ (self, other):
        return self.grid_pos[0] == other.grid_pos[0] and self.grid_pos[1] == other.grid_pos[1]

    def __lt__(self, other):
        return (self.gscore is not None) and (other.gscore is None or self.gscore < other.gscore)
