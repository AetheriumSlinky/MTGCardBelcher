"""Contains login info and reply target subreddits."""

# Create a text file (here oauth.txt) with five rows
# or any other preferred method of delivering login info.

# 1. User Agent information
# 2. Account Username
# 3. Account Password
# 4. Client ID
# 5. Secret

oauth = "oauth.txt"

# Which subs is this bot pointed at?
target_subreddits = ["magicthecirclejerking", "MTGCardBelcher_dev"]

# Which subs is this bot fetching from?
submissions_subreddits = ["MTGCardBelcher"]

# Scryfall headers, required for Scryfall API usage
sf_headers = {'user-agent': 'MTGCardBelcher/1.2.0', "accept": "*/*"}
