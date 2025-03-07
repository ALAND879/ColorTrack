class ScoreTable:
    def __init__(self):
        self.scores = {}

    def add_score(self, name, score):
        self.scores[name] = score

    def get_scores(self):
        return self.scores

    def get_score(self, name):
        return self.scores.get(name)

    def remove_score(self, name):
        if name in self.scores:
            del self.scores[name]

    def clear_scores(self):
        self.scores.clear()

    def order_scores(self):
        return dict(sorted(self.scores.items(), key=lambda x: x[1], reverse=True))

    def get_top_scores(self, n=5):
        return dict(list(self.order_scores().items())[:n])