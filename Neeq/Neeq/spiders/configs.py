#/usr/bin/env python
#! -*- coding:utf-8 -*-


class Configs(object):
    def __init__(self):
        self.configs1 = {'list':{'n':'基础信息','t':'json','v':'baseinfo'},
                           'data':[{'n':'','En':'address','t':'json','v':'address','dt':''},
                                   {'n':'','En':'area','t':'json','v':'area','dt':''},
                                   {'n':'','En':'broker','t':'json','v':'broker','dt':''},
                                   {'n':'','En':'code','t':'json','v':'code','dt':''},
                                   {'n':'','En':'email','t':'json','v':'email','dt':''},
                                   {'n':'','En':'englishName','t':'json','v':'englishName','dt':''},
                                   {'n':'','En':'fax','t':'json','v':'fax','dt':''},
                                   {'n':'','En':'industry','t':'json','v':'industry','dt':''},
                                   {'n':'','En':'legalRepresentative','t':'json','v':'legalRepresentative','dt':''},
                                   {'n':'','En':'listingDate','t':'json','v':'listingDate','dt':''},
                                   {'n':'','En':'name','t':'json','v':'name','dt':''},
                                   {'n':'','En':'phone','t':'json','v':'phone','dt':''},
                                   {'n':'','En':'postcode','t':'json','v':'postcode','dt':''},
                                   {'n':'','En':'secretaries','t':'json','v':'secretaries','dt':''},
                                   {'n':'','En':'shortname','t':'json','v':'shortname','dt':''},
                                   {'n':'','En':'totalStockEquity','t':'json','v':'totalStockEquity','dt':''},
                                   {'n':'','En':'transferMode','t':'json','v':'transferMode','dt':''},
                                   {'n':'','En':'website','t':'json','v':'website','dt':''}
                                   ]
                           }

        self.configs2 = {'list':{'n':'高管人员','t':'json','v':'executives'},
                       'data':[{'n':'年龄','En':'age','t':'json','v':'age','dt':''},
                               {'n':'学历','En':'education','t':'json','v':'education','dt':''},
                               {'n':'性别','En':'gender','t':'json','v':'gender','dt':''},
                               {'n':'职务','En':'job','t':'json','v':'job','dt':''},
                               {'n':'姓名','En':'name','t':'json','v':'name','dt':''},
                               {'n':'','En':'salary','t':'json','v':'salary','dt':''},
                               {'n':'','En':'term','t':'json','v':'term','dt':''}
                               ]
                       }
        self.configs3 = {'list':{'n':'十大股东','t':'json','v':'topTenHolders'},
                   'data':[{'n':'','En':'changeQty','t':'json','v':'changeQty','dt':''},
                           {'n':'','En':'date','t':'json','v':'date','dt':''},
                           {'n':'','En':'last_quantity','t':'json','v':'last_quantity','dt':''},
                           {'n':'','En':'limitedQuantity','t':'json','v':'limitedQuantity','dt':''},
                           {'n':'','En':'name','t':'json','v':'name','dt':''},
                           {'n':'','En':'num','t':'json','v':'num','dt':''},
                           {'n':'','En':'quantity','t':'json','v':'quantity','dt':''},
                           {'n':'','En':'ratio','t':'json','v':'ratio','dt':''},
                           {'n':'','En':'unlimitedQuantity','t':'json','v':'unlimitedQuantity','dt':''}
                           ]
                   }
        self.configs4 = {'list':{'n':'财务指标','t':'json','v':'finance'},
                   'data':[{'n':'','En':'earningsPerShare','t':'json','v':'earningsPerShare','dt':''},
                           {'n':'','En':'income','t':'json','v':'income','dt':''},
                           {'n':'','En':'netAssets','t':'json','v':'netAssets','dt':''},
                           {'n':'','En':'netAssetsPerShare','t':'json','v':'netAssetsPerShare','dt':''},
                           {'n':'','En':'netAssetsYield','t':'json','v':'netAssetsYield','dt':''},
                           {'n':'','En':'netProfit','t':'json','v':'netProfit','dt':''},
                           {'n':'','En':'nonDistributeProfit','t':'json','v':'nonDistributeProfit','dt':''},
                           {'n':'','En':'profit','t':'json','v':'profit','dt':''},
                           {'n':'','En':'totalAssets','t':'json','v':'totalAssets','dt':''},
                           {'n':'','En':'totalLiability','t':'json','v':'totalLiability','dt':''}
                           ]
                   }
        self.configs = {'list':{'t':'json','v':'content'},
                   'data':[{'n':'公司代码','En':'Company_code','t':'json','v':'xxzqdm','dt':''}]
                   }
#if __name__ == '__main__':
#    a = Configs()
#    print(dir(a))