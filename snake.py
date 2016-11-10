
import requests,re,os,xlsxwriter,urllib,pymysql
from bs4 import BeautifulSoup

# 每页租房的数据
def getRoomList(pageNum):
    houseUrl = 'http://www.uoko.com/rent/c1a1/p%s' %pageNum
    pageData = sess.get(houseUrl).content.decode()
    soup = BeautifulSoup(pageData,'html.parser')
    houseInfoList = soup.find_all('div',class_='thumb-box')
    for house in houseInfoList:
        # 每页房子详情页的数据
        url = 'http://www.uoko.com%s' %house.a['href']
        data = sess.get(url).content.decode()
        soupinfo = BeautifulSoup(data,'html.parser')
        # 获取房子的ID
        houseId = house.a['href']
        houseId = houseId.split('/')
        houseId = houseId[2]
        # 房子标题
        title = soupinfo.title.text
        # 房子类型
        type = soupinfo.find_all('div',class_='pro_content')[2].text
        if '合租' in type:
            type = 1
        elif '标间' in type:
            type = 2
        elif '整租' in type:
            type = 3
        # 房子地址
        address = soupinfo.find_all('a',class_='ImageMapNav')[0].text
        # 区域ID  area_id
        area = soupinfo.find('span',class_='pro_area').a.text
        if area == '龙泉驿':
            areaId = 510112
        elif area == '青羊区':
            areaId = 510105
        elif area == '青白江区':
            areaId = 510113
        elif area == '锦江区':
            areaId = 510104
        elif area == '金牛区':
            areaId = 510106
        elif area == '武侯区':
            areaId = 510107
        elif area == '成华区':
            areaId = 510108
        elif area == '双流':
            areaId = 510122
        else:
            areaId = 510100
        status = 1
        cmd = soupinfo.find_all('div',class_='col-md-10')
        # 附近商圈
        business = cmd[0].text.strip()
        # 适合人群
        crowd = cmd[1].text.strip()
        # 地铁
        train = cmd[2].text.strip()
        # 公交
        bus = cmd[3].text.strip()
        # 超市
        market = cmd[4].text.strip()
        # 菜市
        food_market = cmd[5].text.strip()
        # 银行
        bank = cmd[6].text.strip()
        # 餐馆
        restaurant = cmd[7].text.strip()
        # 医院
        hospital = cmd[8].text.strip()
        # //获取封面图片
        img = soupinfo.find_all('li',class_='diagram-img-big')[0].a['href']
        img = img.split('&')
        img = 'http://www.uoko.com'+img[0]
        # 获取户型图
        houseTypeImg = soupinfo.find('a',class_='house_type')['href']
        houseTypeImg = 'http://www.uoko.com'+houseTypeImg.split('&')[0]
        # 暂时不抓取图片到本地 占磁盘空间
        # imgPath = 'F:\\tsewell\Public\images\\20160902'
        # imgName = '12.jpg'
        # getImg(img,imgPath,imgName)

        # 房子(house表)需要的数据
        house = {'title':"'"+title+"'",
                 'id':houseId,
                 'type':type,
                 'img':"'"+img+"'",
                 'house_type_img':"'"+houseTypeImg+"'",
                 'address':"'"+address+"'",
                 'area_id':areaId,
                 'status':status,
                 'business':"'"+business+"'",
                 'crowd':"'"+crowd+"'",
                 'train':"'"+train+"'",
                 'bus':"'"+bus+"'",
                 'market':"'"+market+"'",
                 'food_market':"'"+food_market+"'",
                 'bank':"'"+bank+"'",
                 'restaurant':"'"+restaurant+"'",
                 'hospital':"'"+hospital+"'"
        }
        houseSql = "INSERT INTO house(id,title,type,img,house_type_img,address,area_id,status,business,crowd,train,bus,market,food_market,bank,restaurant,hospital)" \
              " VALUE(%(id)s,%(title)s,%(type)s,%(img)s,%(house_type_img)s,%(address)s,%(area_id)s,%(status)s,%(business)s,%(crowd)s,%(train)s,%(bus)s,%(market)s,%(food_market)s,%(bank)s,%(restaurant)s,%(hospital)s)" %house
        # 房子数据入库
        print(houseSql)
        addData(houseSql)
        houseInfoImgs = soupinfo.find_all('div',class_='pro_public_img')
        for houseInfoImg in houseInfoImgs:
            InfoImg = houseInfoImg.img['data-original'].split('&')[0]
            InfoImg = 'http://www.uoko.com'+InfoImg
            # 房子图文详情表需要的数据
            houseimg = {'house_id':houseId,
                        'img':"'"+InfoImg+"'"
            }
            imgSQL = "INSERT INTO house_imgs(house_id,img) VALUE(%(house_id)s,%(img)s)" %houseimg
            # 房子图片数据入库
            print(imgSQL)
            addData(imgSQL)
        room = soupinfo.find('tbody',class_='config_content').find_all('td')
        roomNum = len(room)//11
        # 判断是整租需求数据还是合租
        if roomNum == 1:
            # 房间图片
            roomImg = soupinfo.find_all('li',class_='diagram-img-big')[0].a['href']
            roomImg = 'http://www.uoko.com'+roomImg.split('&')[0]
            # 房间名字
            roomName = room[0].text
            # 房间是否入住
            roomStatus = room[1].img['data-original-title']
            if roomStatus == '就他了！':
                roomStatus = 2
            else:
                roomStatus = 1
            # 面积
            size = int(float(list(room[2].strings)[0]))
            # 房间类型
            typeArr = [3,4,5,6,7]
            types = []
            for t in typeArr:
                if room[t].i != None:
                    types.append(str(t-2))
            type = ",".join(types)
            # 价格
            if len(room[8].text.strip()) == 0:
                prince = 780
            else:
                prince = int(list(room[8].strings)[2])
            roomInfo = {'name':"'"+roomName+"'",
                        'status':roomStatus,
                        'house_id':houseId,
                        'size':size,
                        'type':"'"+type+"'",
                        'prince':prince,
                        'img':"'"+roomImg+"'"
            }
            roomSql = "INSERT INTO room(name,status,house_id,size,type,price,img) VALUE(%(name)s,%(status)s,%(house_id)s,%(size)s,%(type)s,%(prince)s,%(img)s)" %roomInfo
            print(roomSql)
            addData(roomSql)
        else:
            for i in range(0,roomNum):
                # 房间图片
                roomImg = soupinfo.find_all('div',class_='col-md-6')[i].img['data-original']
                roomImg = 'http://www.uoko.com'+roomImg.split('&')[0]
                i = i*11
                # 房间名字
                roomName = room[i].text
                # 房间是否入住
                roomStatus = room[i+1].img['data-original-title']
                if roomStatus == '就他了！':
                    roomStatus = 2
                else:
                    roomStatus = 1
                # 面积
                size = int(float(list(room[i+2].strings)[0]))
                # 房间类型
                typeArr = [3,4,5,6,7]
                types = []
                for t in typeArr:
                    if room[i+t].i != None:
                        types.append(str(t-2))
                type = ",".join(types)
                # 价格
                if len(room[i+8].text.strip()) == 0:
                    prince = 780
                else:
                    prince = int(list(room[i+8].strings)[2])
                roomInfo = {'name':"'"+roomName+"'",
                            'status':roomStatus,
                            'house_id':houseId,
                            'size':size,
                            'type':"'"+type+"'",
                            'prince':prince,
                            'img':"'"+roomImg+"'"
                }
                roomSql = "INSERT INTO room(name,status,house_id,size,type,price,img) VALUE(%(name)s,%(status)s,%(house_id)s,%(size)s,%(type)s,%(prince)s,%(img)s)" %roomInfo
                print(roomSql)
                addData(roomSql)
    return

# 抓取图片
def getImg(url,imgPath,imgName):
    res = urllib.request.urlopen(url)
    filename = os.path.join(imgPath,imgName)
    file = open(filename,'wb')
    file.write(res.read())

# 把数据写入数据库
def addData(sql):
    conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='root',db='mysql',charset='UTF8')
    cur = conn.cursor()
    cur.execute("USE uoko")
    rst = cur.execute(sql)
    conn.commit()
    return rst
#>>0:初始化一些变量
sess = requests.Session()
maxPageNum = 21

#>>1:爬取所有工作
for pageNum in range(1,maxPageNum):
    print(pageNum)
    getRoomList(pageNum)
