import requests
import json
import time
from discord_hooks import Webhook

dis_url = 'https://discord.com/api/webhooks/757555905255440425/o7bCTtNznpo4tvrOnU04zXKcrcXU_iV0QTU_bFYgfZ6Cp6R1dNHQ4ngTc2Z8n00uzrpw'
cool_json = 'https://api.nike.com/product_feed/threads/v2/?anchor=0&count=36&filter=marketplace(RU)&filter=language(ru)&filter=upcoming(true)&filter=channelId(010794e5-35fe-4e32-aaff-cd2c74f89d61)&filter=exclusiveAccess(true%2Cfalse)&sort=effectiveStartSellDateAsc&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title'


def main():
    try:
        cool_request = json.loads(requests.get(cool_json).text)
        filename = 'nikeIds.txt'
        # CHECKING LINKS IN TXT
        for i in range(len(cool_request['objects'])):
            for j in range(len(cool_request['objects'][i]['productInfo'])):
                print("https://www.nike.com/ru/launch/t/" +
                      cool_request['objects'][i]['publishedContent']['properties']['seo']['slug'])
                print(cool_request['objects'][i]['productInfo'][j]['merchProduct']['id'])
                with open(filename, 'r+', encoding='utf-8') as f:
                    read = f.read()
                    if cool_request['objects'][i]['productInfo'][j]['merchProduct']['id'] not in read:
                        try:
                            price = cool_request['objects'][i]['productInfo'][j]['merchPrice']['fullPrice']
                            method = cool_request['objects'][i]['productInfo'][j]['launchView']['method']
                            launchtime = cool_request['objects'][i]['productInfo'][j]['launchView']['startEntryDate']
                            title = cool_request['objects'][i]['productInfo'][j]['merchProduct']['labelName']
                            img = cool_request['objects'][i]['productInfo'][j]['imageUrls']['productImageUrl']
                            oos_or_na = 0
                            size = ""
                            for k in range(len(cool_request['objects'][i]['productInfo'][j][
                                                   'skus'])):  # "k" insted of 7 cause 7 is max amount of lines
                                # earlLink = link + "?size=" + smth['objects'][0]['productInfo'][0]['skus'][i]['nikeSize'] + "&productId=" + productId
                                # size = size + "\n" + "["+smth['objects'][0]['productInfo'][0]['skus'][i]['nikeSize']+"]("+earlLink+")" + " [" + \
                                # smth['objects'][0]['productInfo'][0]['availableSkus'][i]['level'] + "]"
                                size = size + "\n" + cool_request['objects'][i]['productInfo'][j]['skus'][k][
                                    'nikeSize'] + " [" + \
                                       cool_request['objects'][i]['productInfo'][j]['availableSkus'][k]['level'] + "]"
                                if cool_request['objects'][i]['productInfo'][j]['availableSkus'][k]['level'] == "OOS" or \
                                        cool_request['objects'][i]['productInfo'][j]['availableSkus'][k][
                                            'level'] == "NA":
                                    oos_or_na = oos_or_na + 1
                            print(size)
                            print(oos_or_na)
                            if oos_or_na > len(cool_request['objects'][i]['productInfo'][j]['skus']) / 2:
                                print("No stock yet...")
                            else:
                                dc = Webhook(dis_url, color=0x0a0a0a)
                                dc.add_field(name="New Product",
                                             value="[" + title + "](https://www.nike.com/ru/launch/t/" +
                                                   cool_request['objects'][i]['publishedContent'][
                                                       'properties']['seo']['slug'] + ")")
                                dc.add_field(name="Price", value=price)
                                dc.add_field(name="Launch method", value=method)
                                dc.add_field(name="Launch time", value=launchtime)
                                dc.add_field(name="Sizes", value=size)
                                dc.set_thumbnail(url=img)
                                dc.set_footer(text='Nike monitor by STARDOM',
                                              icon='https://cdn1.savepice.ru/uploads/2020/11/15/65f29f00c7101c021161bd74c1cbe314-full.png',
                                              ts=True)
                                dc.post()
                                f.write(cool_request['objects'][i]['productInfo'][j]['merchProduct']['id'] + '\n')
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
