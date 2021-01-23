import folium
import pandas
import os
import requests
import json

# 震度のデータを処理する：
def scale_convert(num):
    if(num == 0 or num == None):
        return "なし"
    elif(num == 45):
        return "4"
    elif(num == 55):
        return "6弱"
    elif (num == 60):
        return "6強"
    else:
        number = int(num / 10)
        return str(number)

# 日本の緯度経度で日本のマップを表示する：
japan = folium.Map([36,138],zoom_start=6,tiles='Stamen Terrain')

# ①火山データの読み込み：
volcano = requests.get("https://gbank.gsj.jp/quatigneous/api/volcano")
volcano_data = json.loads(volcano.content.decode('utf-8'))

print(volcano_data["features"][0])

# vlist = [i for i in volcano_data.features]
vlist = [i for i in volcano_data["features"]]
coodinates = []
place_name = []

# ②地震データの読み込み：
earthquake = requests.get("https://api.p2pquake.net/v1/human-readable?limit=100")
# print(earthquake.content.decode('utf-8'))
# str式のjsonデータを取得した：
earthquake_data = earthquake.content.decode('utf-8')
earthquake_publish_time = []
earthquake_time = []
earthquake_coodinates = []  #震源地の緯度経度
earthquake_scale = []   #最大震度の値
earthquake_hypocenter = []  #震源地

# str式のjsonデータをdict式のデータへ変換：
dict_earthquake_data = json.loads(earthquake_data)

for data in dict_earthquake_data:
    if(data["code"] == 551):
        if(data['earthquake']['hypocenter']['latitude'][1:] == '' or data['earthquake']['hypocenter']['longitude'][1:] == ''):
            print("下記のデータには不備がありました：")
            print(dict_earthquake_data.index(data)) 
            print( dict_earthquake_data[dict_earthquake_data.index(data)])
        else:
            # print([data['earthquake']['hypocenter']['latitude'][1:],data['earthquake']['hypocenter']['longitude'][1:]])
            index = dict_earthquake_data.index(data)
            earthquake_publish_time.append(data['time'][:10])
            earthquake_time.append(data['earthquake']['time'])
            earthquake_hypocenter.append(data['earthquake']['hypocenter']['name'])  #震源地
            earthquake_scale.append(scale_convert(data['earthquake']['maxScale']))  #最大震度の値
            earthquake_coodinates.append([float(data['earthquake']['hypocenter']['latitude'][1:]),float(data['earthquake']['hypocenter']['longitude'][1:])]) #震源地の緯度経度
    
# 火山のjsonデータから火山名と緯度経度を取得し、listにまとめる：
for item in vlist:
    indx = vlist.index(item)
    coodinates.append(vlist[indx]["geometry"]["coordinates"])
    place_name.append(vlist[indx]["name"])


# マップに火山のデータを１つグループとしてまとめる：
volcano_fg = folium.FeatureGroup(name = "日本火山の分布図 ")

# 火山名と緯度経度を順次にマップに表示し、マークポイントをつけていく
for cood, place in zip(coodinates,place_name):
    volcano_fg.add_child(folium.Marker(
        location = [cood[1],cood[0]],
        popup = folium.Popup(place, max_width=450),
        icon = folium.Icon(color="blue")
    ))

# 地震情報を順次にマップに表示し、マークポイントをつけていく
earthquake_fg = folium.FeatureGroup(name= "日本地震の分布図（最新）")
for pubtime, time, city, scale, coodinate in zip(earthquake_publish_time, earthquake_time, earthquake_hypocenter,  earthquake_scale, earthquake_coodinates):
    earthquake_fg.add_child(folium.Marker(
        location = coodinate,
        popup = folium.Popup("・発表時間："+pubtime+"・発生日時："+time+"・震源地："+city+"・最大震度："+str(scale), max_width=400),
        icon = folium.Icon(color="red")
    ))

# 都道府県の境線を一つのレーヤとしてグループを作成：
layer_fg = folium.FeatureGroup(name= "都道府県別日本地図")
layer_fg.add_child(folium.GeoJson(data=(open('Main/japan.geojson' ,'r', encoding='UTF-8').read())))


japan.add_child(volcano_fg)
japan.add_child(layer_fg)
japan.add_child(earthquake_fg)


# レーヤのコントロールバーを作成と表示：
japan.add_child(folium.LayerControl())

japan.save("Volcano and Earthquake in Japan.html")