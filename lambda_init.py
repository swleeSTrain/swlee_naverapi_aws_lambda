import json
import sys
import urllib.request
import boto3

client_id = "apiid"
client_secret = "secretid"
encText = urllib.parse.quote("코로나19")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('naverapi1')
sns = boto3.client('sns')
start = 1
end = 10
display = 10

def lambda_handler(event, context):
    # TODO implement
    idx = 0
    newslist=[]
    snsnews=[]
    for start_index in range(start, end, display):
        url = "https://openapi.naver.com/v1/search/news?query=" + encText \
            + "&dislay=" + str(display) \
            + "&start=" + str(start_index) +"sort=date" # JSON 결과
    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            response_dict = json.loads(response_body.decode('utf-8'))
            items = response_dict['items']
            for item_index in range(0,len(items)):
                #remove_tag = re.compile('<,*?>')
                #title = re.sub(remove_tag, '',items[item_index]['title'])
                title = items[item_index]['title']
                des = items[item_index]['description']  
                id = items[item_index]['link']
                idx += 1
                result = {
                    "제목": title,
                    "내용": des,
                    "PartitionKey": idx,
                    "id": id
                }
                snsresult = {
                    "제목": title,
                    "id": id
                }
                newslist.append(result)
                snsnews.append(snsresult)
                table.put_item(Item =result)
               
        print(newslist)

    
    response = sns.publish (
      TargetArn = "input_sns_arn",
      Message = json.dumps(snsnews, ensure_ascii=False),
      
      
    )
    return {
        'statusCode': 200,
        'body': json.dumps(newslist, ensure_ascii=False)
    }