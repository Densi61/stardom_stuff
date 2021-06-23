import requests
import json
import time
import traceback
from discord_hooks import Webhook

stardom_dis_url = 'https://discord.com/api/webhooks/744862500503420928/2BJl7dxcQKtSk7dK6tlHjtuHqEWQ9f9VDYndMLtrvT_XvgkJ3uVToT770QXWfjPb5TpG'
test_dis_url = 'https://discord.com/api/webhooks/757555905255440425/o7bCTtNznpo4tvrOnU04zXKcrcXU_iV0QTU_bFYgfZ6Cp6R1dNHQ4ngTc2Z8n00uzrpw'
json_url = 'https://api.nike.com/product_feed/threads/v2/?anchor=0&count=36&filter=marketplace(RU)&filter=language(ru)&filter=upcoming(true)&filter=channelId(010794e5-35fe-4e32-aaff-cd2c74f89d61)&filter=exclusiveAccess(true%2Cfalse)&sort=effectiveStartSellDateAsc&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title'
user_agent = {
                                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36'
                                                  ' (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
                                    'sec-fetch-dest': 'none',
                                    'accept': '*/*',
                                    'sec-fetch-site': 'cross-site',
                                    'sec-fetch-mode': 'cors',
                                    'accept-language': 'en-US',
                                    'X-B3-ParentSpanId':'4e8ff9bf134c67c4',
                                    'X-B3-SpanId':'168fbad389c28342',
                                    'X-B3-TraceId':'aade437bd0d8fc3d'
                                }
active_pairs = {}


def disc_sent(cont, title, slug, price, method, launchtime, size, url_key, img):
    dc = Webhook(stardom_dis_url, color=0x0a0a0a)
    dc.add_field(name=cont,
                 value=f"[{title}](https://www.nike.com/ru/launch/t/{slug})")
    dc.add_field(name="Price", value=price)
    dc.add_field(name="Launch method", value=method)
    dc.add_field(name="Launch time", value=launchtime)
    dc.add_field(name="Sizes", value=size)
    dc.add_field(name="Useful links", value=f"[StockX](https://stockx.com/{url_key})")
    dc.set_thumbnail(url=img)
    dc.set_footer(text='Nike monitor by STARDOM',
                  icon='https://cdn.discordapp.com/icons/734105721213288592/4ebca262eb40799a586d9582f2d6898f.png?size=256',
                  ts=True)
    dc.post()


def get_stock(request, j):
    size = ""
    oos_or_na = 0
    for k in range(len(request['productInfo'][j]['skus'])):  # "k" insted of 7 cause 7 is max amount of lines
        # earlLink = link + "?size=" + smth['objects'][0]['productInfo'][0]['skus'][i]['nikeSize'] + "&productId=" + productId
        # size = size + "\n" + "["+smth['objects'][0]['productInfo'][0]['skus'][i]['nikeSize']+"]("+earlLink+")" + " [" + \
        # smth['objects'][0]['productInfo'][0]['availableSkus'][i]['level'] + "]"
        size = f"{size}\n{request['productInfo'][j]['skus'][k]['nikeSize']}[{request['productInfo'][j]['availableSkus'][k]['level']}]"
        if request['productInfo'][j]['availableSkus'][k]['level'] == "OOS" or request['productInfo'][j]['availableSkus'][k]['level'] == "NA":
            oos_or_na += 1
    return size, oos_or_na


def get_info(request):
    price = request['merchPrice']['fullPrice']
    method = request['launchView']['method']
    launchtime = request['launchView']['startEntryDate']
    title = request['merchProduct']['labelName']
    img = request['imageUrls']['productImageUrl']
    styleColor = request['merchProduct']['styleColor']
    return price, method, launchtime, title, img, styleColor


def main():
        request = json.loads(requests.get(json_url, headers=user_agent).text)
        print(request)
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
                            price, method, launchtime, title, img, styleColor = get_info(request['objects'][i]['productInfo'][j])
                            size, oos_or_na = get_stock(request['objects'][i], j)
                            if oos_or_na > len(request['objects'][i]['productInfo'][j]['skus']) / 2:
                                print("No stock yet...")
                            else:
                                print(styleColor)
                                stockx_search = json.loads(requests.get(f"https://stockx.com/api/browse?_search={styleColor}&dataType=product&country=US", headers=user_agent).text)
                                url_key = stockx_search['Products'][0]['urlKey']
                                disc_sent("New Product", title, request['objects'][i]['publishedContent']['properties']['seo']['slug'], price, method, launchtime, size, url_key, img)
                                f.write(request['objects'][i]['productInfo'][j]['merchProduct']['id'] + '\n')
                                active_pairs[request['objects'][i]['productInfo'][j]['merchProduct']['id']] = size
                        except:
                            print(traceback.format_exc())
                    else:
                        print("Not new product")
                        size, oos_or_na = get_stock(request['objects'][i], j)
                        if (size != active_pairs[request['objects'][i]['productInfo'][j]['merchProduct']['id']]) and (oos_or_na < len(request['objects'][i]['productInfo'][j]['skus']) / 2):
                            price, method, launchtime, title, img, styleColor = get_info(request['objects'][i]['productInfo'][j])
                            stockx_search = json.loads(requests.get(f"https://stockx.com/api/browse?_search={styleColor}&dataType=product&country=US",headers=user_agent).text)
                            url_key = stockx_search['Products'][0]['urlKey']
                            disc_sent("Stock changed", title, request['objects'][i]['publishedContent']['properties']['seo']['slug'], price, method, launchtime, size, url_key, img)
                            active_pairs[request['objects'][i]['productInfo'][j]['merchProduct']['id']] = size


while True:
    main()
    print("sleeping...")
    time.sleep(10)
