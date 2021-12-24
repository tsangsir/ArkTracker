#!/usr/bin/python3.9

from lxml import html 
from datetime import datetime, timedelta 
from dateutil import parser 

import requests 
import cx_Oracle 
import json 

exec(open('config.py').read())

def get_last_trade_date(): 
    sql = "select max(trade_date) from ark_trade" 
    cursor = conn.cursor() 
    cursor.execute(sql) 
    lastdate, = cursor.fetchone() 
    cursor.close() 
    return lastdate

def save_trade(arkTrade, lastdate):
    parm={
            "ticker": "A",# None,
            "date": None,
            "shares": None,
            "weight": None,
            "fund": None,
            "direction": None,
            "hidden": None}

    for atk in arkTrade.keys():
        parm[atk]=arkTrade.get(atk)

    parm["date"] = parser.parse(parm.get("date")[0:10])

    if (parm["date"] > lastdate):
        sql = """insert into ark_trade
                (ticker , trade_date, shares, weight,
                fund, direction, hidden) values  
                (:1, :2, :3, :4, :5, :6, :7)"""
                #(:ticker , :date, :shares, weight, 
                # :fund, :direction, :hidden) """

        cursor = conn.cursor()
        cursor.execute(sql, [
                parm.get("ticker"), 
                parm.get("date"),
                int(parm.get("shares")),
                float(parm.get("weight")),
                parm.get("fund"),
                parm.get("direction"),
                parm.get("hidden")])

        cursor.close()
        conn.commit()

def notify_trade():
    sql = """
            /*with function theoffset return number
            as
                oset number; 
            begin
                select trunc(sysdate)-max(trade_date) into oset from ark_trade;
                return oset;
            end;
            */
            with last_info as (
                select trunc(sysdate)-max(trade_date) theoffset,
                max(trade_date) last_date
                from ark_trade
            )
            select last_date, listagg(distinct direction, '/') within group 
            (order by direction)  directions,
            t.ticker || ': ' ||
            sum((dir_value+1)*days_within_1)/2  || ',' ||
            -sum((dir_value-1)*days_within_1)/2   || ',' ||
            sum(shares*dir_value*days_within_1)   || '; ' ||
            sum((dir_value+1)*days_within_7)/2   || ',' ||
            -sum((dir_value-1)*days_within_7)/2   || ',' ||
            sum(shares*dir_value*days_within_7)   || '; ' ||
            sum((dir_value+1)*days_within_31)/2   || ',' ||
            -sum((dir_value-1)*days_within_31)/2   || ',' ||
            sum(shares*dir_value*days_within_31)    || '; ' ||
            listagg(distinct fund, ',') within group (order by fund) rec
            from (
                select last_date, t.*,
                case when trade_date > sysdate-1-theoffset 
                then 1 else 0 end days_within_1,
                case when trade_date > sysdate-7-theoffset 
                then 1 else 0 end days_within_7,
                case when trade_date > sysdate-31-theoffset 
                then 1 else 0 end days_within_31,
                decode(direction, 'Buy', 1, 'Sell', -1) dir_value
                from ark_trade t, last_info
                where trade_date > sysdate-31-theoffset
            ) t
            group by last_date, ticker
            having sum(days_within_1) > 0
            order by directions
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    prevdir=""
    message = ""
    for last_date, direction, details in cursor:
        if direction != prevdir:
            if prevdir != "":
                message="```\n" + prevdir + " Operations 31 days within " + str(last_date) + ": \r" + message + "\n```"
                request_url="https://api.telegram.org/bot" + botapikey + "/sendMessage?chat_id=" + chatid + "&parse_mode=MarkdownV2&text=" + message
                page = requests.get(request_url)
                message =""
        prevdir = direction 
        message = message + "\n" + details 

    if message != "": 
        message="```\n" + prevdir + " Operations 31 days within " + str(last_date) + ": \r" + message + "\n```"
        request_url="https://api.telegram.org/bot" + botapikey + "/sendMessage?chat_id=" + chatid + "&parse_mode=MarkdownV2&text=" + message
        page = requests.get(request_url)

def notify_trade_old(lastdate):
    sql = """select direction, ticker,
            listagg(fund) within group (order by fund) funds, sum(shares) total_shares, count(*) num_trades
            from ark_trade
            where trade_date>:1
            group by direction, ticker
            order by direction, ticker"""

    cursor = conn.cursor()
    cursor.execute(sql, [lastdate])
    #cursor.execute(sql)
    for direction, ticker, funds, total_shares, num_trades in cursor:
        message=direction + "," + ticker + "," + str(total_shares) + "," + str(num_trades)
        request_url="https://api.telegram.org/bot" + botapikey + "/sendMessage?chat_id=" + chatid + "&text=" + message
        page = requests.get(request_url)

        print(message)

    cursor.close()

    request_url="https://api.telegram.org/bot" + botapikey + "/sendMessage?chat_id=" + chatid + "&text=" + "Sent trades since " + str(lastdate)
    page = requests.get(request_url)
    print(request_url)
    return lastdate



def get_update_id(tbody, fund):
    ribbon = tbody.xpath('//div[@class="ant-ribbon-wrapper"]')

    update_date = parser.parse(ribbon[0].xpath('//div[contains(@class, "ant-ribbon-placement-end")]')[0].text, fuzzy=True) + timedelta(hours=8)


#update_id_wrapper = cursor.var(cx_Oracle.NUMBER)
#sql_params = { "update_id" : update_id_wrapper }
#sql = "insert into ark_update_tbl ( update_date ) values (sysdate) " + \
#      "returning update_id into :update_id"
#cursor.execute(sql, sql_params)
#update_id=update_id_wrapper.getvalue()

#print(update_id[0])

    cursor = conn.cursor()
    sql = "select count(*) from ark_update_tbl " + \
            "where update_date=:update_date " + \
            "and fund = :fund"
    cursor.execute(sql, (update_date, fund))
    c, = cursor.fetchone()
    cursor.close()

    if c > 0:
        return -1


    cursor = conn.cursor()
    update_id_wrapper = cursor.var(cx_Oracle.NUMBER)
    sql_params = { "update_date": update_date, 
            "fund": fund, 
            "update_id" : update_id_wrapper }
    update_id = -1
    sql = "insert into ark_update_tbl ( update_date, fund ) values " + \
            "(:update_date, :fund) " + \
            "returning update_id into :update_id"
    cursor.execute(sql, sql_params)
    update_id = update_id_wrapper.getvalue()
    cursor.close()

    print (update_id)
    return update_id[0]
    

def capture_holdings(fund, start_col):
    url="https://cathiesark.com/" + fund + "/complete-holdings"
    if fund == "ark-funds-combined":
        fund = "COMBINED"
    else:
        fund = fund.upper()
    
    
    page = requests.get(url)
    tree = html.fromstring(page.content)

    tbody = tree.xpath('//tbody')[0]

    jsontext = tree.xpath('//script[@id="__NEXT_DATA__"]')[0].text
    pp = json.loads(jsontext).get("props").get("pageProps")



    for k in pp.keys():
        print(k)
        maxposcnt = -1
        maxposkey = ""
        if k == "DISABLEarkPositions":
            print (k, ": ")
            #f = open("arkPositionsKeys.txt", "a")
            f = open("arkPositionsKeys_nxpi.txt", "w")
            for i in range(0, len(pp.get(k))-1):
                arkPos = pp.get(k)[i]
                # Step 1: Check Key list
                #for apk in arkPos.keys():
                #    f.write(apk + '\n')
                # Step 2: Check ticker with most keys
                #if len(arkPos) > maxposcnt:
                #    maxposcnt = len(arkPos)
                #    maxposkey = arkPos.get("ticker")
                # Step 3: List keys
                # Table will be created based on this
                if arkPos.get("ticker") == "NXPI":
                    for apk in arkPos.keys():
                        f.write(apk + '\n')
            f.close()
            print(maxposkey + ": " + str(maxposcnt))

        if k == "arkTrades":
            print (k, ": ")
            last_date = get_last_trade_date()
            for i in range(0, len(pp.get(k))-1):
                arkPos = pp.get(k)[i]
                save_trade(arkPos, last_date)

            #notify_trade_old(last_date)
            notify_trade()
#        for kk in arkPos.keys():
#        for kk in arkPos.keys():
#            print (kk, arkPos.get(kk))

        
#    else:
#        print (k, pp.get(k))

conn = cx_Oracle.connect("", "", dbconnect)
capture_holdings("ark-funds-combined", 1)


