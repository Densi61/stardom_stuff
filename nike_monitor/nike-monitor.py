import requests
import json
import time
from discord_hooks import Webhook

dis_url = 'https://discord.com/api/webhooks/757555905255440425/o7bCTtNznpo4tvrOnU04zXKcrcXU_iV0QTU_bFYgfZ6Cp6R1dNHQ4ngTc2Z8n00uzrpw'
json_url = 'https://api.nike.com/product_feed/threads/v2/?anchor=0&count=36&filter=marketplace(RU)&filter=language(ru)&filter=upcoming(true)&filter=channelId(010794e5-35fe-4e32-aaff-cd2c74f89d61)&filter=exclusiveAccess(true%2Cfalse)&sort=effectiveStartSellDateAsc&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title'


def main():
    try:
        request = json.loads(requests.get(json_url).text)
        filename = 'nike_monitor/nikeIds.txt'
        # CHECKING IDS IN TXT
        for i in range(len(request['objects'])):
            for j in range(len(request['objects'][i]['productInfo'])):
                print(f"https://www.nike.com/ru/launch/t/{request['objects'][i]['publishedContent']['properties']['seo']['slug']}")
                print(request['objects'][i]['productInfo'][j]['merchProduct']['id'])
                with open(filename, 'r+', encoding='utf-8') as f:
                    read = f.read()
                    if request['objects'][i]['productInfo'][j]['merchProduct']['id'] not in read:
                        try:
                            price = request['objects'][i]['productInfo'][j]['merchPrice']['fullPrice']
                            method = request['objects'][i]['productInfo'][j]['launchView']['method']
                            launchtime = request['objects'][i]['productInfo'][j]['launchView']['startEntryDate']
                            title = request['objects'][i]['productInfo'][j]['merchProduct']['labelName']
                            img = request['objects'][i]['productInfo'][j]['imageUrls']['productImageUrl']
                            styleColor = request['objects'][i]['productInfo'][j]['merchProduct']['styleColor']
                            oos_or_na = 0
                            size = ""
                            for k in range(len(request['objects'][i]['productInfo'][j]['skus'])):  # "k" insted of 7 cause 7 is max amount of lines
                                # earlLink = link + "?size=" + smth['objects'][0]['productInfo'][0]['skus'][i]['nikeSize'] + "&productId=" + productId
                                # size = size + "\n" + "["+smth['objects'][0]['productInfo'][0]['skus'][i]['nikeSize']+"]("+earlLink+")" + " [" + \
                                # smth['objects'][0]['productInfo'][0]['availableSkus'][i]['level'] + "]"
                                size = f"{size}\n{request['objects'][i]['productInfo'][j]['skus'][k]['nikeSize']}[{request['objects'][i]['productInfo'][j]['availableSkus'][k]['level']}]"
                                if request['objects'][i]['productInfo'][j]['availableSkus'][k]['level'] == "OOS" or \
                                        request['objects'][i]['productInfo'][j]['availableSkus'][k][
                                            'level'] == "NA":
                                    oos_or_na = oos_or_na + 1
                            print(size)
                            print(oos_or_na)
                            if oos_or_na > len(request['objects'][i]['productInfo'][j]['skus']) / 2:
                                print("No stock yet...")
                            else:
                                print(styleColor)
                                user_agent = {
                                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36'
                                                  ' (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
                                    'sec-fetch-dest': 'none',
                                    'accept': '*/*',
                                    'sec-fetch-site': 'cross-site',
                                    'sec-fetch-mode': 'cors',
                                    'accept-language': 'en-US'
                                }
                                stockx_search = json.loads(requests.get(f"https://stockx.com/api/browse?_search={styleColor}&dataType=product&country=US", headers = user_agent).text)
                                url_key = stockx_search['Products'][0]['urlKey']
                                dc = Webhook(dis_url, color=0x0a0a0a)
                                dc.add_field(name="New Product",
                                             value=f"[{title}](https://www.nike.com/ru/launch/t/{request['objects'][i]['publishedContent']['properties']['seo']['slug']})")
                                dc.add_field(name="Price", value=price)
                                dc.add_field(name="Launch method", value=method)
                                dc.add_field(name="Launch time", value=launchtime)
                                dc.add_field(name="Sizes", value=size)
                                dc.add_field(name="Useful links", value=f"[StockX](https://stockx.com/{url_key})")
                                dc.set_thumbnail(url=img)
                                dc.set_footer(text='Nike monitor by STARDOM',
                                              icon='https://cdn1.savepice.ru/uploads/2020/11/15/65f29f00c7101c021161bd74c1cbe314-full.png',
                                              ts=True)
                                dc.post()
                                f.write(request['objects'][i]['productInfo'][j]['merchProduct']['id'] + '\n')
                        except Exception as e:
                            print("an exception {} of type {} occurred".format(e, type(e).__name__))
                    else:
                        print("Not new product")
    except Exception as e:
        print("an exception {} of type {} occurred".format(e, type(e).__name__))


while True:
    main()
    print("sleeping...")
    time.sleep(1000)
