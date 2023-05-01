import tweepy
auth = tweepy.OAuthHandler("pIIOK0Q5ypGqKJtWOwtFWgYY4","2kvYCEAxXmc5l2FJwOxrlHwdF6uBKMZTB01V33JonveG2BAZBL")
auth.set_access_token("440809914-RN1RLIcMwKckpLJfinJah3hZReI5h852hK8SAEGs","19kAUyQ8ilOp37YXTk0MvjVbsSv3PohqpTpB8I0biMa1b")
api = tweepy.API(auth,wait_on_rate_limit=True)