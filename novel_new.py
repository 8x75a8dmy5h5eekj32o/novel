'''
Created at :2017-10-01 14:38:05
By : C4rB0n


                   _ooOoo_ 
                  o8888888o 
                  88" . "88 
                  (| -_- |) 
                  O\  =  /O 
               ____/`---'\____ 
             .'  \\|     |//  `. 
            /  \\|||  :  |||//  \ 
           /  _||||| -:- |||||-  \ 
           |   | \\\  -  /// |   | 
           | \_|  ''\---/''  |   | 
           \  .-\__  `-`  ___/-. / 
         ___`. .'  /--.--\  `. . __ 
      ."" '<  `.___\_<|>_/___.'  >'"". 
     | | :  `- \`.;`\ _ /`;.`/ - ` : | | 
     \  \ `-.   \_ __\ /__ _/   .-` /  / 
======`-.____`-.___\_____/___.-`____.-'====== 
                   `=---=' 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
         佛祖保佑       永无BUG 

'''
import requests,urllib,re,time,os,threading
from bs4 import BeautifulSoup

FUZZ_STR = '<div class="list-lastupdate">'
TRUE_STR = '<dl class="chapter-list clrfix">'

#所有小说网爬虫的父类，某些统一功能由此实现
class Main_spider(object):
	"""
		所有小说网爬虫的父类，某些统一功能由此实现
	"""
	def __init__(self):
		self.count 		= 0		#
		self.start		= 0
		self.html 		= ''	#每个页面的html文本
		self.url		= ''	#每个页面的link
		self.chapter_li = []	#每个小说的文章列表
		self.href_li 	= []	#每个小说的文章连接列表
		self.content_li = []	#每个小说的文章内容列表
		self.CH_li 		= []	#每文章链接以及内容的合集
		
	def get_html(self,url,choice):
		headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
		html = requests.get(url,headers=headers)
		if choice == 1:
			html.encoding = 'gbk'
		elif choice == 2:
			html.encoding = 'utf-8'
		self.url = html.url
		self.html = html.text
	


class UC_Spider(Main_spider):
	"""
		书源：UC书盟
	"""
	def __init__(self,Novel_name):
		super(UC_Spider,self).__init__()
		self.Novel_name = Novel_name
		self.host = 'http://www.uctxt.com'
		self.interface = "http://www.uctxt.com/modules/article/search.php?searchkey="
		#UC书盟的搜书系统对小说名进行gb2312编码
		self.Novel_name_gb2312 = urllib.parse.quote(self.Novel_name.encode('gb2312'))
		#构造搜书接口
		self.Novel_link = self.interface + self.Novel_name_gb2312
	
	#用来匹配小说文章标题跟文章标题目标链接
	def get_CH_li(self):
		#match example : <a href="349067.html">003章 绝症</a></dd>
		re_original = r'<a href=".+\.html">.+</a></dd>'
		#match the chapter name
		re_chapter = r'>.+</a>'
		#match the href
		re_href = r'".+\.html'
		#match the dd for example:<a href="9338018.html">第七十一章 拉拢</a></dd>
		pattern_dd = re.compile(re_original)
		matchs_dd = pattern_dd.findall(self.html)
		#------------
		#match the chaptr
		pattern_chapter = re.compile(re_chapter)
		#add the chapter to self.chapter_li
		for original in matchs_dd:
			match_chapter = pattern_chapter.findall(str(original))[0]
			chapter = match_chapter.replace('>','').replace('</a','')
			self.chapter_li.append(chapter)
		#------------
		#match the href
		pattern_href = re.compile(re_href)
		#add the href to self.href_li
		for original in matchs_dd:
			match_href = pattern_href.findall(original)[0]
			href = self.url + match_href.replace('"','')
			self.href_li.append(href)
		#------------
	#筛选因模糊搜索而出现的多余选项
	def get_true_novel(self):
		hrefs = []
		re_fuzz_name = r'<a href="/.+/">[\u4e00-\u9fa5]+</a>'
		re_a = r'<a href=".+".'
		pattern_name = re.compile(re_fuzz_name)
		pattern_a = re.compile(re_a)
		li = pattern_name.findall(self.html)
		print("[!]现在有%d个相似的小说，请自行选择 >>" % len(li))
		count = 1
		for name in li:
			novel_a = pattern_a.findall(name)[0]
			a = self.host + novel_a.replace('<a href="','').replace('">','')
			hrefs.append(a)
			novel_name = name.replace(novel_a,"").replace("</a>","")
			print("\n\t\t[%d] %s" % (count,novel_name))
			count += 1
		num = int(input(" >> ")) - 1
		return hrefs[num]

	#抓取内容
	def get_content(self,link):
		#get the content web
		self.get_html(link,1)
		#match the content
		re_content = r'.+<br />.+'
		pattern_content = re.compile(re_content)
		try:
			match_content = pattern_content.findall(self.html)[0]
			content = match_content.replace('<br />','\n').replace('&nbsp;',' ').replace('/p>','')
			self.content_li.append(content)
		except IndexError :
			print("[!]Has no content")

class ZHETIAN_Spider(Main_spider):
	"""
		书源：遮天小说网
	"""
	def __init__(self):
		super(ZHETIAN_Spider,self).__init__()


#所有功能的入口
def main():
	###############################
	#函数区
	#格式化输出
	def init_print(chapter_li):
		os.system('cls')
		count = 1
		print('\n----------------')
		for chapter in chapter_li:
			print('[%d] %s' % (count , chapter))
			count += 1
		print('----------------')
	#save file
	def save_novel_file(name,contents):
		file_name = '%s.txt' % name
		file = open(file_name , 'a')
		for content in contents:
			file.write(content)
		file.close()
	#启动uc书盟爬虫
	def UC(Novel_name):
		uc = UC_Spider(Novel_name)
		uc.get_html(uc.Novel_link,1)
		
		#deal with fuzz search
		if FUZZ_STR in uc.html:
			new_link = uc.get_true_novel()
			uc.get_html(new_link,1)
		if TRUE_STR in uc.html:
			uc.get_CH_li()
			init_print(uc.chapter_li)
		#选择下载的文章
		start = int(input('[+] start :')) - 1
		over = int(input('[+] over :'))
		for href in uc.href_li[start:over]:
			uc.get_content(href)
		save_novel_file(Novel_name,uc.content_li)
		
	###############################
	
	#--------------------------------------------------

	###############################
	#代码区

	#由用户输入小说名称
	Novel_name = input('[+] Novel Name： ')
	UC(Novel_name)

	##############################

if __name__ == '__main__':
	main()