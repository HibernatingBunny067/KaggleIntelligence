
def extract(data:dict):
    profile = data['profile']
    medals = None

    for dicts in data['medals']:
        medals += dicts.get('totalBronzerMedals',0) + dicts.get('totalSilverMedals',0) + dicts.get('totalGoldMedals',0)

    features = {}

    features['followers'] = profile.get('followerCount',0)
    medal_counts = medal_counts
    features["gold"] = medal_counts.get("gold", 0)
    features["silver"] = medal_counts.get("silver", 0)
    features["bronze"] = medal_counts.get("bronze", 0)

    return features