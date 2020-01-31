import csv
import json
import logging
import pprint
import requests
import time
import typing
import xmltodict

def is_error_response(http_response, seconds_to_sleep: float = 1) -> bool:
    """
    Returns False if status_code is 503 (system unavailable) or 200 (success),
    otherwise it will return True (failed). This function should be used
    after calling the commands requests.post() and requests.get().
    :param http_response:
        The response object returned from requests.post or requests.get.
    :param seconds_to_sleep:
        The sleep time used if the status_code is 503. This is used to not
        overwhelm the service since it is unavailable.
    """
    if http_response.status_code == 503:
        time.sleep(seconds_to_sleep)
        return False

    return http_response.status_code != 200

def get_xml(url) -> typing.Union[dict, None]:
    """
    Returns xml response if any. Returns None if no xml found.
    :param url:
        The url go get the xml from.
    """
    response = requests.get(url)
    if is_error_response(response):
        return None

    xml_response = response.text
    # print("response.encoding: " + str(response.encoding))
    return xml_response
    
def get_all_reviews_available_from_XML(app_id,page=1) -> typing.List[dict]:
    """
    Returns a list of dictionaries with each dictionary being one review. 
    
    :param app_id:
        The app_id you are searching. 
    :param page:
        The page id to start the loop. Once it reaches the final page + 1, the 
        app will return a non valid json, thus it will exit with the current 
        reviews. 
    """
    reviews: typing.List[dict] = []

    while True:

        url = (
            f'https://itunes.apple.com/ca/rss/customerreviews/page={page}/'
            f'id={app_id}/sortby=mostrecent/xml?urlDesc=/customerreviews/'
            f'page={page}/id={app_id}/sortby=mostrecent/xml')

        xml_response = get_xml(url)

        # File_object = open(str(int(time.time())) + ".txt","a")
        # File_object.write(xml_response)

        # Convert the XML into dictionary
        dict_doc = xmltodict.parse(xml_response)

        print("page num: " + str(page))

        # Break out of the loop and return the dictionary
        # when we run out of "entry"
        if dict_doc.get("feed").get("entry") == None:
            return reviews

        # Loop through each <entry> 
        for entry in dict_doc['feed']['entry']:

            # Extract the text comment from the <content> list
            for content in entry['content']:
                if content['@type'] == "text":
                    comment = content['#text']

            # Write a single line onto the dictionary
            reviews += [
                {
                    'id'        : entry['id'],
                    'updated'   : entry['updated'],
                    'title'     : entry['title'], 
                    'comment'   : comment, 
                    'voteSum'   : entry['im:voteSum'], 
                    'voteCount' : entry['im:voteCount'], 
                    'rating'    : entry['im:rating'], 
                    'version'   : entry['im:version'],
                    'name'      : entry['author']['name'],
                    'uri'       : entry['author']['uri']
                }
            ]

        page += 1        

    
def dump_reviews_iter():
    # TODO: Grab the XML from the HTTP request
    File_object = open("sample.txt","r")
    dict_doc = xmltodict.parse(File_object.read())

    # Open up a blank CSV file
    csvfile = open(str(int(time.time())) + ".csv","w")
    
    # Initialize the CSV writer
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting= csv.QUOTE_ALL)
        
    # Create the header row
    row = [
        "id",
        "updated", 
        "title", 
        "comment",
        "voteSum",
        "voteCount",
        "rating",
        "version",
        "name",
        "uri"
    ]

    # Write the first row
    csvwriter.writerow(row)

    # Loop through each <entry> 
    for entry in dict_doc['feed']['entry']:

        # Extract the text comment from the <content> list
        for content in entry['content']:
            if content['@type'] == "text":
                comment = content['#text']

        # Create a row of data
        row = [
            entry['id'], 
            entry['updated'], 
            entry['title'], 
            comment, 
            entry['im:voteSum'], 
            entry['im:voteCount'], 
            entry['im:rating'], 
            entry['im:version'],
            entry['author']['name'],
            entry['author']['uri']
            ]

        # Write the row of data into the file
        csvwriter.writerow(row)

        # TODO: Change these into debug lines
        # The entire print dump 
        # print(entry['id'])
        # print(entry['updated'])
        # print(entry['title'])
        # for content in entry['content']:
        #     if content['@type'] == "text":
        #         print(content['#text'])
            # print(content['@type'])

        # TODO: Figure out the purpose of this content type
        # print(entry['im:contentType'])
        # print(entry['im:voteSum'])
        # print(entry['im:voteCount'])
        # print(entry['im:rating'])
        # print(entry['im:version'])
        # print(entry['author']['name'])
        # print(entry['author']['uri'])

def write_dict_to_csv(reviews):

    # Declare header columns
    csv_columns = [
        "id",
        "updated", 
        "title", 
        "comment",
        "voteSum",
        "voteCount",
        "rating",
        "version",
        "name",
        "uri"
    ]

    # Open up a blank CSV file
    csvfile = open(str(int(time.time())) + ".csv","w", encoding="utf-8-sig")
    
    # Initialize the CSV writer
    csvwriter = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=csv_columns)
        
    # Write the first row (a.k.a the header)
    csvwriter.writeheader()

    # write the rest of the reviews
    for review in reviews:
        csvwriter.writerow(review)

    # for review in reviews:
    #     row = [
    #         review['id'], 
    #         review['updated'], 
    #         ]
    #     csvwriter.writerow(row)

reviews = get_all_reviews_available_from_XML(1200050042)
write_dict_to_csv(reviews)
print(reviews)

# dump_reviews_iter()



## url https://itunes.apple.com/ca/rss/customerreviews/id=1200050042/page=1/sortby=mostrecent/xml
## https://itunes.apple.com/ca/rss/customerreviews/page=1/id=1200050042/sortby=mostrecent/xml?urlDesc=/customerreviews/page=1/id=1200050042/sortby=mostrecent/xml









## unused code

