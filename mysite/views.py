#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from models import User
import urllib
import urllib2
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

CLIENT_ID = '1076529568'
CLIENT_SECRET = '094e967845f519e83d2c40932246fa53'
REDIRECT_URI = 'hbs12.pythonanywhere.com/weibo_login'
HTTP_TIMEOUT = 10


def text_filter(text):
    t = text.replace('/','')
    t = t.replace('%','')
    t = t.replace('#','')
    return t

def oauth2(request):
    post_data = {}
    post_data['client_id'] = '1076529568'
    post_data['redirect_uri'] = 'hbs12.pythonanywhere.com/weibo_login'
    post_data['scope'] = 'all'
    post_data_encode = urllib.urlencode(post_data)
    auth_url = "https://api.weibo.com/oauth2/authorize?" + post_data_encode
    return HttpResponseRedirect(auth_url)

def weibo_login(request):
    #Use Code to Get Access Token
    if request.method == "GET":
        code = request.GET.get('code','')
        token_url = 'https://api.weibo.com/oauth2/access_token'
        post_data = {}
        post_data['client_id'] = CLIENT_ID
        post_data['client_secret'] = CLIENT_SECRET
        post_data['grant_type'] = 'authorization_code'
        post_data['code'] = code
        post_data['redirect_uri'] = REDIRECT_URI
        post_data_encode = urllib.urlencode(post_data)

        req = urllib2.Request(token_url, post_data_encode)
        res = urllib2.urlopen(req, timeout = HTTP_TIMEOUT).read()
        res = json.loads(res)

        _uid = res['uid']
        expires_in = res['expires_in']
        u = User.objects.filter(uid=_uid)
        if not u:
            user_new = User(uid = _uid, access_token = res['access_token'])
            user_new.save()
            print 'New user'
        else:
            u = u[0]
            u.access_token = res['access_token']
            u.save()
            print 'Old User'
        return render_to_response('mid.html',{'uid': _uid})


def home(request):
    return render_to_response('home.html')

def users(request):
    u = User.objects.all()
    return render_to_response('users.html', {'users':u })

def posts(request, uid):
    u = User.objects.filter(uid = uid)
    if not u:
        return HttpResponse('User ID not valid')
    u = u[0]
    valid_token = 'https://api.weibo.com/oauth2/get_token_info'
    data_token = {}
    data_token['access_token'] = u.access_token
    try:
        valid_req = urllib2.Request(valid_token, urllib.urlencode(data_token))
        valid_res = urllib2.urlopen(valid_req, timeout = HTTP_TIMEOUT).read()
        valid_res = json.loads(valid_res)
        if int(valid_res['expire_in']) < 100:
            return HttpResponse("Access Token Expired!!")
    except:
        return HttpResponse("There are some problems with this user's access token")

    weibo_url = 'https://api.weibo.com/2/statuses/user_timeline.json'
    weibo_post = {}
    weibo_post['access_token'] = u.access_token # request.session['access_token']
    weibo_post['count'] = 100

    req = urllib2.Request('%s?%s' % (weibo_url, urllib.urlencode(weibo_post)))
    res = urllib2.urlopen(req, timeout = HTTP_TIMEOUT).read()
    res = json.loads(res)

    user = res['statuses'][0]['user']
    statuses = res['statuses']

    # Analysis Keywords in it
    key_url = 'http://api.yutao.us/api/keyword/'
    keywords = []
    all_t = ""
    for status in statuses:
        all_t += status['text']
    all_t = all_t.replace('/','')
    all_t = all_t.replace('%','')
    req = urllib2.Request(key_url+all_t)
    res = urllib2.urlopen(req, timeout = HTTP_TIMEOUT).read().split(',')
    print 'KEYS:',res
    for r in res:
        if r:
            keywords.append(r)

    filtered_statuses = statuses
    k = []
    if request.method == 'GET':
        k = request.GET.get('keywords','')
        if k:
            filtered_statuses = []
            for status in statuses:
                """
                req = urllib2.Request(key_url+text_filter(status['text']))
                res = urllib2.urlopen(req, timeout = HTTP_TIMEOUT).read().split(',')
                print status['text'], '##############', res
                if k in res:
                    filtered_statuses.append(status)
                """
                if k in status['text']:
                    filtered_statuses.append(status)
    return render_to_response('posts.html',{'user': user, 'statuses':filtered_statuses, 'keywords': keywords, 'cur_key':k})
