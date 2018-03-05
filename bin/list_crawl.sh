#!/bin/sh
cd /data/crawler_system/projects/di/amazon_crawl
program=list_crawl.py

sn=`ps -ef | grep $program | grep -v grep |awk '{print $2}'`
if ["${sn}" = ""]
then
/usr/bin/python3.6 list_crawl.py 2> list_crawl.log 
echo start ok !
else
pkill -9 -p ${sn}
kill -9 ${sn}
/usr/bin/python3.6 list_crawl.py 2> list_crawl.log
echo restart ok !
fi
