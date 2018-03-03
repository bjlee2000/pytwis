from flask import Flask
from flask import request
import pytwis_clt
import pytwis

# Return value is just string. we can change this to Json format.

# Init
# http://127.0.0.1:5000/init?server=<ip_address>&port=<port>&password=<password>

# Register/Login/Login/Post works.

# http://127.0.0.1:5000/pytwis?cmd=register&username=bjlee3&password=test3
# http://127.0.0.1:5000/pytwis?cmd=login&username=bjlee3&password=test3
# http://127.0.0.1:5000/pytwis?cmd=post&tweet=test12345

# Somehow timeline/followers don't work yet.

app = Flask(__name__)
auth_secret = ['']
twis = None

@app.route('/')
def homepage():
    return "Hello Sammamish Study Group"

@app.route('/test', methods=['GET','POST'])
def test_request():
    try:
        if(request.method == 'GET'):
            name = request.args['name']
            return 'GET' + name
    except ValueError as e:
        return "error"

@app.route('/init', methods=['GET'])
def init():
    try:
        global twis

        if(request.method == 'GET'):
            server = request.args['server']
            port = request.args['port']
            password = request.args['password']
            twis =  pytwis.Pytwis(server, port, password)
            if twis is None:
                return "Error"
            else:
                return "Success"
    except ValueError as e:
        return "error"

@app.route('/pytwis', methods=['GET'])
def pytwis_get_request():
    global auth_secret
    command = request.args['cmd']
    print(command)
    command_with_args = [request.args['cmd'], request.args]
    response = pytwis_get_request_processor(twis, auth_secret, command_with_args)
    print(response)
    return response

def pytwis_get_request_processor(twis, auth_secret, command_with_args):
    command = command_with_args[0]
    args = command_with_args[1]
    results = []

    if command == 'register':
        succeeded, result = twis.register(args['username'], args['password'])
        if succeeded:
            results.append('Succeeded in registering {}'.format(args['username']))
        else:
            results.append('Failed to register {} with error = {}'.format(args['username'], result['error']))
    elif command == 'login':
        succeeded, result = twis.login(args['username'], args['password'])
        if succeeded:
            auth_secret[0] = result['auth']
            results.append('Succeeded in logging into username {}'.format(args['username']))
        else:
            results.append("Couldn't log into username {} with error = {}".format(args['username'], result['error']))
    elif command == 'logout':
        succeeded, result = twis.logout(auth_secret[0])
        if succeeded:
            auth_secret[0] = ''
            results.append('Logged out of username {}'.format(result['username']))
        else:
            results.append("Couldn't log out with error = {}".format(result['error']))
    elif command == 'changepassword':
        succeeded, result = twis.change_password(auth_secret[0], args['old_password'], args['new_password'])
        if succeeded:
            auth_secret[0] = result['auth']
            results.append('Succeeded in changing the password')
        else:
            results.append("Couldn't change the password with error = {}".format(result['error']))
    elif command == 'post':
        succeeded, result = twis.post_tweet(auth_secret[0], args['tweet'])
        if succeeded:
            results.append('Succeeded in posting the tweet')
        else:
            results.append("Couldn't post the tweet with error = {}".format(result['error']))
    elif command == 'follow':
        succeeded, result = twis.follow(auth_secret[0], args['followee'])
        if succeeded:
            results.append('Succeeded in following username {}'.format(args['followee']))
        else:
            results.append("Couldn't follow the username {} with error = {}".format(args['followee'], result['error']))
    elif command == 'unfollow':
        succeeded, result = twis.unfollow(auth_secret[0], args['followee'])
        if succeeded:
            results.append('Succeeded in unfollowing username {}'.format(args['followee']))
        else:
            results.append("Couldn't unfollow the username {} with error = {}".format(args['followee'], result['error']))
    elif command == 'followers':
        succeeded, result = twis.get_followers(auth_secret[0])
        if succeeded:
            results.append('Succeeded in get the list of {} followers'.format(len(result['follower_list'])))
            results.append('=' * 20)
            for follower in result['follower_list']:
                results.append('\t' + follower)
            results.append('=' * 20)
        else:
            results.append("Couldn't get the follower list with error = {}".format(result['error']))
    elif command == 'followings':
        succeeded, result = twis.get_following(auth_secret[0])
        if succeeded:
            results.append('Succeeded in get the list of {} followings'.format(len(result['following_list'])))
            results.append('=' * 60)
            for following in result['following_list']:
                results.append('\t' + following)
            results.append('=' * 60)
        else:
            results.append("Couldn't get the following list with error = {}".format(result['error']))
    elif command == 'timeline':
        succeeded, result = twis.get_timeline(auth_secret[0], args['max_cnt_tweets'])
        if succeeded:
            if auth_secret[0] != '':
                results.append('Succeeded in get {} tweets in the user timeline'.format(len(result['tweets'])))
            else:
                results.append('Succeeded in get {} tweets in the general timeline'.format(len(result['tweets'])))
            # print_tweets(result['tweets'])
        else:
            if auth_secret[0] != '':
                results.append("Couldn't get the user timeline with error = {}".format(result['error']))
            else:
                results.append("Couldn't get the general timeline with error = {}".format(result['error']))
    else:
        pass

    return "\n".join(results)
    
if __name__ ==  "__main__":
    app.run()
