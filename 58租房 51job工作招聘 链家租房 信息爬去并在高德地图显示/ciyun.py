#!/usr/bin/Python
# -*- coding: utf-8 -*-
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud, STOPWORDS
###当前文件路径
d = path.dirname(__file__)

# Read the whole text.
file = open(path.join(d, 'qq.txt'),encoding = 'utf-8').read()
##进行分词
#刚开始是分完词放进txt再打开却总是显示不出中文很奇怪
default_mode =jieba.cut(file)
text = " ".join(default_mode)


# read the mask image
# taken from
# http://www.stencilry.org/stencils/movies/alice%20in%20wonderland/255fk.jpg
alice_mask = np.array(Image.open(path.join(d, "qq.jpg")))
stopwords = set(STOPWORDS)
stopwords.add("said")
fontname = 'simsun.ttf'
wc = WordCloud(  
    #设置字体，不指定就会出现乱码,这个字体文件需要下载
    font_path = fontname,  
    background_color="white",   
    max_words=2000,   
    mask=alice_mask,  
    stopwords=stopwords)  
# generate word cloud
wc.generate(text)

# store to file
wc.to_file(path.join(d, "qq_result1.jpg"))

# show
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.figure()
plt.imshow(alice_mask, cmap=plt.cm.gray, interpolation='bilinear')
plt.axis("off")
plt.show()
