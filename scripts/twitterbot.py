import tweepy

class TwitterBot:
    """ Class for interacting with the Twitter API."""

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.client = tweepy.Client(
            consumer_key=consumer_key, 
            consumer_secret=consumer_secret,
            access_token=access_token, 
            access_token_secret=access_token_secret)

    def tweet(self, message):
        """ Send a tweet to the Twitter API. """
        return self.client.create_tweet(text=message)

    def add_comment(self, tweet_id, message):
        """ Add a comment to a tweet. """
        return self.client.create_tweet(text=message, in_reply_to_tweet_id=tweet_id)