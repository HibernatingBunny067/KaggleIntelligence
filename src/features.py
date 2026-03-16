from src.collector import Collector
from statistics import pstdev
class FeatureExtractor:
    def __init__(this,schema:Collector):
        this.schema = schema
        this.features = {}

    def build(this):
        this._get_competition_feats()
        this._get_activity_feats()
        this._get_publication_feats()
        this._get_intersection_feats()
        this._get_temporal_feats()
        return this.features


    def _get_competition_feats(this) -> None:
        nCompetitions = len(this.schema.user_schema.get('competitions',[]))
        percentiles = [(1-c['rank']/c['teams']) for c in this.schema.user_schema.get('competitions',[])]
        percentiles = percentiles or [0]
        bestPercentile = max(percentiles)
        averagePercentile = sum(percentiles)/len(percentiles)
        stdPercentile = pstdev(percentiles)

        ##TODO
        #top10PercentFinishes
        #top5PercentFinishes
        #top1PercentFinishes
        #consistencyScore
        #performanceTrend = slope(percentiles/competition_index)
        
        this.features['CompetitionFeatures'] = {
            "totalCompetitions":nCompetitions,
            "percentiles":percentiles,
            "bestPercentitle":bestPercentile,
            "averagePercentile":averagePercentile,
            "stdPercentile":stdPercentile
        }

    def _get_activity_feats(this) -> None:
        activity = this.schema.user_schema['activity']
        totalSubmissions = sum(a['submissions'] for a in activity)
        active_days = len(activity)
        totalActions = sum(
            a['scripts'] + a['submissions'] + a['datasets'] + a['discussions']
            for a in activity
        )
        actions_per_day = totalActions / active_days

        ## TODO: advanced activity metrics

        # longestStreak
        # -> longest consecutive active day streak

        # maxDailyActivity
        # -> max(actions per day)

        # activityVariance
        # -> pstdev of daily action counts

        # experimentDays
        # -> days where scripts >= 5




        this.features['ActivityFeatures'] = {
            # "totalScriptsWritten":nScripts,
            "totalSubmissions":totalSubmissions,
            "totalActiveDays":active_days,
            "ActionsPerDay":actions_per_day
        }
    
    def _get_publication_feats(this) -> None:
        scripts = len(this.schema.user_schema.get('scripts',[]))
        datasets = len(this.schema.user_schema.get('datasets',[]))
        discussions = len(this.schema.user_schema.get('discussions',[]))
        knowledge_score = scripts + datasets + discussions

        this.features['PublicationFeatures'] = {
            "publishedScripts":scripts,
            "publishedDatasets":datasets,
            "publishedDiscussions":discussions
        }
    
    def _get_intersection_feats(this):

        activity = this.schema.user_schema['activity']

        total_script_actions = sum(a['scripts'] for a in activity)
        total_submissions = this.features['ActivityFeatures']['totalSubmissions']
        total_competitions = this.features['CompetitionFeatures']['totalCompetitions']

        published_scripts = this.features['PublicationFeatures']['publishedScripts']

        experimentation_ratio = total_script_actions / max(total_submissions,1)

        submissions_per_comp = total_submissions / max(total_competitions,1)

        notebook_efficiency = published_scripts / max(total_script_actions,1)
        
        ## TODO: publication behavior metrics

        # knowledgeScore
        # -> scripts + datasets + discussions

        # contributionEntropy
        # -> entropy of (scripts, datasets, discussions)
        # measures diversity of contributions



        breakthrough_days = sum(
            1 for a in activity if a['submissions'] >=5
        )
        this.features['BehaviourFeatures'] = {
            "experimentationRatio": experimentation_ratio,
            "submissionsPerCompetition": submissions_per_comp,
            "notebookEfficiency": notebook_efficiency,
            "breakthroughDays":breakthrough_days
        }

    def _get_temporal_feats(this):
        pass

