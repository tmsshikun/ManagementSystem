import requests
from requests.exceptions import *
from urllib.parse import urlencode
from pyquery import PyQuery as pq
import json
import http.client
import re
import pymongo
import urllib3

client = pymongo.MongoClient('localhost')
db = client['paper']
# proxy_pool_url = 'http://127.0.0.1:5000/get'
max_count = 20
proxy = None
base_url = 'http://apps.webofknowledge.com/summary.do?'
qid = 5000  # 默认为1
sid = ''  # 默认为空
headers = {
    'Cookie': 'AUTO_LOGIN="ed2497ff87d7d493c4c7211ace5480175a75695965654368696e6140476d61696c2e636f6d"; SID="8FhgYPACqoFqlzFl7fo"; CUSTOMER="Anhui University"; E_GROUP_NAME="Anhui University"; ak_bmsc=34B7A76323A04820EF0408E40ACB552BB81A5BC50A1A00005053F65A85A8896E~pl0D3KtxnpH3MubLOChH4Ofc2F5qan1uYj4vD+Es406B0jwjel9OYBJrJNW/cXfYxAtmqNKjt06f/AZEUyyCM/MdLoF9p40LtQLASPFhMmMjTKuRU49a/4r5yvVLyMDSbNU4JZb+VHNrKoVk9OfYz1YcSZKUJoM7HMxpIZOBR8KmNF7g+zwdhw+lZAjYRkU+FmXWuiulv4QVScOqg1+wluWN2V0SSOA9E15zY4cLeK+iOwR5pzyk6SVbhN01AHaV7h; JSESSIONID=A6FB5AFA1867C8FEE3E9ADFD647DA950; bm_sv=1B2A7687195CED6E3D793AE198D9E532~tKz6JZE822c/ZxUjR8/Tl/FawxAdO7Px6R6vurILo9fHr55IudJqFfi98xpi2bTbu8akIpymQpO25ixMGJy1DA4VxvC3TBBdOxdkM/HskYQQ+GKW/PPAGYsd5AoR2OzDw4FRWEADUJZO9D9HDMwZ2GTFajNrplUvcB43cSPbC+4=',
    'Host': 'apps.webofknowledge.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}



def get_sid():
    global sid
    try:
        sid_url = 'http://www.webofknowledge.com/'
        sid_url_response = requests.get(sid_url)
        if sid_url_response.status_code == 200:
            sid = re.findall(r'SID=\w+&', sid_url_response.url)[0].replace('SID=', '').replace('&', '')
            print("获取sid成功!sid=", sid)
        else:
            print("Get Sid Failed!")
            return None
    except ConnectionError:
        print("获取SID时连接错误，重试中...")
        get_sid()


def get_qid():
    global sid, qid
    form_data = {
        'fieldCount': 1,
        'action': 'search',
        'product': 'UA',
        'search_mode': 'GeneralSearch',
        'SID': sid,
        'max_field_count': 25,
        'max_field_notice': '',  # 注意: 无法添加另一字段。
        'input_invalid_notice': '',  # 检索错误: 请输入检索词。
        'exp_notice': '',  # 检索错误: 专利检索词可在多个家族中找到
        'input_invalid_notice_limits': '',  # <br/>注: 滚动框中显示的字段必须至少与一个其他检索字段相组配。
        'sa_params': 'UA||6CJReJ5m9lwBBxjs8t8|http://apps.webofknowledge.com|',
        'formUpdated': 'true',
        'value(input1)': 'Anhui Univ',
        'value(select1)': 'AD',
        'value(hidInput1)': '',
        'limitStatus': 'collapsed',
        'ss_lemmatization': 'On',
        'ss_spellchecking': 'Suggest',
        'SinceLastVisit_UTC': '',
        'SinceLastVisit_DATE': '',
        'period': 'Range Selection',
        'range': 'ALL',
        'startYear': '1950',
        'endYear': '2018',
        'update_back2search_link_param': 'yes',
        'ssStatus': 'display:none',
        'ss_showsuggestions': 'ON',
        'ss_query_language': 'auto',
        'ss_numDefaultGeneralSearchFields': 1,
        'rs_sort_by': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
    }
    try:
        qid_url = 'http://apps.webofknowledge.com/UA_GeneralSearch.do'
        qid_session = requests.Session()
        qid_response = qid_session.post(qid_url, data=form_data)
        if qid_response.status_code == 200:
            qid_response.encoding = qid_response.apparent_encoding
            qid_doc = pq(qid_response.text)
            qid_items = qid_doc('.l-body .l-wrapper .l-wrapper-row .l-column-sidebar .refineSideBarCol').items()
            for qid_item in qid_items:
                qid_url = qid_item.attr('url')
            qid = re.findall(r'qid=\w+&', qid_url)[0].replace('qid=', '').replace('&', '')
            print("获取qid成功!,qid=", qid)
        else:
            print("Get qid failde!")
            return None
    except ConnectionError:
        print("获取QID时连接错误，重试中...")
        get_qid()


def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_html(url, page):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("Error Ourred!")
            return None
    except RequestException:
        print("连接错误4")
        handle_error1(page)
    except ConnectionError:
        print("连接错误5")
        handle_error1(page)
    except http.client.IncompleteRead:
        print("连接错误6")
        handle_error1(page)
    except requests.exceptions.ChunkedEncodingError:
        print("连接错误7")
        handle_error1(page)
    except urllib3.exceptions.NewConnectionError:
        print("连接错误8")
        handle_error1(page)
    except urllib3.exceptions.MaxRetryError:
        print("连接错误9")
        handle_error1(page)
    except requests.exceptions.ConnectionError:
        print("连接错误10")
        handle_error1(page)
    except TimeoutError:
        print("连接错误10")
        handle_error1(page)
    except urllib3.exceptions.NewConnectionError:
        print("连接错误11")
        handle_error1(page)


def get_index(page):
    global sid, qid
    data = {
        'product': 'UA',
        'colName': '',
        'qid': qid,
        'SID': sid,
        'search_mode': 'GeneralSearch',
        'formValue(summary_mode)': 'GeneralSearch',
        'update_back2search_link_param': 'yes',
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    print(url)
    html = get_html(url, page)
    return html


def parse_index(html):
    doc = pq(html)
    items = doc(' .search-results .search-results-content div div a').items()
    for item in items:
        yield item.attr('href')


def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("连接错误1")
    except ConnectionError:
        print("连接错误2")
        handle_response = handle_error2(url)
        return handle_response.text
    except TimeoutError:
        print("连接错误3")
        handle_response = handle_error2(url)
        return handle_response.text


def parse_detail(html):
    doc = pq(html)
    Author = '',
    Title = '',
    Periodical = '',
    Year = '',
    Volume = '',
    Stage = '',
    Leaf = '',
    DOI = '',

    Titles = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(11)').items()
    for Title in Titles:
        Title = Title.attr('value')
    print('Title=', Title)

    Periodicals = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(9)').items()
    for Periodical in Periodicals:
        Periodical = Periodical.attr('value')
    print('Periodical=', Periodical)

    Years = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(8)').items()
    for Year in Years:
        Year = Year.attr('value')
    print('Year=', Year)

    Volumes = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(6)').items()
    for Volume in Volumes:
        Volume = Volume.attr('value')
    print('Volume=', Volume)

    Stages = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(7)').items()
    for Stage in Stages:
        Stage = Stage.attr('value')
    print('Stage=', Stage)

    Leafs = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(10)').items()
    for Leaf in Leafs:
        Leaf = Leaf.attr('value')
    print('Leaf=', Leaf)

    DOIs = doc(
        'body > div.EPAMdiv.main-container > div.NEWfullRecord > form:nth-child(1) > input[type="hidden"]:nth-child(5)').items()
    for DOI in DOIs:
        DOI = DOI.attr('value')
    print('dol=', DOI)

    JCR_categorys = []  # JCR类别
    i = 1
    while True:
        i = i + 1
        JCR_category = ''
        JCR_category = doc('.JCR_Category_table  tr:nth-child(%d) td:nth-child(1)' % i).text()
        if JCR_category:
            JCR_categorys.append(JCR_category)
        else:
            break
    print("JCR_categorys=", JCR_categorys)

    JCR_sorts = []  # JCR类别中的排序
    i = 1
    while True:
        i = i + 1
        JCR_sort = ''
        JCR_sort = doc('.JCR_Category_table  tr:nth-child(%d) td:nth-child(2)' % i).text()
        if JCR_sort:
            JCR_sorts.append(JCR_sort)
        else:
            break
    print("JCR_sorts=", JCR_sorts)

    JCR_partitions = []  # JCR分区
    i = 1
    while True:
        i = i + 1
        JCR_partition = ''
        JCR_partition = doc('.JCR_Category_table  tr:nth-child(%d) td:nth-child(3)' % i).text()
        if JCR_partition:
            JCR_partitions.append(JCR_partition)
        else:
            break
    print("JCR_partitions=", JCR_partitions)

    Authors = []
    i = 0
    while True:
        i = i + 2
        Author = ''
        Author = doc('.l-column-content .l-content div:nth-child(6) > p > a:nth-child(%d)' % i).text()
        if Author:
            Authors.append(Author)
        else:
            break
    print("Authors=", Authors)

    Authors_number = []
    i = 1
    while True:
        i = i + 2
        Author_number = ''
        Author_number = doc(
            '.l-column-content .l-content div:nth-child(6) > p > sup:nth-child(%d) > b > a > b' % i).text()
        if Author_number:
            Authors_number.append(Author_number)
        else:
            break
    print("Authors_number=", Authors_number)

    body = doc('.l-column-content .l-content div:nth-child(8) > p').text()
    print(body)

    Author_key_words = []
    i = 1
    while True:
        i = i + 1
        Author_key_word = ''
        Author_key_word = doc(
            '.l-column-content .l-content div:nth-child(9) > p:nth-child(2) > a:nth-child(%d)' % i).text()
        if Author_key_word:
            Author_key_words.append(Author_key_word)
        else:
            break
    print("Author_key_words=", Author_key_words)

    Key_words_pluses = []
    i = 1
    while True:
        i = i + 1
        Key_words_plus = ''
        Key_words_plus = doc(
            '.l-column-content .l-content div:nth-child(9) > p:nth-child(3) > a:nth-child(%d)' % i).text()
        if Key_words_plus:
            Key_words_pluses.append(Key_words_plus)
        else:
            break
    print("Key_words_pluses=", Key_words_pluses)

    # 通讯作者
    communication_author = doc('.l-column-content .l-content div:nth-child(10) > p:nth-child(2)').text().replace(
        'Reprint Address:', '')
    print("communication_author=", communication_author)

    # 通讯作者地址
    communication_author_address = doc(
        '.l-column-content .l-content div:nth-child(10) > table:nth-child(3) .fr_address_row2').text().replace(
        'Organization-Enhanced Name(s)', '').replace('Anhui University', '').replace('\n', '')
    print("communication_author_address=", communication_author_address)

    addresses = []
    i = 0
    while True:
        i = i + 1
        address = ''
        address = doc('.l-column-content tr:nth-child(%d) .fr_address_row2 a' % i).text()
        if address:
            addresses.append(address)
        else:
            break
    print("addresses=", addresses)

    email = []
    email = doc(' .l-column-content div:nth-child(10) p:nth-child(8) a:nth-child(2)').text()
    print("email=", email)

    i = 1
    Fund_funded_institutionses = []  # 基金资助机构
    while True:
        i = i + 1
        Fund_funded_institutions = ''
        Fund_funded_institutions = doc(
            '.l-column-content .l-content div:nth-child(11) tr:nth-child(%d) td:nth-child(1)' % i).text()
        if Fund_funded_institutions:
            Fund_funded_institutionses.append(Fund_funded_institutions)
        else:
            break
    print("Fund_funded_institutions=", Fund_funded_institutionses)

    i = 1
    Fund_funded_institutions_authorization_numbers = []  # 基金资助机构授权号
    while True:
        i = i + 1
        Fund_funded_institutions_authorization_number = ''
        Fund_funded_institutions_authorization_number = doc(
            '.l-column-content .l-content div:nth-child(11) tr:nth-child(%d) td:nth-child(2)' % i).text()  # 基金资助机构
        if Fund_funded_institutions_authorization_number:
            Fund_funded_institutions_authorization_numbers.append(Fund_funded_institutions_authorization_number)
        else:
            break
    print("Fund_funded_institutions_authorization_numbers=", Fund_funded_institutions_authorization_numbers)

    Fund_information = doc('#show_fund_blurb > p').text()  # 基金资助信息
    print('Fund_information=', Fund_information)

    Influence_factor = doc(' .Impact_Factor_table td:nth-child(1)').text()  # 对应年份影响因子
    print('Influence_factor=', Influence_factor)

    Influence_factors = doc(' .Impact_Factor_table td:nth-child(2)').text()  # 近几年影响因子
    print('Influence_factors=', Influence_factors)

    Influence_factors_year = doc(' .Impact_Factor_table th:nth-child(1)').text()  # 对应年份影响因子
    print('Influence_factors_year=', Influence_factors_year)

    Influence_factors_years = doc(' .Impact_Factor_table th:nth-child(2)').text()  # 对应年份影响因子
    print('Influence_factors_years=', Influence_factors_years)

    ISSN = doc('#show_journal_overlay_7 > p.FR_field.sameLine > value:nth-child(2)').text()
    print('ISSN=', ISSN)

    eISSN = doc('#show_journal_overlay_7 > p.FR_field.sameLine > value:nth-child(5)').text()
    print('eISSN=', eISSN)

    i = 0
    Research_fields = []  # 研究领域
    while True:
        i = i + 2
        Research_field = ''
        Research_field = doc('#show_journal_overlay_7 > p:nth-child(5) > value:nth-child(%d)' % i).text()  # 基金资助机构
        if Research_field:
            Research_fields.append(Research_field)
        else:
            break
    print("Research_fields=", Research_fields)

    Collection_number = doc('#hidden_section > div:nth-child(1) > p:nth-child(3) > value').text()
    print('Collection_number=', Collection_number)

    IDS = doc('#hidden_section > div:nth-child(2) > p:nth-child(2) > value').text()
    print('IDS=', IDS)

    return {
        'authors': Authors,
        'authors_number': Authors_number,
        'title': Title,
        'periodical': Periodical,
        'year': Year,
        'volume': Volume,
        'stage': Stage,
        'leaf': Leaf,
        'DOI': DOI,
        'JCR_categories': JCR_categorys,
        'JCR_sorts': JCR_sorts,
        'JCR_partitions': JCR_partitions,
        'body': body,
        'author_key_words': Author_key_words,
        'KeyWords_Plus': Key_words_pluses,
        'Key_words_pluses': communication_author,
        'communication_author_address': communication_author_address,
        'addresses': addresses,
        'email': email,
        'Fund_funded_institutions': Fund_funded_institutions,
        'Fund_funded_institutions_authorization_numbers': Fund_funded_institutions_authorization_numbers,
        'Fund_information': Fund_information,
        'Influence_factor': Influence_factor,
        'Influence_factors_year': Influence_factors_year,
        'Influence_factors_years': Influence_factors_years,
        'ISSN': ISSN,
        'eISSN': eISSN,
        'Research_fields': Research_fields,
        'Collection_number': Collection_number,
        'IDS': IDS
    }


def save_to_mongo(data, page, count):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved page%d_article%d to Mongo' % (page, count))
    else:
        print('Saved page%d_article%d to Mongo Failed' % (page, count))


def save_to_local(content, page, count):
    with open("result_page%d_article%d.txt" % (page, count), 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        print("save result_page%d_article%d.txt successfully" % (page, count))
        f.close()


def main(page):
    article_count = 0
    html = get_index(page)
    if html:
        article_urls = parse_index(html)
        for article_url in article_urls:
            article_count += 1
            article_html = get_detail("http://apps.webofknowledge.com" + article_url)
            if article_html:
                article_data = parse_detail(article_html)
                save_to_mongo(article_data, page, article_count)


def handle_error1(page):
    get_sid()
    get_qid()
    get_index(page)
    print("handle the error1 completely!")


def handle_error2(url):
    global sid, qid
    get_sid()
    get_qid()
    error_doc = re.findall(r'doc=\w+', url)[0].replace('doc=', '')
    error_page = re.findall(r'page=\w+&', url)[0].replace('page=', '').replace('&', '')
    error_base_url = 'http://apps.webofknowledge.com/full_record.do?'
    data = {
        'product': 'UA',
        'search_mode': 'GeneralSearch',
        'qid': qid,
        'SID': sid,
        'page': error_page,
        'doc': error_doc
    }
    error_queries = urlencode(data)
    new_url = error_base_url + error_queries
    response = requests.get(new_url)
    if response.status_code == 200:
        return response
    else:
        print("handle the error2 Failed!")
    print("handle the error2 completely!")


if __name__ == '__main__':
    get_sid()
    get_qid()
    for page in range(1, 1700):
        main(page)
