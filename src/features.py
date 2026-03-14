from src.collector import Collector
from statistics import pstdev
class features:
    def __init__(self,schema:Collector):
        self.schema = schema
        self.features = {}

    def _get_competition_feats(self) -> None:
        nCompetitions = len(self.schema.user_schema.get('competitions',[]))
        percentiles = [(1-c['rank']/c['teams']) for c in self.schema.user_schema.get('competitions',[])]
        bestPercentile = sorted(percentiles,reverse=True)[0]
        averagePercentile = sum(percentiles)/len(percentiles)
        stdPercentile = pstdev(percentiles)

        self.features['CompetitionFeatures'] = {
            "totalCompetitions":nCompetitions,
            "percentiles":percentiles,
            "bestPercentitle":bestPercentile,
            "averagePercentile":averagePercentile,
            "stdPercentile":stdPercentile
        }

    def _get_activity_feats(self) -> None:
        pass