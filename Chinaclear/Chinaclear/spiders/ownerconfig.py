#!/usr/bin/env python
#-*- coding:utf-8  -*-   

from items import Items


Configs = [{'list':{'n':'','v':'//table[.//tr[@class]]//tr[@style]','t':'xpath','keys':['date','code'],'check':'code','db':'dbo.chinaclear'},
            'data':[{'n':'日期','En':'date','v':'//input[@id="queryDate"]/@value','t':'xpath_first'},
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'无限售股份质押数量(万) ','En':'unlimitedSale','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'有限售股份质押数量(万)','En':'limitedSale ','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'A股总股本(万)','En':'AshareCapital','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'质押笔数','En':'pledgeNumbers','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'质押比例(%)','En':'Pledgeratio','v':'td[7]/text()','t':'xpath_first'},
                     
                     ]
            }
            ]

             