def classify_user(features:dict):
    medals = (
        features['gold']+
        features['silver']+
        features['bronze']
    )

    followers = features['totalFollowers']

    if medals > 50:
        return "Elite Competitor"

    if followers > 200:
        return "Community Influencer"

    if medals > 10:
        return "Active Competitor"

    return "Explorer"
