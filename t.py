import requests, json, re, time
req = requests.Session()

with open("config.json", "r") as config:
    config = json.load(config)

cookie = config['cookie']
webhook = config['webhook']
discordid = config['discord_id']
req.cookies['.ROBLOSECURITY'] = cookie
already = []

def rolimons():
    ids = []
    information = []
    r = requests.get('https://www.rolimons.com/deals').text
    items = re.findall('item_details = (.*?);', r)[0]
    total = json.loads(items)
    for x in total:
        info = total[x]
        if info[5] == None:
            name, use, projected, itemid = info[0], info[2], info[4], x
            ids.append(itemid)
            information.append(f'{use}/{name}/{projected}')
        elif info[5] != None:
            name, use, projected, itemid = info[0], info[5], info[4], x
            ids.append(itemid)
            information.append(f'{use}/{name}/{projected}')
    c = zip(ids, information)
    values = dict(c)
    return values

def overall():
    global already
    r = req.get('https://trades.roblox.com/v1/trades/completed?cursor=&limit=25&sortOrder=Desc').json()
    for x in r['data']:
        already.append(x['id'])

def trades():
    all = []
    r = req.get('https://trades.roblox.com/v1/trades/completed?cursor=&limit=25&sortOrder=Desc').json()
    for x in r['data']:
        if not x['id'] in already:
            all.append(x['id'])
    check(all)

def check(all):
    global already
    for tid in all:
        me, them = 0, 0
        me_hook, them_hook, themvalues_hook, mevalues_hook = [], [], [], []
        r = req.get(f'https://trades.roblox.com/v1/trades/{tid}').json()

        myrobux, theirrobux = r['offers'][0]['robux'], r['offers'][1]['robux']
        me_hook.append(f'\u200b\n**Robux**: {myrobux}\n')
        them_hook.append(f'\u200b\n**Robux**: {theirrobux}\n')

        for i in range(len(r['offers'][0]['userAssets'])):
            id = str(r['offers'][0]['userAssets'][i]['assetId'])
            current, name, proj = values[id].split('/',3)
            me_hook.append(f'**Item**: {name}\n**Value**: {"{:,}".format(int(current))}\n')
            me += int(current)

        for i in range(len(r['offers'][1]['userAssets'])):
            id = str(r['offers'][1]['userAssets'][i]['assetId'])
            current, name, proj = values[id].split('/',3)
            them_hook.append(f'**Item**: {name}\n**Value**: {"{:,}".format(int(current))}\n')
            them += int(current)

        me_hook, them_hook = '\n'.join(me_hook), '\n'.join(them_hook)
        profit, percentage = int(them) - int(me), (1 - int(me) / int(them)) * 100

        if '.' in str(percentage):
            if len(str(percentage).split('.')[1]) >= 3:
                percentage = round(percentage, 2)

        data = {
            'content': f'<@{discordid}>',
            'embeds':[{
                'color': int('00FF00',16),
                'fields': [
                    {'name': f'📤 Gave [{me}]','value': f'{me_hook}','inline':True},
                    {'name': f'\u200b','value': f'\u200b','inline':True},
                    {'name': f'📥 Received Items: [{them}]','value': f'{them_hook}','inline':True},
                    {'name': '💸 Profit','value': f'{profit} ({percentage}%)','inline':False},
                    ]
                }]
            }
        requests.post(webhook, json=data)
        already.append(tid)


values = rolimons()
overall()
while True:
    trades()
    time.sleep(300)
