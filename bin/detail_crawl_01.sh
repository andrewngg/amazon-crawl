#!/bin/sh
cd /data/crawler_system/projects/di/amazon_crawl
program=detail_crawl_01.py

sn=`ps -ef | grep $program | grep -v grep |awk '{print $2}'`
if ["${sn}" = ""]
then
/usr/bin/python3.6 detail_crawl_01.py 2> detail_crawl_01.log 
echo start ok !
else
pkill -9 -p ${sn}
kill -9 ${sn}
/usr/bin/python3.6 detail_crawl_01.py 2> detail_crawl_01.log
echo restart ok !
fi
