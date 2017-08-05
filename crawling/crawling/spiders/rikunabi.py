# -*- coding: utf-8 -*-
import scrapy, csv


class RikunabiSpider(scrapy.Spider):

    #Scrapyを使う上で最低限設定する変数。
    name = 'rikunabi'       #この名前をシェルに記載すればクローリングが開始される
    allowed_domains = ['job.rikunabi.com']

    #各メソッドの垣根を超えて使うものをクラス変数で定義
    companyCount = 0    #リクナビのデータが多すぎる場合にどれくらい進行しているか確認しやすいようカウントする
    #リクナビデータの中でも抽出したいものだけを予め定義する
    checkList =['資本金','事業内容','代表者','事業所','売上高','設立','従業員数','沿革','関連会社','主要取引先','平均年齢','本社所在地','創業','グループ会社','取引銀行','株式上場']


    #クロールURL、ファイル保存先など場合によって変更したくなるものをクラス変数で定義
    filename = './list03.csv'       #抽出されたリストの保存先。本ソースコードと同じ場所に保存される
    pgGoal = 289                    #クローリングしたいカテゴリが何ページ目まであるのか設定する。
    url_default = "https://job.rikunabi.com/2018/search/company/result/?"   #クローリングしたいカテゴリのURLを貼り付ける。このとき「?」が含まれているようにする


    #Scrapyにおいて、必ず最初に読み込まれる関数
    def start_requests(self):

        #リストの最初の行をファイルに記載
        file_opened = open(self.filename,'a')
        csvWriter = csv.writer(file_opened)
        csvWriter.writerow(['企業名','サブ','業種','業種サブ','連絡先']+self.checkList)
        file_opened.close()

        #設定したページまで、全ての企業一覧ページを見ていく
        for i in range(201,self.pgGoal + 1):
            url_search = self.url_default + 'pn=' + str(i)
            yield scrapy.Request(url_search,self.parse)

    #各企業一覧ページで行うことを記載
    def parse(self, response):
        #全ての企業サイトURLをxpathを指定することで抽出
        urls_company = response.xpath('//div[@class="search-cassette-title"]/a/@href').extract()

        #抽出した企業サイトURLを順に見ていく
        for j in urls_company:
            url_companypage = "https://job.rikunabi.com" + j
            yield scrapy.Request(url_companypage,self.parse_company)

    #各企業ページで行うことを記載
    def parse_company(self, response):
        #企業ごとに追加される一行は、infoListにとりまとめてから一括記載する
        infoList =[]
        #邪魔なHTMLタグを予め指定し、後で全部取り除く
        deleteword = ['<div class="ts-h-company-sentence">','<br>','</div>']

        #企業名
        infoList.append(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/h1/a/text()').extract()[0].replace(',',''))

        #企業名のすぐ下に記載の文章。（ないこともあるため、ifで対応）
        if len(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div/text()')) > 0:
            infoList.append(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div/text()').extract()[0].replace(',',''))
        else:
            infoList.append('')

        #業種名。（サブのものがないこともあるため、ifで対応）
        for l in response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[3]/table/tr[1]/td/div/text()').extract():
            infoList.append(l.replace(',',''))
        if len(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[3]/table/tr[1]/td/div/text()')) == 1:
            infoList.append('')

        #連絡先
        infoList.append(response.xpath('//*[@id="company-data04"]/div[@class="ts-h-company-sentence"]').extract()[0].replace(',','').replace(deleteword[0],'').replace(deleteword[1],'').replace(deleteword[2],''))

        #予めクラス変数「checklist」に記載した項目が企業ページ内にあれば、値をinfoListに収納。なければ空白。
        for l in self.checkList:
            flag = 0
            for k in range(len(response.xpath('/html/body/div[1]/div[2]/div[2]/div/table/tr/th/text()').extract())):
                infoCat = response.xpath('/html/body/div[1]/div[2]/div[2]/div/table/tr/th/text()').extract()[k]
                if infoCat == l:
                    infoList.append(response.xpath('/html/body/div[1]/div[2]/div[2]/div/table/tr/td').extract()[k].replace(',','').replace('<td class="ts-h-mod-dataTable02-cell ts-h-mod-dataTable02-cell_td">','').replace(deleteword[1],'').replace('</td>',''))
                    flag = 1
                    break
            if flag == 0:
                infoList.append('')

        #infoListに取りまとめた企業ページ内の情報をまとめてファイルに記載
        file_opened = open(self.filename,'a')
        csvWriter = csv.writer(file_opened)
        csvWriter.writerow(infoList)
        file_opened.close()

        #今何番目の企業を記載終わったのか進捗がわかるようにカウント＆プリント
        self.companyCount =self.companyCount + 1
        print(self.companyCount)
        pass
