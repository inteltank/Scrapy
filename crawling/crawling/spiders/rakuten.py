# -*- coding:utf-8 -*-
import scrapy, re, requests, csv, sys, codecs, cStringIO, os

class RakutensiteSpider(scrapy.Spider):
    name = "rakutenranking"

    checklist =[u'クレジットカード',u'楽天バンク決済',u'代金引換',u'楽天Edy決済',u'銀行振込',u'auかんたん決済',u'Alipay',u'後払い',u'NP後払い',u'後払い\.com',u'クロネコ',u'ニッセン',u'セイノーフィナンシャル',u'GMO',u'ジャックス']
    gen_input = ""
    
    def start_requests(self):

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
        #カテゴリの指定
        self.gen_input = input("catID input here: ")        
        #保存フォルダの作成
        os.mkdir(str(self.gen_input))

        #楽天ランキングAPIは30商品/頁。1000個の情報しゅとくのため34頁まで取得のため反復
        url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20120927?"        
        for i in range(34):
            #楽天ランキングAPI(返り値:json)を用いて取得
            st_load = {
                "genreId":self.gen_input,
                "applicationId": 1008116817122424220,
                "page": i+1,
            }
            r = requests.get(url, params=st_load)
            res = r.json()
            
            #取得結果をcsvに記載
            f = open(str(self.gen_input) + '/' + str(self.gen_input) + '_ranking.csv' , "ab")
            writer = csv.writer(f)
            for j in res["Items"]:
                item = j["Item"]
                Rank = item["rank"]
                Name = (item["itemName"].encode("utf-8"))
                Url = item["itemUrl"]
                Price = item["itemPrice"]
                ShopUrl = item["shopCode"]
                GenreID = item["genreId"]
                writer.writerow([Rank, Name, Url, Price,ShopUrl,GenreID])
                url_tmp = "http://www.rakuten.co.jp/" + ShopUrl + "/info.html"
                
                #取得した店舗コードが初出の場合、その会社情報ページを開き、find_infoメソッドを起動する
                yield scrapy.http.Request(url_tmp,callback=self.find_info)
            f.close()
        
        
    def find_info(self, response):
        
        f_sub = open(str(self.gen_input) + '/' + str(self.gen_input) + '_shop_info.csv', 'ab')
        csvWriter_sub = csv.writer(f_sub)
        
        
        #決済手法のチェックをし、結果を check に格納
        check = [0]*len(self.checklist)
        for i in range(len(self.checklist)):
            for tmp in response.xpath('//text()').extract():
                if re.compile(self.checklist[i]).search(tmp):
                    check[i] = 1
                    break
        
        #企業・担当者の情報を取得し、結果をinfoListに格納
        infoList =[]
        infoList_check = [u'代表者',u'店舗運営責任者',u'店舗セキュリティ責任者',u'@',u'TEL',u'〒']
        for i in range(len(infoList_check)):
            for tmp in response.xpath('//text()').extract():
                if re.compile(infoList_check[i]).search(tmp):
                    if i == 5:
                        infoList.append(tmp.lstrip(u'〒').split(' ',1)[0].strip().encode('utf8'))
                        if len(tmp.lstrip(u'〒').split(' ',1)) > 1:
                            infoList.append(tmp.lstrip(u'〒').split(' ',1)[1].strip().encode('utf8'))
                        break
                    elif i == 4:
                        infoList.append(tmp.split(' ',1)[0].lstrip(u'TEL').lstrip(':').strip().encode('utf8'))
                        break
                    
                    elif i < 3 :
                        infoList.append(tmp.lstrip(infoList_check[i]).lstrip(':').strip().encode('utf8'))
                        break
                    else:
                        infoList.append(tmp.strip().encode('utf8'))
                        break
        #check,infoListの情報をcsvに記載
        csvWriter_sub.writerow([response.url] + check + infoList)
        f_sub.close()
        
        #Terminalにおいて「処理中」であることが分かるように出力
        print ('----------------------------------------------------------------')