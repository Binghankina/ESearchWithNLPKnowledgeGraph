# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-18 10:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='机构ID')),
                ('organization_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='机构名称')),
                ('announcement_date', models.DateField(null=True, verbose_name='公告日期')),
                ('end_date', models.DateField(null=True, verbose_name='截止日期')),
                ('report_year', models.DateField(null=True, verbose_name='报告年度')),
                ('merge_type', models.CharField(blank=True, max_length=128, null=True, verbose_name='合并类型')),
                ('report_source', models.CharField(blank=True, max_length=128, null=True, verbose_name='报表来源')),
                ('hbzj', models.FloatField(blank=True, null=True, verbose_name='货币资金')),
                ('ygyjzjlqqbdjrdqsydjrzc', models.FloatField(blank=True, null=True, verbose_name='以公允价值计量且其变动计入当期损益的金融资产')),
                ('yspj', models.FloatField(blank=True, null=True, verbose_name='应收票据')),
                ('yszk', models.FloatField(blank=True, null=True, verbose_name='应收账款')),
                ('yfkx', models.FloatField(blank=True, null=True, verbose_name='预付款项')),
                ('qtysk', models.FloatField(blank=True, null=True, verbose_name='其他应收款')),
                ('ysglgsk', models.FloatField(blank=True, null=True, verbose_name='应收关联公司款')),
                ('yslx', models.FloatField(blank=True, null=True, verbose_name='应收利息')),
                ('ysgl', models.FloatField(blank=True, null=True, verbose_name='应收股利')),
                ('ch', models.FloatField(blank=True, null=True, verbose_name='存货')),
                ('qzxhxswzc', models.FloatField(blank=True, null=True, verbose_name='其中消耗性生物资产')),
                ('nndqdfldzc', models.FloatField(blank=True, null=True, verbose_name='年内到期的非流动资产')),
                ('qtldzc', models.FloatField(blank=True, null=True, verbose_name='其他流动资产')),
                ('ldzchj', models.FloatField(blank=True, null=True, verbose_name='流动资产合计')),
                ('kgcsjrzc', models.FloatField(blank=True, null=True, verbose_name='可供出售金融资产')),
                ('cyzdqtz', models.FloatField(blank=True, null=True, verbose_name='持有至到期投资')),
                ('cqysk', models.FloatField(blank=True, null=True, verbose_name='长期应收款')),
                ('cqgqtz', models.FloatField(blank=True, null=True, verbose_name='长期股权投资')),
                ('tzxfdc', models.FloatField(blank=True, null=True, verbose_name='投资性房地产')),
                ('gdzc', models.FloatField(blank=True, null=True, verbose_name='固定资产')),
                ('zjgc', models.FloatField(blank=True, null=True, verbose_name='在建工程')),
                ('gcwz', models.FloatField(blank=True, null=True, verbose_name='工程物资')),
                ('gdzcql', models.FloatField(blank=True, null=True, verbose_name='固定资产清理')),
                ('scxswzc', models.FloatField(blank=True, null=True, verbose_name='生产性生物资产')),
                ('yqzc', models.FloatField(blank=True, null=True, verbose_name='油气资产')),
                ('wxzc', models.FloatField(blank=True, null=True, verbose_name='无形资产')),
                ('kfzc', models.FloatField(blank=True, null=True, verbose_name='开发支出')),
                ('sy', models.FloatField(blank=True, null=True, verbose_name='商誉')),
                ('cqdtfy', models.FloatField(blank=True, null=True, verbose_name='长期待摊费用')),
                ('dysdszc', models.FloatField(blank=True, null=True, verbose_name='递延所得税资产')),
                ('qtfldzc', models.FloatField(blank=True, null=True, verbose_name='其他非流动资产')),
                ('fldzchj', models.FloatField(blank=True, null=True, verbose_name='非流动资产合计')),
                ('zczj', models.FloatField(blank=True, null=True, verbose_name='资产总计')),
                ('dqjk', models.FloatField(blank=True, null=True, verbose_name='短期借款')),
                ('ygyjzjlqqbdjrdqsydjrfz', models.FloatField(blank=True, null=True, verbose_name='以公允价值计量且其变动计入当期损益的金融负债')),
                ('yfpj', models.FloatField(blank=True, null=True, verbose_name='应付票据')),
                ('yfzk', models.FloatField(blank=True, null=True, verbose_name='应付账款')),
                ('yskx', models.FloatField(blank=True, null=True, verbose_name='预收款项')),
                ('yfzgxc', models.FloatField(blank=True, null=True, verbose_name='应付职工薪酬')),
                ('yjsf', models.FloatField(blank=True, null=True, verbose_name='应交税费')),
                ('yflx', models.FloatField(blank=True, null=True, verbose_name='应付利息')),
                ('yfgl', models.FloatField(blank=True, null=True, verbose_name='应付股利')),
                ('qtyfk', models.FloatField(blank=True, null=True, verbose_name='其他应付款')),
                ('yfglgsk', models.FloatField(blank=True, null=True, verbose_name='应付关联公司款')),
                ('nndqdfldfz', models.FloatField(blank=True, null=True, verbose_name='年内到期的非流动负债')),
                ('qtldfz', models.FloatField(blank=True, null=True, verbose_name='其他流动负债')),
                ('ldfzhj', models.FloatField(blank=True, null=True, verbose_name='流动负债合计')),
                ('cqjk', models.FloatField(blank=True, null=True, verbose_name='长期借款')),
                ('yfzq', models.FloatField(blank=True, null=True, verbose_name='应付债券')),
                ('cqyfk', models.FloatField(blank=True, null=True, verbose_name='长期应付款')),
                ('zxyfk', models.FloatField(blank=True, null=True, verbose_name='专项应付款')),
                ('yjfz', models.FloatField(blank=True, null=True, verbose_name='预计负债')),
                ('dysdsfz', models.FloatField(blank=True, null=True, verbose_name='递延所得税负债')),
                ('qtfldfz', models.FloatField(blank=True, null=True, verbose_name='其他非流动负债')),
                ('fldfzhj', models.FloatField(blank=True, null=True, verbose_name='非流动负债合计')),
                ('fzhj', models.FloatField(blank=True, null=True, verbose_name='负债合计')),
                ('sszbhgb', models.FloatField(blank=True, null=True, verbose_name='实收资本或股本')),
                ('zbgj', models.FloatField(blank=True, null=True, verbose_name='资本公积')),
                ('yygj', models.FloatField(blank=True, null=True, verbose_name='盈余公积')),
                ('zxcb', models.FloatField(blank=True, null=True, verbose_name='专项储备')),
                ('jkcg', models.FloatField(blank=True, null=True, verbose_name='减库存股')),
                ('bfxzb', models.FloatField(blank=True, null=True, verbose_name='般风险准备')),
                ('wfplr', models.FloatField(blank=True, null=True, verbose_name='未分配利润')),
                ('gsymgssyzqy', models.FloatField(blank=True, null=True, verbose_name='归属于母公司所有者权益')),
                ('ssgdqy', models.FloatField(blank=True, null=True, verbose_name='少数股东权益')),
                ('wbbbzsjc', models.FloatField(blank=True, null=True, verbose_name='外币报表折算价差')),
                ('fzcjyxmsydz', models.FloatField(blank=True, null=True, verbose_name='非正常经营项目收益调整')),
                ('syzqyhgdqyhj', models.FloatField(blank=True, null=True, verbose_name='所有者权益或股东权益合计')),
                ('fzhsyzhgdqyhj', models.FloatField(blank=True, null=True, verbose_name='负债和所有者或股东权益合计')),
                ('qtzhsy', models.FloatField(blank=True, null=True, verbose_name='其他综合收益')),
                ('dysyfldfz', models.FloatField(blank=True, null=True, verbose_name='递延收益非流动负债')),
                ('jsbfj', models.FloatField(blank=True, null=True, verbose_name='结算备付金')),
                ('cczj', models.FloatField(blank=True, null=True, verbose_name='拆出资金')),
                ('ffdkjdkldzc', models.FloatField(blank=True, null=True, verbose_name='发放贷款及垫款流动资产')),
                ('ysjrzc', models.FloatField(blank=True, null=True, verbose_name='衍生金融资产')),
                ('ysbf', models.FloatField(blank=True, null=True, verbose_name='应收保费')),
                ('ysfbzk', models.FloatField(blank=True, null=True, verbose_name='应收分保账款')),
                ('ysfbhtzbj', models.FloatField(blank=True, null=True, verbose_name='应收分保合同准备金')),
                ('mrfsjrzc', models.FloatField(blank=True, null=True, verbose_name='买入返售金融资产')),
                ('hfwcydsdzc', models.FloatField(blank=True, null=True, verbose_name='划分为持有待售的资产')),
                ('ffdkjdkfldzc', models.FloatField(blank=True, null=True, verbose_name='发放贷款及垫款非流动资产')),
                ('xzyyxjk', models.FloatField(blank=True, null=True, verbose_name='向中央银行借款')),
                ('xsckjtycf', models.FloatField(blank=True, null=True, verbose_name='吸收存款及同业存放')),
                ('crzj', models.FloatField(blank=True, null=True, verbose_name='拆入资金')),
                ('ysjrfz', models.FloatField(blank=True, null=True, verbose_name='衍生金融负债')),
                ('mchgjrzck', models.FloatField(blank=True, null=True, verbose_name='卖出回购金融资产款')),
                ('yfsxfjyj', models.FloatField(blank=True, null=True, verbose_name='应付手续费及佣金')),
                ('yffbzk', models.FloatField(blank=True, null=True, verbose_name='应付分保账款')),
                ('bxhtzbj', models.FloatField(blank=True, null=True, verbose_name='保险合同准备金')),
                ('dlmmzqk', models.FloatField(blank=True, null=True, verbose_name='代理买卖证券款')),
                ('dlcxzqk', models.FloatField(blank=True, null=True, verbose_name='代理承销证券款')),
                ('hfwcydsdfz', models.FloatField(blank=True, null=True, verbose_name='划分为持有待售的负债')),
                ('yjfzldfz', models.FloatField(blank=True, null=True, verbose_name='预计负债流动负债')),
                ('dysyldfz', models.FloatField(blank=True, null=True, verbose_name='递延收益流动负债')),
                ('qzyxgfldfz', models.FloatField(blank=True, null=True, verbose_name='其中优先股非流动负债')),
                ('yxzfldfz', models.FloatField(blank=True, null=True, verbose_name='永续债非流动负债')),
                ('cqyfzgxc', models.FloatField(blank=True, null=True, verbose_name='长期应付职工薪酬')),
                ('qtqygj', models.FloatField(blank=True, null=True, verbose_name='其他权益工具')),
                ('qzyxgsyzqy', models.FloatField(blank=True, null=True, verbose_name='其中优先股所有者权益')),
                ('yxzsyzqy', models.FloatField(blank=True, null=True, verbose_name='永续债所有者权益')),
            ],
        ),
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='机构ID')),
                ('organization_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='机构名称')),
                ('announcement_date', models.DateField(null=True, verbose_name='公告日期')),
                ('begin_date', models.DateField(null=True, verbose_name='开始日期')),
                ('end_date', models.DateField(null=True, verbose_name='截止日期')),
                ('report_year', models.DateField(null=True, verbose_name='报告年度')),
                ('merge_type', models.CharField(blank=True, max_length=128, null=True, verbose_name='合并类型')),
                ('report_source', models.CharField(blank=True, max_length=128, null=True, verbose_name='报表来源')),
                ('xssptglwsddxj', models.FloatField(blank=True, null=True, verbose_name='销售商品提供劳务收到的现金')),
                ('sddsffh', models.FloatField(blank=True, null=True, verbose_name='收到的税费返还')),
                ('sdqtyjyhdygdxj', models.FloatField(blank=True, null=True, verbose_name='收到其他与经营活动有关的现金')),
                ('jyhdxjlrxj', models.FloatField(blank=True, null=True, verbose_name='经营活动现金流入小计')),
                ('gmspjslwzfdxj', models.FloatField(blank=True, null=True, verbose_name='购买商品接受劳务支付的现金')),
                ('zfgzgyjwzgzfdxj', models.FloatField(blank=True, null=True, verbose_name='支付给职工以及为职工支付的现金')),
                ('zfdgxsf', models.FloatField(blank=True, null=True, verbose_name='支付的各项税费')),
                ('zfqtyjyhdygdxj', models.FloatField(blank=True, null=True, verbose_name='支付其他与经营活动有关的现金')),
                ('jyhdxjlcxj', models.FloatField(blank=True, null=True, verbose_name='经营活动现金流出小计')),
                ('jyhdcsdxjllje', models.FloatField(blank=True, null=True, verbose_name='经营活动产生的现金流量净额')),
                ('shtzsddxj', models.FloatField(blank=True, null=True, verbose_name='收回投资收到的现金')),
                ('qdtzsysddxj', models.FloatField(blank=True, null=True, verbose_name='取得投资收益收到的现金')),
                ('czgdzcwxzchqtcqzcshdxjje', models.FloatField(blank=True, null=True, verbose_name='处置固定资产无形资产和其他长期资产收回的现金净额')),
                ('czzgsjqtyydwsddxjje', models.FloatField(blank=True, null=True, verbose_name='处置子公司及其他营业单位收到的现金净额')),
                ('sdqtytzhdygdxj', models.FloatField(blank=True, null=True, verbose_name='收到其他与投资活动有关的现金')),
                ('tzhdxjlrxj', models.FloatField(blank=True, null=True, verbose_name='投资活动现金流入小计')),
                ('gjgdzcwxzchqtcqzczfdxj', models.FloatField(blank=True, null=True, verbose_name='购建固定资产无形资产和其他长期资产支付的现金')),
                ('tzzfdxj', models.FloatField(blank=True, null=True, verbose_name='投资支付的现金')),
                ('zydkjzje', models.FloatField(blank=True, null=True, verbose_name='质押贷款净增加额')),
                ('qdzgsjqtyydwzfdxjje', models.FloatField(blank=True, null=True, verbose_name='取得子公司及其他营业单位支付的现金净额')),
                ('zfqtytzhdygdxj', models.FloatField(blank=True, null=True, verbose_name='支付其他与投资活动有关的现金')),
                ('tzhdxjlcxj', models.FloatField(blank=True, null=True, verbose_name='投资活动现金流出小计')),
                ('tzhdcsdxjllje', models.FloatField(blank=True, null=True, verbose_name='投资活动产生的现金流量净额')),
                ('xstzsddxj', models.FloatField(blank=True, null=True, verbose_name='吸收投资收到的现金')),
                ('qdjksddxj', models.FloatField(blank=True, null=True, verbose_name='取得借款收到的现金')),
                ('fxzqsddxj', models.FloatField(blank=True, null=True, verbose_name='发行债券收到的现金')),
                ('sdqtyczhdygdxj', models.FloatField(blank=True, null=True, verbose_name='收到其他与筹资活动有关的现金')),
                ('czhdxjlrxj', models.FloatField(blank=True, null=True, verbose_name='筹资活动现金流入小计')),
                ('chzwzfdxj', models.FloatField(blank=True, null=True, verbose_name='偿还债务支付的现金')),
                ('fpgllrhcflxzfdxj', models.FloatField(blank=True, null=True, verbose_name='分配股利利润或偿付利息支付的现金')),
                ('zfqtyczhdygdxj', models.FloatField(blank=True, null=True, verbose_name='支付其他与筹资活动有关的现金')),
                ('czhdxjlcxj', models.FloatField(blank=True, null=True, verbose_name='筹资活动现金流出小计')),
                ('czhdcsdxjllje', models.FloatField(blank=True, null=True, verbose_name='筹资活动产生的现金流量净额')),
                ('hlbddxjdyx', models.FloatField(blank=True, null=True, verbose_name='汇率变动对现金的影响')),
                ('qtyydxjdyx', models.FloatField(blank=True, null=True, verbose_name='()其他原因对现金的影响')),
                ('xjjxjdjwjzje', models.FloatField(blank=True, null=True, verbose_name='现金及现金等价物净增加额')),
                ('qcxjjxjdjwye', models.FloatField(blank=True, null=True, verbose_name='期初现金及现金等价物余额')),
                ('qmxjjxjdjwye', models.FloatField(blank=True, null=True, verbose_name='期末现金及现金等价物余额')),
                ('fz', models.FloatField(blank=True, null=True, verbose_name='附注')),
                ('jjlrdjwjyhdxjll', models.FloatField(blank=True, null=True, verbose_name='将净利润调节为经营活动现金流量')),
                ('jlr', models.FloatField(blank=True, null=True, verbose_name='净利润')),
                ('jzcjzzb', models.FloatField(blank=True, null=True, verbose_name='加资产减值准备')),
                ('gdzczjyqzczhscxswzczj', models.FloatField(blank=True, null=True, verbose_name='固定资产折旧油气资产折耗生产性生物资产折旧')),
                ('wxzctx', models.FloatField(blank=True, null=True, verbose_name='无形资产摊销')),
                ('cqdtfytx', models.FloatField(blank=True, null=True, verbose_name='长期待摊费用摊销')),
                ('czgdzcwxzchqtcqzcdss', models.FloatField(blank=True, null=True, verbose_name='处置固定资产无形资产和其他长期资产的损失')),
                ('gdzcbfss', models.FloatField(blank=True, null=True, verbose_name='固定资产报废损失')),
                ('gyjzbdss', models.FloatField(blank=True, null=True, verbose_name='公允价值变动损失')),
                ('cwfy', models.FloatField(blank=True, null=True, verbose_name='财务费用')),
                ('tzss', models.FloatField(blank=True, null=True, verbose_name='投资损失')),
                ('dysdszcjs', models.FloatField(blank=True, null=True, verbose_name='递延所得税资产减少')),
                ('dysdsfzzj', models.FloatField(blank=True, null=True, verbose_name='递延所得税负债增加')),
                ('chdjs', models.FloatField(blank=True, null=True, verbose_name='存货的减少')),
                ('jyxysxmdjs', models.FloatField(blank=True, null=True, verbose_name='经营性应收项目的减少')),
                ('jyxyfxmdzj', models.FloatField(blank=True, null=True, verbose_name='经营性应付项目的增加')),
                ('qt', models.FloatField(blank=True, null=True, verbose_name='其他')),
                ('jyhdcsdxjllje_2', models.FloatField(blank=True, null=True, verbose_name='经营活动产生的现金流量净额')),
                ('bsjxjszdzdtzhczhd', models.FloatField(blank=True, null=True, verbose_name='不涉及现金收支的重大投资和筹资活动')),
                ('zwzwzb', models.FloatField(blank=True, null=True, verbose_name='债务转为资本')),
                ('nndqdkzhgszq', models.FloatField(blank=True, null=True, verbose_name='年内到期的可转换公司债券')),
                ('rzzrgdzc', models.FloatField(blank=True, null=True, verbose_name='融资租入固定资产')),
                ('xjjxjdjwjbdqk', models.FloatField(blank=True, null=True, verbose_name='现金及现金等价物净变动情况')),
                ('xjdqmye', models.FloatField(blank=True, null=True, verbose_name='现金的期末余额')),
                ('jxjdqcye', models.FloatField(blank=True, null=True, verbose_name='减现金的期初余额')),
                ('jxjdjwdqmye', models.FloatField(blank=True, null=True, verbose_name='加现金等价物的期末余额')),
                ('jxjdjwdqcye', models.FloatField(blank=True, null=True, verbose_name='减现金等价物的期初余额')),
                ('jqtyydxjdyx', models.FloatField(blank=True, null=True, verbose_name='加其他原因对现金的影响')),
                ('xjjxjdjwjzje_2', models.FloatField(blank=True, null=True, verbose_name='现金及现金等价物净增加额')),
                ('khckhtycfkxjzje', models.FloatField(blank=True, null=True, verbose_name='客户存款和同业存放款项净增加额')),
                ('xzyyxjkjzje', models.FloatField(blank=True, null=True, verbose_name='向中央银行借款净增加额')),
                ('xqtjrjgcrzjjzje', models.FloatField(blank=True, null=True, verbose_name='向其他金融机构拆入资金净增加额')),
                ('sdybxhtbfqddxj', models.FloatField(blank=True, null=True, verbose_name='收到原保险合同保费取得的现金')),
                ('sdzbxywxjje', models.FloatField(blank=True, null=True, verbose_name='收到再保险业务现金净额')),
                ('bhcjjtzkjzje', models.FloatField(blank=True, null=True, verbose_name='保户储金及投资款净增加额')),
                ('czygyjzjlqqbdjrdqsydjrzcjzje', models.FloatField(blank=True, null=True, verbose_name='处置以公允价值计量且其变动计入当期损益的金融资产净增加额')),
                ('sqlxsxfjyjdxj', models.FloatField(blank=True, null=True, verbose_name='收取利息手续费及佣金的现金')),
                ('crzjjzje', models.FloatField(blank=True, null=True, verbose_name='拆入资金净增加额')),
                ('hgywzjjzje', models.FloatField(blank=True, null=True, verbose_name='回购业务资金净增加额')),
                ('khdkjdkjzje', models.FloatField(blank=True, null=True, verbose_name='客户贷款及垫款净增加额')),
                ('cfzyyxhtykxjzje', models.FloatField(blank=True, null=True, verbose_name='存放中央银行和同业款项净增加额')),
                ('zfybxhtpfkxdxj', models.FloatField(blank=True, null=True, verbose_name='支付原保险合同赔付款项的现金')),
                ('zflxsxfjyjdxj', models.FloatField(blank=True, null=True, verbose_name='支付利息手续费及佣金的现金')),
                ('zfbdhldxj', models.FloatField(blank=True, null=True, verbose_name='支付保单红利的现金')),
                ('qzzgsxsssgdtzsddxj', models.FloatField(blank=True, null=True, verbose_name='其中子公司吸收少数股东投资收到的现金')),
                ('qzzgszfgssgddgllr', models.FloatField(blank=True, null=True, verbose_name='其中子公司支付给少数股东的股利利润')),
                ('tzxfdcdzjjtx', models.FloatField(blank=True, null=True, verbose_name='投资性房地产的折旧及摊销')),
            ],
        ),
        migrations.CreateModel(
            name='Profit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='机构ID')),
                ('organization_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='机构名称')),
                ('announcement_date', models.DateField(null=True, verbose_name='公告日期')),
                ('begin_date', models.DateField(null=True, verbose_name='开始日期')),
                ('end_date', models.DateField(null=True, verbose_name='截止日期')),
                ('report_year', models.DateField(null=True, verbose_name='报告年度')),
                ('merge_type', models.CharField(blank=True, max_length=128, null=True, verbose_name='合并类型')),
                ('report_source', models.CharField(blank=True, max_length=128, null=True, verbose_name='报表来源')),
                ('yyzsr', models.FloatField(blank=True, null=True, verbose_name='营业总收入')),
                ('qzyysr', models.FloatField(blank=True, null=True, verbose_name='其中营业收入')),
                ('yyzcb', models.FloatField(blank=True, null=True, verbose_name='营业总成本')),
                ('qzyycb', models.FloatField(blank=True, null=True, verbose_name='其中营业成本')),
                ('yysjjfj', models.FloatField(blank=True, null=True, verbose_name='营业税金及附加')),
                ('xsfy', models.FloatField(blank=True, null=True, verbose_name='销售费用')),
                ('glfy', models.FloatField(blank=True, null=True, verbose_name='管理费用')),
                ('ktfy', models.FloatField(blank=True, null=True, verbose_name='堪探费用')),
                ('cwfy', models.FloatField(blank=True, null=True, verbose_name='财务费用')),
                ('zcjzss', models.FloatField(blank=True, null=True, verbose_name='资产减值损失')),
                ('jgyjzbdjsy', models.FloatField(blank=True, null=True, verbose_name='加公允价值变动净收益')),
                ('tzsy', models.FloatField(blank=True, null=True, verbose_name='投资收益')),
                ('qzdlyqyhhyqydtzsy', models.FloatField(blank=True, null=True, verbose_name='其中对联营企业和合营企业的投资收益')),
                ('hdsy', models.FloatField(blank=True, null=True, verbose_name='汇兑收益')),
                ('yxyylrdqtkm', models.FloatField(blank=True, null=True, verbose_name='影响营业利润的其他科目')),
                ('yylr', models.FloatField(blank=True, null=True, verbose_name='营业利润')),
                ('jbtsr', models.FloatField(blank=True, null=True, verbose_name='加补贴收入')),
                ('yywsr', models.FloatField(blank=True, null=True, verbose_name='营业外收入')),
                ('jyywzc', models.FloatField(blank=True, null=True, verbose_name='减营业外支出')),
                ('qzfldzcczss', models.FloatField(blank=True, null=True, verbose_name='其中非流动资产处置损失')),
                ('jyxlrzedqtkm', models.FloatField(blank=True, null=True, verbose_name='加影响利润总额的其他科目')),
                ('lrze', models.FloatField(blank=True, null=True, verbose_name='利润总额')),
                ('jsds', models.FloatField(blank=True, null=True, verbose_name='减所得税')),
                ('jyxjlrdqtkm', models.FloatField(blank=True, null=True, verbose_name='加影响净利润的其他科目')),
                ('jlr', models.FloatField(blank=True, null=True, verbose_name='净利润')),
                ('gsymgssyzdjlr', models.FloatField(blank=True, null=True, verbose_name='归属于母公司所有者的净利润')),
                ('ssgdsy', models.FloatField(blank=True, null=True, verbose_name='少数股东损益')),
                ('mgsy', models.FloatField(blank=True, null=True, verbose_name='每股收益')),
                ('jbmgsy', models.FloatField(blank=True, null=True, verbose_name='基本每股收益')),
                ('xsmgsy', models.FloatField(blank=True, null=True, verbose_name='稀释每股收益')),
                ('qtzhsy', models.FloatField(blank=True, null=True, verbose_name='其他综合收益')),
                ('zhsyze', models.FloatField(blank=True, null=True, verbose_name='综合收益总额')),
                ('qzgsymgs', models.FloatField(blank=True, null=True, verbose_name='其中归属于母公司')),
                ('qzgsyssgd', models.FloatField(blank=True, null=True, verbose_name='其中归属于少数股东')),
                ('lxsr', models.FloatField(blank=True, null=True, verbose_name='利息收入')),
                ('yzbf', models.FloatField(blank=True, null=True, verbose_name='已赚保费')),
                ('sxfjyjsr', models.FloatField(blank=True, null=True, verbose_name='手续费及佣金收入')),
                ('lxzc', models.FloatField(blank=True, null=True, verbose_name='利息支出')),
                ('sxfjyjzc', models.FloatField(blank=True, null=True, verbose_name='手续费及佣金支出')),
                ('tbj', models.FloatField(blank=True, null=True, verbose_name='退保金')),
                ('pfzcje', models.FloatField(blank=True, null=True, verbose_name='赔付支出净额')),
                ('tqbxhtzbjje', models.FloatField(blank=True, null=True, verbose_name='提取保险合同准备金净额')),
                ('bdhlzc', models.FloatField(blank=True, null=True, verbose_name='保单红利支出')),
                ('fbfy', models.FloatField(blank=True, null=True, verbose_name='分保费用')),
                ('qzfldzcczld', models.FloatField(blank=True, null=True, verbose_name='其中非流动资产处置利得')),
            ],
        ),
    ]
