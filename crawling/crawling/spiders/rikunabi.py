# -*- coding: utf-8 -*-
import scrapy, csv


class RikunabiSpider(scrapy.Spider):
    name = 'rikunabi'
    allowed_domains = ['job.rikunabi.com']
    pageCount = 0
    companyCount = 0
    checkList =['資本金','事業内容','代表者','事業所','売上高','設立','従業員数','沿革','関連会社','主要取引先','平均年齢','本社所在地','創業','グループ会社','取引銀行','株式上場']

    filename = './list03.csv'
    pgGoal = 289
    url_default = "https://job.rikunabi.com/2018/search/company/result/?"

    def start_requests(self):
        file_opened = open(self.filename,'a')
        csvWriter = csv.writer(file_opened)
        csvWriter.writerow(['企業名','サブ','業種','業種サブ','連絡先']+self.checkList)
        file_opened.close()
        for i in range(201,self.pgGoal + 1):
            url_search = self.url_default + 'pn=' + str(i)
            yield scrapy.Request(url_search,self.parse)

    def parse(self, response):
        urls_company = response.xpath('//div[@class="search-cassette-title"]/a/@href').extract()

        for j in urls_company:
            url_companypage = "https://job.rikunabi.com" + j
            yield scrapy.Request(url_companypage,self.parse_company)

        self.pageCount = self.pageCount + 1
        print(self.pageCount)
        pass


    def parse_company(self, response):
        infoList =[]

        deleteword = ['<div class="ts-h-company-sentence">','<br>','</div>']
        infoList.append(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/h1/a/text()').extract()[0].replace(',',''))
        if len(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div/text()')) > 0:
            infoList.append(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[1]/div/text()').extract()[0].replace(',',''))
        else:
            infoList.append('')

        for l in response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[3]/table/tr[1]/td/div/text()').extract():
            infoList.append(l.replace(',',''))
        if len(response.xpath('/html/body/div[1]/div[2]/div[1]/div[1]/div[3]/table/tr[1]/td/div/text()')) == 1:
            infoList.append('')

        infoList.append(response.xpath('//*[@id="company-data04"]/div[@class="ts-h-company-sentence"]').extract()[0].replace(',','').replace(deleteword[0],'').replace(deleteword[1],'').replace(deleteword[2],''))

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

        file_opened = open(self.filename,'a')
        csvWriter = csv.writer(file_opened)
        csvWriter.writerow(infoList)
        file_opened.close()

        self.companyCount =self.companyCount + 1
        print(self.companyCount)
        pass
